import chess
import evaluation
from constants import NodeState, MAX_DEPTH_QUIESCENCE
from evaluation import piece_value, position_value
from chess_node import ChessNode
from collections import deque

def solve_position(input):
    (board, max_depth, move) = (input[0], input[1], input[2])
    initial_value = -_calculate_move_value(move, board)
    board.push(move)
    root_node = ChessNode(move=move, value=initial_value, children=[])
    while root_node.state != NodeState.SOLVED:
        root_node.min_value = _recursiveSearch(root_node, board, 1, max_depth, False)

    # print(root_node)

    return [move, root_node.min_value]

def _recursiveSearch(current_node: ChessNode, board: chess.Board, depth, max_depth, quiescence):
    """ SSS* search algorithm implementation. """
    is_leaf, leaf_value, quiescence = _is_leaf_node_quiescence(current_node, board, depth, max_depth, quiescence) if MAX_DEPTH_QUIESCENCE > 0 else _is_leaf_node(current_node, board, depth, max_depth, current_node.value)
    if is_leaf:
        current_node.state = NodeState.SOLVED
        # if current_node.value == -42 and str(board.move_stack[0]) == 'e7e5':
        #     print('found')
        #     test = current_node
        #     path = [current_node]
        #     while (test.parent):
        #         path.append(test.parent)
        #         test = test.parent
        #     path.reverse()
        #     for node in path:
        #         print(node)
        return min(leaf_value, current_node.min_value)
    
    if current_node.state == NodeState.UNEXPANDED:
        leaf_value = _expand_node(current_node, board, depth, max_depth, quiescence)
        if leaf_value is not None:
            return leaf_value
    
    grandson_node = _process_children(current_node, board, depth, max_depth, quiescence)
    
    if grandson_node.state == NodeState.SOLVED:
        current_node.state = NodeState.SOLVED

    return grandson_node.min_value

def _is_leaf_node_quiescence(node: ChessNode, board: chess.Board, depth, max_depth, quiescence):
    total_depth = max_depth + MAX_DEPTH_QUIESCENCE
    if quiescence:
        max_depth = total_depth
    if not node:
        if depth >= max_depth:
            return (True, True) if quiescence else (board.is_checkmate(), True)
        else:
            return (board.is_checkmate(), False) if not quiescence else (False, True)
        
    if board.is_checkmate():
        value = -10**10 - (total_depth - depth) if board.turn else 10**10 + (total_depth - depth)
        return (True, value, quiescence)
    elif depth >= max_depth:
        # return (True, node.value, quiescence) if quiescence else (False, 0, True)
        return (True, node.value if node.value > 0 or not _any_quescience_moves(board) else node.value / 100.0, quiescence) if quiescence else (False, 0, True)
    return (False, 0, quiescence)

def _is_leaf_node(node: ChessNode, board, depth, max_depth, value):
    if not node:
        return (depth >= max_depth or (len(board.move_stack) > 2 and not board.move_stack[-3] and value > 0) or board.is_checkmate(), False)
        
    if board.is_checkmate():
        value = -10**10 - (max_depth - depth) if board.turn else 10**10 + (max_depth - depth)
        return (True, value, False)
    elif depth >= max_depth:
        return (True, node.value, False)
    elif len(board.move_stack) > 2 and not board.move_stack[-3] and (value < 0 if board.turn else value > 0):
        return (True, node.value, False)
    return (False, 0, False)

def _expand_node(node: ChessNode, board, depth, max_depth, quiescence):
    node.state = NodeState.LIVE
    legal_moves = _generate_legal_moves(board) if not quiescence else _generate_quiescence_moves(board)
    if not legal_moves:
        node.state = NodeState.SOLVED
        return min(0, node.min_value) if not quiescence else min(node.value, node.min_value)
    evaluated_moves = _sorted_evaluated_legal_moves(board, legal_moves)
    for x in range(len(evaluated_moves)):
        son_value = node.value + evaluated_moves[x][1]
        son_node = ChessNode(move=evaluated_moves[x][0], value=son_value, min_value=node.min_value, children=[], parent=node, legal_moves=evaluated_moves, move_index=x)
        board.push(evaluated_moves[x][0])
        is_leaf, quiescence = _is_leaf_node_quiescence(None, board, depth + 1, max_depth, quiescence) if MAX_DEPTH_QUIESCENCE > 0 else _is_leaf_node(None, board, depth + 1, max_depth, son_value)
        if is_leaf:
            node.children.append(son_node)
        else:
            s_legal_moves = _generate_legal_moves(board) if not quiescence else _generate_quiescence_moves(board)
            if s_legal_moves:
                s_evaluated_moves = _sorted_evaluated_legal_moves(board, s_legal_moves)
                grandson_value = son_value - s_evaluated_moves[0][1]
                grandson_node = ChessNode(move=s_evaluated_moves[0][0], value=grandson_value, min_value=node.min_value, children=[], parent=son_node, legal_moves=s_evaluated_moves, move_index=0)
                node.children.append(grandson_node)
            else:
                node.children.append(son_node)
        board.pop()
        
    return None

