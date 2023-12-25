from enum import Enum

class NodeState(Enum):
	UNEXPANDED = 0
	LIVE = 1
	SOLVED = 2

MAX_DEPTH = 5
MAX_FEN_HISTORY = 2
PROCESS_COUNT = 8
MAX_VALUE = 10**11