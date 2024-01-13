import chess

board = chess.Board()
board.push(chess.Move.null())

print(board)
print(board.peek())
if chess.Move.null():
    print('true')
else:
    print('false')