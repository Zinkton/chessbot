from ctypes import Array
from typing import List, Optional
import chess

from chess_node import MtdfNode

class MtdfInput():
    def __init__(self, board: chess.Board, initial_value: int, start: float, depth: int, root: Optional[MtdfNode] = None):
        self.board = board
        self.initial_value = initial_value
        self.start = start
        self.depth = depth
        self.root = root

class IterativeDeepeningInput():
    def __init__(self, max_depth: int, mtdf_inputs: List[MtdfInput]):
        self.max_depth = max_depth
        self.mtdf_inputs = mtdf_inputs