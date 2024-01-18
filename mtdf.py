import itertools
import time
from typing import Dict, Iterator, List, Optional, Tuple

import chess

import constants
from chess_node import MtdfNode
from constants import MAX_VALUE, SECONDS_PER_MOVE, MIN_DEPTH
from zobrist import update_hash, zobrist_hash
from evaluation import calculate_move_value

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
    root_node = MtdfNode(move=None, value=0, children={}, hash=zobrist_hash(board), sorted_children_keys=[])
    (depth, move_scores) = _iterative_deepening(root_node, board, pos_table, killer_table, max_depth)
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


def _iterative_deepening(root: MtdfNode, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], max_depth: Optional[int]) -> Tuple[int, List[Tuple[chess.Move, int]]]:
    start = time.perf_counter()
    _mtdf(root, 1, board, pos_table, killer_table)
    result = (1, [(key, root.children[key].gamma) for key in root.sorted_children_keys])
    for depth in range(2, max_depth + 1):
        if abs(root.gamma) < MAX_VALUE and _mtdf(root, depth, board, pos_table, killer_table, start):
            result = (depth, [(key, root.children[key].gamma) for key in root.sorted_children_keys])
        else:
            break
        
    return result

def _mtdf(root: MtdfNode, depth: int, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move], start: Optional[float] = None) -> int:
    pos_result = pos_table.get(root.hash, None)
    if root.gamma is None:
        if pos_result is not None and pos_result[2] == constants.EXACT:
            root.gamma = pos_result[1] if board.turn else -pos_result[1]
        else:
            root.gamma = 0
    
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
    
    _save_score(pos_table, depth + 1, board.turn, constants.EXACT, pos_result, root, root.gamma)
    pos_table[root.hash] = (depth + 1, root.gamma if board.turn else -root.gamma, constants.EXACT)

    return True

# @profile
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
        # elif node_type == constants.UPPERBOUND and saved_score < beta:
        #     score = saved_score
    
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
    # else:
    #     _save_score(pos_table, depth_left, board.turn, constants.UPPERBOUND, saved_value, child, score)
    if score > best_score[1]:
        best_score = (child.move, score)

    return score, alpha, beta, best_score

# @profile
def _alpha_beta(node: MtdfNode, alpha: int, beta: int, depth_left: int, board: chess.Board, pos_table: Dict[int, Tuple[int, int, int, bool]], killer_table: Dict[int, chess.Move]) -> Tuple[chess.Move, int]:
    best_score = (None, -(MAX_VALUE + depth_left))

    if depth_left == 0:
        return (None, _quiescence(node, alpha, beta, board))
    
    children_found = bool(node.children)
    if not children_found:
        node.move_generator = _generate_ordered_moves(board, node)
    # else:
    #     node.children.sort(key=lambda x: x.gamma, reverse=True)

    killer_move = killer_table.get(node.hash, None)
    if killer_move:
        killer_child = node.children.get(killer_move, None)
        killer_child_found = killer_child is not None
        if not killer_child_found:
            child_hash = update_hash(node.hash, board, killer_move)
            move_value = calculate_move_value(killer_move, board)
            killer_child = MtdfNode(move=killer_move, value=move_value - node.value, parent=node, children={}, hash=child_hash, sorted_children_keys=[], killer_move=killer_move)
            node.children[killer_move] = killer_child
            node.sorted_children_keys.insert(0, killer_move)

        score, alpha, beta, best_score = _evaluate_child(killer_child, depth_left, alpha, beta, pos_table, board, best_score, killer_table)
        if best_score[0] is None:
            return (killer_move, score) # fail-soft beta-cutoff
        
        # if killer_child is None:
        #     print("BUG")
        #     print(killer_move, killer_child)
        #     node.print_children()
        #     raise Exception('bug?')
        

    # sort keys
    if children_found:
        node.sorted_children_keys.sort(key=lambda x: node.children[x].gamma, reverse=True)
    
    sorted_children = _sorted_child_generator(node)

    for child in itertools.chain(sorted_children, node.move_generator):
        if killer_move is not None and killer_move == child.move:
            killer_move = None
            continue
        score, alpha, beta, best_score = _evaluate_child(child, depth_left, alpha, beta, pos_table, board, best_score, killer_table)
        # if node.move == chess.Move.from_uci('c6e4') and node.parent.move == chess.Move.from_uci('d5f4'):
        #         print(f'child move: {child.move} score {score} alpha {alpha} beta {beta} best_score {best_score}')
        if best_score[0] is None:
            killer_table[node.hash] = child.move
            return (child.move, score) # fail-soft beta-cutoff

    if not node.children:
        if board.is_check():
            return (None, -(MAX_VALUE + depth_left))
        else:
            return (None, 0)

    return best_score

