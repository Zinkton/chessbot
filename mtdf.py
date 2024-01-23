from collections import deque
import time
import uuid
from typing import Optional, Tuple
from uuid import UUID

import constants
import custom_chess as chess
from chess_node import MtdfNode
from constants import MAX_VALUE, SECONDS_PER_MOVE
from evaluation import SEE_capture, evaluate_board, get_total_material, set_king_position_values, piece_value, promotion_queen, delta_pruning_delta
from move_generation import generate_ordered_moves, generate_sorted_evasions, generate_quiescence_moves, is_check
from tt_utilities_dict import probe_tt_scores, save_tt_killer, save_tt_score
from zobrist import update_hash, zobrist_hash

current_game_id = None
tt_scores = None
tt_killers = None
last_pos = None
is_late_game = None
start = None
def solve_position_root(board: chess.Board, game_id: UUID, min_depth: int = constants.MIN_DEPTH, max_depth: int = constants.MAX_DEPTH) -> Tuple[chess.Move, int]:
    global current_game_id
    global tt_scores
    global tt_killers
    global last_pos
    global is_late_game
    global start

    start = time.perf_counter()

    if current_game_id != game_id:
        current_game_id = game_id
        tt_scores = {}
        tt_killers = {}
        last_pos = {chess.WHITE: deque(), chess.BLACK: deque()}
        is_late_game = False

    if not is_late_game:
        if get_total_material(board) <= 750:
            is_late_game = True
            tt_scores = {}
            set_king_position_values(lategame=True)
        else:
            set_king_position_values(lategame=False)

    initial_value = -evaluate_board(board) if board.turn else evaluate_board(board)
    root_node = MtdfNode(move=None, value=initial_value, hash=zobrist_hash(board))

    repetition_moves = [pos[1] for pos in last_pos[board.turn] if pos[0] == root_node.hash]
    repetition_move = repetition_moves[-1] if repetition_moves else None

    depth, move, score = _iterative_deepening(root_node, board, min_depth, max_depth, repetition_move)

    last_pos[board.turn].append((root_node.hash, move))
    print(f'depth: {depth}, score: {score}')

    return (move, score)

def _iterative_deepening(root: MtdfNode, board: chess.Board, min_depth: int, max_depth: int, repetition_move: Optional[chess.Move] = None) -> Tuple[int, chess.Move, int]:
    result = None
    for depth in range(1, max_depth + 1):
        if root.gamma is not None and abs(root.gamma) >= MAX_VALUE:
            break
        if time.perf_counter() - start >= (SECONDS_PER_MOVE - 2.5) and depth > min_depth:
            break
        mtdf_result = _mtdf(root, depth, board, repetition_move)
        if mtdf_result is not None:
            result_move, result_score = mtdf_result
            result = (depth, result_move, result_score)
        else:
            break
        
    return result

def _mtdf(root: MtdfNode, depth: int, board: chess.Board, repetition_move: Optional[chess.Move] = None) -> Tuple[chess.Move, int]:
    pos_result = probe_tt_scores(tt_scores, root.hash)
    if root.gamma is None:
        if pos_result is not None and pos_result[2] == constants.EXACT:
            root.gamma = pos_result[1] if board.turn else -pos_result[1]
        else:
            root.gamma = -root.value

    upper_bound = MAX_VALUE + depth
    lower_bound = -MAX_VALUE - depth

    while upper_bound - lower_bound > 0:
        beta = root.gamma + 1 if root.gamma == lower_bound else root.gamma
        (best_move, root.gamma) = _alpha_beta(root.value, beta - 1, beta, depth, board, root.hash, repetition_move)
        
        if root.gamma < beta:
            upper_bound = root.gamma
        else:
            lower_bound = root.gamma
    
    if repetition_move is None or repetition_move.from_square != best_move.from_square or repetition_move.to_square != best_move.to_square:
        save_tt_score(tt_scores, depth + 1, board.turn, constants.EXACT, pos_result, root.hash, root.gamma)

    return best_move, root.gamma

