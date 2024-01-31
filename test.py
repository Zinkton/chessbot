import random
import time
from typing import Iterator
import uuid
import custom_chess as chess
from mtdf import solve_position_root

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

if __name__ == '__main__':
    # board = chess.Board('R7/1p5p/2p2p1k/4pq2/8/8/4n1R1/7K b - - 7 55')
    # game_id = uuid.uuid4()
    # result = solve_position_root(board, game_id, 8)
    # board.push(result[0])
    # print(result)
    # start = time.perf_counter()
    # for x in range(5):
    #     result = solve_position_root(board, game_id, 6)
    #     print(result)
    #     board.push(result[0])

    # print(time.perf_counter() - start)
    # num = 123456789
    # iterations = 100000000000

    # start = time.perf_counter()
    # for i in range(iterations):
    #     if (i % 2 == 0):
    #         num ^= 987654321 & i | i >> 2
    #     else:
    #         num ^= 987654321 & i | i << 2
    #     if (i % 100000000 == 0):
    #         print(i)

    # print(time.perf_counter() - start)
    
    start = time.perf_counter()
    games = []
    for x in range(100):
        board = chess.Board()
        game = []
        while True:
            legal_moves = list(board.legal_moves)
            random_legal_move = random.choice(legal_moves)
            game.append((random_legal_move, legal_moves, board.board_fen()))
            board.push(random_legal_move)
            if board.outcome():
                break
        games.append((game, board.outcome().termination))
    
    f = open("legal_moves_test.txt", "w+")
    f.write(str(len(games)) + "\n")
    for game, termination in games:
        f.write(str(len(game)) + '\n')
        for move, legal_moves, fen in game:
            f.write(str(move) + "\n")
            f.write(" ".join([str(move) for move in legal_moves]) + "\n")
            f.write(fen + "\n")
        f.write(str(termination) + "\n")
    f.close()
    print(time.perf_counter() - start)