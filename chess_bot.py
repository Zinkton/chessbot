import uuid
from time import perf_counter, sleep

import requests

import constants
import custom_chess as chess
from custom_chess import Board
from mtdf import solve_position_root


class ChessBot():
    def __init__(self):
        self.game_id = uuid.uuid4()
        self.opening = True

    # Main chess bot logic
    def get_move(self, bot_input):
        isCasual = bool(bot_input['isCasual'])
        depth = int(bot_input['depth'])
        get_move_start = perf_counter() # Start stopwatch
        
        fen = bot_input['boardFen']
        if constants.OPENING_BOOK and self.opening:
            move = self.opening_book(fen)
            if move is not None:
                sleep(1)
                return move
            else:
                self.opening = False # Avoiding spamming requests

        board = Board(fen)
        piece_count = len([True for square in chess.SQUARES if bool(board.piece_type_at(square))])

        if constants.ENDGAME_BOOK and piece_count <= 7:
            move = self.endgame_book(fen)
            if move is not None:
                print('error probing endgame tablebase')
                sleep(1)
                return move
        
        move, _ = solve_position_root(board, self.game_id) if not isCasual else solve_position_root(board, self.game_id, 1, depth)
        
        time_spent_so_far = perf_counter() - get_move_start
        if isCasual and time_spent_so_far < 2.0:
            sleep(2.0 - time_spent_so_far)

        return move
    
    def opening_book(self, fen):
        r = requests.get(url='https://explorer.lichess.ovh/masters', params={'fen': fen})
        data = r.json()
        moves = data['moves']
        if not moves:
            return None
        moves.sort(key=lambda x: x['draws'] + x['white'] + x['black'], reverse=True)
        return moves[0]['uci']
    
    def endgame_book(self, fen):
        r = requests.get(url='http://tablebase.lichess.ovh/standard', params={'fen': fen})
        data = r.json()
        moves = data['moves']
        if not moves:
            return None
        return moves[0]['uci']