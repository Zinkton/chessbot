from typing import Optional, Tuple
import custom_chess as chess
from constants import MAX_VALUE

# Piece values
piece_value = {
    chess.PAWN: 100,
    chess.KNIGHT: 280,
    chess.BISHOP: 320,
    chess.ROOK: 479,
    chess.QUEEN: 929,
    chess.KING: MAX_VALUE
}

delta_pruning_delta = piece_value[chess.PAWN] * 2
promotion_queen = piece_value[chess.QUEEN] * 2 - delta_pruning_delta

# Position tables for each piece type
pawn_table = [ 100, 100, 100, 100, 105, 100, 100,  100,
  78,  83,  86,  73, 102,  82,  85,  90,
   7,  29,  21,  44,  40,  31,  44,   7,
 -17,  16,  -2,  15,  14,   0,  15, -13,
 -26,   3,  10,   9,   6,   1,   0, -23,
 -22,   9,   5, -11, -10,  -2,   3, -19,
 -31,   8,  -7, -37, -36, -14,   3, -31,
   0,   0,   0,   0,   0,   0,   0,   0]
knight_table = [-66, -53, -75, -75, -10, -55, -58, -70,
             -3,  -6, 100, -36,   4,  62,  -4, -14,
             10,  67,   1,  74,  73,  27,  62,  -2,
             24,  24,  45,  37,  33,  41,  25,  17,
             -1,   5,  31,  21,  22,  35,   2,   0,
            -18,  10,  13,  22,  18,  15,  11, -14,
            -23, -15,   2,   0,   2,   0, -23, -20,
            -74, -23, -26, -24, -19, -35, -22, -69]
bishop_table = [-59, -78, -82, -76, -23,-107, -37, -50,
-11,  20,  35, -42, -39,  31,   2, -22,
 -9,  39, -32,  41,  52, -10,  28, -14,
 25,  17,  20,  34,  26,  25,  15,  10,
 13,  10,  17,  23,  17,  16,   0,   7,
 14,  25,  24,  15,   8,  25,  20,  15,
 19,  20,  11,   6,   7,   6,  20,  16,
 -7,   2, -15, -12, -14, -15, -10, -10]
rook_table = [ 35,  29,  33,   4,  37,  33,  56,  50,
 55,  29,  56,  67,  55,  62,  34,  60,
 19,  35,  28,  33,  45,  27,  25,  15,
  0,   5,  16,  13,  18,  -4,  -9,  -6,
-28, -35, -16, -21, -13, -29, -46, -30,
-42, -28, -42, -25, -25, -35, -26, -46,
-53, -38, -31, -26, -29, -43, -44, -53,
-30, -24, -18,   5,  -2, -18, -31, -32]
queen_table = [  6,   1,  -8,-104,  69,  24,  88,  26,
 14,  32,  60, -10,  20,  76,  57,  24,
 -2,  43,  32,  60,  72,  63,  43,   2,
  1, -16,  22,  17,  25,  20, -13,  -6,
-14, -15,  -2,  -5,  -1, -10, -20, -22,
-30,  -6, -13, -11, -16, -11, -16, -27,
-36, -18,   0, -19, -15, -15, -21, -38,
-39, -30, -31, -13, -31, -36, -34, -42]
king_table = [  4,  54,  47, -99, -99,  60,  83, -62,
-32,  10,  55,  56,  56,  55,  10,   3,
-62,  12, -57,  44, -67,  28,  37, -31,
-55,  50,  11,  -4, -19,  13,   0, -49,
-55, -43, -52, -28, -51, -47,  -8, -50,
-47, -42, -43, -79, -64, -32, -29, -32,
 -4,   3, -14, -50, -57, -18,  13,   4,
 17,  30,  -3, -14,   6,  -1,  40,  18]
