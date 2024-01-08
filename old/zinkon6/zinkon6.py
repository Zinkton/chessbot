import random, time, chess, uuid, math, nodestatus, zinkon6
from chess import Board, Move
from multiprocessing import Pool, Array

last_fen = []
last_score = 0

def get_move(input):
	global last_fen
	board = Board(input['boardFen'])
	time_left = input['remainingSeconds']
	is_real_time = input['isRealTime']
	max_depth = 5
	enemy_piece_count = get_piece_count(board, not board.turn)
	ally_piece_count = get_piece_count(board, board.turn)
	total_piece_count = enemy_piece_count + ally_piece_count
	move_scores = [[move, 0] for move in board.legal_moves]
	
	legal_move_count = len(move_scores)

	if is_real_time and time_left <= 15:
		max_depth = 1
	elif is_real_time and time_left <= 30:
		max_depth = 2
	elif is_real_time and time_left <= 60:
		max_depth = 3
	elif is_real_time and time_left <= 180:
		max_depth = 4
	elif enemy_piece_count == 0 and total_piece_count < 3:
		max_depth = 5

	print('total_piece_count %s' % (enemy_piece_count + ally_piece_count))
	print('depth %s' % max_depth)
	now = time.time()
	move_scores = process_scores(board, move_scores, max_depth)
	time_taken = time.time() - now
	print('took %s seconds' % time_taken)
	for move_score in move_scores:
		print(move_score)
	best_moves = [move_score[0] for move_score in move_scores if move_score[1] == move_scores[0][1]]
	choice = random.choice(best_moves)
	board.push(choice)
	last_fen.append(board.board_fen())
	if len(last_fen) == 3:
		del last_fen[0]

	return choice
	# return None

def get_piece_count(board, color):
	n = len(board.pieces(chess.KNIGHT, color))
	b = len(board.pieces(chess.BISHOP, color))
	r = len(board.pieces(chess.ROOK, color))
	q = len(board.pieces(chess.QUEEN, color))

	return n + b + r + q

def get_piece_score(board):
	white_score = 0.0
	black_score = 0.0
	now = time.time()
	white_pawns = board.pieces(chess.PAWN, chess.WHITE)
	black_pawns = board.pieces(chess.PAWN, chess.BLACK)
	white_knights = board.pieces(chess.KNIGHT, chess.WHITE)
	black_knights = board.pieces(chess.KNIGHT, chess.BLACK)
	white_bishops = board.pieces(chess.BISHOP, chess.WHITE)
	black_bishops = board.pieces(chess.BISHOP, chess.BLACK)
	white_rooks = board.pieces(chess.ROOK, chess.WHITE)
	black_rooks = board.pieces(chess.ROOK, chess.BLACK)
	white_queens = board.pieces(chess.QUEEN, chess.WHITE)
	black_queens = board.pieces(chess.QUEEN, chess.BLACK)
	
	white_pawn_count = len(white_pawns)
	black_pawn_count = len(black_pawns)
	white_knight_count = len(white_knights)
	black_knight_count = len(black_knights)
	white_bishop_count = len(white_bishops)
	black_bishop_count = len(black_bishops)
	white_rook_count = len(white_rooks)
	black_rook_count = len(black_rooks)
	white_queen_count = len(white_queens)
	black_queen_count = len(black_queens)
	
	white_score += white_pawn_count * 10
	black_score += black_pawn_count * 10
	white_score += white_knight_count * 30
	black_score += black_knight_count * 30
	white_score += white_bishop_count * 30
	black_score += black_bishop_count * 30
	white_score += white_rook_count * 50
	black_score += black_rook_count * 50
	white_score += white_queen_count * 90
	black_score += black_queen_count * 90

	result = 0
	if white_score > black_score:
		result = min(9999999999.0, (white_score - black_score) * (white_score / max(1.0, black_score))) / 10.0
	else:
		result = max(-9999999999.0, (white_score - black_score) * (black_score / max(1.0, white_score))) / 10.0
	
	return result

