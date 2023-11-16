def read_board_from_stdin():
    # Read the score from the first line
    score_line = input().strip()
    _, score = score_line.split(": ")
    score = int(score)

    # Skip the second line (instruction line)
    _ = input()

    # Initialize empty board
    board = []

    # Read the next 4 lines to get the board state
    for _ in range(4):
        row_line = input().strip()
        row = []

        # Each cell is a fixed width of 5 characters
        for i in range(0, len(row_line), 6):
            cell = row_line[i:i+5].strip()

            # Convert cell to integer if not empty (.)
            if cell == '.':
                row.append(0)
            else:
                row.append(int(cell))

        board.append(row)

    return score, board

# Test the function
if __name__ == "__main__":
    score, board = read_board_from_stdin()
    print("Score:", score)
    print("Board:")
    for row in board:
        print(row)
