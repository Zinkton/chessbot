from typing import Dict, List
import chess, random, time
from chess_node import MtdfNode
from zobrist import zobrist_hash, update_hash
from evaluation import evaluate_board

# @profile
# def test_zobrist():
#     total_update = 0.0
#     total_full = 0.0

#     for x in range(100):
#         board = chess.Board()
#         updateable_hash = zobrist_hash(board)
#         move_stack = []
#         while True:
#             move = random.choice(list(board.legal_moves))
#             updateable_hash = update_hash(updateable_hash, board, move)
#             move_stack.append(board.san(move))
#             board.push(move)
#             expected_hash = zobrist_hash(board)
#             if updateable_hash != expected_hash:
#                 print(board)
#                 print(' '.join(move_stack))
#                 print(move)
#                 raise Exception('failure')
#             if board.outcome():
#                 break

#     print(f'success, update: {total_update}, full: {total_full}')

# test_zobrist()
@profile
def test_dict_vs_list():
    board = chess.Board()
    print(evaluate_board(board))

    dictionary: Dict[chess.Move, MtdfNode] = {}
    list_obj: List[MtdfNode] = []

    legal_moves = list(board.legal_moves)
    for move in legal_moves:
        node = MtdfNode(move=move, value=0, children=[])
        dictionary[move] = node
        list_obj.append(node)

    legal_moves_len = len(legal_moves)
    for x in range(1000):
        the_move = dictionary[legal_moves[x % legal_moves_len]]
        children_enumeration = enumerate(list_obj)
        (index, the_move_list) = next(((index, child) for (index, child) in children_enumeration if child.move == legal_moves[x % legal_moves_len]), (None, None))

test_dict_vs_list()
