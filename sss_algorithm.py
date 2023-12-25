import chess
from constants import NodeState
from evaluation import piece_value, position_value

def solve_position(input):
    (board, max_depth, move) = (input[0], input[1], input[2])
    src_piece = board.piece_type_at(move.from_square)
    dest_piece = board.piece_type_at(move.to_square)
    if (move.promotion):
        prom = move.promotion
        pos_score = position_value[chess.BLACK][prom][move.to_square] - position_value[chess.BLACK][src_piece][move.from_square]
        prom_score = piece_value[prom] - piece_value[src_piece]
        initial_value = -(pos_score + prom_score)
    else:
        initial_value = -(position_value[chess.BLACK][src_piece][move.to_square] - position_value[chess.BLACK][src_piece][move.from_square])
    if dest_piece:
        initial_value -= piece_value[dest_piece] + position_value[chess.WHITE][dest_piece][move.to_square]
    board.push(move)
    root_node = [move, NodeState.UNEXPANDED, 10**11, [], False, False, False, initial_value]
    while root_node[1] != NodeState.SOLVED:
        root_node[2] = _RecSSS(root_node, board, 1, max_depth)
    
    return [move, root_node[2]]

def _RecSSS(current_node, board, depth, max_depth):
    is_leaf_result = _is_leaf(current_node, board, depth, max_depth)
    if is_leaf_result[0]:
        current_node[1] = NodeState.SOLVED
        return min(is_leaf_result[1], current_node[2])
    
    if current_node[1] == NodeState.UNEXPANDED:
        _expand_node(current_node, board, depth, max_depth)
    
    grandson = _process_children(current_node, board, depth, max_depth)
    
    if grandson[1] == NodeState.SOLVED:
        current_node[1] = NodeState.SOLVED

    return grandson[2]
    
def _is_leaf_bool(board, depth, max_depth):
    return depth >= max_depth or board.is_checkmate()

def _is_leaf(node, board, depth, max_depth):
    if board.is_checkmate():
        value = -10**10 - (max_depth - depth) if board.turn else 10**10 + (max_depth - depth)
        return True, value
    elif depth >= max_depth:
        return (True, node[7])
    return (False, 0)

def _expand_node(node, board, depth, max_depth):
    node[1] = NodeState.LIVE
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        node[1] = NodeState.SOLVED
        return min(0, node[2])
    for x in range(len(legal_moves)):
        s_src = board.piece_type_at(legal_moves[x].from_square)
        s_dest = board.piece_type_at(legal_moves[x].to_square)

        if (legal_moves[x].promotion):
            prom = legal_moves[x].promotion
            pos_score = (position_value[chess.WHITE][prom][legal_moves[x].to_square] - position_value[chess.WHITE][s_src][legal_moves[x].from_square])
            prom_score = piece_value[prom] - piece_value[s_src]
            son_value = node[7] + pos_score + prom_score
        else:
            son_value = node[7] + (position_value[chess.WHITE][s_src][legal_moves[x].to_square] - position_value[chess.WHITE][s_src][legal_moves[x].from_square])

        if s_dest:
            son_value += piece_value[s_dest] + position_value[chess.BLACK][s_dest][legal_moves[x].to_square]
        son = [legal_moves[x], NodeState.UNEXPANDED, node[2], [], node, legal_moves, x, son_value]
        board.push(legal_moves[x])
        if _is_leaf_bool(board, depth + 1, max_depth):
            node[3].append(son)
        else:
            s_legal_moves = list(board.legal_moves)
            if s_legal_moves:
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
                gson = [s_legal_moves[0], NodeState.UNEXPANDED, node[2], [], son, s_legal_moves, 0, grandson_value]
                node[3].append(gson)
            else:
                node[3].append(son)
        board.pop()
        
def _process_children(current_node, board, depth, max_depth):
    grandson = max(current_node[3], key=lambda s: s[2])
    while grandson[2] == current_node[2] and grandson[1] != NodeState.SOLVED:
        is_gson = grandson[4][0] != current_node[0]
        depth_adder = 1
        if is_gson:
            depth_adder = 2
            board.push(grandson[4][0])
        board.push(grandson[0])
        grandson[2] = _RecSSS(grandson, board, depth + depth_adder, max_depth)
        if is_gson:
            board.pop()
        if is_gson and grandson[1] == NodeState.SOLVED and grandson[6] != (len(grandson[5]) - 1):
            grandson[6] += 1
            grandson[0] = grandson[5][grandson[6]]
            grandson[1] = NodeState.UNEXPANDED
            grandson[3] = []
            gs_src = board.piece_type_at(grandson[0].from_square)
            gs_dest = board.piece_type_at(grandson[0].to_square)
            if (grandson[0].promotion):
                gs_prom = grandson[0].promotion
                gs_pos_score = position_value[chess.BLACK][gs_prom][grandson[0].to_square] - position_value[chess.BLACK][gs_src][grandson[0].from_square]
                gs_prom_score = piece_value[gs_prom] - piece_value[gs_src]
                grandson[7] = grandson[4][7] - gs_pos_score - gs_prom_score
            else:
                grandson[7] = grandson[4][7] - (position_value[chess.BLACK][gs_src][grandson[0].to_square] - position_value[chess.BLACK][gs_src][grandson[0].from_square])
            if gs_dest:
                grandson[7] -= piece_value[gs_dest] + position_value[chess.WHITE][gs_dest][grandson[0].to_square] 
        board.pop()
        grandson = max(current_node[3], key=lambda s: s[2])
        
    return grandson