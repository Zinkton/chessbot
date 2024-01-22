import uuid
from time import perf_counter, sleep

import requests

import constants
from custom_chess import Board
from mtdf import solve_position_root


class ChessBot():
    def __init__(self):
        self.game_id = uuid.uuid4()

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

        board = Board(fen)
        _, move, _ = solve_position_root(board, self.game_id) if not isCasual else solve_position_root(board, self.game_id, 0, depth)
        
        if isCasual and perf_counter() - start < 2.0:
            sleep(2.0 - (perf_counter() - start))

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