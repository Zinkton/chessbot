import torch
import random
import os
import chess
from chess_agent import ChessAgent

def check_castling(move, board_state, board):
    if board.kings & chess.BB_SQUARES[move.from_square]:
        diff = chess.square_file(move.from_square) - chess.square_file(move.to_square)
        if abs(diff) > 1:
            is_king_castling = diff < 0
            k_index = 4
            k_target = None
            r_target = None
            r_index = None
            if is_king_castling:
                r_index = 7
                r_target = 5
                k_target = 6
            else:
                r_index = 0
                r_target = 3
                k_target = 2

            board_state[[k_index, k_target]] = board_state[[k_target, k_index]]
            board_state[[r_index, r_target]] = board_state[[r_target, r_index]]

            return True
        
    return False
    
def check_promotion(move: chess.Move, board_state, board):
    if move.promotion:
        board_state[move.from_square] = 0.0
        board_state[move.to_square] = move.promotion / 6.0 if board.turn else -move.promotion / 6.0
        
        return True
    
    return False

def _get_additional_state(board):
    # Get additional state information and convert to tensor
    ep = -1.0
    if board.ep_square is not None:
        ep = board.ep_square
        if 16 <= ep <= 23:
            ep = ep - 16
        elif 40 <= ep <= 47:
            ep = ep - 40
        ep = ep / 7.0
    w_k_castling = float(board.has_kingside_castling_rights(chess.WHITE))
    b_k_castling = float(board.has_kingside_castling_rights(chess.BLACK))
    w_q_castling = float(board.has_queenside_castling_rights(chess.WHITE))
    b_q_castling = float(board.has_queenside_castling_rights(chess.BLACK))
    additional_state = [ep, w_k_castling, b_k_castling, w_q_castling, b_q_castling, board.halfmove_clock / 100.0]

    return additional_state
    
def get_additional_state_tensor(board):
        return torch.tensor(_get_additional_state(board), dtype=torch.float32)

def move_piece_on_state(board_state, move: chess.Move, board):
    if not check_promotion(move, board_state, board):
        board_state[move.to_square] = board_state[move.from_square]
        board_state[move.from_square] = 0.0

def get_board_state(board):
    """
    Converts the board state to a numerical format that can be used as input to the neural network.
    """
    # Initialize a PyTorch tensor for the board state
    board_state = torch.zeros(64, dtype=torch.float32)

    # Populate the tensor based on the board
    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            board_state[i] = piece.piece_type / 6.0 if piece.color == chess.WHITE else -piece.piece_type / 6.0

    return board_state
    
def invert_state(state) -> torch.tensor:
    # Negate the tensor values
    inverted_state = -state

    # Reshape the tensor to 8x8, reverse each row, then flatten back to 1D
    inverted_state = inverted_state.view(8, 8).flip(dims=[0]).flatten()

    return inverted_state
    
def invert_additional_state(additional_state):
    # Invert castling rights
    additional_state[[1, 2, 3, 4]] = additional_state[[2, 1, 4, 3]]

    return additional_state

def make_move_on_state(state, move, board):
    inverted_state = None

    # Checking castling doesn't require inverting the board
    if not check_castling(move, state, board):
        # We need to invert the board before making a move if we're black
        if board.turn:
            move_piece_on_state(state, move, board)
        else:
            inverted_state = invert_state(state)
            move_piece_on_state(inverted_state, move, board)

    return inverted_state

def copy_model(model):
    # Create a new instance
    new_model = ChessAgent()
    new_model.eval()
    # Copy the weights from the original model to the new one
    new_model.load_state_dict(model.state_dict())
    new_model.name = model.name

    return new_model

def print_8x8_tensor(tensor):
    """
    Prints an 8x8 space-separated representation of a 64-value torch float tensor.
    Assumes the tensor is 1D with 64 elements.
    """
    if tensor.numel() != 64:
        raise ValueError("Tensor must have exactly 64 elements.")

    # Reshape tensor to 8x8 for printing
    tensor_8x8 = tensor.view(8, 8)

    for row in tensor_8x8:
        print(' '.join(f'{value:.0f}' for value in row.tolist()))

def softmax_selection(moves_evaluations):
    evaluations = torch.tensor([item[1] for item in moves_evaluations], dtype=torch.float32)

    # We want the moves with the lowest scores because it's from the opponent POV
    evaluations = evaluations.max() - evaluations

    # Scale evaluations to make probabilities more sensitive
    scaled_evaluations = evaluations * 10
    probabilities = torch.softmax(scaled_evaluations, dim=0)

    move_indices = list(range(len(moves_evaluations)))
    sorted_moves = sorted(zip(move_indices, probabilities), key=lambda x: x[1], reverse=True)

    # Select one of the top two moves
    selected_index = random.choice(sorted_moves[:2])[0]

    return moves_evaluations[selected_index]

def pick_random_opponent(filenames):
    opponents = sorted([int(filename) for filename in filenames])
    num_opponents = len(opponents)

    # Generate weights based on a quadratic distribution
    # The latest model (last in the list) gets the highest weight
    weights = [(i / num_opponents) ** 2 for i in range(num_opponents)]

    # Normalize weights so that the sum equals 1
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    # Ensure the newest model has a weight of 0.5 (50%)
    normalized_weights[-1] = 0.5
    remaining_weight = 1 - 0.5
    for i in range(num_opponents - 1):
        normalized_weights[i] *= remaining_weight

    # Select an opponent based on the weights
    selected_opponent = random.choices(opponents, weights=normalized_weights, k=1)[0]
    return str(selected_opponent)

def save_model(model, version):
    filename = f"models/{version}"
    model.name = str(version)
    torch.save(model.state_dict(), filename)

def load_latest_model():
    model = ChessAgent().to('cuda')

    files = os.listdir('models/.')
    if files:
        latest_model_file = str(max([int(filename) for filename in files]))
        model.load_state_dict(torch.load(f'models/{latest_model_file}'))
        model.name = latest_model_file
    else:
        model.name = '0'
        save_model(model, 0)

    return model

def load_model(models, filename = None, agent_name = None):
    model = ChessAgent()

    if filename is None:
        files = os.listdir('models/.')
        files = [file for file in files if str(file) != agent_name]
        if not files:
            model.name = '0'
            models['0'] = model
            model.eval()

            return model
        
        if len(files) == 1:
            filename = files[0]
        else:
            # Pick random opponent, favoring latest models
            filename = pick_random_opponent(files)
        
        if filename in models:
            return models[filename]
    
    model.load_state_dict(torch.load(f'models/{filename}'))
    model.name = filename
    models[filename] = model
    model.eval()

    return model

def load_values(filename):
    values = {}
    if not os.path.exists(filename):
        return values
    
    with open(filename, 'r+') as file:
        for line in file:
            name, value = line.strip().split(' ')
            value = float(value)
            values[name] = value

    return values

def save_values(values, filename):
    keys = [int(key) for key in values.keys()]
    keys.sort()
    with open(filename, 'w') as file:
        for key in keys:
            file.write(f"{key} {values[str(key)]}\n")