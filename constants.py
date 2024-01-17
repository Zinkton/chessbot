from enum import Enum

class NodeState(Enum):
	UNEXPANDED = 0
	LIVE = 1
	SOLVED = 2

MAX_DEPTH = 6
MAX_DEPTH_QUIESCENCE = 0
MAX_DEPTH_AI = 3
MAX_FEN_HISTORY = 2
PROCESS_COUNT = 8
MAX_VALUE = 10**6
OPENING_BOOK = False
SECONDS_PER_MOVE = 5
EXACT = 0
UPPERBOUND = 1
LOWERBOUND = 2
MIN_DEPTH = 5