king_table_endgame = [
            -50, -40, -30, -20, -20, -30, -40, -50,
            -30, -20, -10,   0,   0, -10, -20, -30,
            -30, -10,  20,  30,  30,  20, -10, -30,
            -30, -10,  30,  40,  40,  30, -10, -30,
            -30, -10,  30,  40,  40,  30, -10, -30,
            -30, -10,  20,  30,  30,  20, -10, -30,
            -30, -30,   0,   0,   0,   0, -30, -30,
            -50, -30, -30, -30, -30, -30, -30, -50
        ]

def _invert_columns(table):
    result = table[::-1]
    reversed_rows = [result[i:i+8][::-1] for i in range(0, len(result), 8)]
    flattened_list = [item for sublist in reversed_rows for item in sublist]
    
    return flattened_list

# Reversed tables for white pieces
position_value = {
    chess.WHITE: {
        chess.PAWN: _invert_columns(pawn_table.copy()),
        chess.KNIGHT: _invert_columns(knight_table.copy()),
        chess.BISHOP: _invert_columns(bishop_table.copy()),
        chess.ROOK: _invert_columns(rook_table.copy()),
        chess.QUEEN: _invert_columns(queen_table.copy()),
        chess.KING: _invert_columns(king_table.copy())
    },
    chess.BLACK: {
        chess.PAWN: pawn_table.copy(),
        chess.KNIGHT: knight_table.copy(),
        chess.BISHOP: bishop_table.copy(),
        chess.ROOK: rook_table.copy(),
        chess.QUEEN: queen_table.copy(),
        chess.KING: king_table.copy()
    }
}

K_CASTLING_VALUE = position_value[chess.WHITE][chess.ROOK][chess.F1] - position_value[chess.WHITE][chess.ROOK][chess.H1] + position_value[chess.WHITE][chess.KING][chess.G1] - position_value[chess.WHITE][chess.KING][chess.E1]
Q_CASTLING_VALUE = position_value[chess.WHITE][chess.ROOK][chess.D1] - position_value[chess.WHITE][chess.ROOK][chess.A1] + position_value[chess.WHITE][chess.KING][chess.C1] - position_value[chess.WHITE][chess.KING][chess.E1]

def set_king_position_values(lategame: bool):
    global position_value
    if lategame:
        position_value[chess.WHITE][chess.KING] = _invert_columns(king_table_endgame.copy())
        position_value[chess.BLACK][chess.KING] = king_table_endgame.copy()
    else:
        position_value[chess.WHITE][chess.KING] = _invert_columns(king_table.copy())
        position_value[chess.BLACK][chess.KING] = king_table.copy()

def calculate_move_value(move: chess.Move, board: chess.Board):
    src_piece = board.piece_type_at(move.from_square)
    dest_piece = board.piece_type_at(move.to_square)

    castle_value = _check_castling(board, move, src_piece)
    if castle_value is not None:
        return (castle_value, src_piece, dest_piece)
    
    value = 0
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

    return (value, src_piece, dest_piece)

def calculate_move_value_quiescence(move: chess.Move, board: chess.Board):    
    value = 0
    src_piece = board.piece_type_at(move.from_square)
    dest_piece = board.piece_type_at(move.to_square)

    src_piece_value = piece_value[src_piece]
    dest_piece_value = None
    
    if move.promotion:
        prom = move.promotion
        pos_score = position_value[board.turn][prom][move.to_square] - position_value[board.turn][src_piece][move.from_square]
        prom_score = piece_value[prom] - src_piece_value
        value = pos_score + prom_score
    else:
        value = position_value[board.turn][src_piece][move.to_square] - position_value[board.turn][src_piece][move.from_square]

    if dest_piece:
        # If we capture, add score based on captured piece value and position value
        dest_piece_value = piece_value[dest_piece]
        value += dest_piece_value + position_value[not board.turn][dest_piece][move.to_square]
    elif src_piece == chess.PAWN and move.to_square == board.ep_square:
        down = -8 if board.turn == chess.WHITE else 8
        capture_square = board.ep_square + down
        dest_piece_value = piece_value[chess.PAWN]
        value += dest_piece_value + position_value[not board.turn][chess.PAWN][capture_square]

    return (value, src_piece_value, dest_piece_value)

