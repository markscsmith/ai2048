import re

def parse_row_data(row_data):
    try:
        row_elements = row_data.split()
        inputs = [int(element) if element != '.' else None for element in row_elements[:16]]
        score_index = row_elements.index('Score:')
        score = int(row_elements[score_index + 1])
        moves_index = row_elements.index('Moves:')
        moves = int(row_elements[moves_index + 1])
        valid = "~" in row_data
        game_over = "X" in row_data
        # data = inputs.copy()
        # array = [['.'.rjust(6) for _ in range(4)] for _ in range(4)]
        # for row in range(4):
        #     for col in range(4):
        #         value = data.pop(0)
        #         if value is not None:
        #             array[row][col] = str(value).rjust(6)  # Right-align and pad to 4 characters
        # # Print the 4x4 array with even spacing
        # for row in array:
        #     print(' '.join(row))

    except ValueError:
        print("Error!: ", row_data)
        return None, None, None, None, True
    return inputs, score, moves, valid, game_over

def read_board(child):
    line = []
    raw_data = child.readline().decode('utf-8').strip()
    data = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_data.strip())
    line.append(data)
    board = []
    
    for row_line in line:
        # print("RowLine:", row_line)
        inputs, score, moves, valid, game_over = parse_row_data(row_line)
        if inputs is None:
            print("Error parsing row data.")
            print(data)
            print(raw_data.strip())
            child.sendline("f")
            retry = read_board(child)
            if retry is not None:
                return retry
            else:
                return None, None, None, None, game_over

        return score, inputs, moves, valid, game_over
    return -1, inputs, moves, valid
