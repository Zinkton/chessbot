import random, time, chess, uuid, math, nodestatus
from chess import Board, Move
from multiprocessing import Pool, Array

last_fen = []

piece_value = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

pawn_table = [
	0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
	5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,
	1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0,
	0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5,
	0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0,
	0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5,
	0.5,  1.0, 1.0,  -2.0, -2.0,  1.0,  1.0,  0.5,
	0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
knight_table = [
	-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
	-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0,
	-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0,
	-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0,
	-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0,
	-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0,
	-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0,
	-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
bishop_table = [
	-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
	-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
	-1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0,
	-1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0,
	-1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0,
	-1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0,
	-1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0,
	-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
rook_table = [
	0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
	0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5,
	-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
	-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
	-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
	-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
	-0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
	0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0]
queen_table = [
	-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
	-1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
	-1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
	-0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
	0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
	-1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
	-1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0,
	-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
king_table = [
	-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
	-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
	-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
	-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
	-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
	-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
	2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0,
	2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0]

position_value = {
	chess.WHITE: {
		chess.PAWN: pawn_table.copy()[::-1],
		chess.KNIGHT: knight_table.copy()[::-1],
		chess.BISHOP: bishop_table.copy()[::-1],
		chess.ROOK: rook_table.copy()[::-1],
		chess.QUEEN: queen_table.copy()[::-1],
		chess.KING: king_table.copy()[::-1]
	},
	chess.BLACK: {
		chess.PAWN: pawn_table.copy(),
		chess.KNIGHT: knight_table.copy(),
		chess.BISHOP: bishop_table.copy(),
		chess.ROOK: rook_table.copy(),
		chess.QUEEN: queen_table.copy(),
		chess.KING: king_table.copy()
	}
}

def get_move(input):
	global last_fen
	fen = input['boardFen']
	isFlip = fen.split(' ')[1] == 'w'
	if isFlip:
		fen = flip_and_mirror_fen(fen)
	board = Board(fen)
	time_left = input['remainingSeconds']
	is_real_time = input['isRealTime']
	max_depth = 5
	enemy_piece_count = get_piece_count(board, not board.turn)
	ally_piece_count = get_piece_count(board, board.turn)
	total_piece_count = enemy_piece_count + ally_piece_count
	move_scores = [[move, 0] for move in board.legal_moves]
	
	legal_move_count = len(move_scores)

	if is_real_time and time_left <= 30:
		max_depth = 3
	elif is_real_time and time_left <= 180:
		max_depth = 4

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

	if isFlip:
		return invert_rank(str(choice))
	return choice
	# return None

def invert_rank(squares):
    # Mapping ranks to their inverted counterparts
	rank_inversion_map = {'1': '8', '2': '7', '3': '6', '4': '5', '5': '4', '6': '3', '7': '2', '8': '1'}
	
	result = ''
	for x in range(len(squares)):
		result += rank_inversion_map.get(squares[x], squares[x])

	return result

def flip_and_mirror_fen(fen):
	# Splitting the FEN string into its parts
	parts = fen.split(' ')
	rows = parts[0].split('/')

	# Flipping and mirroring the board
	flipped_rows = []
	for row in reversed(rows):
		flipped_row = ''.join(char.swapcase() if char.isalpha() else char for char in row)
		flipped_rows.append(flipped_row)

	# Reconstructing the FEN string for the board
	flipped_fen = '/'.join(flipped_rows)
	parts[0] = flipped_fen

	# Turn reverse
	parts[1] = 'b' if parts[1] == 'w' else 'b'

	# Inverting castling rights
	castling_rights = parts[2]
	if castling_rights != '-':
		inverted_castling = ''.join(char.swapcase() for char in castling_rights)
		# Separating uppercase and lowercase letters
		uppercase_chars = [char for char in inverted_castling if char.isupper()]
		lowercase_chars = [char for char in inverted_castling if char.islower()]
		parts[2] = ''.join(uppercase_chars + lowercase_chars)

	# Invert en-passant
	if len(parts[3]) == 2:
		parts[3] = invert_rank(parts[3])

	return ' '.join(parts)

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
	
	return (result, white_score, black_score)

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

def is_leaf(node, board, depth, max_depth):
	if board.is_checkmate():
		if board.turn:
			return (True, -10**10 - (max_depth - depth))
		else:
			return (True, 10**10 + (max_depth - depth))
	elif depth >= max_depth:
		return (True, node[7])
	return (False, 0)

def RecSSS(node, board, depth, max_depth):
	is_leaf_result = is_leaf(node, board, depth, max_depth)
	if is_leaf_result[0]:
		node[1] = nodestatus.SOLVED
		return min(is_leaf_result[1], node[2])
	if node[1] == nodestatus.UNEXPANDED:
		node[1] = nodestatus.LIVE
		legal_moves = list(board.legal_moves)
		if not legal_moves:
			node[1] = nodestatus.SOLVED
			return min(0, node[2])
		for x in range(len(legal_moves)):
			s_src = board.piece_type_at(legal_moves[x].from_square)
			s_dest = board.piece_type_at(legal_moves[x].to_square)
   
			if (legal_moves[x].promotion):
				prom = legal_moves[x].promotion
				pos_score = (position_value[chess.WHITE][prom][legal_moves[x].to_square] - position_value[chess.WHITE][s_src][legal_moves[x].from_square])
				prom_score = piece_value[prom] - piece_value[s_src]
				sv = node[7] + pos_score + prom_score
			else:
				sv = node[7] + (position_value[chess.WHITE][s_src][legal_moves[x].to_square] - position_value[chess.WHITE][s_src][legal_moves[x].from_square])

			if s_dest:
				sv += piece_value[s_dest] + position_value[chess.BLACK][s_dest][legal_moves[x].to_square]
			son = [legal_moves[x], nodestatus.UNEXPANDED, node[2], [], node, legal_moves, x, sv]
			board.push(legal_moves[x])
			if is_leaf_bool(board, depth + 1, max_depth):
				node[3].append(son)
			else:
				s_legal_moves = list(board.legal_moves)
				if s_legal_moves:
					gs_src = board.piece_type_at(s_legal_moves[0].from_square)
					gs_dest = board.piece_type_at(s_legal_moves[0].to_square)
					if (s_legal_moves[0].promotion):
						g_prom = s_legal_moves[0].promotion
						g_pos_score = (position_value[chess.BLACK][g_prom][s_legal_moves[0].to_square] - position_value[chess.BLACK][gs_src][s_legal_moves[0].from_square])
						g_prom_score = piece_value[g_prom] - piece_value[gs_src]
						gsv = sv - g_pos_score - g_prom_score
					else:
						gsv = sv - (position_value[chess.BLACK][gs_src][s_legal_moves[0].to_square] - position_value[chess.BLACK][gs_src][s_legal_moves[0].from_square])
					if gs_dest:
						gsv -= piece_value[gs_dest] + position_value[chess.WHITE][gs_dest][s_legal_moves[0].to_square]
					gson = [s_legal_moves[0], nodestatus.UNEXPANDED, node[2], [], son, s_legal_moves, 0, gsv]
					node[3].append(gson)
				else:
					node[3].append(son)
			board.pop()
	gson = max(node[3], key=lambda s: s[2])
	while gson[2] == node[2] and gson[1] != nodestatus.SOLVED:
		is_gson = gson[4][0] != node[0]
		depth_adder = 1
		if is_gson:
			depth_adder = 2
			board.push(gson[4][0])
		board.push(gson[0])
		gson[2] = RecSSS(gson, board, depth + depth_adder, max_depth)
		if is_gson:
			board.pop()
		if is_gson and gson[1] == nodestatus.SOLVED and gson[6] != (len(gson[5]) - 1):
			gson[6] += 1
			gson[0] = gson[5][gson[6]]
			gson[1] = nodestatus.UNEXPANDED
			gson[3] = []
			gs_src = board.piece_type_at(gson[0].from_square)
			gs_dest = board.piece_type_at(gson[0].to_square)
			if (gson[0].promotion):
				gs_prom = gson[0].promotion
				gs_pos_score = position_value[chess.BLACK][gs_prom][gson[0].to_square] - position_value[chess.BLACK][gs_src][gson[0].from_square]
				gs_prom_score = piece_value[gs_prom] - piece_value[gs_src]
				gson[7] = gson[4][7] - gs_pos_score - gs_prom_score
			else:
				gson[7] = gson[4][7] - (position_value[chess.BLACK][gs_src][gson[0].to_square] - position_value[chess.BLACK][gs_src][gson[0].from_square])
			if gs_dest:
				gson[7] -= piece_value[gs_dest] + position_value[chess.WHITE][gs_dest][gson[0].to_square] 
		board.pop()
		gson = max(node[3], key=lambda s: s[2])
	if gson[1] == nodestatus.SOLVED:
		node[1] = nodestatus.SOLVED

	return gson[2]

def solve_position(input):
	(board, max_depth, move) = (input[0], input[1], input[2])
	src_piece = board.piece_type_at(move.from_square)
	dest_piece = board.piece_type_at(move.to_square)
	if (move.promotion):
		prom = move.promotion
		pos_score = position_value[chess.BLACK][prom][move.to_square] - position_value[chess.BLACK][src_piece][move.from_square]
		prom_score = piece_value[prom] - piece_value[src_piece]
		v = -(pos_score + prom_score)
	else:
		v = -(position_value[chess.BLACK][src_piece][move.to_square] - position_value[chess.BLACK][src_piece][move.from_square])
	if dest_piece:
		v -= piece_value[dest_piece] + position_value[chess.WHITE][dest_piece][move.to_square]
	board.push(move)
	root_node = [move, nodestatus.UNEXPANDED, 10**11, [], False, False, False, v]
	while root_node[1] != nodestatus.SOLVED:
		root_node[2] = RecSSS(root_node, board, 1, max_depth)
	
	return [move, root_node[2]]

def process_scores(board, move_scores, max_depth):
	global last_fen

	with Pool(processes=8) as p:
		inputs = []
		for x in range(len(move_scores)):
			inputs.append([board.copy(), max_depth, move_scores[x][0]])

		results = p.map(solve_position, inputs)
		results.sort(key=lambda result: result[1], reverse=board.turn)

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
			if best_result[0].promotion:
				if board.turn:
					best_result[1] += piece_value[best_result[0].promotion]
				else:
					best_result[1] -= piece_value[best_result[0].promotion]
			if board.piece_at(best_result[0].to_square):
				if board.turn:
					best_result[1] += piece_value[board.piece_at(best_result[0].to_square).piece_type]
				else:
					best_result[1] -= piece_value[board.piece_at(best_result[0].to_square).piece_type]
		# for best_result in best_results:
		# 	board.push(best_result[0])
		# 	board.has_white_castled_c = False
		# 	board.has_black_castled_c = False
		# 	best_result[1] += get_detailed_score(board, best_result[1])
		# 	board.pop()

		best_results.sort(key=lambda best_result: best_result[1], reverse=board.turn)

		return best_results