def _sorted_child_generator(node: MtdfNode):
    for key in node.sorted_children_keys:
        yield node.children[key]

# @profile
def _quiescence(node: MtdfNode, alpha: int, beta: int, board: chess.Board) -> int:
    if board.is_checkmate():
        return -MAX_VALUE
    else:
        return -node.value
    # any_legal_moves = any(board.generate_legal_moves())
    # if not any_legal_moves:
    #     if board.is_check():
    #         return -MAX_VALUE
    #     else:
    #         return 0
    # else:
    #     return -node.value
# @profile
def _generate_ordered_moves(board: chess.Board, node: MtdfNode) -> Iterator[Tuple[chess.Move, int]]:
    sorted_moves = _generate_ordered_legal_moves(board)
    # sorted_moves = _sorted_evaluated_legal_moves(board)

    for move in sorted_moves:
        if node.killer_move is not None and node.killer_move == move:
            node.killer_move = None
            continue
        child_hash = update_hash(node.hash, board, move[0])
        child = MtdfNode(move=move[0], value=move[1] - node.value, parent=node, children={}, hash=child_hash, sorted_children_keys=[])
        node.children[move[0]] = child
        node.sorted_children_keys.append(move[0])
        
        yield child
        
# @profile
def _sorted_evaluated_legal_moves(board: chess.Board) -> List[Tuple[chess.Move, int]]:
    evaluated_legal_moves = [[move, calculate_move_value(move, board)] for move in board.legal_moves]
    evaluated_legal_moves.sort(key=lambda x: x[1], reverse=True)
    
    return evaluated_legal_moves

def _generate_ordered_legal_moves(board: chess.Board) -> Iterator[Tuple[chess.Move, int]]:
    king_mask = board.kings & board.occupied_co[board.turn]
    king = chess.msb(king_mask)
    blockers = board._slider_blockers(king)
    checkers = board.attackers_mask(not board.turn, king)
    if checkers:
        # In check, return all possible moves that escape check
        evasion_generator = _generate_ordered_evasions(king, checkers, board)
        # Captures
        captures = next(evasion_generator)
        legal_captures = [(capture, calculate_move_value(capture, board)) for capture in captures if board._is_safe(king, blockers, capture)]
        legal_captures.sort(key=lambda x: x[1], reverse=True)
        for legal_capture in legal_captures:
            yield legal_capture
        
        other_moves = next(evasion_generator)
        legal_other_moves = [(other_move, calculate_move_value(other_move, board)) for other_move in other_moves if board._is_safe(king, blockers, other_move)]
        legal_other_moves.sort(key=lambda x: x[1], reverse=True)
        for legal_other_move in legal_other_moves:
            yield legal_other_move
        # TEST get all moves and then order them by _calculate_move_value
        # all_evasions = [(move, calculate_move_value(move, board)) for move in board._generate_evasions(board, king, checkers) if board._is_safe(king, blockers, move)]
        # all_evasions.sort(key=lambda x: x[1], reverse=True)
        # for item in all_evasions:
        #     yield item
    else:
        move_generator = _generate_ordered_pseudo_legal_moves(board)

        captures_promotions = next(move_generator)
        legal_captures = [(capture, calculate_move_value(capture, board)) for capture in captures_promotions if board._is_safe(king, blockers, capture)]
        legal_captures.sort(key=lambda x: x[1], reverse=True)
        for legal_capture in legal_captures:
            yield legal_capture
        
        other_moves = next(move_generator)
        legal_other_moves = [(other_move, calculate_move_value(other_move, board)) for other_move in other_moves if board._is_safe(king, blockers, other_move)]
        legal_other_moves.sort(key=lambda x: x[1], reverse=True)
        for legal_other_move in legal_other_moves:
            yield legal_other_move

