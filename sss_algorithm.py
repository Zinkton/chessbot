import chess
import evaluation
from constants import NodeState, SECONDS_FOR_ITERATIVE_DEEPENING
from evaluation import piece_value, position_value
from chess_node import ChessNode
from time import perf_counter

from saved_values import SavedValues

def _get_saved_value(move_chain, move, board, sign, saved_values: SavedValues, parent_value = None, value = None):
    if move_chain in saved_values.value_table:
        return saved_values.value_table[move_chain]
    else:
        new_value = sign * (_calculate_move_value(move, board) if value is None else value) 
        if parent_value:
            new_value += parent_value
        saved_values.value_table[move_chain] = new_value
        return new_value
    
def _get_saved_legal_moves(move_chain, board, saved_values: SavedValues):
    if move_chain in saved_values.legal_move_table:
        return saved_values.legal_move_table[move_chain]
    else:
        new_legal_moves = list(board.legal_moves)
        if new_legal_moves:
            evaluated_moves = _sorted_evaluated_legal_moves(board, new_legal_moves)
            saved_values.legal_move_table[move_chain] = evaluated_moves

            return evaluated_moves
        else:
            return None

def solve_position(input):
    (board, max_depth, move, start, saved_values) = (input[0], input[1], input[2], input[3], input[4])
    start = perf_counter()
    move_chain = str(move)
    root_node = ChessNode(move=move, value=_get_saved_value(move_chain, move, board, -1, saved_values), children=[], move_chain=move_chain)

    board.push(move)
    if start is None:
        while root_node.state != NodeState.SOLVED:
            root_node.min_value = _recursiveSearch(root_node, board, 1, max_depth, saved_values)
    else:
        while root_node.state != NodeState.SOLVED:
            root_node.min_value = _recursiveSearch(root_node, board, 1, max_depth, saved_values)
            if perf_counter() - start >= SECONDS_FOR_ITERATIVE_DEEPENING:
                break
    
    if root_node.state == NodeState.SOLVED:
        root_node.depth = max_depth

    return [move, root_node.min_value, root_node, saved_values]

def _recursiveSearch(current_node: ChessNode, board, depth, max_depth, saved_values: SavedValues):
    """ SSS* search algorithm implementation. """
    is_leaf, leaf_value = _is_leaf_node(current_node, board, depth, max_depth)
    if is_leaf:
        current_node.state = NodeState.SOLVED
        return min(leaf_value, current_node.min_value)
    
    if current_node.state == NodeState.UNEXPANDED:
        leaf_value = _expand_node(current_node, board, depth, max_depth, saved_values)
        if leaf_value is not None:
            return leaf_value
    
    grandson_node = _process_children(current_node, board, depth, max_depth, saved_values)
    
    if grandson_node.state == NodeState.SOLVED:
        current_node.state = NodeState.SOLVED

    return grandson_node.min_value
    
def _is_leaf_node(node: ChessNode, board, depth, max_depth):
    if not node:
        return depth >= max_depth or board.is_checkmate()
        
    if board.is_checkmate():
        value = -10**10 - (max_depth - depth) if board.turn else 10**10 + (max_depth - depth)
        return (True, value)
    elif depth >= max_depth:
        return (True, node.value)
    return (False, 0)

