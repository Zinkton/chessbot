from typing import Dict, List
import chess, random, time
import custom_chess
import numpy as np
import constants
from chess_node import MtdfNode
from move_generation import generate_ordered_legal_moves
from mtdf import solve_position_multiprocess, solve_position_root
from zobrist import zobrist_hash, update_hash
from evaluation import calculate_move_value, evaluate_board

# def worker_function(args):
#     shared_memory_name, index = args
#     existing_shm = shared_memory.SharedMemory(name=shared_memory_name)
#     shared_array = np.ndarray((constants.PROCESS_COUNT,), dtype=np.uint64, buffer=existing_shm.buf)
#     shared_array[index] = index # Example operation
#     value = shared_array[index]
#     existing_shm.close()  # Close the shared memory block reference
#     some_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#     print(some_list[value*2])
#     return value

# def main():

#     shm = shared_memory.SharedMemory(create=True, size=constants.PROCESS_COUNT*np.uint64().itemsize)
#     try:
#         # Create shared memory
#         shared_array = np.ndarray((constants.PROCESS_COUNT,), dtype=np.uint64, buffer=shm.buf)
#         shared_array.fill(0)  # Initialize the array with zeros

#         inputs = [(shm.name, i) for i in range(constants.PROCESS_COUNT)]
        
        
#         with multiprocessing.Pool(processes=constants.PROCESS_COUNT) as pool:
#             results = pool.map(worker_function, inputs)
        
#     finally:
#         # Clean up
#         shm.close()
#         shm.unlink()

#     print(results)

# if __name__ == '__main__':
#     number = np.uint64()
#     main()

# test_array = np.ndarray((5,), dtype=np.uint64)
# test_array.fill(5)
# some_list = [0, 1, 2, 3, 4, 5]
# print(some_list[test_array[4]])

# def pack_values(d, s, t):
#     # Ensure the values are within their ranges
#     assert 0 <= d <= 63
#     assert -1048576 <= s <= 1048576
#     assert 0 <= t <= 2

#     # Convert s to a 21-bit representation
#     s = s & 0x1FFFFF  # 21 bits mask

#     # Pack the values
#     packed_value = d | (s << 6) | (t << 27)
#     return packed_value

# def unpack_values(packed_value):
#     # Unpack the values
#     d = packed_value & 0b111111  # 6 bits for d
#     s = (packed_value >> 6) & 0x1FFFFF  # 21 bits for s
#     t = (packed_value >> 27) & 0b11  # 2 bits for t

#     # Adjust s for two's complement representation of negative values
#     if s >= 0x100000:  # Check if the sign bit is set (21st bit)
#         s -= 0x200000  # Convert back from two's complement

#     return d, s, t

# # Example usage
# packed = pack_values(45, -500000, 2)  # Example values for d, s, t
# d, s, t = unpack_values(packed)
# print(f"Packed value: {packed}")
# print(f"Unpacked values: d = {d}, s = {s}, t = {t}")



# for x in range(100):
    # custom_board = custom_chess.Board()
    # real_board = chess.Board()
    # while True:
    #     move = random.choice(list(custom_board.generate_legal_moves()))
    #     custom_board.push(move)
    #     real_board.push(move)
    #     if zobrist_hash(custom_board) != zobrist_hash(real_board):
    #         print(custom_board)
    #         print(real_board)
    #         raise Exception("lol")
            
    #     if real_board.outcome():
    #         break
    # while real_board.move_stack:
    #     custom_board.pop()
    #     real_board.pop()
    #     assert zobrist_hash(custom_board) == zobrist_hash(real_board)
# board = chess.Board('1K6/8/8/8/8/8/4k3/N7 w - - 1 3')
# print(evaluate_board(board))
        

# # Example usage
# packed = pack_values(45, -500000, 2)  # Example values for d, s, t
# d, s, t = unpack_values(packed)
# print(f"Packed value: {packed}")
# print(f"Unpacked values: d = {d}, s = {s}, t = {t}")

def performance_test_multiprocess():
    board = chess.Board()
    start = time.perf_counter()
    stack = []
    while True:
        move = solve_and_filter_multiprocess(board, 6)[0][0]
        stack.append(board.san(move))
        board.push(move)
        if board.outcome(claim_draw=True):
            break
    print(time.perf_counter() - start)
    print(' '.join(stack))

def performance_test():
    board = chess.Board('6k1/r7/8/6p1/6p1/6K1/8/8 b - - 1 55')
    move = solve_and_filter(board, 6)[0]
    move_mp = solve_and_filter_multiprocess(board, 6)[0][0]
    if str(move) != str(move_mp):
        print('error', move, move_mp)

def solve_and_filter_multiprocess(board, max_depth):
    solve_position_params = []
    for move, _ in generate_ordered_legal_moves(board):
        board.push(move)
        solve_position_params.append([board.copy(), max_depth - 1, None])
        board.pop()
    result = solve_position_multiprocess(solve_position_params)
    result = [r for r in result if r[2] == result[0][2]]
    print(result)
    # print([calculate_move_value(r[1], board) for r in result])
    depth, move, score = result[0]
    return [(move, score)]

def solve_and_filter(board, max_depth):
    depth, move, score = solve_position_root([board, max_depth, None])
    print(depth, move, score)
    return (move, score)

if __name__ == '__main__':
    performance_test()