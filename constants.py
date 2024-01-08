from enum import Enum

class NodeState(Enum):
	UNEXPANDED = 0
	LIVE = 1
	SOLVED = 2

MAX_DEPTH = 6
MAX_DEPTH_AI = 3
MAX_FEN_HISTORY = 2
PROCESS_COUNT = 8
MAX_VALUE = 10**11