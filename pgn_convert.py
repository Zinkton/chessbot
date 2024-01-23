moves = """ 0: wPe2e4
1: bNb8c6
2: wNg1f3
3: bNg8f6
4: wPe4e5
5: bNf6g4
6: wPd2d4
7: bPd7d6
8: wPh2h3
9: bNg4h6
10: wNb1c3
11: bPd6e5x
12: wPd4d5
13: bNc6d4
14: wNf3e5x
15: bPc7c5
16: wQd1d4x
17: bPc5d4x
18: wBf1b5
19: bBc8d7
20: wBb5d7x
21: bQd8d7x
22: wNe5d7x
23: bKe8d7x
24: wNc3b5
25: bNh6f5
26: wBc1f4
27: bPa7a6
28: wNb5a3
29: bPe7e6
30: wNa3c4
31: bBf8c5
32: wPg2g4
33: bNf5h4
34: wPd5e6x
35: bKd7e6x
36: wKe1a1OOO
37: bKe6d5
38: wNc4a5
39: bPb7b5
40: wNa5b3
41: bRh8c8
42: wBf4e3
43: bNh4f3
44: wPc2c3
45: bKd5e4
46: wBe3d4x
47: bNf3d4x
48: wNb3c5x
49: bRc8c5x
50: wRd1d4x
51: bKe4f3
52: wRh1e1
53: bKf3f2x
54: wRe1e7
55: bRa8f8
56: wRd4d7
57: bPh7h6
58: wRd7d2
59: bKf2g3
60: wRd2d3
61: bKg3g2
62: wRe7e2
63: bKg2f1
64: wRe2h2
65: bRf8e8
66: wRd3d1
67: bRe8e1
68: wRh2h1
69: bKf1g2
70: wRh1e1x
71: bRc5c7
72: wRe1e3
73: bKg2f2
74: wRe3d3
75: bRc7c4
76: wRd1d2
77: bKf2g1
78: wRd3g3
79: bKg1f1
80: wRg3f3
81: bKf1g1
82: wRf3f7x
83: bPg7g5
84: wKc1b1
85: bRc4e4
86: wRd2d1
87: bKg1g2
88: wRf7h7
89: bRe4e6
90: wPa2a3
91: bKg2h3x
92: wRh7h6x
93: bRe6h6x
94: wRd1h1
95: bKh3g4x
96: wRh1h6x
97: bKg4f3
98: wRh6f6
99: bKf3e3
100: wRf6g6
101: bKe3f4
102: wRg6f6
103: bKf4e3
104: wRf6e6
105: bKe3f3
106: wRe6f6
107: bKf3g3
108: wRf6a6x
109: bPg5g4
110: wRa6g6
111: bKg3f3
112: wRg6f6
113: bKf3e2
114: wRf6e6
115: bKe2f2
116: wRe6f6
117: bKf2e2
118: wRf6g6
119: bKe2f3
120: wPa3a4
121: bPb5a4x
122: wPc3c4
123: bPg4g3
124: wPc4c5
125: bPg3g2
126: wPc5c6
127: bKf3f2
128: wPc6c7
129: bPg2g1Q
130: wRg6g1x
131: bKf2g1x
132: wPc7c8Q
133: bKg1f2
134: wQc8g4
135: bKf2e3
136: wKb1c2
137: bKe3f2
138: wQg4c8
139: bKf2g3
140: wQc8a8
141: bPa4a3
142: wPb2b4
143: bPa3a2
144: wPb4b5
145: bPa2a1Q
146: wQa8a1x
147: bKg3f4
148: wPb5b6
149: bKf4e3
150: wPb6b7
151: bKe3f2
152: wPb7b8Q
153: bKf2f3
154: wQa1f1
155: bKf3g4
156: wQf1f6
157: bKg4h5
158: wQf6g7
159: bKh5h4
160: wQb8h8 """.split('\n')

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