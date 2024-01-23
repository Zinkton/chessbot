moves = """ 0: wPe2e4
1: bPe7e6
2: wPd2d4
3: bPd7d5
4: wNb1c3
5: bBf8b4
6: wPa2a3
7: bBb4a5
8: wPb2b4
9: bBa5b6
10: wNg1f3
11: bNg8e7
12: wBf1e2
13: bKe8h8OO
14: wKe1h1OO
15: bPf7f5
16: wPe4e5
17: bBc8d7
18: wBc1b2
19: bNe7g6
20: wPg2g3
21: bRf8e8
22: wPh2h4
23: bPa7a6
24: wPh4h5
25: bNg6e7
26: wQd1d2
27: bNb8c6
28: wQd2f4
29: bRa8c8
30: wRa1d1
31: bBb6a7
32: wPh5h6
33: bNe7g6
34: wQf4e3
35: bPg7h6x
36: wQe3h6x
37: bQd8e7
38: wBb2c1
39: bQe7f8
40: wQh6h5
41: bQf8e7
42: wRf1e1
43: bQe7g7
44: wBc1g5
45: bNg6e7
46: wPb4b5
47: bPa6b5x
48: wNc3b5x
49: bBa7b6
50: wPc2c4
51: bQg7g6
52: wNf3h4
53: bQg6h5x
54: wBe2h5x
55: bRe8f8
56: wBh5e2
57: bBb6a5
58: wRe1f1
59: bRf8e8
60: wBe2h5
61: bRe8f8
62: wBg5e7x
63: bNc6e7x
64: wBh5e2
65: bRc8d8
66: wBe2d3
67: bNe7g6
68: wPf2f4
69: bNg6h4x
70: wPg3h4x
71: bPd5c4x
72: wBd3c4x
73: bBd7b5x
74: wBc4b5x
75: bBa5b6
76: wKg1h1
77: bBb6d4x
78: wBb5c4
79: bRf8e8
80: wRd1d3
81: bPb7b6
82: wRf1d1
83: bPc7c5
84: wRd1b1
85: bRd8b8
86: wPa3a4
87: bPh7h6
88: wRd3b3
89: bKg8f7
90: wRb3b6x
91: bRb8b6x
92: wRb1b6x
93: bBd4e3
94: wPa4a5
95: bBe3f4x
96: wPa5a6
97: bRe8d8
98: wPa6a7
99: bBf4e5x
100: wRb6e6x
101: bKf7g7
102: wRe6e5x
103: bRd8d1
104: wKh1g2
105: bRd1a1
106: wRe5e7
107: bKg7h8
108: wRe7e8
109: bKh8g7
110: wPa7a8Q
111: bRa1a8x
112: wRe8a8x
113: bKg7f6
114: wRa8c8
115: bKf6e5
116: wRc8c5x
117: bKe5d4
118: wRc5c7
119: bKd4e3
120: wRc7e7
121: bKe3d4
122: wRe7c7
123: bKd4e3
124: wPh4h5
125: bKe3d4
126: wKg2f3
127: bKd4e5
128: wRc7h7
129: bKe5f6
130: wRh7h6x
131: bKf6e5
132: wRh6c6
133: bKe5d4
134: wPh5h6
135: bKd4c3
136: wPh6h7
137: bKc3c2
138: wPh7h8Q
139: bPf5f4
140: wBc4a2
141: bKc2d2
142: wQh8f6
143: bKd2e1
144: wRc6c1
145: bKe1d2
146: wRc1c6
147: bKd2e1
148: wQf6e6
149: bKe1f1
150: wRc6c1 """.split('\n')

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