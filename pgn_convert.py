moves = """0: wNb1c3
1: bPe7e5
2: wNg1f3
3: bQd8f6
4: wNc3d5
5: bQf6c6
6: wPe2e4
7: bBf8d6
8: wPd2d4
9: bPe5d4x
10: wQd1d4x
11: bPf7f6
12: wBf1d3
13: bBd6c5
14: wQd4c4
15: bPd7d6
16: wKe1f1
17: bPa7a6
18: wPb2b4
19: bPb7b5
20: wQc4c5x
21: bPd6c5x
22: wBc1f4
23: bRa8a7
24: wPb4c5x
25: bPb5b4
26: wRa1b1
27: bBc8g4
28: wRb1b4x
29: bNb8d7
30: wNf3d2
31: bNd7c5x
32: wRb4b8
33: bKe8f7
34: wNd5b4
35: bQc6a4
36: wBd3c4
37: bBg4e6
38: wBf4e3
39: bBe6c4x
40: wNd2c4x
41: bRa7b7
42: wBe3c5x
43: bRb7b8x
44: wNc4b2
45: bQa4b5
46: wPc2c4
47: bQb5d7
48: wKf1g1
49: bQd7d2
50: wPh2h3
51: bQd2b2x
52: wNb4a6x
53: bRb8d8
54: wNa6c7x
55: bQb2a2x
56: wNc7b5
57: bKf7g6
58: wPf2f4
59: bKg6h6
60: wNb5d6
61: bRd8d6x
62: wBc5d6x
63: bQa2d2
64: wPc4c5
65: bQd2a5
66: wPe4e5
67: bPf6f5
68: wPh3h4
69: bQa5e1
70: wKg1h2
71: bQe1e4
72: wRh1f1
73: bQe4d5
74: wRf1a1
75: bQd5e4
76: wPe5e6
77: bQe4e6x
78: wRa1a7
79: bNg8f6
80: wBd6e5
81: bQe6d5
82: wBe5f6x
83: bPg7f6x
84: wPh4h5
85: bRh8g8 """.split('\n')

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