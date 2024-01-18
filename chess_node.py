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
    def __init__(self, move: Optional[chess.Move], value: int, children: Dict[chess.Move, "MtdfNode"] = None, parent: "MtdfNode" = None, gamma: Optional[int] = None, move_generator: Iterator[Tuple[chess.Move, int]] = None, hash: int = 0, sorted_children_keys: List[int] = None, killer_move: Optional[chess.Move] = None):
        self.move = move
        self.children = children
        self.parent = parent
        self.value = value
        self.gamma = gamma
        self.move_generator = move_generator
        self.hash = hash
        self.sorted_children_keys = sorted_children_keys
        self.killer_move = killer_move
        
    def print_children(self):
        for child in self.children:
            print(child)

    def __repr__(self):
        return '; '.join([str(self.move), str(self.gamma), str(len(self.children)), str(self.value)])