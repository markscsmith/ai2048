import time

sequence = 'urdl'

while True:
    for char in sequence:
        print(char, end='\n', flush=True)
        time.sleep(0.1)  # wait for half a second before sending the next character