# @profile
def _evaluate_child(value: int, parent_hash: int, move: chess.Move, depth_left: int, alpha: int, beta: int, board: chess.Board, best_score: Tuple[Optional[chess.Move], int], repetition_move: Optional[chess.Move] = None) -> Tuple[int, int, int, Tuple[Optional[chess.Move], int]]:
    if repetition_move is not None and repetition_move.from_square == move.from_square and repetition_move.to_square == move.to_square:
        score = 0
        if score >= beta:
            return score, alpha, beta, (None, score) # fail-soft beta-cutoff
        
        if score > best_score[1]:
            best_score = (move, score)
            if score > alpha:
                alpha = score

        return score, alpha, beta, best_score

    hash = update_hash(parent_hash, board, move)
    score = None

    saved_value = probe_tt_scores(tt_scores, hash)
    if saved_value is not None and saved_value[0] >= depth_left: # no touching
        _, saved_score, node_type = saved_value
        saved_score = saved_score if board.turn else -saved_score

        if node_type == constants.EXACT:
            score = saved_score
        elif node_type == constants.LOWERBOUND and saved_score > alpha:
            score = saved_score
        elif node_type == constants.UPPERBOUND and saved_score < beta:
            score = saved_score

    if score is None:
        board.push(move)
        (best_move, score) = _alpha_beta(value, -beta, -alpha, depth_left - 1, board, hash)
        score = -score
        board.pop()

    if score >= beta:
        save_tt_score(tt_scores, depth_left, board.turn, constants.LOWERBOUND, saved_value, hash, score)
        return score, alpha, beta, (None, score) # fail-soft beta-cutoff
    elif score > best_score[1]:
        best_score = (move, score)
        if score > alpha:
            save_tt_score(tt_scores, depth_left, board.turn, constants.EXACT, saved_value, hash, score)
            alpha = score
    else:
        save_tt_score(tt_scores, depth_left, board.turn, constants.UPPERBOUND, saved_value, hash, score)

    return score, alpha, beta, best_score

# @profile
def _alpha_beta(value: int, alpha: int, beta: int, depth_left: int, board: chess.Board, hash: int, repetition_move: Optional[chess.Move] = None) -> Tuple[Optional[chess.Move], int]:
    if depth_left == 0:
        return (None, _quiescence(value, alpha, beta, board, True))
    
    best_score = (None, -(MAX_VALUE + depth_left - 1))

    for move, move_value in generate_ordered_moves(board, hash, tt_killers):
        score, alpha, beta, best_score = _evaluate_child(move_value - value, hash, move, depth_left, alpha, beta, board, best_score, repetition_move)
        if best_score[0] is None:
            save_tt_killer(tt_killers, move, hash)
            return (move, score) # fail-soft beta-cutoff

    if best_score[0] is None:
        return (board.peek(), 0) if not is_check(board) else (board.peek(), best_score[1])

    return best_score

# @profile
def _quiescence(value: int, alpha: int, beta: int, board: chess.Board, first_call: bool = False) -> int:
    stand_pat = -value
    
    king_mask = board.kings & board.occupied_co[board.turn]
    king = chess.msb(king_mask)
    checkers = board.attackers_mask(not board.turn, king)

    if checkers:
        best_score = -MAX_VALUE

        score = None
        for move, move_value in generate_sorted_evasions(board, king, checkers):                
            board.push(move)
            score = -_quiescence(stand_pat + move_value, -beta, -alpha, board)
            board.pop()

            if score >= beta:
                return score # fail soft beta cut-off
            if score > best_score:
                best_score = score
                if score > alpha:
                    alpha = score

        if not first_call and best_score == -MAX_VALUE:
            return score if score is not None else stand_pat
        
        return best_score
    else:
        if stand_pat >= beta:
            return stand_pat # fail soft beta cut-off
        
        if not is_late_game:
            big_delta = piece_value[chess.QUEEN] if not _is_promoting_pawn(board) else promotion_queen
            
            if stand_pat < alpha - big_delta:
                return stand_pat

        best_score = stand_pat
        if stand_pat > alpha:
            alpha = stand_pat

        for move, move_value_src_dest in generate_quiescence_moves(board, king):
            move_value, src_piece_val, dest_piece_val = move_value_src_dest
            new_value = stand_pat + move_value
            if not is_late_game and new_value < alpha - delta_pruning_delta:
                continue
                
            if move.promotion or SEE_capture(move, board, src_piece_val, dest_piece_val) >= 0:
                board.push(move)
                score = -_quiescence(new_value, -beta, -alpha, board)
                board.pop()

                if score >= beta:
                    return score # fail soft beta cut-off
                if score > best_score:
                    best_score = score
                    if score > alpha:
                        alpha = score

        return best_score

def _is_promoting_pawn(board: chess.Board):
    board.pawns & board.occupied_co[board.turn] & (chess.BB_RANK_7 if board.turn else chess.BB_RANK_2)

if __name__ == '__main__':
    # for x in range(1000):
    #     board = chess.Board()
    #     while True:
    #         legal_moves = list(board.legal_moves)
    #         my_legal_moves = list(_generate_ordered_legal_moves(board))
    #         if ((len(legal_moves) - len(my_legal_moves)) % 3 != 0):
    #             raise Exception("failure")
    #         board.push(random.choice(legal_moves))
    #         if board.outcome() is not None:
    #             break
    # print('success')
    board = chess.Board()
    stack = []
    game_id = uuid.uuid4()
    while True:
        move, score = solve_position_root(board, game_id, 7, 7)
        stack.append(board.san(move))
        board.push(move)
        if board.outcome(claim_draw=True):
            break
    print(stack)