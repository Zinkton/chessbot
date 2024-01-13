from typing import List
import constants
import random
import requests
from saved_values import SavedValues
from time import perf_counter, sleep
from utilities import flip_and_mirror_fen, invert_rank
from evaluation import piece_value
from chess import Board
from multiprocessing import Pool
from sss_algorithm import solve_position
from collections import deque

class ChessBot():
    def __init__(self):
        self.fen_history = deque(maxlen=constants.MAX_FEN_HISTORY)

    # Main chess bot logic
    def get_move(self, bot_input):
        isCasual = bool(bot_input['isCasual'])
        depth = int(bot_input['depth'])
        start = perf_counter()
        
        fen = bot_input['boardFen']
        if constants.OPENING_BOOK:
            move = self.opening_book(fen)
            if move is not None:
                return move
            
        # We want the algorithm to always calculate moves from black's POV so we do some FEN manipulation
        is_board_flipped = fen.split(' ')[1] == 'w'
        if is_board_flipped:
            fen = flip_and_mirror_fen(fen)

        board = Board(fen)
        move = self._select_random_best_move(board) if not isCasual else self._select_random_best_move(board, depth)

        self._update_fen_history(board, move)
        
        if isCasual and perf_counter() - start < 2.0:
            sleep(2.0 - (perf_counter() - start))
        # We want to convert the move back to white's POV
        if is_board_flipped:
            return invert_rank(move)
        return move
    
    def opening_book(self, fen):
        r = requests.get(url='https://explorer.lichess.ovh/masters', params={'fen': fen})
        data = r.json()
        moves = data['moves']
        if not moves:
            return None
        sleep(2)
        moves.sort(key=lambda x: x['draws'] + x['white'] + x['black'], reverse=True)
        return moves[0]['uci']
        # board = Board(fen)
        # for move in moves:
        #     if board.turn and move['white'] > move['black']:
        #         return move['uci']
        #     if not board.turn and move['black'] > move['white']:
        #         return move['uci']
                
        # return moves[0]['uci']

    def _select_random_best_move(self, board, max_depth = constants.MAX_DEPTH):
        unevaluated_moves = [[move, 0] for move in board.legal_moves]
        start = perf_counter()
        best_moves = self._evaluate_and_filter_best_moves(
            board, unevaluated_moves, max_depth)
        stop = perf_counter()
        print('took %s seconds' % (stop - start))
        
        return random.choice(best_moves)

    def _update_fen_history(self, board, move):
        board.push(move)
        self.fen_history.append(board.board_fen())

    def _combine_saved_values(self, evaluated_moves):
        saved_values_list = []
        for evaluated_move in evaluated_moves:
            saved_values_list.append(evaluated_move[3])

        final_saved_values = SavedValues({}, {})
        for saved_values in saved_values_list:
            final_saved_values.value_table.update(saved_values.value_table)
            final_saved_values.legal_move_table.update(saved_values.legal_move_table)
        
        return final_saved_values

    def _evaluate_and_filter_best_moves(self, board, unevaluated_moves, max_depth):
        # A board copy to manipulate, depth of search and the move to evaluate
        solve_position_params = [[board.copy(), max_depth, move, None, SavedValues({}, {})] for move, _ in unevaluated_moves]
        start = perf_counter()
        evaluated_moves = None
        with Pool(processes=constants.PROCESS_COUNT) as p:
            evaluated_moves = p.map(solve_position, solve_position_params)
        print(f'{perf_counter() - start} finished depth {max_depth}')

        outputs = evaluated_moves
        while constants.SECONDS_FOR_ITERATIVE_DEEPENING - (perf_counter() - start) > 0 and not any(output[1] < -100000 and output[2].state == constants.NodeState.SOLVED for output in outputs):
            max_depth += 1
            evaluated_moves = outputs
            saved_values = self._combine_saved_values(evaluated_moves)
            solve_position_params = [[board.copy(), max_depth, move, start, saved_values.clone()] for move, _ in unevaluated_moves]
            with Pool(processes=constants.PROCESS_COUNT) as p:
                outputs = p.map(solve_position, solve_position_params)
            
            print(f'{perf_counter() - start} finished depth {max_depth}')
        
        merged = {}
        for evaluation_move in evaluated_moves:
            merged[str(evaluation_move[0])] = evaluation_move
        
        for output in outputs:
            if output[2].state == constants.NodeState.SOLVED and output[2].depth > merged[str(output[0])][2].depth:
                merged[str(output[0])] = output
        
        evaluated_moves = list(merged.values())

        #winning_evaluated_moves = self._filter_winning_evaluated_moves(evaluated_moves)
        if len(evaluated_moves) > 1:
            self._remove_repeating_move(evaluated_moves, board)
            
        best_evaluated_moves = self._filter_best_evaluated_moves(evaluated_moves, max_depth)
        if len(best_evaluated_moves) > 1:
            self._prioritize_promotion_and_capture(best_evaluated_moves, board)
            # Filter again after adjusting scores
            best_evaluated_moves = self._filter_best_evaluated_moves(evaluated_moves)
            
        return [best_evaluated_move[0] for best_evaluated_move in best_evaluated_moves]
    
    def _filter_winning_evaluated_moves(self, evaluated_moves):
        return [evaluated_move for evaluated_move in evaluated_moves if evaluated_move[1] <= 0]
        
    def _remove_repeating_move(self, evaluated_moves, board):
        """ Find and remove the repeating move """
        if len(self.fen_history) == 2:
            repeating_move = self._find_repeating_move(evaluated_moves, board)
            
            if repeating_move:
                evaluated_moves.remove(repeating_move)
    
    def _find_repeating_move(self, move_evaluations, board):
        repeating_move = None
        for move_evaluation in move_evaluations:
            board.push(move_evaluation[0])
            if board.board_fen() == self.fen_history[0]:
                repeating_move = move_evaluation
                board.pop()
                break
            board.pop()
        
        return repeating_move
    
    def _prioritize_promotion_and_capture(self, best_moves, board):
        """ Adjust scores for moves that involve promotion or capture. """        
        for move in best_moves:
            if move[0].promotion:
                move[1] -= piece_value[move[0].promotion]
            if board.piece_at(move[0].to_square):
                move[1] -= piece_value[board.piece_at(move[0].to_square).piece_type]
        
    def _filter_best_evaluated_moves(self, evaluated_moves, max_depth):
        """ Return only the move evaluations with the best score """
        max_depth_moves = [evaluated_move for evaluated_move in evaluated_moves if evaluated_move[2].depth == max_depth]
        best_max_depth_score = min(evaluated_move[1] for evaluated_move in max_depth_moves) if max_depth_moves else None
        if best_max_depth_score is not None and best_max_depth_score < 0:
            return [evaluated_move for evaluated_move in max_depth_moves if evaluated_move[1] == best_max_depth_score]
        else:
            best_score = min(evaluated_move[1] for evaluated_move in evaluated_moves)
            if best_max_depth_score is None or best_score < best_max_depth_score:
                return [evaluated_move
                        for evaluated_move in evaluated_moves if evaluated_move[1] == best_score]
            else:
                return [evaluated_move for evaluated_move in max_depth_moves if evaluated_move[1] == best_max_depth_score]