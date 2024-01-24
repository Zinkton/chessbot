from typing import Dict, Optional, Tuple

import numpy as np

import custom_chess as chess
import constants


def probe_tt_scores(tt_scores: np.ndarray, hash: np.uint64) -> Optional[Tuple[int, int, int]]:
    index = hash % constants.TT_INDEX
    tt_score_key = tt_scores[index]
    if tt_score_key == 0:
        return None
    tt_score = tt_scores[constants.TT_INDEX + index]
    if tt_score_key == hash ^ tt_score:
        depth = tt_score & 0x3F
        score = (tt_score >> 6) & 0x3FFFFF
        node_type = (tt_score >> 28) & 0x03
        score = score - 4194304 if score >= 2097152 else score
        return depth, score, node_type
    else:
        return None

def save_tt_score(tt_scores: np.ndarray, depth_left: int, turn: bool, node_type: int, saved_value: Optional[Tuple[int, int, int]], hash: int, score: int):
    if saved_value is None or saved_value[0] < depth_left: # no touching
        index = hash % constants.TT_INDEX
        neutral_score = (score if turn else -score)
        neutral_score = neutral_score if neutral_score >= 0 else neutral_score + 4194304
        neutral_score = neutral_score << 6
        node_type = node_type << 28
        packed_score = depth_left | neutral_score | node_type
        score_key = hash ^ packed_score

        tt_scores[index] = score_key
        tt_scores[constants.TT_INDEX + index] = packed_score

def probe_tt_killers(tt_killers: np.ndarray, hash: int) -> Optional[chess.Move]:
    index = hash % constants.TT_INDEX
    tt_killer_key = tt_killers[index]
    if tt_killer_key == 0:
        return None
    tt_killer = int(tt_killers[constants.TT_INDEX + index])
    if tt_killer_key == hash ^ tt_killer:
        tt_killer = tt_killer
        promotion = (tt_killer >> 12) & 0x07
        promotion = promotion if promotion else None
        from_square = (tt_killer >> 6) & 0x3F
        to_square = tt_killer & 0x3F
        return chess.Move(from_square, to_square, promotion)
    else:
        return None

def save_tt_killer(tt_killers: np.ndarray, move: chess.Move, hash: int):
    index = hash % constants.INDEX_1
    promotion_value = (0 if move.promotion is None else move.promotion)
    packed_value = (promotion_value << 12) | (move.from_square << 6) | move.to_square
    tt_killers[index] = hash ^ packed_value
    tt_killers[constants.INDEX_1 + index] = packed_value