moves = """ 0: wPe2e4
1: bNb8c6
2: wNg1f3
3: bPd7d5
4: wPe4d5x
5: bQd8d5x
6: wNb1c3
7: bQd5e6
8: wBf1e2
9: bBc8d7
10: wPd2d4
11: bQe6f5
12: wKe1h1OO
13: bNg8f6
14: wBe2d3
15: bQf5a5
16: wBc1d2
17: bBd7g4
18: wNc3b5
19: bQa5b6
20: wPc2c4
21: bNc6d4x
22: wNb5d4x
23: bPc7c6
24: wBd2c3
25: bRa8d8
26: wPh2h3
27: bBg4f3x
28: wNd4f3x
29: bNf6e4
30: wQd1c2
31: bNe4c3x
32: wPb2c3x
33: bPe7e6
34: wBd3h7x
35: bQb6c7
36: wRa1d1
37: bRd8d1x
38: wRf1d1x
39: bBf8e7
40: wBh7e4
41: bPf7f5
42: wBe4d3
43: bKe8h8OO
44: wRd1e1
45: bRf8f6
46: wNf3d4
47: bQc7d7
48: wQc2e2
49: bPc6c5
50: wNd4e6x
51: bBe7d6
52: wPg2g4
53: bPf5g4x
54: wPh3g4x
55: bBd6h2
56: wKg1h2x
57: bRf6h6
58: wKh2g1
59: bRh6h4
60: wRe1d1
61: bQd7c6
62: wBd3e4
63: bQc6b6
64: wQe2f3
65: bRh4g4x
66: wQf3g4x
67: bQb6c7
68: wRd1d6
69: bPb7b5
70: wQg4g6
71: bQc7d7
72: wQg6g4
73: bQd7c7
74: wQg4f5
75: bQc7d6x
76: wQf5h7
77: bKg8f7
78: wQh7g6
79: bKf7e7
80: wBe4f5
81: bQd6e5
82: wPc4b5x
83: bQe5c3x
84: wNe6g7x
85: bQc3a1
86: wKg1g2
87: bQa1b2
88: wQg6e8
89: bKe7f6
90: wQe8f8
91: bKf6e5
92: wQf8e7
93: bKe5d4
94: wQe7f6
95: bKd4c4
96: wQf6b2x
97: bKc4d5
98: wPf2f4
99: bPa7a6
100: wNg7h5
101: bPa6b5x
102: wQb2b5x
103: bKd5d4
104: wQb5d3 """.split('\n')

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