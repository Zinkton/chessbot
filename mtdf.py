import itertools
import time
from typing import Dict, List, Optional, Tuple

import custom_chess as chess

import constants
from chess_node import MtdfNode
from constants import MAX_VALUE, SECONDS_PER_MOVE
from move_generation import is_check, generate_ordered_moves, is_checkmate, sorted_child_generator
from zobrist import update_hash, zobrist_hash
from evaluation import calculate_move_value, evaluate_board

# def solve_position(input):
#     (board, time, move) = (input[0], input[1], input[2])
#     initial_value = -_calculate_move_value(move, board)
#     board.push(move)
#     root_node = MtdfNode(move=move, value=initial_value, children=[])
#     _iterative_deepening(root_node, board)
    
#     return [move, root_node.min_value]

pos_table = {}
killer_table = {}
def solve_position_root(board: chess.Board, max_depth: Optional[int] = 100):
    global pos_table
    global killer_table
    # fixed_depth = 6
    # initial_score = evaluate_board(board) if board.turn else -evaluate_board(board)
    initial_value = evaluate_board(board) if board.turn else -evaluate_board(board)
    root_node = MtdfNode(move=None, value=initial_value, children={}, hash=zobrist_hash(board), sorted_children_keys=[])
    (depth, move_score) = _iterative_deepening(root_node, board, pos_table, killer_table, max_depth)
    # root_node.print_children()
    # current = [child for child in root_node.children if child.gamma == root_node.gamma][0]
    # print(current)
    # while current.children:
    #     current = [child for child in current.children if child.gamma == -current.gamma][0]
    #     print(current)
    # print(sorted(move_scores, key=lambda x: x[1], reverse=True))
    # children = [child for child in root_node.children if child.move == chess.Move.from_uci('b6g6')]
    # key_child = children[0] if children else None
    # if key_child:
    #     key_child.print_children()
    # best_score = max(move_score[1] for move_score in move_scores)
    # best_moves = [move_score for move_score in move_scores if move_score[1] == best_score]
    # print(f'move: {best_moves} depth: {depth} best_score: {best_score}')
    print(f'depth: {depth}')
    return [move_score]

def _iterative_deepening(root: MtdfNode, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], max_depth: Optional[int]) -> Tuple[int, List[Tuple[chess.Move, int]]]:
    start = time.perf_counter()
    _mtdf(root, 1, board, pos_table, killer_table)
    result = (1, _mtdf(root, 1, board, pos_table, killer_table))
    for depth in range(2, max_depth + 1):
        if abs(root.gamma) < MAX_VALUE:
            mtdf_result = _mtdf(root, depth, board, pos_table, killer_table, start)
            if mtdf_result is not None:
                result = (depth, mtdf_result)
        else:
            break
        
    return result

def _mtdf(root: MtdfNode, depth: int, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], start: Optional[float] = None) -> Tuple[chess.Move, int]:
    pos_result = pos_table.get(root.hash, None)
    if root.gamma is None:
        if pos_result is not None and pos_result[2] == constants.EXACT:
            root.gamma = pos_result[1] if board.turn else -pos_result[1]
        else:
            root.gamma = root.value
    
    upper_bound = MAX_VALUE + depth
    lower_bound = -MAX_VALUE - depth
    
    while upper_bound - lower_bound > 0:
        if start and time.perf_counter() - start >= SECONDS_PER_MOVE:
            return None
        
        beta = root.gamma + 1 if root.gamma == lower_bound else root.gamma
        # if depth == 3:
        #     print(f'lowerbound: {lower_bound}, upperbound: {upper_bound}, beta: {beta}, gamma: {root.gamma}')
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
    
    generate_ordered_moves(board, hash, killer_table)

    for move, move_value in generate_ordered_moves(board, hash, killer_table):
        child_hash = update_hash(hash, board, move)
        score, alpha, beta, best_score = _evaluate_child(move_value - value, child_hash, move, depth_left, alpha, beta, pos_table, board, best_score, killer_table)
        # if node.move == chess.Move.from_uci('c6e4') and node.parent.move == chess.Move.from_uci('d5f4'):
        #         print(f'child move: {child.move} score {score} alpha {alpha} beta {beta} best_score {best_score}')
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
        # if child.hash == 14107997451098753891 and abs(score) >= MAX_VALUE:
        #     print(score, 'saving', turn, depth_left, child.parent)
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