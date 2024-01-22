def invert_rank(squares):
    squares_str = str(squares)
    # Mapping ranks to their inverted counterparts
    rank_inversion_map = {'1': '8', '2': '7', '3': '6', '4': '5', '5': '4', '6': '3', '7': '2', '8': '1'}
    result = ''
    for x in range(len(squares_str)):
        result += rank_inversion_map.get(squares_str[x], squares_str[x])
    return result

def flip_and_mirror_fen(fen):
    # Splitting the FEN string into its parts
    parts = fen.split(' ')
    rows = parts[0].split('/')

    # Flipping and mirroring the board
    flipped_rows = []
    for row in reversed(rows):
        flipped_row = ''.join(char.swapcase() if char.isalpha() else char for char in row)
        flipped_rows.append(flipped_row)

    # Reconstructing the FEN string for the board
    flipped_fen = '/'.join(flipped_rows)
    parts[0] = flipped_fen

    # Turn reverse
    parts[1] = 'b' if parts[1] == 'w' else 'w'

    # Inverting castling rights
    castling_rights = parts[2]
    if castling_rights != '-':
        inverted_castling = ''.join(char.swapcase() for char in castling_rights)
        # Separating uppercase and lowercase letters
        uppercase_chars = [char for char in inverted_castling if char.isupper()]
        lowercase_chars = [char for char in inverted_castling if char.islower()]
        parts[2] = ''.join(uppercase_chars + lowercase_chars)

    # Invert en-passant
    if len(parts[3]) == 2:
        parts[3] = invert_rank(parts[3])

    return ' '.join(parts)
