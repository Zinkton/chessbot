moves = """   0: wPe2e4
1: bPc7c5
2: wNg1f3
3: bPd7d6
4: wPd2d4
5: bPc5d4x
6: wNf3d4x
7: bNg8f6
8: wNb1c3
9: bPa7a6
10: wBc1e3
11: bPe7e5
12: wNd4b3
13: bBc8e6
14: wPf2f3
15: bBf8e7
16: wQd1d2
17: bKe8h8OO
18: wKe1a1OOO
19: bNb8d7
20: wPg2g4
21: bPb7b5
22: wPg4g5
23: bPb5b4
24: wNc3a4
25: bNf6h5
26: wKc1b1
27: bRa8b8
28: wBf1a6x
29: bQd8c7
30: wPc2c4
31: bQc7c6
32: wNa4b6
33: bNd7b6x
34: wBa6b5
35: bQc6c7
36: wBe3b6x
37: bQc7b6x
38: wRh1g1
39: bRb8c8
40: wRd1c1
41: bBe6c4x
42: wBb5c4x
43: bRc8c4x
44: wRc1c4x
45: bQb6g1x
46: wRc4c1
47: bQg1g5x
48: wQd2b4x
49: bQg5e3
50: wQb4b7
51: bBe7f6
52: wRc1c3
53: bQe3f2
54: wNb3c1
55: bNh5f4
56: wQb7d7
57: bBf6h4
58: wQd7d6x
59: bPf7f6
60: wQd6b4
61: bRf8d8
62: wRc3c7
63: bQf2f3x
64: wQb4e7
65: bQf3e4x
66: wKb1a1
67: bNf4e6
68: wQe7e6x
69: bKg8h8
70: wQe6d7
71: bRd8g8
72: wRc7c8
73: bPh7h6
74: wPa2a3
75: bRg8c8x
76: wQd7c8x
77: bKh8h7
78: wQc8c5
79: bQe4g2
80: wKa1b1
81: bQg2h2x
82: wPb2b4
83: bBh4g5
84: wPb4b5
85: bQh2g2
86: wPb5b6
87: bQg2e4
88: wQc5c2
89: bQe4c2x
90: wKb1c2x
91: bBg5e3
92: wPb6b7
93: bBe3a7
94: wPa3a4
95: bKh7g8
96: wPa4a5
97: bPe5e4
98: wNc1e2
99: bPe4e3
100: wPa5a6
101: bBa7b8
102: wKc2d3
103: bPg7g5
104: wNe2d4
105: bPg5g4
106: wNd4c6
107: bPe3e2
108: wKd3e2x
109: bPg4g3
110: wNc6b8x
111: bPg3g2
112: wKe2f2
113: bPh6h5
114: wNb8c6
115: bKg8g7
116: wPb7b8Q
117: bPh5h4
118: wPa6a7
119: bPh4h3
120: wQb8g3
121: bKg7h7
122: wQg3h3x
123: bKh7g6
124: wPa7a8Q
125: bPg2g1Q
126: wKf2g1x
127: bKg6g7
128: wQa8h8
129: bKg7f7
130: wQh8h7
131: bKf7e8
132: wQh7g8   """.split('\n')

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