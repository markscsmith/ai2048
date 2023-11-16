import subprocess
import time
import re

def read_board_from_stdout(stdout):
    lines = []
    while len(lines) < 7:
        line = stdout.readline().strip()
        if not line:
            return None, None
        line = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
        lines.append(line)

    score_line = lines[0]
    _, score = score_line.split(": ")
    score = int(score)

    board = []
    for row_line in lines[2:6]:
        row = []
        for i in range(0, len(row_line), 6):
            cell = row_line[i:i+5].strip()
            if cell == '.':
                row.append(0)
            else:
                row.append(int(cell))
        board.append(row)

    return score, board

# Start the ai2048 subprocess
p = subprocess.Popen(["target/debug/ai2048"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

sequence = 'urdl'

for char in sequence:
    # send char + carrige return
    p.stdout.flush()
    p.stdin.write(char)
    p.stdin.write('\n')
    p.stdin.flush()
    time.sleep(0.1)

    score, board = read_board_from_stdout(p.stdout)
    if score is None:
        print("Failed to read board.")
        break

    print("Score:", score)
    print("Board:")
    for row in board:
        print(row)
