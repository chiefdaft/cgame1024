#!/usr/bin/env python3
""" Console game of 1024
    Try to move the squares upwards, downwards, to the left or right
    to squares with the same value. These will merge and double their
    value. When you reach 1024 (2^10) you win the the game.
    """
# from ast import YieldFrom
import os
import math
if os.name == 'posix':
    import tty
    import sys
    import termios
# Get the game1024 class rules
import game1024

# define size of the grid
rows, cols = 4, 4

# Get the size
# of the terminal
size = os.get_terminal_size()

# Define some console colors
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
M = '\033[36m'  # magenta

colors = [W, W, W, R, G, O, B, P, M, G, B]
# begin values and global variables
empty_cell = "{1}[{2}{0:1}{3}]"

margins = {
    "top": math.floor((size.lines - rows) / 2) if size.lines > rows else 0,
    "left": math.floor((size.columns - (cols * 3)) / 2)
    if size.columns > 3 * cols
    else 0,
}

def clear_console():
    os.system("cls" if os.name in ("nt", "dos") else "clear")

def print_top_margin():
        for l in range(margins["top"] - 3):
            print()

def print_bottom_margin():
    for li in range(margins["top"] - 2):
        print()

def print_left_margin(fr=1):
    lm = "\n"
    for spi in range(math.floor(fr*margins["left"])):
        lm += " "
    print("%s" % (lm), end="")

def print_grid(grid):
    for row in grid:
        for cell in row:
            if cell == 0:
                c, i = " ", 0
            else:
                c, i = cell, cell
            print(empty_cell.format(c, W, colors[i], W), end="")
        else:
            print_left_margin()

# make a sub class of the game and adapt it for linux console use
class cgame1024(game1024.Game1024):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.orig_settings = termios.tcgetattr(sys.stdin)

    def end(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.orig_settings)
        quit()

    def over(self):
        """ End the game and tell the user it's over """
        print(f"You scored {self.score}, too bad but it's G A M E  O V E R !")
        self.end()

    def won(self):
        """ End the game and tell the user he/she has won """
        print(f"You scored {self.score}, and Y O U   H A V E   W O N ! !")
        self.end()
        
    def run(self, inp=""):
        dir = self.get_dir(inp)
        clear_console()
        print_top_margin()
        print_left_margin(0.5)
        print("Up = U/w, Down = D/s, Left = L/a, Right = R/d")
        self.squares = self.step(dir)
        # if dir in dir_transp.keys():
        #     squares = move_cells(squares, dir)
        #     squares = add_random_number(squares)
        print_left_margin()
        print_grid(self.squares)
        print_left_margin(0.5)
        print("| SCORE = ", self.score, " | > Direction =", dir)
        print_bottom_margin()
        return self.squares

def main():
    # instantiate a game object
    game = cgame1024(rows, cols)
    game.init()

    tty.setcbreak(sys.stdin)
    keystr = 0
    game.run()
    while True:
        print("?> (Press X to exit the game)")
        keystr = sys.stdin.read(1)[0]
        if keystr in game.transl_dir.keys():
            game.squares = game.run(keystr)
        elif keystr == 'X':
            break
        else:
            game.squares = game.run("neutral")
    game.end()


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()