def get_detailed_score(board, evaluation):
	white_score = 0
	black_score = 0

	white_pawns = board.pieces(chess.PAWN, chess.WHITE)
	black_pawns = board.pieces(chess.PAWN, chess.BLACK)
	white_knights = board.pieces(chess.KNIGHT, chess.WHITE)
	black_knights = board.pieces(chess.KNIGHT, chess.BLACK)
	white_bishops = board.pieces(chess.BISHOP, chess.WHITE)
	black_bishops = board.pieces(chess.BISHOP, chess.BLACK)
	white_rooks = board.pieces(chess.ROOK, chess.WHITE)
	black_rooks = board.pieces(chess.ROOK, chess.BLACK)
	white_queens = board.pieces(chess.QUEEN, chess.WHITE)
	black_queens = board.pieces(chess.QUEEN, chess.BLACK)

	last_move = board.peek()
	destination_piece = board.piece_at(last_move.to_square)
	if destination_piece.piece_type == chess.KING and abs(last_move.from_square - last_move.to_square) == 2:
		if board.turn:
			board.has_black_castled_c = True
		else:
			board.has_white_castled_c = True
		
	if board.has_white_castled_c:
		white_score += 0.5
	if board.has_black_castled_c:
		black_score += 0.5

	if board.has_kingside_castling_rights(chess.WHITE):
		white_score += 0.05
	if board.has_kingside_castling_rights(chess.BLACK):
		black_score += 0.05
	if board.has_queenside_castling_rights(chess.WHITE):
		white_score += 0.05
	if board.has_queenside_castling_rights(chess.BLACK):
		black_score += 0.05
	
	castle_w = board.has_castling_rights(chess.WHITE)
	castle_b = board.has_castling_rights(chess.BLACK)

	for white_pawn in white_pawns:
		rank = int((white_pawn / 8)) + 1
		pawn_multiplier = 1
		if evaluation > 0:
			pawn_multiplier = min(100.0, evaluation)
		piece_value = (rank - 2) * 2 * pawn_multiplier
		piece_value += get_attack_value(board, white_pawn, chess.WHITE)
		white_score += piece_value / 100.0
	for black_pawn in black_pawns:
		rank = int((black_pawn / 8)) + 1
		pawn_multiplier = 1
		if evaluation < 0:
			pawn_multiplier = min(100.0, abs(evaluation))
		piece_value = (7 - rank) * 2 * pawn_multiplier
		piece_value += get_attack_value(board, black_pawn, chess.BLACK)
		black_score += piece_value / 100.0
	for white_knight in white_knights:
		rank = int((white_knight / 8)) + 1
		piece_value = 6 - abs(6 - rank)
		if board.has_white_castled_c or (rank > 1 and castle_w):
			piece_value += 25
		piece_value += get_attack_value(board, white_knight, chess.WHITE)
		white_score += piece_value / 100.0
	for black_knight in black_knights:
		rank = int((black_knight / 8)) + 1
		piece_value = 3 - abs(3 - rank)
		if board.has_black_castled_c or (rank < 8 and castle_b):
			piece_value += 25
		piece_value += get_attack_value(board, black_knight, chess.BLACK)
		black_score += piece_value / 100.0
	for white_bishop in white_bishops:
		piece_value = get_attack_value(board, white_bishop, chess.WHITE)
		rank = int((white_bishop / 8)) + 1
		if board.has_white_castled_c or (rank > 1 and castle_w):
			piece_value += 25
		white_score += piece_value / 100.0
	for black_bishop in black_bishops:
		piece_value = get_attack_value(board, black_bishop, chess.BLACK)
		rank = int((black_bishop / 8)) + 1
		if board.has_black_castled_c or (rank < 8 and castle_b):
			piece_value += 25
		black_score += piece_value / 100.0
	for white_rook in white_rooks:
		piece_value = get_attack_value(board, white_rook, chess.WHITE)
		white_score += piece_value / 100.0
	for black_rook in black_rooks:
		piece_value = get_attack_value(board, black_rook, chess.BLACK)
		black_score += piece_value / 100.0
	for white_queen in white_queens:
		piece_value = get_attack_value(board, white_queen, chess.WHITE)
		rank = int((white_queen / 8)) + 1
		if board.has_white_castled_c or (rank > 1 and castle_w):
			piece_value += 25
		white_score += piece_value / 100.0
	for black_queen in black_queens:
		piece_value = get_attack_value(board, black_queen, chess.BLACK)
		rank = int((black_queen / 8)) + 1
		if board.has_black_castled_c or (rank < 8 and castle_b):
			piece_value += 25
		black_score += piece_value / 100.0
	white_score += get_attack_value(board, board.king(chess.WHITE), chess.WHITE) / 100.0
	black_score += get_attack_value(board, board.king(chess.BLACK), chess.BLACK) / 100.0

	return (white_score - black_score) / 10.0

def get_piece_value(piece, multiplier):
	if piece == chess.PAWN:
		return 1 * multiplier
	if piece == chess.KNIGHT:
		return 3 * multiplier
	if piece == chess.BISHOP:
		return 3 * multiplier
	if piece == chess.ROOK:
		return 5 * multiplier
	if piece == chess.QUEEN:
		return 9 * multiplier
	if piece == chess.KING:
		if multiplier == 1:
			return -1
		return 20

def get_square_value(board, square, color):
	
	rank = int(square / 8) + 1
	square_score = 1
	if (color and rank > 4) or (not color and rank < 5):
		square_score += 1

	if square in [27, 28]:
		if color:
			square_score += 1
		else:
			square_score += 2
	if square in [35, 36]:
		if color:
			square_score += 2
		else:
			square_score += 1

	piece = board.piece_at(square)
	if piece:
		multiplier = 1
		if color != piece.color:
			multiplier = 2
		piece_value = get_piece_value(piece.piece_type, multiplier)
		square_score += piece_value
	
	return square_score

