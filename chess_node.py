from constants import NodeState

class ChessNode:
    def __init__(self, board, move=None, depth=0, parent=None, children=None):
        self.board = board.copy()
        self.move = move
        self.depth = depth
        self.parent = parent
        self.children = children or []
        self.value = None
        self.state = NodeState.UNEXPANDED