def _expand_node(node: ChessNode, board, depth, max_depth, saved_values: SavedValues):
    node.state = NodeState.LIVE
    evaluated_moves = _get_saved_legal_moves(node.move_chain, board, saved_values)
    if not evaluated_moves:
        node.state = NodeState.SOLVED
        return min(0, node.min_value)
    for x in range(len(evaluated_moves)):
        son_move_chain = node.move_chain + str(evaluated_moves[x][0])
        son_value = _get_saved_value(son_move_chain, evaluated_moves[x][0], board, 1, saved_values, node.value, evaluated_moves[x][1])
        son_node = ChessNode(move=evaluated_moves[x][0], value=son_value, min_value=node.min_value, children=[], parent=node, legal_moves=evaluated_moves, move_index=x, move_chain=son_move_chain)
        board.push(evaluated_moves[x][0])
        if _is_leaf_node(None, board, depth + 1, max_depth):
            node.children.append(son_node)
        else:
            s_evaluated_moves = _get_saved_legal_moves(son_move_chain, board, saved_values)
            if s_evaluated_moves:
                grandson_move_chain = son_move_chain + str(s_evaluated_moves[0][0])
                grandson_value = _get_saved_value(grandson_move_chain, evaluated_moves[0][0], board, -1, saved_values, son_value, s_evaluated_moves[0][1]) 
                grandson_node = ChessNode(move=s_evaluated_moves[0][0], value=grandson_value, min_value=node.min_value, children=[], parent=son_node, legal_moves=s_evaluated_moves, move_index=0, move_chain=grandson_move_chain)
                node.children.append(grandson_node)
            else:
                node.children.append(son_node)
        board.pop()
        
    return None

def _process_children(current_node: ChessNode, board, depth, max_depth, saved_values: SavedValues) -> ChessNode:
    grandson_node = max(current_node.children, key=lambda s: s.min_value)
    while grandson_node.min_value == current_node.min_value and grandson_node.state != NodeState.SOLVED:
        is_gson = grandson_node.parent.move != current_node.move
        depth_adder = 1
        if is_gson:
            depth_adder = 2                
            board.push(grandson_node.parent.move)
        board.push(grandson_node.move)
        grandson_node.min_value = _recursiveSearch(grandson_node, board, depth + depth_adder, max_depth, saved_values)
        if is_gson:
            board.pop()
        if is_gson and grandson_node.state == NodeState.SOLVED and grandson_node.move_index != (len(grandson_node.legal_moves) - 1):
            grandson_node.move_index += 1
            grandson_node.move = grandson_node.legal_moves[grandson_node.move_index][0]
            grandson_node.state = NodeState.UNEXPANDED
            grandson_node.children = []
            grandson_node.move_chain = grandson_node.parent.move_chain + str(grandson_node.move)
            grandson_node.value = _get_saved_value(grandson_node.move_chain, grandson_node.move, board, -1, saved_values, grandson_node.parent.value, grandson_node.legal_moves[grandson_node.move_index][1])
        board.pop()
        grandson_node = max(current_node.children, key=lambda s: s.min_value)
        
    return grandson_node

def _calculate_move_value(move, board):
    castle_value = _check_castling(board, move)
    if castle_value is not None:
        return castle_value
    
    value = 0
    src_piece = board.piece_type_at(move.from_square)
    dest_piece = board.piece_type_at(move.to_square)
    
    if move.promotion:
        prom = move.promotion
        pos_score = position_value[board.turn][prom][move.to_square] - position_value[board.turn][src_piece][move.from_square]
        prom_score = piece_value[prom] - piece_value[src_piece]
        value = pos_score + prom_score
    else:
        value = position_value[board.turn][src_piece][move.to_square] - position_value[board.turn][src_piece][move.from_square]

    if dest_piece:
        # If we capture, add score based on captured piece value and position value
        value += piece_value[dest_piece] + position_value[not board.turn][dest_piece][move.to_square]
        
    return value

def _check_castling(board, move):
    if board.kings & chess.BB_SQUARES[move.from_square]:
        diff = chess.square_file(move.from_square) - chess.square_file(move.to_square)
        if abs(diff) > 1:
            return evaluation.K_CASTLING_VALUE if diff < 0 else evaluation.Q_CASTLING_VALUE
        
    return None

def _sorted_evaluated_legal_moves(board, legal_moves):
    evaluated_legal_moves = [[move, _calculate_move_value(move, board)] for move in legal_moves]
    evaluated_legal_moves.sort(key=lambda x: x[1], reverse=True)
    
    return evaluated_legal_moves
            