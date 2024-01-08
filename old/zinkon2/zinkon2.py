import random, time, chess, uuid
from chess import Board, Move
from multiprocessing import Pool

def get_move(input):
	board = Board(input['boardFen'])
	time_left = input['remainingSeconds']
	is_real_time = input['isRealTime']
	max_depth = 4
	
	if is_real_time and time_left <= 30:
		max_depth = 2
	elif is_real_time and time_left <= 90:
		max_depth = 3
	
	
	move_scores = [[move, 0] for move in board.legal_moves]
	move_scores = process_scores(board, move_scores, 1, max_depth)

	move_scores.sort(key=lambda move_score: move_score[1], reverse=board.turn)
	print(move_scores)
	best_moves = [move_score[0] for move_score in move_scores if move_score[1] == move_scores[0][1]]

	return random.choice(best_moves)

def check_game_over(board):
	if board.is_checkmate():
		if board.turn:
			return (-100, True)
		else:
			return (100, True)

	if board.is_stalemate():
		return (0, True)

	return (0, False)

def get_piece_score(board):
	score = 0
	score += len(board.pieces(chess.PAWN, chess.WHITE))
	score -= len(board.pieces(chess.PAWN, chess.BLACK))
	score += len(board.pieces(chess.KNIGHT, chess.WHITE)) * 3
	score -= len(board.pieces(chess.KNIGHT, chess.BLACK)) * 3
	score += len(board.pieces(chess.BISHOP, chess.WHITE)) * 3
	score -= len(board.pieces(chess.BISHOP, chess.BLACK)) * 3
	score += len(board.pieces(chess.ROOK, chess.WHITE)) * 5
	score -= len(board.pieces(chess.ROOK, chess.BLACK)) * 5
	score += len(board.pieces(chess.QUEEN, chess.WHITE)) * 9
	score -= len(board.pieces(chess.QUEEN, chess.BLACK)) * 9

	return score

def get_board_score(board):
	(score, is_game_over) = check_game_over(board)
	if (is_game_over):
		return (score, is_game_over)

	score = get_piece_score(board)

	return (score, False)

def process_scores(board, move_scores, depth, max_depth):
	inputs = []
	for x in range(len(move_scores)):
		inputs.append((board, move_scores[x], depth, max_depth))
	
	with Pool(8) as p:
		return p.starmap(process_score, inputs)

def process_score(board, move_score, depth, max_depth):
	new_board = board.copy()
	new_board.push(move_score[0])
	(score, isGameOver) = get_board_score(new_board)
	move_score[1] = score

	if not isGameOver and depth < max_depth:
		new_move_scores = [[move, 0] for move in new_board.legal_moves]
		for x in range(len(new_move_scores)):
			process_score(new_board, new_move_scores[x], depth + 1, max_depth)

		if new_board.turn:
			move_score[1] = max(new_move_scores, key=lambda s: s[1])[1]
		else:
			move_score[1] = min(new_move_scores, key=lambda s: s[1])[1]
	
	return move_score