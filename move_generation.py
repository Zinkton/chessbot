from typing import Iterator, List, Tuple
import chess
from chess_node import MtdfNode
from evaluation import calculate_move_value
from zobrist import update_hash


def sorted_child_generator(node: MtdfNode):
    for key in node.sorted_children_keys:
        yield node.children[key]
        
# @profile
def is_checkmate(board: chess.Board) -> bool:
    if not _is_check(board):
        return False
    
    return not any(board.generate_legal_moves())

def _checkers_mask(board: chess.Board) -> chess.Bitboard:
    king = _king(board, board.turn)
    return board.attackers_mask(not board.turn, king)

def _is_check(board: chess.Board()) -> bool:
    return bool(_checkers_mask(board))

def _king(board: chess.Board, color: chess.Color) -> chess.Square:
    king_mask = board.occupied_co[color] & board.kings
    return chess.msb(king_mask)

# @profile
def generate_ordered_moves(board: chess.Board, node: MtdfNode) -> Iterator[Tuple[chess.Move, int]]:
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

# @profile
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