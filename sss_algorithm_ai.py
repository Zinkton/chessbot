import chess
import evaluation
import model_utilities
from constants import NodeState
from evaluation import piece_value, position_value
from chess_node import ChessNode
from chess_agent import ChessAgent

def solve_position(input):
    (board, max_depth, move, agent) = (input[0], input[1], input[2], input[3])
    agent = model_utilities.copy_model(agent).cuda()
    state = model_utilities.invert_state(model_utilities.get_board_state(board))
    calculation_result = _calculate_move_value(move, board, agent, state)
    initial_value = -calculation_result[0]
    state = calculation_result[1]
    board.push(move)
    
    root_node = ChessNode(move=move, value=initial_value, children=[])
    while root_node.state != NodeState.SOLVED:
        root_node.min_value = _recursiveSearch(root_node, board, 1, max_depth, agent, state)
    
    return [move, root_node.min_value]

def _recursiveSearch(current_node: ChessNode, board, depth, max_depth, agent, state):
    """ SSS* search algorithm implementation. """
    is_leaf, leaf_value = _is_leaf_node(current_node, board, depth, max_depth)
    if is_leaf:
        current_node.state = NodeState.SOLVED
        return min(leaf_value, current_node.min_value)
    
    if current_node.state == NodeState.UNEXPANDED:
        leaf_value = _expand_node(current_node, board, depth, max_depth, agent, state)
        if leaf_value is not None:
            return leaf_value
    
    grandson_node = _process_children(current_node, board, depth, max_depth, agent, state)
    
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

def _expand_node(node: ChessNode, board, depth, max_depth, agent, state):
    node.state = NodeState.LIVE
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        node.state = NodeState.SOLVED
        return min(0, node.min_value)
    evaluated_moves = _sorted_evaluated_legal_moves(board, legal_moves, agent, state.clone())
    for x in range(len(evaluated_moves)):
        son_value = node.value + evaluated_moves[x][1][0]
        son_node = ChessNode(move=evaluated_moves[x][0], value=son_value, min_value=node.min_value, children=[], parent=node, legal_moves=evaluated_moves, move_index=x)
        board.push(evaluated_moves[x][0])
        son_state = evaluated_moves[x][1][1]
        if _is_leaf_node(None, board, depth + 1, max_depth):
            node.children.append(son_node)
        else:
            s_legal_moves = list(board.legal_moves)
            if s_legal_moves:
                s_evaluated_moves = _sorted_evaluated_legal_moves(board, s_legal_moves, agent, son_state.clone())
                grandson_value = son_value - s_evaluated_moves[0][1][0]
                grandson_node = ChessNode(move=s_evaluated_moves[0][0], value=grandson_value, min_value=node.min_value, children=[], parent=son_node, legal_moves=s_evaluated_moves, move_index=0)
                node.children.append(grandson_node)
            else:
                node.children.append(son_node)
        board.pop()
        
    return None

def _process_children(current_node: ChessNode, board, depth, max_depth, agent, state) -> ChessNode:
    grandson_node = max(current_node.children, key=lambda s: s.min_value)
    while grandson_node.min_value == current_node.min_value and grandson_node.state != NodeState.SOLVED:
        is_gson = grandson_node.parent.move != current_node.move
        depth_adder = 1
        if is_gson:
            depth_adder = 2                
            board.push(grandson_node.parent.move)
        board.push(grandson_node.move)
        gs_state = grandson_node.legal_moves[grandson_node.move_index][1][1]
        grandson_node.min_value = _recursiveSearch(grandson_node, board, depth + depth_adder, max_depth, agent, gs_state)
        if is_gson:
            board.pop()
        if is_gson and grandson_node.state == NodeState.SOLVED and grandson_node.move_index != (len(grandson_node.legal_moves) - 1):
            grandson_node.move_index += 1
            grandson_node.move = grandson_node.legal_moves[grandson_node.move_index][0]
            grandson_node.state = NodeState.UNEXPANDED
            grandson_node.children = []
            grandson_node.value = grandson_node.parent.value - grandson_node.legal_moves[grandson_node.move_index][1][0]
        board.pop()
        grandson_node = max(current_node.children, key=lambda s: s.min_value)
        
    return grandson_node

def _calculate_move_value(move, board, agent: ChessAgent, state):
    add_state = model_utilities.get_additional_state_tensor(board)
    if not board.turn:
        model_utilities.invert_additional_state(add_state)
    states = []
    add_states = []
    states.append(state.clone())
    add_states.append(add_state)
    inverted_state = model_utilities.make_move_on_state(state, move, board)
    board.push(move)
    add_state_2 = model_utilities.get_additional_state_tensor(board)
    inverted_state = inverted_state if inverted_state is not None else model_utilities.invert_state(state)
    
    board.pop()
    
    states.append(inverted_state.clone())
    add_states.append(add_state_2)
    evaluations = agent.get_multiple_position_evaluations(states, add_states)
    
    value = -evaluations[1][0] - evaluations[0][0]
    
    return [value, inverted_state]

def _sorted_evaluated_legal_moves(board, legal_moves, agent, state):
    states = []
    add_states = []
    evaluated_legal_moves = []
    for move in legal_moves:
        add_state = model_utilities.get_additional_state_tensor(board)
        if not board.turn:
            model_utilities.invert_additional_state(add_state)
        states.append(state.clone())
        add_states.append(add_state)
        inverted_state = model_utilities.make_move_on_state(state, move, board)
        board.push(move)
        add_state_2 = model_utilities.get_additional_state_tensor(board)
        inverted_state = inverted_state if inverted_state is not None else model_utilities.invert_state(state)
        
        board.pop()
        
        states.append(inverted_state.clone())
        add_states.append(add_state_2)
        evaluated_legal_moves.append([move, 0])
        
    evaluations = agent.get_multiple_position_evaluations(states, add_states)
    evaluated_legal_moves = []
    for x in range(len(legal_moves)):
        before = evaluations[x*2][0]
        after = -evaluations[x*2+1][0]
        value = after - before
        evaluated_legal_moves[x][1] = value
        
    evaluated_legal_moves.sort(key=lambda x: x[1][0], reverse=True)
    
    return evaluated_legal_moves
            