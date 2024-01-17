import itertools
import time
from typing import Dict, Iterator, List, Optional, Tuple

import chess

import constants
from chess_node import MtdfNode
from constants import MAX_VALUE, SECONDS_PER_MOVE, MIN_DEPTH
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

def solve_position_root(board: chess.Board, fixed_depth: Optional[int] = None):
    global pos_table
    global killer_table
    # fixed_depth = 6
    # initial_score = evaluate_board(board) if board.turn else -evaluate_board(board)
    root_node = MtdfNode(move=None, value=0, children=[], gamma=0, hash=zobrist_hash(board))
    (depth, move_scores) = _iterative_deepening(root_node, board, pos_table, killer_table, fixed_depth)
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
    best_score = max(move_score[1] for move_score in move_scores)
    best_moves = [move_score for move_score in move_scores if move_score[1] == best_score]
    # print(f'move: {best_moves} depth: {depth} best_score: {best_score}')
    print(f'depth: {depth}')
    return [best_moves[0]]

def _iterative_deepening(root: MtdfNode, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], fixed_depth: Optional[int] = None) -> Tuple[int, List[Tuple[chess.Move, int]]]:
    start = time.perf_counter()
    min_depth = MIN_DEPTH if not fixed_depth else fixed_depth
    max_depth = 100 if not fixed_depth else fixed_depth
    for depth in range(1, min_depth + 1):
        _mtdf(root, depth, board, pos_table, killer_table)
    
    result = (min_depth, [(child.move, child.gamma) for child in root.children])
    for depth in range(min_depth + 1, max_depth + 1):
        if _mtdf(root, depth, board, pos_table, killer_table, start):
            result = (depth, [(child.move, child.gamma) for child in root.children])
        else:
            break
        
    return result

def _mtdf(root: MtdfNode, depth: int, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], start: Optional[float] = None) -> int:
    pos_result = pos_table.get(root.hash, None)
    if pos_result is not None and pos_result[0] >= depth + 1 and pos_result[2] == constants.EXACT:
        root.gamma = pos_result[1] if board.turn else -pos_result[1]
        return True
    
    upper_bound = MAX_VALUE + depth
    lower_bound = -MAX_VALUE - depth
    
    while upper_bound - lower_bound > 0:
        if start and time.perf_counter() - start >= SECONDS_PER_MOVE:
            return False
        
        beta = root.gamma + 1 if root.gamma == lower_bound else root.gamma
        # if depth == 3:
        #     print(f'lowerbound: {lower_bound}, upperbound: {upper_bound}, beta: {beta}, gamma: {root.gamma}')
        (best_move, root.gamma) = _alpha_beta(root, beta - 1, beta, depth, board, pos_table, killer_table)
        
        if root.gamma < beta:
            upper_bound = root.gamma
        else:
            lower_bound = root.gamma
    
    # killer_table[root.hash] = best_move
    _save_score(pos_table, depth + 1, board.turn, constants.EXACT, pos_result, root, root.gamma)
    pos_table[root.hash] = (depth + 1, root.gamma if board.turn else -root.gamma, constants.EXACT)

    return True

def _evaluate_child(child: MtdfNode, depth_left: int, alpha: int, beta: int, pos_table: Dict[int, Tuple[int, int, int, bool]], board: chess.Board, best_score: Tuple[Optional[chess.Move], int], killer_table: Dict[int, Optional[chess.Move]]) -> Optional[int]:
    saved_value = pos_table.get(child.hash, None)
    score = None
    if saved_value and saved_value[0] >= depth_left:
        # if child.move == chess.Move.from_uci('h8g8'):
        #     print(saved_value, 'lul loaded', board.turn, child.hash, child.parent)
        _, saved_score, node_type = saved_value
        saved_score = saved_score if board.turn else -saved_score
        # print(f'move: {child.move} depth_left: {depth_left}, saved_depth: {saved_value[0]}, alpha: {alpha}, beta: {beta}, saved_score: {saved_score}, saved_type: {node_type}')
        if node_type == constants.EXACT:
            score = saved_score
        elif node_type == constants.LOWERBOUND and saved_score > alpha:
            score = saved_score
        elif node_type == constants.UPPERBOUND and saved_score < beta:
            score = saved_score
    
    found_value = score is not None
    if not found_value:
        board.push(child.move)
        (best_move, score) = _alpha_beta(child, -beta, -alpha, depth_left - 1, board, pos_table, killer_table)
        score = -score
        board.pop()
        # if child.move == chess.Move.from_uci('b6b7') and abs(score) >= MAX_VALUE:
        #     print(score, 'lul', root_turn, board.turn)
        #     child.print_children()

    child.gamma = score

    if score > beta:
        _save_score(pos_table, depth_left, board.turn, constants.LOWERBOUND, saved_value, child, score)
        return score, alpha, beta, (None, score) # fail-soft beta-cutoff
    elif score > alpha:
        _save_score(pos_table, depth_left, board.turn, constants.EXACT, saved_value, child, score)
        alpha = score
    else:
        _save_score(pos_table, depth_left, board.turn, constants.UPPERBOUND, saved_value, child, score)
    if score > best_score[1]:
        best_score = (child.move, score)

    return score, alpha, beta, best_score