def _generate_ordered_evasions(king: chess.Square, checkers: chess.Bitboard, board: chess.Board) -> Iterator[List[chess.Move]]:
    captures = []
    sliders = checkers & (board.bishops | board.rooks | board.queens)

    checker = chess.msb(checkers)
    single_checker = chess.BB_SQUARES[checker] == checkers
    if single_checker:
        # Capture a single checker.
        target = checkers
        
        captures.extend(list(board.generate_pseudo_legal_moves(~board.kings, target)))

        # Capture the checking pawn en passant (but avoid yielding
        # duplicate moves).
        if board.ep_square and not chess.BB_SQUARES[board.ep_square] & target:
            last_double = board.ep_square + (-8 if board.turn == chess.WHITE else 8)
            if last_double == checker:
                captures.extend(list(_generate_pseudo_legal_ep(board)))

    attacked = 0
    for checker in chess.scan_reversed(sliders):
        attacked |= chess.ray(king, checker) & ~chess.BB_SQUARES[checker]

    # King moves that are captures
    for to_square in chess.scan_reversed(chess.BB_KING_ATTACKS[king] & board.occupied_co[not board.turn] & ~attacked):
        captures.append(chess.Move(king, to_square))

    yield captures

    other_moves = []
    if single_checker:
        # Block a single checker
        target = chess.between(king, checker)

        other_moves.extend(list(board.generate_pseudo_legal_moves(~board.kings, target)))

    # King moves that are not captures
    for to_square in chess.scan_reversed(chess.BB_KING_ATTACKS[king] & ~board.occupied & ~attacked):
        other_moves.append(chess.Move(king, to_square))

    yield other_moves

def _generate_ordered_pseudo_legal_moves(board: chess.Board) -> Iterator[List[chess.Move]]:
    captures_promotions = []
    all_pawns = board.pawns & board.occupied_co[board.turn]
    promotion_pawns = all_pawns & (chess.BB_RANK_7 if board.turn else chess.BB_RANK_2)
    if promotion_pawns:
        # Generate pawn captures.
        capturers = promotion_pawns
        for from_square in chess.scan_reversed(capturers):
            targets = (
                chess.BB_PAWN_ATTACKS[board.turn][from_square] &
                board.occupied_co[not board.turn])

            for to_square in chess.scan_reversed(targets):
                captures_promotions.append(chess.Move(from_square, to_square, chess.QUEEN))
                # Try comment the rook/bishop/knight?
                # yield chess.Move(from_square, to_square, chess.ROOK)
                # yield chess.Move(from_square, to_square, chess.BISHOP)
                # yield chess.Move(from_square, to_square, chess.KNIGHT)

        # Prepare pawn advance generation.
        if board.turn == chess.WHITE:
            single_moves = promotion_pawns << 8 & ~board.occupied
        else:
            single_moves = promotion_pawns >> 8 & ~board.occupied

        # Generate single pawn moves.
        for to_square in chess.scan_reversed(single_moves):
            from_square = to_square + (8 if board.turn == chess.BLACK else -8)
            captures_promotions.append(chess.Move(from_square, to_square, chess.QUEEN))
            # yield chess.Move(from_square, to_square, chess.ROOK)
            # yield chess.Move(from_square, to_square, chess.BISHOP)
            # yield chess.Move(from_square, to_square, chess.KNIGHT)
    
    pawns = all_pawns & (~chess.BB_RANK_7 if board.turn else ~chess.BB_RANK_2)
    if pawns:
        # Generate pawn captures.
        capturers = pawns
        for from_square in chess.scan_reversed(capturers):
            targets = (
                chess.BB_PAWN_ATTACKS[board.turn][from_square] &
                board.occupied_co[not board.turn])

            for to_square in chess.scan_reversed(targets):
                captures_promotions.append(chess.Move(from_square, to_square))
        
        # Generate en passant captures.
        if board.ep_square:
            captures_promotions.extend(list(_generate_pseudo_legal_ep(board)))

    our_pieces = board.occupied_co[board.turn]
    enemy_pieces = board.occupied_co[not board.turn]

    # Generate piece captures
    non_pawns = our_pieces & ~board.pawns
    saved_attacks = {}
    for from_square in chess.scan_reversed(non_pawns):
        attacks = board.attacks_mask(from_square)
        saved_attacks[from_square] = attacks
        moves = attacks & enemy_pieces
        for to_square in chess.scan_reversed(moves):
            captures_promotions.append(chess.Move(from_square, to_square))
    
    yield captures_promotions

    other_moves = []
    # Generate castling moves.
    other_moves.extend(list(_generate_castling_moves(board)))

    # Generate piece non-capture moves
    for from_square in saved_attacks:
        moves = saved_attacks[from_square] & ~board.occupied
        for to_square in chess.scan_reversed(moves):
            other_moves.append(chess.Move(from_square, to_square))

    if pawns:
        # Prepare pawn advance generation.
        if board.turn == chess.WHITE:
            single_moves = pawns << 8 & ~board.occupied
            double_moves = single_moves << 8 & ~board.occupied & (chess.BB_RANK_3 | chess.BB_RANK_4)
        else:
            single_moves = pawns >> 8 & ~board.occupied
            double_moves = single_moves >> 8 & ~board.occupied & (chess.BB_RANK_6 | chess.BB_RANK_5)

        # Generate double pawn moves.
        for to_square in chess.scan_reversed(double_moves):
            from_square = to_square + (16 if board.turn == chess.BLACK else -16)
            other_moves.append(chess.Move(from_square, to_square))

        # Generate single pawn moves.
        for to_square in chess.scan_reversed(single_moves):
            from_square = to_square + (8 if board.turn == chess.BLACK else -8)
            other_moves.append(chess.Move(from_square, to_square))
    
    yield other_moves

