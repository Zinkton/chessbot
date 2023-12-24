import random, time, chess
from chess import Board

def get_move(input):
	board = Board(input['boardFen'])
	legal_moves = [move for move in board.legal_moves]
	time.sleep(5)
	return random.choice(legal_moves)