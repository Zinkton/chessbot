import chess
import evaluation
from constants import NodeState, MAX_VALUE
from evaluation import piece_value, position_value
from chess_node import ChessNode

def solve_position(input):
    (board, max_depth, move) = (input[0], input[1], input[2])
    initial_value = -_calculate_move_value(move, board)
    board.push(move)
    root_node = ChessNode(move=move, value=initial_value, children=[])
    while root_node.state != NodeState.SOLVED:
        root_node.min_value = _recursiveSearch(root_node, board, 1, max_depth)
    
    return [move, root_node.min_value]

def _recursiveSearch(current_node: ChessNode, board, depth, max_depth):
    """ SSS* search algorithm implementation. """
    is_leaf, leaf_value = _is_leaf_node(current_node, board, depth, max_depth)
    if is_leaf:
        current_node.state = NodeState.SOLVED
        return min(leaf_value, current_node.min_value)
    
    if current_node.state == NodeState.UNEXPANDED:
        leaf_value = _expand_node(current_node, board, depth, max_depth)
        if leaf_value is not None:
            return leaf_value
    
    grandson_node = _process_children(current_node, board, depth, max_depth)
    
    if grandson_node.state == NodeState.SOLVED:
        current_node.state = NodeState.SOLVED

    return grandson_node.min_value
    
def _is_leaf_node(node: ChessNode, board, depth, max_depth):
    if not node:
        return depth >= max_depth or board.is_checkmate()
        
    if board.is_checkmate():
        value = -MAX_VALUE - (max_depth - depth) if board.turn else MAX_VALUE + (max_depth - depth)
        return (True, value)
    elif depth >= max_depth:
        return (True, node.value)
    return (False, 0)

def _expand_node(node: ChessNode, board: chess.Board, depth, max_depth):
    node.state = NodeState.LIVE
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        node.state = NodeState.SOLVED
        return min(0, node.min_value)
    evaluated_moves = _sorted_evaluated_legal_moves(board, legal_moves)
    for x in range(len(evaluated_moves)):
        son_value = node.value + evaluated_moves[x][1]
        son_node = ChessNode(move=evaluated_moves[x][0], value=son_value, min_value=node.min_value, children=[], parent=node, legal_moves=evaluated_moves, move_index=x)
        board.push(evaluated_moves[x][0])
        if _is_leaf_node(None, board, depth + 1, max_depth):
            node.children.append(son_node)
        else:
            s_legal_moves = list(board.legal_moves)
            if s_legal_moves:
                s_evaluated_moves = _sorted_evaluated_legal_moves(board, s_legal_moves)
                grandson_value = son_value - s_evaluated_moves[0][1]
                grandson_node = ChessNode(move=s_evaluated_moves[0][0], value=grandson_value, min_value=node.min_value, children=[], parent=son_node, legal_moves=s_evaluated_moves, move_index=0)
                node.children.append(grandson_node)
            else:
                node.children.append(son_node)
        board.pop()
        
    return None

def _process_children(current_node: ChessNode, board, depth, max_depth) -> ChessNode:
    grandson_node = max(current_node.children, key=lambda s: s.min_value)
    while grandson_node.min_value == current_node.min_value and grandson_node.state != NodeState.SOLVED:
        is_gson = grandson_node.parent.move != current_node.move
        depth_adder = 1
        if is_gson:
            depth_adder = 2                
            board.push(grandson_node.parent.move)
        board.push(grandson_node.move)
        grandson_node.min_value = _recursiveSearch(grandson_node, board, depth + depth_adder, max_depth)
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
    elif src_piece == chess.PAWN and move.to_square == board.ep_square:
        down = -8 if board.turn == chess.WHITE else 8
        capture_square = board.ep_square + down
        value += piece_value[chess.PAWN] + position_value[not board.turn][chess.PAWN][capture_square]
        
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
            