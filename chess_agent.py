import torch
import torch.nn as nn
import torch.nn.functional as F

class ChessAgent(nn.Module):
    def __init__(self):
        super(ChessAgent, self).__init__()
        # Convolutional layers for the board
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(64)
        self.conv4 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.bn4 = nn.BatchNorm2d(128)

        # 1x1 Convolution for dimension matching in residual connection
        self.match_dimensions1 = nn.Conv2d(1, 32, kernel_size=1)
        self.match_dimensions2 = nn.Conv2d(32, 128, kernel_size=1)

        # Fully connected layers for the board
        self.fc1_board = nn.Linear(128 * 8 * 8, 256)
        self.dropout = nn.Dropout(0.5)

        # Additional inputs layer
        self.fc1_additional = nn.Linear(6, 32)

        # Combined layers
        self.fc2 = nn.Linear(256 + 32, 128)
        self.out = nn.Linear(128, 1)

    def forward(self, board, additional_inputs):
        # Reshape the board input to [batch_size, channels, height, width]
        # Assuming board is a flattened 8x8 board with 1 channel
        board = board.view(-1, 1, 8, 8)  # Reshape to [batch_size, 1, 8, 8]

        identity1 = board
        # Process the board with residual connection and batch normalization
        x_board = self.bn1(F.relu(self.conv1(board)))

        x_board = self.conv2(x_board)
        
        identity1 = self.match_dimensions1(identity1)
        x_board = self.bn2(F.relu(x_board + identity1))

        identity2 = x_board
        x_board = self.bn3(F.relu(self.conv3(x_board)))
        x_board = self.conv4(x_board)
        
        identity2 = self.match_dimensions2(identity2)
        x_board = self.bn4(F.relu(x_board + identity2))

        x_board = x_board.view(-1, 128 * 8 * 8)  # Flatten
        x_board = self.dropout(F.relu(self.fc1_board(x_board)))

        # Process the additional inputs
        x_additional = F.relu(self.fc1_additional(additional_inputs))

        # Combine and process further
        x_combined = torch.cat((x_board, x_additional), dim=1)
        x_combined = F.relu(self.fc2(x_combined))

        # Output layer with tanh activation for output range of [-1, 1]
        x_combined = torch.tanh(self.out(x_combined))

        return x_combined

    def get_position_evaluation(self, board_state, additional_inputs):
        # Convert the board state to a tensor and run it through the network
        additional_inputs_tensor = additional_inputs.unsqueeze(0)
        with torch.no_grad():  # Ensure no gradients are calculated
            return self.forward(board_state, additional_inputs_tensor).item()
        
    def get_multiple_position_evaluations(self, board_states, additional_inputs):
        states_tensor = torch.stack(board_states).cuda()
        add_states_tensor = torch.stack(additional_inputs).cuda()

        with torch.no_grad():  # Ensure no gradients are calculated
            result = self.forward(states_tensor, add_states_tensor).tolist()
        
            return result
        