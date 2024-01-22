from typing import Optional

import custom_chess as chess


class MtdfNode:
    def __init__(self, move: Optional[chess.Move], value: int, gamma: Optional[int] = None, hash: int = 0):
        self.move = move
        self.value = value
        self.gamma = gamma
        self.hash = hash

    def __repr__(self):
        return '; '.join([str(self.move), str(self.gamma), str(self.value), str(self.hash)])