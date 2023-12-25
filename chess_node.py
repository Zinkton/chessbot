from constants import NodeState
import constants

class ChessNode:
    def __init__(self, move, value, min_value = constants.MAX_VALUE, children = None, parent = None, legal_moves = None, move_index = None):
        self.move = move
        self.min_value = min_value
        self.children = children
        self.parent = parent
        self.legal_moves = legal_moves
        self.move_index = move_index
        self.value = value
        self.state = NodeState.UNEXPANDED