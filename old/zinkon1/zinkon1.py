import random, time, chess
from chess import Board, Move

def get_move(input):
	board = Board(input['boardFen'])
	time_left = input['remainingSeconds']
	is_real_time = input['isRealTime']
	max_depth = 3
	
	if is_real_time and time_left <= 30:
		max_depth = 2

	move_scores = [[move, 0] for move in board.legal_moves]
	process_scores(board, move_scores, 1, max_depth)
	is_white_move = board.fen().split(' ')[1] == 'w'

	move_scores.sort(key=lambda move_score: move_score[1], reverse=is_white_move)
	best_moves = [move_score[0] for move_score in move_scores if move_score[1] == move_scores[0][1]]
	return random.choice(best_moves)

def get_board_score(board):
	fen = board.fen().split(' ')
	is_white_move = fen[1] == 'w'

	if board.is_checkmate():
		if is_white_move:
			return (-100, True)
		else:
			return (100, True)

	if board.is_stalemate():
		return (0, True)
	
	pieces = fen[0].replace('/', '')
	score = 0
	for piece in pieces:
		if piece == 'p':
			score -= 1
		if piece == 'n' or piece == 'b':
			score -= 3
		if piece == 'r':
			score -= 5
		if piece == 'q':
			score -= 9
		if piece == 'P':
			score += 1
		if piece == 'N' or piece == 'B':
			score += 3
		if piece == 'R':
			score += 5
		if piece == 'Q':
			score += 9

	return (score, False)

def process_scores(board, move_scores, depth, max_depth):
	for x in range(len(move_scores)):
		new_board = Board(board.fen())
		new_board.push(move_scores[x][0])
		(score, isGameOver) = get_board_score(new_board)
		move_scores[x][1] = score

		if not isGameOver and depth < max_depth:
			new_move_scores = [[move, 0] for move in new_board.legal_moves]
			process_scores(new_board, new_move_scores, depth + 1, max_depth)
			
			is_white_move = new_board.fen().split(' ')[1] == 'w'
			if is_white_move:
				move_scores[x][1] = max(new_move_scores, key=lambda s: s[1])[1]
			else:
				move_scores[x][1] = min(new_move_scores, key=lambda s: s[1])[1]
		