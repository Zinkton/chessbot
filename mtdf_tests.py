
import time
import chess
from move_generation import generate_ordered_legal_moves
from mtdf import solve_position_multiprocess, solve_position_root
from constants import MAX_VALUE
from shared_memory_manager import SharedMemoryManager


def checkmate_in_one():
    for depth in range(2, 7):
        board = chess.Board('4k3/Q7/5P2/8/8/5p2/q7/4K3 w - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[0] == chess.Move.from_uci('a7e7') and result[1] == MAX_VALUE
        board = chess.Board('4k3/Q7/5P2/8/8/5p2/q7/4K3 b - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[0] == chess.Move.from_uci('a2e2') and result[1] == MAX_VALUE

def checkmated_in_one():
    for depth in range(3, 7):
        board = chess.Board('4k3/8/8/8/8/1r6/r7/4K3 w - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[1] <= -MAX_VALUE
        board = chess.Board('4k3/1R6/R7/8/8/8/8/4K3 b - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[1] <= -MAX_VALUE

def checkmate_in_two():
    for depth in range(4, 7):
        board = chess.Board('7k/8/RR6/8/8/8/8/4K3 w - - 0 1')
        result = solve_and_filter(board, depth)
        assert (result[0] == chess.Move.from_uci('a6a7') or result[0] == chess.Move.from_uci('b6b7')) and result[1] == MAX_VALUE
        board = chess.Board('7k/8/8/8/8/rr6/8/7K b - - 0 1')
        result = solve_and_filter(board, depth)
        assert (result[0] == chess.Move.from_uci('a3a2') or result[0] == chess.Move.from_uci('b3b2')) and result[1] == MAX_VALUE

def checkmated_in_two():
    for depth in range(5, 7):
        board = chess.Board('7k/8/RR6/8/8/8/8/4K3 b - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[1] <= -MAX_VALUE
        board = chess.Board('7k/8/8/8/8/rr6/8/7K w - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[1] <= -MAX_VALUE

def checkmate_in_three():
    for depth in range(6, 7):
        board = chess.Board('r4r2/1R1R2pk/7p/8/8/5Ppq/P7/6K1 w - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[0] == chess.Move.from_uci('d7g7')

def checkmated_in_three():
    board = chess.Board('r4r1k/1R1R2pQ/7p/8/8/5Ppq/P7/6K1 b - - 0 1')
    result = solve_and_filter(board, 7)
    assert result[1] <= -MAX_VALUE

def capture_in_one():
    for depth in range(1, 7):
        board = chess.Board('1k6/8/8/4q3/4Q3/8/8/1K6 w - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[0] == chess.Move.from_uci('e4e5')
        board = chess.Board('1k6/8/8/4q3/4Q3/8/8/1K6 b - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[0] == chess.Move.from_uci('e5e4')

def captured_in_one():
    for depth in range(2, 7):
        board = chess.Board('1k6/8/8/8/8/8/2n5/R3K3 w - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[1] < -150
        board = chess.Board('r3k3/2N5/8/8/8/8/8/4K3 b - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[1] < -150

def capture_in_two():
    for depth in range(3, 7):
        board = chess.Board('1K6/8/8/8/3N4/r7/8/4k3 w - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[0] == chess.Move.from_uci('d4c2')
        board = chess.Board('1k6/8/8/8/3n4/R7/8/4K3 b - - 0 1')
        result = solve_and_filter(board, depth)
        assert result[0] == chess.Move.from_uci('d4c2')

def queen_sack():
    start = time.perf_counter()
    board = chess.Board('rnb1k1nr/2p3pp/p1qp1p2/1pbN4/1PQ1P3/3B1N2/P1P2PPP/R1B2K1R w kq - 0 11')
    result = solve_and_filter(board, 6)
    assert result[0] != chess.Move.from_uci('c4c5')
    print(time.perf_counter() - start)

def performance_test():
    board = chess.Board()
    start = time.perf_counter()
    stack = []
    while True:
        move = solve_and_filter(board, 6)[0]
        stack.append(board.san(move))
        board.push(move)
        if board.outcome(claim_draw=True):
            break
    print(time.perf_counter() - start)
    print(' '.join(stack))

def checkmate_in_one_multiprocess(manager):
    for depth in range(2, 7):
        board = chess.Board('4k3/Q7/5P2/8/8/5p2/q7/4K3 w - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][0] == chess.Move.from_uci('a7e7') and result[0][1] == -MAX_VALUE
        board = chess.Board('4k3/Q7/5P2/8/8/5p2/q7/4K3 b - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][0] == chess.Move.from_uci('a2e2') and result[0][1] == -MAX_VALUE

def checkmated_in_one_multiprocess(manager):
    for depth in range(3, 7):
        board = chess.Board('4k3/8/8/8/8/1r6/r7/4K3 w - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][1] >= MAX_VALUE
        board = chess.Board('4k3/1R6/R7/8/8/8/8/4K3 b - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][1] >= MAX_VALUE

def checkmate_in_two_multiprocess(manager):
    for depth in range(4, 7):
        board = chess.Board('7k/8/RR6/8/8/8/8/4K3 w - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert (result[0][0] == chess.Move.from_uci('a6a7') or result[0][0] == chess.Move.from_uci('b6b7')) and result[0][1] == -MAX_VALUE
        board = chess.Board('7k/8/8/8/8/rr6/8/7K b - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert (result[0][0] == chess.Move.from_uci('a3a2') or result[0][0] == chess.Move.from_uci('b3b2')) and result[0][1] == -MAX_VALUE

def checkmated_in_two_multiprocess(manager):
    for depth in range(5, 7):
        board = chess.Board('7k/8/RR6/8/8/8/8/4K3 b - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][1] >= MAX_VALUE
        board = chess.Board('7k/8/8/8/8/rr6/8/7K w - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][1] >= MAX_VALUE

def checkmate_in_three_multiprocess(manager):
    for depth in range(6, 7):
        board = chess.Board('r4r2/1R1R2pk/7p/8/8/5Ppq/P7/6K1 w - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][0] == chess.Move.from_uci('d7g7')

def checkmated_in_three_multiprocess(manager):
    board = chess.Board('r4r1k/1R1R2pQ/7p/8/8/5Ppq/P7/6K1 b - - 0 1')
    result = solve_and_filter_multiprocess(board, 7, manager)
    assert result[0][1] >= MAX_VALUE

def capture_in_one_multiprocess(manager):
    for depth in range(1, 7):
        board = chess.Board('1k6/8/8/4q3/4Q3/8/8/1K6 w - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][0] == chess.Move.from_uci('e4e5')
        board = chess.Board('1k6/8/8/4q3/4Q3/8/8/1K6 b - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][0] == chess.Move.from_uci('e5e4')

def captured_in_one_multiprocess(manager):
    for depth in range(2, 7):
        board = chess.Board('1k6/8/8/8/8/8/2n5/R3K3 w - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][1] > 150
        board = chess.Board('r3k3/2N5/8/8/8/8/8/4K3 b - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][1] > 150

def capture_in_two_multiprocess(manager):
    for depth in range(3, 7):
        board = chess.Board('1K6/8/8/8/3N4/r7/8/4k3 w - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][0] == chess.Move.from_uci('d4c2')
        board = chess.Board('1k6/8/8/8/3n4/R7/8/4K3 b - - 0 1')
        result = solve_and_filter_multiprocess(board, depth, manager)
        assert result[0][0] == chess.Move.from_uci('d4c2')

def queen_sack_multiprocess(manager):
    start = time.perf_counter()
    board = chess.Board('rnb1k1nr/2p3pp/p1qp1p2/1pbN4/1PQ1P3/3B1N2/P1P2PPP/R1B2K1R w kq - 0 11')
    result = solve_and_filter_multiprocess(board, 6, manager)
    assert result[0][0] != chess.Move.from_uci('c4c5')
    print(time.perf_counter() - start)

def performance_test_multiprocess(manager):
    board = chess.Board()
    start = time.perf_counter()
    stack = []
    while True:
        move = solve_and_filter_multiprocess(board, 6, manager)[0][0]
        stack.append(board.san(move))
        board.push(move)
        if board.outcome(claim_draw=True):
            break
    print(time.perf_counter() - start)
    print(' '.join(stack))

def compare_performance(manager: SharedMemoryManager):
    board = chess.Board()
    multi_process_time = 0
    single_process_time = 0
    stack = 'f4 Nc6 Nf3 e6 e4 Bc5 Bc4 Na5 Be2 Nf6 d4 Bb6 e5 Nd5 c4 Nb4 a3 Nbc6 c5 Nxd4 cxb6 Nxf3+ Bxf3 axb6 O-O b5 Be2 O-O Be3 Nc4 Bd4 b6 Bf3 d5 exd6 Ra7 dxc7 Rxc7 Bf2 Qxd1 Rxd1 Nxb2 Bxb6 Rc4 Rf1 Na4 Be3 Rd8 Be2 Re4 Bxb5 Rxe3 Bxa4 Ba6 Rc1 Rd4 Bb5 Bb7 Rc7 Re1+ Kf2 Rh1 Rxb7 Rxf4+ Kg3 g5 h4 Rfxh4 Be8 f5 Bf7+ Kh8 Rb8+ Kg7 Bxe6 Rg4+ Kf2 Rf4+ Kg3 h5 Rg8+ Kf6 Rf8+ Kxe6 Re8+ Kf7 Rh8 h4+ Rxh4 Rfxh4 Kf2 Kg8 a4 Rb4 a5 Rb2+ Kf3 Rbxb1 Rxb1 Rxb1 a6 Ra1 g4 Ra3+ Kg2 fxg4 a7 Rxa7 Kg3 Ra4 Kg2 Ra1 Kg3 Ra4 Kg2 Ra1 Kg3'.split(' ')
    for move in stack:
        # start = time.perf_counter()
        # mp_move, mp_score = solve_and_filter_multiprocess(board, 6, manager)[0]
        # multi_process_time += time.perf_counter() - start
        start = time.perf_counter()
        sp_move, sp_score = solve_and_filter(board, 6)
        single_process_time += time.perf_counter() - start
        # if mp_score != -sp_score:
        #     print('ERROR', mp_score, sp_score, mp_move, sp_move)
        board.push(board.parse_san(move))
    print(f'single process: {single_process_time} multi process: {multi_process_time}')

def solve_and_filter_multiprocess(board: chess.Board, max_depth, manager: SharedMemoryManager):
    boards = []
    for move, _ in generate_ordered_legal_moves(board):
        board.push(move)
        boards.append(board.copy())
        board.pop()
    result = solve_position_multiprocess(boards, manager, max_depth)
    depth, move, score = result[0]
    return [(move, score)]

def solve_and_filter(board, max_depth):
    depth, move, score = solve_position_root(board, max_depth)
    return (move, score)


if __name__ == '__main__':
    # start = time.perf_counter()
    # checkmate_in_one()
    # checkmated_in_one()
    # checkmate_in_two()
    # checkmated_in_two()
    # checkmate_in_three()
    # checkmated_in_three()
    # capture_in_one()
    # captured_in_one()
    # capture_in_two()
    # queen_sack()
    # print(f'total test time: {time.perf_counter() - start}')

    # performance_test()
    
    manager = SharedMemoryManager()
    try:
        # start = time.perf_counter()
        # checkmate_in_one_multiprocess(manager)
        # checkmated_in_one_multiprocess(manager)
        # checkmate_in_two_multiprocess(manager)
        # checkmated_in_two_multiprocess(manager)
        # checkmate_in_three_multiprocess(manager)
        # checkmated_in_three_multiprocess(manager)
        # capture_in_one_multiprocess(manager)
        # captured_in_one_multiprocess(manager)
        # capture_in_two_multiprocess(manager)
        # queen_sack_multiprocess(manager)
        # print(f'total test time: {time.perf_counter() - start}')

    # performance_test_multiprocess(manager)

        compare_performance(manager)
    finally:
        manager.close()