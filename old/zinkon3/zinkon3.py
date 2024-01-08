import random, time, chess, uuid
from chess import Board, Move
from multiprocessing import Pool

def get_move(input):
	board = Board(input['boardFen'])
	time_left = input['remainingSeconds']
	is_real_time = input['isRealTime']
	max_depth = 3
	enemy_piece_count = get_piece_count(board, not board.turn)
	ally_piece_count = get_piece_count(board, board.turn)
	total_piece_count = enemy_piece_count + ally_piece_count
	move_scores = [[move, 0] for move in board.legal_moves]
	
	legal_move_count = len(move_scores)
	print(is_real_time)
	print(time_left)
	if is_real_time and time_left <= 15:
		max_depth = 1
	elif is_real_time and time_left <= 30:
		max_depth = 2
	elif is_real_time and time_left <= 60:
		max_depth = 3
	elif is_real_time and time_left > 300 or legal_move_count <= 8 or total_piece_count < 8 and (enemy_piece_count < 4 or ally_piece_count < 4):
		max_depth = 4
	
	print('total_piece_count %s' % (enemy_piece_count + ally_piece_count))
	print('depth %s' % max_depth)
	now = time.time()
	move_scores = process_scores(board, move_scores, max_depth)
	time_taken = time.time() - now
	print('took %s seconds' % time_taken)
	move_scores.sort(key=lambda move_score: move_score[1], reverse=board.turn)
	best_moves = [move_score[0] for move_score in move_scores if move_score[1] == move_scores[0][1]]
	
	print('evaluation: %s' % move_scores[0][1])
	print(best_moves)

	return random.choice(best_moves)

def get_piece_count(board, color):
	n = len(board.pieces(chess.KNIGHT, color))
	b = len(board.pieces(chess.BISHOP, color))
	r = len(board.pieces(chess.ROOK, color))
	q = len(board.pieces(chess.QUEEN, color))

	return n + b + r + q

def get_piece_score(board):
	white_score = 0.0
	black_score = 0.0

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
		piece_value = (rank - 2) * 2
		piece_value += get_attack_value(board, white_pawn, chess.WHITE)
		white_score += piece_value / 100.0
	for black_pawn in black_pawns:
		rank = int((black_pawn / 8)) + 1
		piece_value = (7 - rank) * 2
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

	if white_score > black_score:
		return min(9999999999.0, (white_score - black_score) * (white_score / max(1.0, black_score))) / 10.0
	else:
		return max(-9999999999.0, (white_score - black_score) * (black_score / max(1.0, white_score))) / 10.0


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

def process_scores(board, move_scores, max_depth):
	inputs = []

	for x in range(len(move_scores)):
		board_copy = board.copy()
		board_copy.has_white_castled_c = False
		board_copy.has_black_castled_c = False
		inputs.append([board_copy, move_scores[x], 1, max_depth])
	
	with Pool(8) as p:
		unordered_results = p.imap_unordered(process_score, inputs)
		results = []
		for res in unordered_results:
			results.append(res)
			
		return results

def process_score(input):
	board = input[0]
	move_score = input[1]
	depth = input[2]
	max_depth = input[3]

	castled_w = board.has_white_castled_c
	castled_b = board.has_black_castled_c

	board.push(move_score[0])

	if board.is_checkmate():
		if board.turn:
			move_score[1] = -10000000000 - (max_depth - depth)
		else:
			move_score[1] = 10000000000 + (max_depth - depth)
	elif depth >= max_depth:
		move_score[1] = get_piece_score(board)
	else:
		new_move_scores = []

		for move in board.legal_moves:
			new_move_score = [move, 0]
			process_score([board, new_move_score, depth + 1, max_depth])
			new_move_scores.append(new_move_score)
		
		if new_move_scores:
			if board.turn:
				max_score =  max(new_move_scores, key=lambda s: s[1])
				move_score[1] = max_score[1]
			else:
				min_score = min(new_move_scores, key=lambda s: s[1])
				move_score[1] = min_score[1]
		else:
			move_score[1] = 0
	
	board.pop()
	board.has_white_castled_c = castled_w
	board.has_black_castled_c = castled_b

	return move_score