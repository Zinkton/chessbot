import chess, random, time
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

board = chess.Board()
print(evaluate_board(board))