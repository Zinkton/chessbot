
import time
import chess
from mtdf import solve_position_root
from constants import MAX_VALUE


def checkmate_in_one():
    for depth in range(2, 7):
        board = chess.Board('4k3/Q7/5P2/8/8/5p2/q7/4K3 w - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][0] == chess.Move.from_uci('a7e7') and result[0][1] == MAX_VALUE
        board = chess.Board('4k3/Q7/5P2/8/8/5p2/q7/4K3 b - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][0] == chess.Move.from_uci('a2e2') and result[0][1] == MAX_VALUE

def checkmated_in_one():
    for depth in range(3, 7):
        board = chess.Board('4k3/8/8/8/8/1r6/r7/4K3 w - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][1] <= -MAX_VALUE
        board = chess.Board('4k3/1R6/R7/8/8/8/8/4K3 b - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][1] <= -MAX_VALUE

def checkmate_in_two():
    for depth in range(4, 7):
        board = chess.Board('7k/8/RR6/8/8/8/8/4K3 w - - 0 1')
        result = solve_position_root(board, depth)
        assert (result[0][0] == chess.Move.from_uci('a6a7') or result[0][0] == chess.Move.from_uci('b6b7')) and result[0][1] == MAX_VALUE
        board = chess.Board('7k/8/8/8/8/rr6/8/7K b - - 0 1')
        result = solve_position_root(board, depth)
        assert (result[0][0] == chess.Move.from_uci('a3a2') or result[0][0] == chess.Move.from_uci('b3b2')) and result[0][1] == MAX_VALUE

def checkmated_in_two():
    for depth in range(5, 7):
        board = chess.Board('7k/8/RR6/8/8/8/8/4K3 b - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][1] <= -MAX_VALUE
        board = chess.Board('7k/8/8/8/8/rr6/8/7K w - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][1] <= -MAX_VALUE

def checkmate_in_three():
    for depth in range(6, 7):
        board = chess.Board('r4r2/1R1R2pk/7p/8/8/5Ppq/P7/6K1 w - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][0] == chess.Move.from_uci('d7g7')

def checkmated_in_three():
    board = chess.Board('r4r1k/1R1R2pQ/7p/8/8/5Ppq/P7/6K1 b - - 0 1')
    result = solve_position_root(board, 7)
    assert result[0][1] <= -MAX_VALUE

def capture_in_one():
    for depth in range(1, 7):
        board = chess.Board('1k6/8/8/4q3/4Q3/8/8/1K6 w - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][0] == chess.Move.from_uci('e4e5')
        board = chess.Board('1k6/8/8/4q3/4Q3/8/8/1K6 b - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][0] == chess.Move.from_uci('e5e4')

def captured_in_one():
    for depth in range(2, 7):
        board = chess.Board('1k6/8/8/8/8/8/2n5/R3K3 w - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][1] < -200
        board = chess.Board('1K6/8/8/8/8/8/2N5/r3k3 b - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][1] < -200

def capture_in_two():
    for depth in range(3, 7):
        board = chess.Board('1K6/8/8/8/3N4/r7/8/4k3 w - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][0] == chess.Move.from_uci('d4c2')
        board = chess.Board('1k6/8/8/8/3n4/R7/8/4K3 b - - 0 1')
        result = solve_position_root(board, depth)
        assert result[0][0] == chess.Move.from_uci('d4c2')

def queen_sack():
    start = time.perf_counter()
    board = chess.Board('rnb1k1nr/2p3pp/p1qp1p2/1pbN4/1PQ1P3/3B1N2/P1P2PPP/R1B2K1R w kq - 0 11')
    result = solve_position_root(board, 6)
    assert result[0][0] != chess.Move.from_uci('c4c5')
    print(time.perf_counter() - start)

def performance_test():
    board = chess.Board()
    start = time.perf_counter()
    board.push(solve_position_root(board, 6)[0][0])
    board.push(solve_position_root(board, 6)[0][0])
    board.push(solve_position_root(board, 6)[0][0])
    board.push(solve_position_root(board, 6)[0][0])
    print(time.perf_counter() - start)

if __name__ == '__main__':
    start = time.perf_counter()
    checkmate_in_one()
    checkmated_in_one()
    checkmate_in_two()
    checkmated_in_two()
    checkmate_in_three()
    checkmated_in_three()
    capture_in_one()
    captured_in_one()
    capture_in_two()
    queen_sack()
    performance_test()
    print(f'total test time: {time.perf_counter() - start}')