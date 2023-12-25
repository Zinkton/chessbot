import chess
from constants import NodeState
from evaluation import piece_value, position_value
from chess_node import ChessNode

def solve_position(input):
    (board, max_depth, move) = (input[0], input[1], input[2])
    initial_value = -_calculate_move_value(move, board)
    board.push(move)
    root_node = ChessNode(move=move, value=initial_value, children=[])
    while root_node.state != NodeState.SOLVED:
        root_node.min_value = _RecSSS(root_node, board, 1, max_depth)
    
    return [move, root_node.min_value]

def _RecSSS(current_node: ChessNode, board, depth, max_depth):
    is_leaf, leaf_value = _is_leaf(current_node, board, depth, max_depth)
    if is_leaf:
        current_node.state = NodeState.SOLVED
        return min(leaf_value, current_node.min_value)
    
    if current_node.state == NodeState.UNEXPANDED:
        _expand_node(current_node, board, depth, max_depth)
    
    grandson = _process_children(current_node, board, depth, max_depth)
    
    if grandson.state == NodeState.SOLVED:
        current_node.state = NodeState.SOLVED

    return grandson.min_value
    
def _is_leaf_bool(board, depth, max_depth):
    return depth >= max_depth or board.is_checkmate()

def _is_leaf(node: ChessNode, board, depth, max_depth):
    if board.is_checkmate():
        value = -10**10 - (max_depth - depth) if board.turn else 10**10 + (max_depth - depth)
        return (True, value)
    elif depth >= max_depth:
        return (True, node.value)
    return (False, 0)

def _expand_node(node: ChessNode, board, depth, max_depth):
    node.state = NodeState.LIVE
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        node.state = NodeState.SOLVED
        return min(0, node.min_value)
    for x in range(len(legal_moves)):
        move_value = _calculate_move_value(legal_moves[x], board)
        son_value = node.value + move_value
        son = ChessNode(move=legal_moves[x], value=son_value, min_value=node.min_value, children=[], parent=node, legal_moves=legal_moves, move_index=x)
        board.push(legal_moves[x])
        if _is_leaf_bool(board, depth + 1, max_depth):
            node.children.append(son)
        else:
            s_legal_moves = list(board.legal_moves)
            if s_legal_moves:
                move_value = _calculate_move_value(s_legal_moves[0], board)
                gs_src = board.piece_type_at(s_legal_moves[0].from_square)
                gs_dest = board.piece_type_at(s_legal_moves[0].to_square)
                if (s_legal_moves[0].promotion):
                    g_prom = s_legal_moves[0].promotion
                    g_pos_score = (position_value[chess.BLACK][g_prom][s_legal_moves[0].to_square] - position_value[chess.BLACK][gs_src][s_legal_moves[0].from_square])
                    g_prom_score = piece_value[g_prom] - piece_value[gs_src]
                    grandson_value = son_value - g_pos_score - g_prom_score
                else:
                    grandson_value = son_value - (position_value[chess.BLACK][gs_src][s_legal_moves[0].to_square] - position_value[chess.BLACK][gs_src][s_legal_moves[0].from_square])
                if gs_dest:
                    grandson_value -= piece_value[gs_dest] + position_value[chess.WHITE][gs_dest][s_legal_moves[0].to_square]
                grandson = ChessNode(move=s_legal_moves[0], value=grandson_value, min_value=node.min_value, children=[], parent=son, legal_moves=s_legal_moves, move_index=0)
                node.children.append(grandson)
            else:
                node.children.append(son)
        board.pop()
        
def _process_children(current_node: ChessNode, board, depth, max_depth) -> ChessNode:
    grandson = max(current_node.children, key=lambda s: s.min_value)
    while grandson.min_value == current_node.min_value and grandson.state != NodeState.SOLVED:
        is_gson = grandson.parent.move != current_node.move
        depth_adder = 1
        if is_gson:
            depth_adder = 2                
            board.push(grandson.parent.move)
        board.push(grandson.move)
        grandson.min_value = _RecSSS(grandson, board, depth + depth_adder, max_depth)
        if is_gson:
            board.pop()
        if is_gson and grandson.state == NodeState.SOLVED and grandson.move_index != (len(grandson.legal_moves) - 1):
            grandson.move_index += 1
            grandson.move = grandson.legal_moves[grandson.move_index]
            grandson.state = NodeState.UNEXPANDED
            grandson.children = []
            move_value = _calculate_move_value(grandson.move, board)
            grandson.value = grandson.parent.value - move_value
        board.pop()
        grandson = max(current_node.children, key=lambda s: s.min_value)
        
    return grandson

def _calculate_move_value(move, board):
    value = 0
    src_piece = board.piece_type_at(move.from_square)
    dest_piece = board.piece_type_at(move.to_square)
    
    if (move.promotion):
        prom = move.promotion
        pos_score = position_value[board.turn][prom][move.to_square] - position_value[board.turn][src_piece][move.from_square]
        prom_score = piece_value[prom] - piece_value[src_piece]
        value = pos_score + prom_score
    else:
        value = position_value[board.turn][src_piece][move.to_square] - position_value[board.turn][src_piece][move.from_square]
        
    if dest_piece:
        value += piece_value[dest_piece] + position_value[not board.turn][dest_piece][move.to_square]
        
    return value