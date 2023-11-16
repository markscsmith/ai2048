import pexpect
import time
import tensorflow as tf
from model import Game2048NN, load_or_create_model
from utils import read_board, parse_row_data
from train import train_model
from threading import Thread, Lock
from queue import Queue
import random
import math
import numpy as np
import traceback
import sys

# Constants
BATCH_SIZE = 256
tf.debugging.set_log_device_placement(True)

# Global lock for updating epsilon
epsilon_lock = Lock()
epsilon = 0.1

# Initialize global variables for single-game training
input_game = []
output_game = []

# Other global variables
current_generation = 0
failed_generations_due_to_error = 0
failed_generations_due_to_game_over = 0
successful_generations = 0
current_record = 0
generations_since_record = 0
previous_record = 0
predicted_move = None
training_events = 0
tf_lock = Lock()

def parallel_training(game_nn, num_threads=10):
    q = Queue()
    threads = []

    for i in range(num_threads):
        t = Thread(target=game_loop, args=(q, game_nn))
        t.start()
        threads.append(t)

    while True:
        if q.qsize() >= BATCH_SIZE:
            training_states, training_moves = q.get()
            states_array = np.stack(training_states)
            moves_array = np.array(training_moves)
            with tf_lock:
                train_model(game_nn, states_array, moves_array)
            print("Model trained.")

def print_board(board):
    if board is None:
        print("Board is None.")
        return
    for i in range(0, 16, 4):
        print("{: >5} {: >5} {: >5} {: >5}".format(*board[i:i+4]))

def get_dynamic_epsilon(consecutive_invalid_moves, generations_since_record):
    alpha_invalid_moves = 0.3
    alpha_generations = 0.01
    exp_invalid_moves = math.exp(alpha_invalid_moves * consecutive_invalid_moves) - 1
    exp_generations = math.exp(alpha_generations * generations_since_record) - 1
    epsilon_invalid_moves = exp_invalid_moves / (1 + exp_invalid_moves)
    epsilon_generations = exp_generations / (1 + exp_generations)
    epsilon = 0.3 * epsilon_invalid_moves + 0.3 * epsilon_generations
    # print(f"epsilon = {epsilon}")
    return min(epsilon, 1.0)

def game_loop(q, game_nn):
    global input_game, output_game, current_generation, failed_generations_due_to_error, failed_generations_due_to_game_over, successful_generations, current_record, generations_since_record, predicted_move, previous_record, training_events

    input_game.clear()
    output_game.clear()
    current_generation += 1
    print(f"Starting generation {current_generation}.")
    consecutive_invalid_moves = 0
    largest = 0
    child = pexpect.spawn("target/release/ai2048")
    child.timeout = 1
    child.flush()
    exploration_prob = 0.2
    while largest < 2048:
        predicted_char = random.choice(['u', 'r', 'd', 'l'])
        try:
            new_score, new_board, moves, valid, game_over = read_board(child)
            if valid:
                consecutive_invalid_moves = 0
            else:
                consecutive_invalid_moves += 1
                exploration_prob = get_dynamic_epsilon(consecutive_invalid_moves, generations_since_record)
            if game_over:
                
                print(f"Game over: Biggest = {max(new_board)}, {new_score},  {new_board}, {moves}, {valid}, {game_over}")
                print(f"Size of input_game: {len(input_game)}, Size of output_game: {len(output_game)}")

                if len(input_game) > 0 and len(output_game) > 0:
                    states_array = np.stack(input_game)
                    moves_array = np.array(output_game)  # Assuming output_game is a list of integers
                    train_model(game_nn, states_array, moves_array)
                    print("Model trained.")
            
                else:
                    print("Either input_game or output_game is empty. Skipping training.")
                try:
                    child.sendline('q')
                    child.expect(pexpect.EOF)
                    child = pexpect.spawn("target/release/ai2048")
                except Exception as e:
                    pass

            
                failed_generations_due_to_game_over += 1
                generations_since_record += 1

                # Train model after the game is over

            if new_score is None:
                print("Error reading board.")
                child.sendline("f")
                continue
            else:
                score = new_score
                board = new_board

            board = [x if x is not None else 0 for x in board]
            input_array = np.array(board + [score, max(board)], dtype=np.float32).reshape(1, -1)

            # Use the model to predict the next move
            if random.random() < exploration_prob:
            # Choose a random move
                predicted_move = random.choice([0, 1, 2, 3])
            else:
            # Use the model to predict the next move
                with tf_lock:
                    output_array = game_nn(input_array).numpy()
                predicted_move = np.argmax(output_array[0])


            # Convert the predicted_move to the corresponding character
            move_dict = {0: 'u', 1: 'r', 2: 'd', 3: 'l'}
            predicted_char = move_dict[predicted_move]

            input_game.append(input_array.reshape(-1).tolist())
            # print(f"Predicted move: {predicted_char}")
            if predicted_move is not None:
                output_game.append(predicted_move)

            child.send(predicted_char + '\n')
            child.readline()
            child.flush()
            board = read_board(child)

        except (RuntimeError, ValueError) as error:
            print(f"{type(error).__name__} occurred: {error}")

            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Error on line {exc_tb.tb_lineno} of main.py")
            failed_generations_due_to_error += 1
            print_board(board)
            generations_since_record += 1
            break
    if len(input_game) > 0 and len(output_game) > 0:
        states_array = np.stack(input_game)
        moves_array = np.array(output_game)
        q.put((states_array.tolist(), moves_array.tolist()))
    input_game.clear()

if __name__ == '__main__':
    game_nn = load_or_create_model()
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    try:
        parallel_training(game_nn)
    except Exception as e:
        print("An exception occurred:", e)
