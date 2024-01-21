import time
from typing import Optional, Tuple

import custom_chess as chess

import constants
from chess_node import MtdfNode
from constants import MAX_VALUE, SECONDS_PER_MOVE
from move_generation import is_check, generate_ordered_moves
from tt_utilities_dict import probe_tt_scores, save_tt_killer, save_tt_score
from zobrist import update_hash, zobrist_hash
from evaluation import evaluate_board

tt_scores = {}
tt_killers = {}
def solve_position_root(board: chess.Board, max_depth: int = 100) -> Tuple[int, chess.Move, int]:
    global tt_scores
    global tt_killers

    initial_value = -evaluate_board(board) if board.turn else evaluate_board(board)
    root_node = MtdfNode(move=None, value=initial_value, hash=zobrist_hash(board))
    depth, move, score = _iterative_deepening(root_node, board, tt_scores, tt_killers, max_depth)

    print(f'depth: {depth}')

    return (move, score)

def _iterative_deepening(root: MtdfNode, board: chess.Board, tt_scores, tt_killers, max_depth: Optional[int]) -> Tuple[int, chess.Move, int]:
    start = time.perf_counter()
    result = None
    for depth in range(0, max_depth + 1):
        if root.gamma is None or abs(root.gamma) < MAX_VALUE:
            mtdf_result = _mtdf(root, depth, board, tt_scores, tt_killers, start)
            if mtdf_result is not None:
                result_move, result_score = mtdf_result
                result = (depth, result_move, result_score)
        else:
            break
        
    return result

def _mtdf(root: MtdfNode, depth: int, board: chess.Board, tt_scores, tt_killers, start: Optional[float] = None) -> Tuple[chess.Move, int]:
    pos_result = probe_tt_scores(tt_scores, root.hash)
    if root.gamma is None:
        if pos_result is not None and pos_result[2] == constants.EXACT:
            root.gamma = pos_result[1] if board.turn else -pos_result[1]
        else:
            root.gamma = -root.value
    
    upper_bound = MAX_VALUE + depth
    lower_bound = -MAX_VALUE - depth
    
    while upper_bound - lower_bound > 0:
        if start and time.perf_counter() - start >= SECONDS_PER_MOVE:
            return None
        
        beta = root.gamma + 1 if root.gamma == lower_bound else root.gamma
        (best_move, root.gamma) = _alpha_beta(root.value, beta - 1, beta, depth, board, tt_scores, tt_killers, root.hash)
        
        if root.gamma < beta:
            upper_bound = root.gamma
        else:
            lower_bound = root.gamma
    
    save_tt_score(tt_scores, depth + 1, board.turn, constants.EXACT, pos_result, root.hash, root.gamma)

    return best_move, root.gamma

# @profile
def _evaluate_child(value: int, hash: int, move: chess.Move, depth_left: int, alpha: int, beta: int, board: chess.Board, best_score: Tuple[Optional[chess.Move], int], tt_scores, tt_killers) -> Tuple[int, int, int, Tuple[Optional[chess.Move], int]]:
    saved_value = probe_tt_scores(tt_scores, hash)
    score = None
    if saved_value is not None and saved_value[0] >= depth_left: # no touching
        _, saved_score, node_type = saved_value
        saved_score = saved_score if board.turn else -saved_score

        if node_type == constants.EXACT:
            score = saved_score
        elif node_type == constants.LOWERBOUND and saved_score > alpha:
            score = saved_score
        elif node_type == constants.UPPERBOUND and saved_score < beta:
            score = saved_score
    found_value = score is not None
    if not found_value:
        board.push(move)
        (best_move, score) = _alpha_beta(value, -beta, -alpha, depth_left - 1, board, tt_scores, tt_killers, hash)
        score = -score
        board.pop()

    if score >= beta:
        save_tt_score(tt_scores, depth_left, board.turn, constants.LOWERBOUND, saved_value, hash, score)
        return score, alpha, beta, (None, score) # fail-soft beta-cutoff
    elif score > alpha:
        save_tt_score(tt_scores, depth_left, board.turn, constants.EXACT, saved_value, hash, score)
        alpha = score
    else:
        save_tt_score(tt_scores, depth_left, board.turn, constants.UPPERBOUND, saved_value, hash, score)
        
    if score > best_score[1]:
        best_score = (move, score)

    return score, alpha, beta, best_score

# @profile
def _alpha_beta(value: int, alpha: int, beta: int, depth_left: int, board: chess.Board, tt_scores, tt_killers, hash: int) -> Tuple[Optional[chess.Move], int]:
    best_score = (None, -(MAX_VALUE + depth_left))

    if depth_left == 0:
        return (None, _quiescence(value, alpha, beta, board))

    for move, move_value in generate_ordered_moves(board, hash, tt_killers):
        child_hash = update_hash(hash, board, move)
        score, alpha, beta, best_score = _evaluate_child(move_value - value, child_hash, move, depth_left, alpha, beta, board, best_score, tt_scores, tt_killers)
        if best_score[0] is None:
            save_tt_killer(tt_killers, move, hash)
            return (move, score) # fail-soft beta-cutoff

    if best_score[0] is None:
        if is_check(board):
            return (None, -(MAX_VALUE + depth_left - 1))
        else:
            return (None, 0)

    return best_score


# @profile
def _quiescence(value: int, alpha: int, beta: int, board: chess.Board) -> int:
    # print(value, alpha, beta)
    return -value
    # stand_pat = -value
    # if stand_pat >= beta:
    #     return stand_pat
    # if alpha < stand_pat:
    #     alpha = stand_pat;

    # until( every_capture_has_been_examined )  {
    #     MakeCapture();
    #     score = -Quiesce( -beta, -alpha );
    #     TakeBackMove();

    #     if( score >= beta )
    #         return beta;
    #     if( score > alpha )
    #        alpha = score;
    # }
    # return alpha;

    # return -value

if __name__ == '__main__':
    # for x in range(1000):
    #     board = chess.Board()
    #     while True:
    #         legal_moves = list(board.legal_moves)
    #         my_legal_moves = list(_generate_ordered_legal_moves(board))
    #         if ((len(legal_moves) - len(my_legal_moves)) % 3 != 0):
    #             raise Exception("failure")
    #         board.push(random.choice(legal_moves))
    #         if board.outcome() is not None:
    #             break
    # print('success')
    board = chess.Board()
    stack = []
    while True:
        move, score = solve_position_root(board, 7)
        stack.append(board.san(move))
        board.push(move)
        if board.outcome(claim_draw=True):
            break
    print(stack)