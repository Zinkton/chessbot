from typing import Dict, Iterator, List, Optional, Tuple

import chess
from constants import NodeState
import constants

class ChessNode:
    def __init__(self, move, value, min_value = constants.MAX_VALUE, children: List["ChessNode"] = None, parent: "ChessNode" = None, legal_moves = None, move_index = None):
        self.move = move
        self.min_value = min_value
        self.children = children
        self.parent = parent
        self.legal_moves = legal_moves
        self.move_index = move_index
        self.value = value
        self.state = NodeState.UNEXPANDED
        
    def __repr__(self):        
        return '; '.join([str(self.move), str(self.min_value), str(len(self.children)), str(self.value), str(self.state)])
    
class MtdfNode:
    def __init__(self, move: Optional[chess.Move], value: int, gamma: Optional[int] = None, hash: int = 0):
        self.move = move
        self.value = value
        self.gamma = gamma
        self.hash = hash

    def __repr__(self):
        return '; '.join([str(self.move), str(self.gamma), str(self.value), str(self.hash)])