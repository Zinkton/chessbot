moves = """ 0: wPf2f4
1: bPd7d5
2: wPe2e3
3: bPg7g6
4: wBf1d3
5: bBf8g7
6: wPh2h4
7: bPe7e5
8: wPf4e5x
9: bNb8c6
10: wNg1f3
11: bNc6e5x
12: wNf3e5x
13: bBg7e5x
14: wQd1f3
15: bNg8f6
16: wKe1h1OO
17: bKe8h8OO
18: wPc2c3
19: bBc8g4
20: wQf3f2
21: bNf6h5
22: wPg2g3
23: bNh5g3x
24: wRf1e1
25: bQd8h4x
26: wQf2g2
27: bNg3e4
28: wRe1f1
29: bBg4h3
30: wQg2f3
31: bNe4g5
32: wQf3f2
33: bBe5g3
34: wQf2f3
35: bBg3h2
36: wKg1h2x
37: bBh3f1x
38: wKh2g1
39: bBf1d3x
40: wQf3g2
41: bNg5h3
42: wKg1h1
43: bNh3f4
44: wKh1g1
45: bQh4e1
46: wKg1h2
47: bNf4g2x
48: wKh2g2x
49: bBd3e4
50: wKg2h3
51: bRa8d8
52: wPd2d3
53: bQe1f2
54: wPd3e4x
55: bPg6g5
56: wKh3g4
57: bPd5e4x
58: wKg4g5x
59: bQf2e1
60: wNb1a3
61: bRd8d5
62: wKg5g4
63: bPf7f6
64: wNa3c4
65: bRd5g5
66: wKg4h3
67: bQe1g3 """.split('\n')

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