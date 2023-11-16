import pexpect
import re
import time


def parse_row_data(row_data):
    # Split the row data using spaces
    
    row_elements = row_data.split()

    # Extract inputs, score, and moves
    inputs = [int(element) if element != '.' else None for element in row_elements[:16]]
    score_index = row_elements.index('Score:')
    score = int(row_elements[score_index + 1])
    moves_index = row_elements.index('Moves:')
    moves = int(row_elements[moves_index + 1])
    valid = "~" in row_data

    return inputs, score, moves, valid


def read_board(child):

    # Read the next line and decode it to string

    # Read five lines
    line = []
    
    raw_data = child.readline().decode('utf-8').strip()
    data = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_data.strip())
    line.append(data)
    
    # Filter out ANSI escape sequences


    # Skip the instruction line
    # parse the rest of the board
    board = []

    for row_line in line[0:5]:
        inputs, score, moves, valid = parse_row_data(row_line)

     
    return score, inputs, moves, valid

# Spawn a child process

child = pexpect.spawn("target/debug/ai2048")

# Set the timeout to 1 second
child.timeout = 1

sequence = 'urdl'
invalid_moves = 0
largest = 0

while True:
    try:
        for char in sequence:
            # Send the command
            score, board, moves, valid = read_board(child)
            time.sleep(0.05)
            child.send(char + '\n')
            
            # Read and parse the board
            child.stdout.flush()
            
            
            # Print the current state
            print("Valid:", valid)
            if not valid:
                invalid_moves += 1
            print("Invalid moves:", invalid_moves)
            print("Score:", score)
            print("Moves:", moves)
            
            # split 16 board cells into rows and columns:
            # 0 1 2 3
            # 4 5 6 7
            # 8 9 10 11
            # 12 13 14 15
            print("Board:")
            # parse the largest value on the board:
            largest = 0
            for i in range(0, 16, 4):

                values = board[i:i+4]
                # list comprehension to convert None to '.'
                values = [value if value is not None else 0 for value in values]
                # find the largest value on the board
                largest = max(values, largest)
                # print the values with a fixed 5 charachter width:
                print("{: >5} {: >5} {: >5} {: >5}".format(*values))
            print("Largest:", largest)


            print("Current Move", char)
    except pexpect.TIMEOUT:
        print("No output received. Exiting.")
        break
    except pexpect.EOF:
        print("End of file reached. Exiting.")
        break
    except ValueError:
        break
    except OSError:
        print("OSError occurred. Game over!")

        print("Score:", score)

        print("Invalid moves:", invalid_moves)
        print("Valid:", valid)
        print("Score:", score)
        print("Moves:", moves)

        # split 16 board cells into rows and columns:
        # 0 1 2 3
        # 4 5 6 7
        # 8 9 10 11
        # 12 13 14 15
        print("Board:")
        # parse the largest value on the board:
        largest = 0
        for i in range(0, 16, 4):
            values = board[i:i+4]
            # list comprehension to convert None to '.'
            values = [value if value is not None else 0 for value in values]
            # find the largest value on the board
            largest = max(values, largest)
            # print the values with a fixed 5 charachter width:
            print("{: >5} {: >5} {: >5} {: >5}".format(*values))
        print("Largest:", largest)
        raw_data = child.before.decode('utf-8')
        print(re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_data.strip()))

        break
    except Exception as e:
        print("Exception occurred:", e, type(e))
        break
    print()
