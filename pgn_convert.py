moves = """ 0: wKc7d7
1: bKg2g3
2: wKd7c7
3: bKg3f3
4: wKc7d7
5: bQa6f6
6: wKd7c7
7: bQf6a6
8: wKc7d7
9: bKf3g3
10: wKd7e7
11: bKg3f4
12: wKe7f7
13: bKf4g5
14: wKf7e7
15: bKg5f4
16: wKe7f7
17: bQa6e2
18: wKf7g6
19: bKf4f3
20: wKg6f5
21: bQe2e1
22: wKf5f6
23: bKf3g2
24: wKf6g5
25: bQe1e6
26: wKg5f4
27: bQe6e1
28: wKf4g4
29: bQe1a5
30: wKg4f4
31: bKg2f2
32: wKf4e4
33: bQa5e1
34: wKe4d5
35: bQe1d1
36: wKd5c5
37: bQd1e1
38: wKc5d5
39: bQe1e7
40: wKd5d4
41: bKf2e2
42: wKd4d5
43: bKe2d2
44: wKd5d4
45: bKd2e2
46: wKd4d5
47: bKe2f2
48: wKd5d4
49: bKf2e2 """.split('\n')

pgn_moves = []
move_number = 1

for move in moves:
    # Split each move into its components (number, player, move)
    components = move.split(": ")
    if len(components) != 2:
        continue

    # Extract the move and convert it to PGN format
    raw_move = components[1]
    player = "w" if "w" in raw_move else "b"
    piece_moved = raw_move[1].replace('P', '')
    move = raw_move[2:].replace('x', '')  # Remove 'x' from captures

    # Append the move to the PGN list
    pgn_move = f"{piece_moved}{move}"
    if 'OOO' in move:
        pgn_move = 'O-O-O'
    elif 'OO' in move:
        pgn_move = 'O-O'
    if player == "w":
        pgn_moves.append(f"{move_number}. {pgn_move}")
        move_number += 1
    else:
        pgn_moves[-1] += f" {pgn_move}"

# Join all PGN moves into a single string
print(' '.join(pgn_moves))