def get_attack_value(board, attacker, color):
	
	attack_value = 0
	if attacker in [27, 28, 35, 36]:
		attack_value += 1
	
	attacked_squares = board.attacks(attacker)
	
	for square in attacked_squares:
		attack_value += get_square_value(board, square, color)
	return attack_value

def is_leaf_bool(board, depth, max_depth):
	return depth >= max_depth or board.is_checkmate()

def is_leaf(board, depth, max_depth):
	if board.is_checkmate():
		if board.turn:
			return (True, -10**10 - (max_depth - depth))
		else:
			return (True, 10**10 + (max_depth - depth))
	elif depth >= max_depth:
		return (True, get_piece_score(board))
	return (False, 0)

def RecSSS(node, board, depth, max_depth):
	if zinkon6.good_score_found:
		return 0
	is_leaf_result = is_leaf(board, depth, max_depth)
	if is_leaf_result[0]:
		node[1] = nodestatus.SOLVED
		return min(is_leaf_result[1], node[2])
	if zinkon6.good_score_found:
		return 0
	if node[1] == nodestatus.UNEXPANDED:
		node[1] = nodestatus.LIVE
		legal_moves = list(board.legal_moves)
		if not legal_moves:
			node[1] = nodestatus.SOLVED
			return min(0, node[2])
		for x in range(len(legal_moves)):
			son = [legal_moves[x], nodestatus.UNEXPANDED, node[2], [], node, legal_moves, x]
			board.push(legal_moves[x])
			if is_leaf_bool(board, depth + 1, max_depth):
				node[3].append(son)
			else:
				s_legal_moves = list(board.legal_moves)
				if s_legal_moves:
					gson = [s_legal_moves[0], nodestatus.UNEXPANDED, node[2], [], son, s_legal_moves, 0]
					node[3].append(gson)
				else:
					node[3].append(son)
			board.pop()
	gson = max(node[3], key=lambda s: s[2])
	while gson[2] == node[2] and gson[1] != nodestatus.SOLVED:
		if zinkon6.good_score_found:
			return 0
		is_gson = gson[4][0] != node[0]
		depth_adder = 1
		if is_gson:
			depth_adder = 2
			board.push(gson[4][0])
		board.push(gson[0])
		gson[2] = RecSSS(gson, board, depth + depth_adder, max_depth)
		if is_gson:
			board.pop()
		board.pop()
		if is_gson and gson[1] == nodestatus.SOLVED and gson[6] != (len(gson[5]) - 1):
			gson[6] += 1
			gson[0] = gson[5][gson[6]]
			gson[1] = nodestatus.UNEXPANDED
			gson[3] = []
		gson = max(node[3], key=lambda s: s[2])
	if gson[1] == nodestatus.SOLVED:
		node[1] = nodestatus.SOLVED

	return gson[2]


def initProcess():
	global last_score
	zinkon6.good_score_found = False
	zinkon6.last_score = last_score

def solve_position(input):
	(board, max_depth, move) = (input[0], input[1], input[2])
	root_node = [move, nodestatus.UNEXPANDED, 10**11, [], False, False, False]
	while not zinkon6.good_score_found and root_node[1] != nodestatus.SOLVED:
		root_node[2] = RecSSS(root_node, board, 1, max_depth)
	if root_node[1] == nodestatus.SOLVED:
		if zinkon6.last_score > root_node[2]:
			zinkon6.last_score = root_node[2]
			zinkon6.good_score_found = True
		return [move, root_node[2]]
	return None

def process_scores(board, move_scores, max_depth):
	global last_fen
	global last_score

	with Pool(processes=8,initializer=initProcess) as p:
		inputs = []
		for x in range(len(move_scores)):
			board_copy = board.copy()
			board_copy.push(move_scores[x][0])
			inputs.append([board_copy, max_depth, move_scores[x][0]])

		results = [result for result in p.map(solve_position, inputs) if result]
		print(results)
		results.sort(key=lambda result: result[1], reverse=board.turn)
		last_score = max(last_score, results[0][1])

		if len(last_fen) == 2 and len(results) > 1:
			if board.turn and results[0][1] >= 0 and results[1][1] >= 0 or not board.turn and results[0][1] <= 0 and results[1][1] <= 0:
				if results[0][1] == results[1][1]:
					best_moves = [result for result in results if result[1] == results[0][1]]
					culprit = None
					for m in best_moves:
						board.push(m[0])
						if board.board_fen() == last_fen[0]:
							culprit = m
							board.pop()
							break
						board.pop()
					if culprit:
						results.remove(culprit)
				else:
					board.push(results[0][0])
					if board.board_fen() == last_fen[0]:
						del results[0]
					board.pop()

		best_results = [result for result in results if result[1] == results[0][1]]

		for best_result in best_results:
			board.push(best_result[0])
			board.has_white_castled_c = False
			board.has_black_castled_c = False
			best_result[1] += get_detailed_score(board, best_result[1])
			board.pop()

		best_results.sort(key=lambda best_result: best_result[1], reverse=board.turn)

		return best_results