def _alpha_beta(node: MtdfNode, alpha: int, beta: int, depth_left: int, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move]) -> Tuple[chess.Move, int]:
    best_score = (None, -(MAX_VALUE + depth_left))

    if depth_left == 0:
        return (None, _quiescence(node, alpha, beta, board))
    
    if not node.children:
        node.move_generator = _generate_ordered_moves(board, node)
    # else:
    #     node.children.sort(key=lambda x: x.gamma, reverse=True)

    killer_move = killer_table.get(node.hash, None)
    killer_index, killer_child = None, None
    if killer_move:
        children_enumeration = enumerate(itertools.chain(node.children, node.move_generator))
        # for index, child in children_enumeration:
        #     print(index, child)
        killer_index, killer_child = next(((index, child) for (index, child) in children_enumeration if child.move == killer_move), (None, None))
        if killer_index is None:
            print("BUG")
            print(killer_index, killer_move, killer_child)
            node.print_children()
            raise Exception('bug?')
    
    if killer_index is not None:
        score, alpha, beta, best_score = _evaluate_child(killer_child, depth_left, alpha, beta, pos_table, board, best_score, killer_table)
        if best_score[0] is None:
            return (killer_move, score) # fail-soft beta-cutoff
        node.children.pop(killer_index)

    node.children.sort(key=lambda x: x.gamma, reverse=True)
        
    for child in itertools.chain(node.children, node.move_generator):
        score, alpha, beta, best_score = _evaluate_child(child, depth_left, alpha, beta, pos_table, board, best_score, killer_table)
        # if node.move == chess.Move.from_uci('c6e4') and node.parent.move == chess.Move.from_uci('d5f4'):
        #         print(f'child move: {child.move} score {score} alpha {alpha} beta {beta} best_score {best_score}')
        if best_score[0] is None:
            killer_table[node.hash] = child.move
            if killer_index is not None:
                node.children.insert(0, killer_child)
            return (child.move, score) # fail-soft beta-cutoff
    
    if killer_index is not None:
        node.children.insert(0, killer_child)

    if not node.children:
        if board.is_check():
            return (None, -(MAX_VALUE + depth_left))
        else:
            return (None, 0)

    return best_score

def _quiescence(node: MtdfNode, alpha: int, beta: int, board: chess.Board) -> int:
    if not any(board.generate_legal_moves()):
        if board.is_check():
            return -MAX_VALUE
        else:
            return 0
    else:
        return -node.value

def _generate_ordered_moves(board: chess.Board, node: MtdfNode) -> Iterator[Tuple[chess.Move, int]]:
    sorted_moves = _sorted_evaluated_legal_moves(board, board.legal_moves)

    for move in sorted_moves:
        child = MtdfNode(move=move[0], value=move[1] - node.value, parent=node, children=[], gamma=0, hash=update_hash(node.hash, board, move[0]))
        node.children.append(child)
        yield child

def _sorted_evaluated_legal_moves(board: chess.Board, legal_moves: Iterator[chess.Move]) -> List[Tuple[chess.Move, int]]:
    evaluated_legal_moves = [[move, calculate_move_value(move, board)] for move in legal_moves]
    evaluated_legal_moves.sort(key=lambda x: x[1], reverse=True)
    
    return evaluated_legal_moves

def _save_score(pos_table: Dict[int, Tuple[int, int, int, bool]], depth_left: int, turn: bool, node_type: int, saved_value: int, child: MtdfNode, score: int):
    if not saved_value or saved_value and saved_value[0] < depth_left:
        # if child.hash == 14107997451098753891 and abs(score) >= MAX_VALUE:
        #     print(score, 'saving', turn, depth_left, child.parent)
        pos_table[child.hash] = (depth_left, score if turn else -score, node_type)

if __name__ == '__main__':
    board = chess.Board()
    stack = []
    while True:
        move = solve_position_root(board)
        stack.append(board.san(move))
        board.push(move)
        
        if board.outcome():
            break
    
    print(' '.join(stack))