def _process_children(current_node: ChessNode, board, depth, max_depth, quiescence) -> ChessNode:
    grandson_node = max(current_node.children, key=lambda s: s.min_value)
    while grandson_node.min_value == current_node.min_value and grandson_node.state != NodeState.SOLVED:
        is_gson = grandson_node.parent.move != current_node.move
        depth_adder = 1
        if is_gson:
            depth_adder = 2                
            board.push(grandson_node.parent.move)
        board.push(grandson_node.move)
        grandson_node.min_value = _recursiveSearch(grandson_node, board, depth + depth_adder, max_depth, quiescence)
        if is_gson:
            board.pop()
        if is_gson and grandson_node.state == NodeState.SOLVED and grandson_node.move_index != (len(grandson_node.legal_moves) - 1):
            grandson_node.move_index += 1
            grandson_node.move = grandson_node.legal_moves[grandson_node.move_index][0]
            grandson_node.state = NodeState.UNEXPANDED
            grandson_node.children = []
            grandson_node.value = grandson_node.parent.value - grandson_node.legal_moves[grandson_node.move_index][1]
        board.pop()
        grandson_node = max(current_node.children, key=lambda s: s.min_value)
        
    return grandson_node

def _calculate_move_value(move, board):
    if not move:
        return 0
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

def custom_sort(x):
    # return x[1]
    return (0, 0) if not x[0] else (1, x[1])

def _sorted_evaluated_legal_moves(board, legal_moves):
    evaluated_legal_moves = [[move, _calculate_move_value(move, board)] for move in legal_moves]
    evaluated_legal_moves.sort(key=custom_sort, reverse=True)
    
    return evaluated_legal_moves

def _generate_legal_moves(board):
    moves = list(board.legal_moves)
    if moves and board.peek():
        moves.append(chess.Move.null())

    return moves

def _any_quescience_moves(board: chess.Board):
    if len(board.move_stack) > 1 and not board.move_stack[-1] and not board.move_stack[-2]:
        return False
    
    return any(board.generate_legal_captures())

def _generate_quiescence_moves(board: chess.Board):
    if len(board.move_stack) > 1 and not board.move_stack[-1] and not board.move_stack[-2]:
        return None
    
    result = list(board.generate_legal_captures())
    if result:
        result.append(chess.Move.null())
    
    return result

def _any_quescience_moves_old(board: chess.Board):
    if len(board.move_stack) > 1 and not board.move_stack[-1] and not board.move_stack[-2]:
        return False
    
    if board.is_check():
        return any(move.promotion or board.is_capture(move) for move in board.legal_moves)
    
    return any(move.promotion or board.is_capture(move) or board.gives_check(move) for move in board.legal_moves)

def _generate_quiescence_moves_old2(board: chess.Board):
    if len(board.move_stack) > 1 and not board.move_stack[-1] and not board.move_stack[-2]:
        return None
    
    if board.is_check():
        return [move for move in board.legal_moves if move.promotion or board.is_capture(move)]
    
    result = [move for move in board.legal_moves if move.promotion or board.is_capture(move) or board.gives_check(move)]
    if result:
        result.append(chess.Move.null())
    
    return result

def _generate_quiescence_moves_old(board: chess.Board):
    if len(board.move_stack) > 1 and not board.move_stack[-1] and not board.move_stack[-2]:
        return None
    
    capture_moves = list(board.generate_legal_captures())
    if not capture_moves:
        return None
    
    capture_moves.append(chess.Move.null())
    
    return capture_moves