def _generate_castling_moves(board: chess.Board) -> Iterator[chess.Move]:
    backrank = chess.BB_RANK_1 if board.turn == chess.WHITE else chess.BB_RANK_8
    king = board.occupied_co[board.turn] & board.kings & backrank
    king &= -king

    bb_c = chess.BB_FILE_C & backrank
    bb_d = chess.BB_FILE_D & backrank
    bb_f = chess.BB_FILE_F & backrank
    bb_g = chess.BB_FILE_G & backrank

    for candidate in chess.scan_reversed(_clean_castling_rights(board) & backrank):
        rook = chess.BB_SQUARES[candidate]

        a_side = rook < king
        king_to = bb_c if a_side else bb_g
        rook_to = bb_d if a_side else bb_f

        king_path = chess.between(chess.msb(king), chess.msb(king_to))
        rook_path = chess.between(candidate, chess.msb(rook_to))

        if not ((board.occupied ^ king ^ rook) & (king_path | rook_path | king_to | rook_to) or
                board._attacked_for_king(king_path | king, board.occupied ^ king) or
                board._attacked_for_king(king_to, board.occupied ^ king ^ rook ^ rook_to)):
            yield board._from_chess960(board.chess960, chess.msb(king), candidate)

def _clean_castling_rights(board: chess.Board) -> chess.Bitboard:
    """
    Returns valid castling rights filtered from
    :data:`~chess.Board.castling_rights`.
    """
    if board._stack:
        # No new castling rights are assigned in a game, so we can assume
        # they were filtered already.
        return board.castling_rights

    castling = board.castling_rights & board.rooks
    white_castling = castling & chess.BB_RANK_1 & board.occupied_co[chess.WHITE]
    black_castling = castling & chess.BB_RANK_8 & board.occupied_co[chess.BLACK]

    # The rooks must be on a1, h1, a8 or h8.
    white_castling &= (chess.BB_A1 | chess.BB_H1)
    black_castling &= (chess.BB_A8 | chess.BB_H8)

    # The kings must be on e1 or e8.
    if not board.occupied_co[chess.WHITE] & board.kings & chess.BB_E1:
        white_castling = 0
    if not board.occupied_co[chess.BLACK] & board.kings & chess.BB_E8:
        black_castling = 0

    return white_castling | black_castling

def _generate_pseudo_legal_ep(board: chess.Board) -> Iterator[chess.Move]:
    if not board.ep_square or not chess.BB_SQUARES[board.ep_square]:
        return

    if chess.BB_SQUARES[board.ep_square] & board.occupied:
        return

    capturers = (
        board.pawns & board.occupied_co[board.turn] &
        chess.BB_PAWN_ATTACKS[not board.turn][board.ep_square] &
        chess.BB_RANKS[4 if board.turn else 3])

    for capturer in chess.scan_reversed(capturers):
        yield chess.Move(capturer, board.ep_square)


def _save_score(pos_table: Dict[int, Tuple[int, int, int, bool]], depth_left: int, turn: bool, node_type: int, saved_value: int, child: MtdfNode, score: int):
    if not saved_value or saved_value and saved_value[0] < depth_left:
        # if child.hash == 14107997451098753891 and abs(score) >= MAX_VALUE:
        #     print(score, 'saving', turn, depth_left, child.parent)
        pos_table[child.hash] = (depth_left, score if turn else -score, node_type)

if __name__ == '__main__':
    board = chess.Board()
    move = solve_position_root(board, 5)