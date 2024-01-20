from typing import Dict, Optional, Tuple
import chess

import numpy as np
import constants
from zobrist import zobrist_hash


def probe_tt_scores(tt_scores: Dict[int, Tuple[int, int, int]], hash: int) -> Optional[Tuple[int, int, int]]:
    return tt_scores.get(hash, None)
    
def save_tt_score(tt_scores: Dict[int, Tuple[int, int, int]], depth_left: int, turn: bool, node_type: int, saved_value: Optional[Tuple[int, int, int]], hash: int, score: int):
    if saved_value is None or saved_value[0] < depth_left:
        tt_scores[hash] = (depth_left, (score if turn else -score), node_type)

def probe_tt_killers(tt_killers: Dict[int, chess.Move], hash: int) -> Optional[chess.Move]:
    return tt_killers.get(hash, None)
    
def save_tt_killer(tt_killers: Dict[int, chess.Move], move: chess.Move, hash: int):
    tt_killers[hash] = move

if __name__ == '__main__':
    board = chess.Board()
    hash = zobrist_hash(board)
    test_array = np.zeros((constants.TT_SIZE,), dtype=np.uint64)
    save_tt_killer(test_array, chess.Move.from_uci('a7a8'), hash)
    print(probe_tt_killers(test_array, hash))
    test_array.fill(0)
    save_tt_score(test_array, 3, board.turn, 1, None, hash, (2**20))
    result = probe_tt_scores(test_array, hash)
    print(result)
    some_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    print(some_list[result[2] * 2])