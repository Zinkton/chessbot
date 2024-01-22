moves = """ 0: wPe2e4
1: bNb8c6
2: wPd2d4
3: bPe7e5
4: wPd4d5
5: bBf8c5
6: wPd5c6x
7: bPd7c6x
8: wQd1d8x
9: bKe8d8x
10: wBc1e3
11: bBc5e3x
12: wPf2e3x
13: bNg8f6
14: wBf1c4
15: bNf6g4
16: wBc4f7x
17: bRh8f8
18: wBf7c4
19: bNg4f2
20: wNb1c3
21: bNf2h1x
22: wKe1a1OOO
23: bKd8e8
24: wNg1f3
25: bNh1f2
26: wRd1d2
27: bNf2g4
28: wNc3a4
29: bPb7b5
30: wBc4e2
31: bPb5a4x
32: wRd2d3
33: bBc8a6
34: wRd3d2
35: bBa6e2x
36: wRd2e2x
37: bPa4a3
38: wPb2b3
39: bRa8b8
40: wPh2h3
41: bNg4f6
42: wNf3e5x
43: bNf6e4x
44: wNe5c6x
45: bRf8f1
46: wRe2e1
47: bRf1e1x """.split('\n')

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