import constants
import random
import requests
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
        move = self._select_random_best_move(board)

        self._update_fen_history(board, move)

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
        sleep(1)
        moves.sort(key=lambda x: x['draws'] + x['white'] + x['black'], reverse=True)
        return moves[0]['uci']
        # board = Board(fen)
        # for move in moves:
        #     if board.turn and move['white'] > move['black']:
        #         return move['uci']
        #     if not board.turn and move['black'] > move['white']:
        #         return move['uci']
                
        # return moves[0]['uci']

    def _select_random_best_move(self, board):
        unevaluated_moves = [[move, 0] for move in board.legal_moves]
        start = perf_counter()
        best_moves = self._evaluate_and_filter_best_moves(
            board, unevaluated_moves, constants.MAX_DEPTH)
        stop = perf_counter()
        print('took %s seconds' % (stop - start))
        
        return random.choice(best_moves)

    def _update_fen_history(self, board, move):
        board.push(move)
        self.fen_history.append(board.board_fen())

    def _evaluate_and_filter_best_moves(self, board, unevaluated_moves, max_depth):
        # A board copy to manipulate, depth of search and the move to evaluate
        solve_position_params = [[board.copy(), max_depth, move] for move, _ in unevaluated_moves]
        
        with Pool(processes=constants.PROCESS_COUNT) as p:
            evaluated_moves = p.map(solve_position, solve_position_params)

        #winning_evaluated_moves = self._filter_winning_evaluated_moves(evaluated_moves)
        if len(evaluated_moves) > 1:
            self._remove_repeating_move(evaluated_moves, board)
            evaluated_moves = evaluated_moves
            
        best_evaluated_moves = self._filter_best_evaluated_moves(evaluated_moves)
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
        
    def _filter_best_evaluated_moves(self, evaluated_moves):
        """ Return only the move evaluations with the best score """
        best_score = min(evaluated_move[1] for evaluated_move in evaluated_moves)
        
        return [evaluated_move
                for evaluated_move in evaluated_moves if evaluated_move[1] == best_score]