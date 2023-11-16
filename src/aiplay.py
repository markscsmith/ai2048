import pexpect
import re
import time
import torch
import torch.nn as nn

# Define the neural network architecture
class Game2048NN(nn.Module):
    def __init__(self):
        super(Game2048NN, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(18, 64),
            nn.ReLU(),
            nn.Linear(64, 4)
        )
        
    def forward(self, x):
        return self.layers(x)

# Initialize or load the neural network
game_nn = Game2048NN()
# Uncomment the next line if you have a pre-trained model to load
# game_nn.load_state_dict(torch.load('path/to/your/model.pth'))

def parse_row_data(row_data):
    row_elements = row_data.split()
    inputs = [int(element) if element != '.' else None for element in row_elements[:16]]
    score_index = row_elements.index('Score:')
    score = int(row_elements[score_index + 1])
    moves_index = row_elements.index('Moves:')
    moves = int(row_elements[moves_index + 1])
    valid = "~" in row_data

    return inputs, score, moves, valid

def read_board(child):
    line = []
    raw_data = child.readline().decode('utf-8').strip()
    data = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_data.strip())
    line.append(data)

    board = []
    for row_line in line[0:5]:
        inputs, score, moves, valid = parse_row_data(row_line)
     
    return score, inputs, moves, valid

child = pexpect.spawn("target/debug/ai2048")
child.timeout = 1
invalid_moves = 0  # Add this line to initialize the count of invalid moves
max_invalid_moves = 10  # Maximum allowed invalid moves before breaking the loop

while True:
    try:
        # Read and parse the board
        score, board, moves, valid = read_board(child)
        board = [x if x is not None else 0 for x in board]

        # Make a prediction using the neural network
        input_tensor = torch.tensor(board + [score, max(board)], dtype=torch.float32)
        with torch.no_grad():
            output = game_nn(input_tensor.unsqueeze(0))
            _, predicted_move = torch.max(output, 1)
            move_dict = {0: 'u', 1: 'r', 2: 'd', 3: 'l'}
            predicted_char = move_dict[predicted_move.item()]

        # Execute the move
        child.send(predicted_char + '\n')
        child.readline()

        # Your existing code for printing and logging
        print("Valid:", valid)
        if not valid:
            invalid_moves += 1  # Update the count of invalid moves
        print("Invalid moves:", invalid_moves)
        print("Score:", score)
        print("Moves:", moves)
        print("Board:")
        largest = 0
        for i in range(0, 16, 4):
            values = board[i:i+4]
            values = [value if value is not None else 0 for value in values]
            largest = max(max(values), largest)
            print("{: >5} {: >5} {: >5} {: >5}".format(*values))
        print("Largest:", largest)
        print("Current Move", predicted_char)
        if invalid_moves >= max_invalid_moves:
            print("Too many invalid moves. Exiting.")
            break

    except Exception as e:
        print("Exception occurred:", e, type(e))
        break
