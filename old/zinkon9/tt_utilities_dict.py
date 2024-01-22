from typing import Dict, Optional, Tuple

import custom_chess as chess


def probe_tt_scores(tt_scores: Dict, hash: int) -> Optional[Tuple[int, int, int]]:
    return tt_scores.get(hash, None)
    
def save_tt_score(tt_scores: Dict, depth_left: int, turn: bool, node_type: int, saved_value: Optional[Tuple[int, int, int]], hash: int, score: int):
    if saved_value is None or saved_value[0] <= depth_left: # no touching
        tt_scores[hash] = (depth_left, score if turn else -score, node_type)

def probe_tt_killers(tt_killers: Dict, hash: int) -> Optional[chess.Move]:
    return tt_killers.get(hash, None)
    
def save_tt_killer(tt_killers: Dict, move: chess.Move, hash: int):
    tt_killers[hash] = move