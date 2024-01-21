import itertools
from multiprocessing import Pool
import time
from typing import Dict, List, Optional, Tuple

import custom_chess as chess

import constants
from chess_node import MtdfNode
from constants import MAX_VALUE, SECONDS_PER_MOVE
from move_generation import is_check, generate_ordered_moves, is_checkmate, sorted_child_generator
from zobrist import update_hash, zobrist_hash
from evaluation import calculate_move_value, evaluate_board

def solve_position_multiprocess(board: chess.Board = None, max_depth: int = 100, solve_position_params: List = None, ) -> List:
    if solve_position_params is None:
        solve_position_params = []
        moves_to_evaluate = list(board.legal_moves)
        for move in moves_to_evaluate:
            board.push(move)
            solve_position_params.append([board.copy(), max_depth - 1])
            board.pop()

    depths_moves_scores = None
    with Pool(processes=constants.PROCESS_COUNT) as p:
        depths_moves_scores = p.map(solve_position_root, solve_position_params)

    depths_moves_scores = [(depth + 1, solve_position_params[i][0].peek(), score) for i, (depth, _, score) in enumerate(depths_moves_scores)]
    depths_moves_scores.sort(key=lambda x: (x[2], -x[0]))
    # print(depths_moves_scores)
    print(f'depth: {depths_moves_scores[0][0]}')
    if depths_moves_scores[0][2] <= -MAX_VALUE:
        depths_moves_scores = [depth_move_score for depth_move_score in depths_moves_scores if depth_move_score[2] <= -MAX_VALUE]
        return [depths_moves_scores[-1]]

    return depths_moves_scores



pos_table = {}
killer_table = {}
def solve_position_root(input: List) -> Tuple[int, chess.Move, int]:
    board, max_depth = input[0], input[1]
    global pos_table
    global killer_table
    # pos_table = {}
    # killer_table = {}
    initial_value = -evaluate_board(board) if board.turn else evaluate_board(board)
    root_node = MtdfNode(move=None, value=initial_value, children={}, hash=zobrist_hash(board), sorted_children_keys=[])
    (depth, move, score) = _iterative_deepening(root_node, board, pos_table, killer_table, max_depth)
    return (depth, move, score)

def _iterative_deepening(root: MtdfNode, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], max_depth: Optional[int]) -> Tuple[int, chess.Move, int]:
    start = time.perf_counter()
    result = None
    for depth in range(0, max_depth + 1):
        if root.gamma is None or abs(root.gamma) < MAX_VALUE:
            mtdf_result = _mtdf(root, depth, board, pos_table, killer_table, start)
            if mtdf_result is not None:
                result_move, result_score = mtdf_result
                result = (depth, result_move, result_score)
        else:
            break
        
    return result

def _mtdf(root: MtdfNode, depth: int, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], start: Optional[float] = None) -> Tuple[chess.Move, int]:
    pos_result = pos_table.get(root.hash, None)
    if root.gamma is None:
        if pos_result is not None and pos_result[2] == constants.EXACT:
            root.gamma = pos_result[1] if board.turn else -pos_result[1]
        else:
            root.gamma = -root.value
    
    upper_bound = MAX_VALUE + depth
    lower_bound = -MAX_VALUE - depth
    
    while upper_bound - lower_bound > 0:
        # if start and time.perf_counter() - start >= SECONDS_PER_MOVE:
        #     return None
        
        beta = root.gamma + 1 if root.gamma == lower_bound else root.gamma
        (best_move, root.gamma) = _alpha_beta(root.value, beta - 1, beta, depth, board, pos_table, killer_table, root.hash)
        
        if root.gamma < beta:
            upper_bound = root.gamma
        else:
            lower_bound = root.gamma
    
    _save_score(pos_table, depth + 1, board.turn, constants.EXACT, pos_result, root.hash, root.gamma)

    return best_move, root.gamma

# @profile
def _evaluate_child(value: int, hash: int, move: chess.Move, depth_left: int, alpha: int, beta: int, pos_table: Dict[int, Tuple[int, int, int, bool]], board: chess.Board, best_score: Tuple[Optional[chess.Move], int], killer_table: Dict[int, Optional[chess.Move]]) -> Optional[int]:
    saved_value = pos_table.get(hash, None)
    score = None
    if saved_value and saved_value[0] >= depth_left:
        
        _, saved_score, node_type = saved_value
        saved_score = saved_score if board.turn else -saved_score
        
        if node_type == constants.EXACT:
            score = saved_score
        elif node_type == constants.LOWERBOUND and saved_score > alpha:
            score = saved_score
        # elif node_type == constants.UPPERBOUND and saved_score < beta:
        #     score = saved_score
    found_value = score is not None
    if not found_value:
        board.push(move)
        (best_move, score) = _alpha_beta(value, -beta, -alpha, depth_left - 1, board, pos_table, killer_table, hash)
        score = -score
        board.pop()

    if score > beta:
        _save_score(pos_table, depth_left, board.turn, constants.LOWERBOUND, saved_value, hash, score)
        return score, alpha, beta, (None, score) # fail-soft beta-cutoff
    elif score > alpha:
        _save_score(pos_table, depth_left, board.turn, constants.EXACT, saved_value, hash, score)
        alpha = score
    # else:
    #     _save_score(pos_table, depth_left, board.turn, constants.UPPERBOUND, saved_value, child, score)
    if score > best_score[1]:
        best_score = (move, score)

    return score, alpha, beta, best_score

# @profile
def _alpha_beta(value: int, alpha: int, beta: int, depth_left: int, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], hash: int) -> Tuple[chess.Move, int]:
    best_score = (None, -(MAX_VALUE + depth_left))

    if depth_left == 0:
        return (None, _quiescence(value, alpha, beta, board))

    for move, move_value in generate_ordered_moves(board, hash, killer_table):
        child_hash = update_hash(hash, board, move)
        score, alpha, beta, best_score = _evaluate_child(move_value - value, child_hash, move, depth_left, alpha, beta, pos_table, board, best_score, killer_table)
        if best_score[0] is None:
            killer_table[hash] = move
            return (move, score) # fail-soft beta-cutoff

    if best_score[0] is None:
        if is_check(board):
            return (None, -(MAX_VALUE + depth_left - 1))
        else:
            return (None, 0)

    return best_score


# @profile
def _quiescence(value: int, alpha: int, beta: int, board: chess.Board) -> int:
    return -value
    # if is_checkmate(board):
    #     return -MAX_VALUE
    # else:
    #     return -node.value
    # any_legal_moves = any(board.generate_legal_moves())
    # if not any_legal_moves:
    #     if board.is_check():
    #         return -MAX_VALUE
    #     else:
    #         return 0
    # else:
    #     return -node.value


def _save_score(pos_table: Dict[int, Tuple[int, int, int, bool]], depth_left: int, turn: bool, node_type: int, saved_value: int, hash: int, score: int):
    if not saved_value or saved_value and saved_value[0] < depth_left:
        pos_table[hash] = (depth_left, score if turn else -score, node_type)

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
    move = solve_position_root(board, 5)