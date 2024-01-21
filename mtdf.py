import itertools
from multiprocessing import Pool, shared_memory
import time
from typing import Dict, List, Optional, Tuple

import numpy as np

import custom_chess as chess

import constants
from chess_node import MtdfNode
from constants import MAX_VALUE, SECONDS_PER_MOVE
from move_generation import is_check, generate_ordered_moves
from shared_memory_manager import SharedMemoryManager
from tt_utilities_dict import probe_tt_scores, save_tt_killer, save_tt_score
from zobrist import update_hash, zobrist_hash
from evaluation import calculate_move_value, evaluate_board

def solve_position_multiprocess(boards: List[chess.Board], manager: SharedMemoryManager, max_depth: int = 60) -> List:
    manager.reset_tables()
    process_chunks = [([], max_depth - 1, (manager.shm_tt_scores.name, manager.shm_tt_killers.name, manager.shm_process_status.name), x) for x in range(constants.PROCESS_COUNT)]
    for index, board in enumerate(boards):
        process_chunks[index % constants.PROCESS_COUNT][0].append(board)

    evaluation_dictionary = {}
    with Pool(processes=constants.PROCESS_COUNT) as p:
        eval_dicts = p.map(iterative_deepening_multiple, process_chunks)
        for dic in eval_dicts:
            evaluation_dictionary.update(dic)

    # print(evaluation_dictionary)

    move_initial_values = {}
    for board in boards:
        for key in evaluation_dictionary:
            if str(board.peek()) == str(key):
                board.pop()
                move_initial_values[key] = calculate_move_value(key, board)
                board.push(key)

    depths_moves_scores = [(evaluation_dictionary[key][0] + 1, key, evaluation_dictionary[key][1]) for key in evaluation_dictionary]
    depths_moves_scores.sort(key=lambda x: (x[2], -x[0], -move_initial_values[x[1]]))
    # print(depths_moves_scores)
    print(f'depth: {depths_moves_scores[0][0]}')
    if depths_moves_scores[0][2] <= -MAX_VALUE:
        depths_moves_scores = [depth_move_score for depth_move_score in depths_moves_scores if depth_move_score[2] <= -MAX_VALUE]
        return [depths_moves_scores[-1]]

    return depths_moves_scores

def iterative_deepening_multiple(input: Tuple) -> Dict:
    start = time.perf_counter()
    boards, max_depth, shared_memory_names, process_index = input
    tt_scores_nm, tt_killers_nm, process_status_nm = shared_memory_names

    shm_tt_scores = shared_memory.SharedMemory(name=tt_scores_nm)
    shm_tt_killers = shared_memory.SharedMemory(name=tt_killers_nm)
    shm_process_status = shared_memory.SharedMemory(name=process_status_nm)

    tt_scores = np.ndarray((constants.TT_SIZE,), dtype=np.uint64, buffer=shm_tt_scores.buf)
    tt_killers = np.ndarray((constants.TT_SIZE,), dtype=np.uint64, buffer=shm_tt_killers.buf)
    process_status = np.ndarray((constants.PROCESS_COUNT,), dtype=np.int16, buffer=shm_process_status.buf)

    roots_boards = []
    for board in boards:
        initial_value = -evaluate_board(board) if board.turn else evaluate_board(board)
        root = MtdfNode(move=board.peek(), value=initial_value, hash=zobrist_hash(board))
        roots_boards.append((root, board))

    if not roots_boards:
        process_status[process_index] = 100
        shm_tt_scores.close()
        shm_tt_killers.close()
        shm_process_status.close()
        return {}
    
    try:
        result = {}
        for depth in range(0, max_depth + 1):
            process_status[process_index] = depth
            if any(status == 101 for status in process_status):
                return {}
            # while not all(status >= depth for status in process_status):
            #     time.sleep(0.01)

            solved_roots = []
            for root, board in roots_boards:
                if root.gamma is None or abs(root.gamma) < MAX_VALUE:
                    mtdf_result = _mtdf(root, depth, board, tt_scores, tt_killers, start)
                    if mtdf_result is not None:
                        _, result_score = mtdf_result
                        result[root.move] = (depth, result_score)
                        if result_score <= -MAX_VALUE:
                            process_status[process_index] = 101
                            return result
                else:
                    solved_roots.append((root, board))
            for solved_root in solved_roots:
                roots_boards.remove(solved_root)
            
            if not roots_boards:
                process_status[process_index] = 100
                return result

        return result
    except:
        process_status[process_index] = 100
        raise
    finally:
        shm_tt_scores.close()
        shm_tt_killers.close()
        shm_process_status.close()

tt_scores = {}
tt_killers = {}
def solve_position_root(board: chess.Board, max_depth: int) -> Tuple[int, chess.Move, int]:
    global tt_scores
    global tt_killers

    initial_value = -evaluate_board(board) if board.turn else evaluate_board(board)
    root_node = MtdfNode(move=None, value=initial_value, hash=zobrist_hash(board))
    result = _iterative_deepening(root_node, board, tt_scores, tt_killers, max_depth)

    return result

def _iterative_deepening(root: MtdfNode, board: chess.Board, pos_table: np.ndarray, killer_table: np.ndarray, max_depth: Optional[int]) -> Tuple[int, chess.Move, int]:
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

def _mtdf(root: MtdfNode, depth: int, board: chess.Board, tt_scores: np.ndarray, tt_killers: np.ndarray, start: Optional[float] = None) -> Tuple[chess.Move, int]:
    pos_result = probe_tt_scores(tt_scores, root.hash)
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
        (best_move, root.gamma) = _alpha_beta(root.value, beta - 1, beta, depth, board, tt_scores, tt_killers, root.hash)
        
        if root.gamma < beta:
            upper_bound = root.gamma
        else:
            lower_bound = root.gamma
    
    save_tt_score(tt_scores, depth + 1, board.turn, constants.EXACT, pos_result, root.hash, root.gamma)

    return best_move, root.gamma

# @profile
def _evaluate_child(value: int, hash: int, move: chess.Move, depth_left: int, alpha: int, beta: int, board: chess.Board, best_score: Tuple[Optional[chess.Move], int], tt_scores: np.ndarray, tt_killers: np.ndarray) -> Tuple[int, int, int, Tuple[Optional[chess.Move], int]]:
    saved_value = probe_tt_scores(tt_scores, hash)
    score = None
    if saved_value is not None and saved_value[0] >= depth_left: # no touching
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
        (best_move, score) = _alpha_beta(value, -beta, -alpha, depth_left - 1, board, tt_scores, tt_killers, hash)
        score = -score
        board.pop()

    if score > beta:
        save_tt_score(tt_scores, depth_left, board.turn, constants.LOWERBOUND, saved_value, hash, score)
        return score, alpha, beta, (None, score) # fail-soft beta-cutoff
    elif score > alpha:
        save_tt_score(tt_scores, depth_left, board.turn, constants.EXACT, saved_value, hash, score)
        alpha = score
    # else:
    #     _save_score(pos_table, depth_left, board.turn, constants.UPPERBOUND, saved_value, child, score)
    if score > best_score[1]:
        best_score = (move, score)

    return score, alpha, beta, best_score

# @profile
def _alpha_beta(value: int, alpha: int, beta: int, depth_left: int, board: chess.Board, tt_scores: np.ndarray, tt_killers: np.ndarray, hash: int) -> Tuple[Optional[chess.Move], int]:
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