def _check_castling(board: chess.Board, move: chess.Move, src_piece: chess.PieceType):
    if src_piece == chess.KING:
        diff = chess.square_file(move.from_square) - chess.square_file(move.to_square)
        if abs(diff) > 1:
            return K_CASTLING_VALUE if diff < 0 else Q_CASTLING_VALUE
        
    return None

def evaluate_board(board: chess.Board):
    score = 0
    for square in range(64):
        piece = board.piece_at(square)
        if piece:
            sign = 1 if piece.color else -1
            score += (piece_value[piece.piece_type] + position_value[piece.color][piece.piece_type][square]) * sign
    
    return score

def SEE(square: chess.Square, board: chess.Board, dest_piece_value: int) -> int:
    value = 0
    piece_value = get_smallest_attacker(board, square)
    if piece_value is not None:
        piece, src_piece_value = piece_value
        board.push(chess.Move(piece, square))
        value = max(0, dest_piece_value - SEE(square, board, src_piece_value))
        board.pop()

    return value

def SEE_capture(move: chess.Move, board: chess.Board, src_piece_val: int, dest_piece_val: int):
    value = 0
    board.push(move)
    value = dest_piece_val - SEE(move.to_square, board, src_piece_val)
    board.pop()

    return value

def get_smallest_attacker(board: chess.Board, square: chess.Square) -> Optional[Tuple[chess.Square, int]]:
    pawn_attackers = board.pawns & chess.BB_PAWN_ATTACKS[not board.turn][square] & board.occupied_co[board.turn]
    if pawn_attackers:
        return (chess.msb(pawn_attackers), piece_value[chess.PAWN])

    knight_attackers = board.knights & chess.BB_KNIGHT_ATTACKS[square] & board.occupied_co[board.turn]
    if knight_attackers:
        return (chess.msb(knight_attackers), piece_value[chess.KNIGHT])
    
    diag_pieces = chess.BB_DIAG_MASKS[square] & board.occupied
    bishop_attackers = board.bishops & chess.BB_DIAG_ATTACKS[square][diag_pieces] & board.occupied_co[board.turn]
    if bishop_attackers:
        return (chess.msb(bishop_attackers), piece_value[chess.BISHOP])
    
    rank_pieces = chess.BB_RANK_MASKS[square] & board.occupied
    rook_attackers = board.rooks & chess.BB_RANK_ATTACKS[square][rank_pieces]
    if rook_attackers:
        return (chess.msb(rook_attackers), piece_value[chess.ROOK])
    file_pieces = chess.BB_FILE_MASKS[square] & board.occupied
    rook_attackers = board.rooks & chess.BB_FILE_ATTACKS[square][file_pieces]
    if rook_attackers:
        return (chess.msb(rook_attackers), piece_value[chess.ROOK])

    queen_attackers = board.queens & chess.BB_RANK_ATTACKS[square][rank_pieces]
    if queen_attackers:
        return (chess.msb(queen_attackers), piece_value[chess.QUEEN])
    queen_attackers = board.queens & chess.BB_FILE_ATTACKS[square][file_pieces]
    if queen_attackers:
        return (chess.msb(queen_attackers), piece_value[chess.QUEEN])
    queen_attackers = board.queens & chess.BB_DIAG_ATTACKS[square][diag_pieces]
    if queen_attackers:
        return (chess.msb(queen_attackers), piece_value[chess.QUEEN])
    
    king_attackers = board.kings & chess.BB_KING_ATTACKS[square]
    if king_attackers:
        return (chess.msb(king_attackers), piece_value[chess.KING])
    
    return None

def get_total_material(board: chess.Board):
    white_material = 0
    black_material = 0
    for square in range(64):
        piece = board.piece_at(square)
        if piece and piece != chess.KING:
            if piece.color:
                white_material += piece_value[piece.piece_type]
            else:
                black_material += piece_value[piece.piece_type]
    
    return min(white_material, black_material)
