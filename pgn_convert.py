moves = """   0: wPe2e4
1: bNb8c6
2: wNg1f3
3: bPe7e5
4: wPd2d4
5: bPe5d4x
6: wNf3d4x
7: bQd8h4
8: wNb1c3
9: bBf8b4
10: wNd4b5
11: bBb4a5
12: wBf1d3
13: bPa7a6
14: wNb5a3
15: bNg8f6
16: wBc1d2
17: bKe8h8OO
18: wPg2g3
19: bQh4h3
20: wBd3f1
21: bQh3e6
22: wBf1g2
23: bPd7d5
24: wKe1h1OO
25: bPd5e4x
26: wRf1e1
27: bRf8d8
28: wBg2e4x
29: bBa5c3x
30: wBe4h7x
31: bKg8h7x
32: wRe1e6x
33: bRd8d2x
34: wQd1f3
35: bBc8e6x
36: wPb2c3x
37: bNf6g4
38: wRa1f1
39: bKh7g8
40: wQf3e4
41: bNg4e5
42: wNa3b1
43: bPf7f5
44: wQe4e3
45: bRd2c2x
46: wPf2f4
47: bBe6d5
48: wRf1f2
49: bNe5g4
50: wQe3c5
51: bRc2f2x
52: wQc5d5x
53: bKg8h8
54: wQd5e6
55: bRa8d8
56: wQe6e1
57: bRf2a2x
58: wPc3c4
59: bNg4h2x
60: wNb1c3
61: bNh2f3
62: wKg1f1
63: bNf3e1x
64: wNc3a2x
65: bNe1c2
66: wNa2c3
67: bRd8d2
68: wPg3g4
69: bNc6d4
70: wNc3d1
71: bPf5g4x
72: wPf4f5
73: bPg4g3
74: wNd1f2
75: bRd2f2x
76: wKf1g1
77: bNd4f3
78: wKg1h1
79: bRf2h2   """.split('\n')

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