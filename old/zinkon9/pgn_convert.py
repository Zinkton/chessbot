moves = """ 0: wPe2e4
1: bPe7e5
2: wNg1f3
3: bNb8c6
4: wBf1b5
5: bPa7a6
6: wBb5a4
7: bNg8f6
8: wPd2d3
9: bBf8c5
10: wKe1h1OO
11: bKe8h8OO
12: wBc1e3
13: bBc5e3x
14: wPf2e3x
15: bPd7d5
16: wNb1c3
17: bPd5d4
18: wPe3d4x
19: bPe5d4x
20: wNc3e2
21: bNf6g4
22: wQd1d2
23: bPb7b5
24: wBa4b3
25: bBc8e6
26: wPh2h3
27: bNg4e5
28: wNf3e5x
29: bNc6e5x
30: wBb3e6x
31: bPf7e6x
32: wRf1f8x
33: bQd8f8x
34: wNe2d4x
35: bQf8d6
36: wQd2e3
37: bRa8d8
38: wNd4b3
39: bQd6b6
40: wNb3c5
41: bNe5d7
42: wPd3d4
43: bNd7c5x
44: wPd4c5x
45: bQb6c6
46: wRa1e1
47: bQc6d7
48: wRe1f1
49: bPe6e5
50: wQe3b3
51: bKg8h8
52: wQb3d5
53: bQd7d5x
54: wPe4d5x
55: bKh8g8
56: wRf1d1
57: bPe5e4
58: wKg1f2
59: bRd8e8
60: wKf2e3
61: bPb5b4
62: wPd5d6
63: bPc7d6x
64: wPc5d6x
65: bRe8d8
66: wKe3e4x
67: bPa6a5
68: wKe4d5
69: bPa5a4
70: wKd5c6
71: bPb4b3
72: wPc2b3x
73: bPa4b3x
74: wPa2b3x
75: bPh7h5
76: wPd6d7
77: bPg7g5
78: wKc6c7
79: bRd8f8
80: wRd1d6
81: bPg5g4
82: wPd7d8Q
83: bRf8d8x
84: wRd6d8x
85: bKg8h7
86: wPg2g3
87: bPg4h3x
88: wRd8d4
89: bKh7g6
90: wRd4h4
91: bPh3h2
92: wPb3b4
93: bKg6g5
94: wPb4b5
95: bPh2h1Q
96: wRh4h1x
97: bKg5g4
98: wRh1h4
99: bKg4g3x
100: wRh4h5x
101: bKg3g4
102: wRh5h7
103: bKg4f4
104: wPb5b6
105: bKf4e3
106: wPb6b7
107: bKe3f2
108: wPb7b8Q
109: bKf2e3
110: wQb8g8
111: bKe3f2
112: wQg8b8
113: bKf2e3
114: wQb8b4
115: bKe3d3
116: wQb4e7
117: bKd3c2
118: wQe7g7
119: bKc2c1
120: wRh7h6
121: bKc1d1
122: wRh6h8
123: bKd1e2
124: wRh8h7
125: bKe2d2
126: wRh7h8
127: bKd2e2
128: wQg7h7
129: bKe2f2
130: wRh8g8
131: bKf2f3
132: wQh7d3
133: bKf3f2
134: wQd3g6
135: bKf2e2
136: wPb2b3
137: bKe2d2
138: wQg6e6
139: bKd2c2
140: wRg8g2
141: bKc2d3
142: wQe6g4
143: bKd3c3
144: wQg4c4 """.split('\n')

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