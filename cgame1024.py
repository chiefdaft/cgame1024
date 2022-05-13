#!/usr/bin/env python3
""" Console game of 1024
    Try to move the squares upwards, downwards, to the left or right
    to squares with the same value. These will merge and double their
    value. When you reach 1024 (2^10) you win the the game.
    """
# from ast import YieldFrom
import os
import math
import random
from random import choice
if os.name == 'posix':
    import tty
    import sys
    import termios

# Define some console colors
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
M = '\033[36m'  # magenta

colors = [W, W, W, R, G, O, B, P, M, G, B]


def clear_console():
    os.system("cls" if os.name in ("nt", "dos") else "clear")

score = 0


transl_dir = {
    "a": "left",
    "L": "left",
    "w": "up",
    "U": "up",
    "d": "right",
    "R": "right",
    "s": "down",
    "D": "down",
}
dir_transp = {
    "left": (1, 1),
    "right": (1, -1),
    "up": (-1, 1),
    "down": (-1, -1),
}


def transpose(mx):
    """Transpose a matrix, a list with lists"""
    # print("transpose",mx)
    mx_w, mx_h = len(mx[0]), len(mx)
    transResult = [[0] * mx_h for i in range(mx_w)]
    for a in range(mx_h):
        for b in range(mx_w):
            transResult[b][a] = mx[a][b]
    return transResult


def mirror_v(mx):
    """Miror a matrix vertically"""
    w, h = len(mx[0]), len(mx)
    mirror_mx = [[0] * w for i in range(h)]
    for rowi in range(w):
        mirror_mx[rowi] = mx[rowi][::-1]
    return mirror_mx


def get_random_empty_cell(cells, game_over):
    """ Find the squares with value 0, these are the empty ones """
    ecls = []
    w, h = len(cells[0]), len(cells)
    for x in range(w):
        for y in range(h):
            if cells[x][y] == 0:
                ecls.append([x, y])
    # rcn = random.randint(0, len(ecls) - 1)
    # return ecls[rcn]
    try:
        return random.choice(ecls)
    except IndexError:
        game_over()

    

def add_random_number(cells, game_over):
    """ Add a random 1 or 2 to a random empty square """
    try:
        rndcell = get_random_empty_cell(cells, game_over)
        (cells[rndcell[0]])[rndcell[1]] = random.randint(1, 2)
        return cells
    except ValueError:
        game_over()
    


def merge_cells_in_trow(trow,game_won):
    """Move all cells>0 to the left, and fill up with zero's on the right.
    Add the merged cell values to the score"""
    srow = list(filter(lambda c: c != 0, trow))
    ls = len(srow)
    m, l = 0, 1
    zeros = []
    while l < ls:
        if srow[m] == srow[l]:
            srow[m] += 1
            srow[l] = 0
            # Keep track of the removed holes, and append them later on
            zeros.append(l)
            global score
            score += 2**srow[m]
            if m == 10:
                game_won()
            m += 2
            l += 2
        else:
            m += 1
            l += 1
    # remove the holes left by the merged cells
    for z in range(len(zeros)):
        srow.pop(zeros[z])
        srow.append(0)
    srow += [0 for i in range(len(trow) - ls)]
    return srow


def move_cells(squares, dir, game_won):
    """Move all cells in the indicated direction and merge equally valued cells"""
    if dir not in dir_transp.keys():
        return
    temp_sqrs = squares
    # in case of up or down, transpose
    if dir_transp[dir][0] == -1:
        temp_sqrs = transpose(squares)
    # in case of right or down, mirror
    if dir_transp[dir][1] == -1:
        temp_sqrs = mirror_v(temp_sqrs)
    merged_cells = []
    for row in temp_sqrs:
        merged_cells.append(merge_cells_in_trow(row,game_won))
    if dir_transp[dir][1] == -1:
        # mirror back
        merged_cells = mirror_v(merged_cells)
    if dir_transp[dir][0] == -1:
        # transpose back
        merged_cells = transpose(merged_cells)
    return merged_cells

# print(squares)

def get_dir(inp):
    try:
        return transl_dir[inp]
    except KeyError:
        return "neutral"

def game_step(dir, squares, game_won, game_over):
    if dir not in dir_transp.keys():
        return squares
    squares = move_cells(squares, dir, game_won)
    squares = add_random_number(squares, game_over)
    return squares

def main():
    # define size of the grid
    cols, rows = 4, 4
    global score
    score = 0
    # begin values and global variables
    legecell = "{1}[{2}{0:1}{3}]"
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
                print(legecell.format(c, W, colors[i], W), end="")
            else:
                print_left_margin()

    
    # Get the size
    # of the terminal
    size = os.get_terminal_size()
    margins = {
        "top": math.floor((size.lines - rows) / 2) if size.lines > rows else 0,
        "left": math.floor((size.columns - (cols * 3)) / 2)
        if size.columns > 3 * cols
        else 0,
    }
    def game_end():
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
        quit()

    def game_over():
        """ End the game and tell the user it's over """
        print(f"You scored {score}, too bad but it's G A M E  O V E R !")
        game_end()

    def game_won():
        """ End the game and tell the user he/she has won """
        print(f"You scored {score}, and Y O U   H A V E   W O N ! !")
        game_end()
        
    def game_run(squares, game_won, game_over, inp=""):
        global score
        dir = get_dir(inp)
        clear_console()
        print_top_margin()
        print_left_margin(0.5)
        print("Up = U/w, Down = D/s, Left = L/a, Right = R/d")
        squares = game_step(dir, squares, game_won, game_over)
        # if dir in dir_transp.keys():
        #     squares = move_cells(squares, dir)
        #     squares = add_random_number(squares)
        print_left_margin()
        print_grid(squares)
        print_left_margin(0.5)
        print("| SCORE = ", score, " | > Direction =", dir)
        print_bottom_margin()
        return squares

    squares = [[0] * cols for i in range(rows)]
    squares = add_random_number(squares, game_over)
    squares = add_random_number(squares, game_over)

    orig_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    keystr = 0
    game_run(squares, game_won, game_over)
    while True:
        print("?> (Press X to exit the game)")
        keystr = sys.stdin.read(1)[0]
        if keystr in transl_dir.keys():
            squares = game_run(squares, game_won, game_over, keystr)
        elif keystr == 'X':
            break
        else:
            squares = game_run(squares, game_won, game_over, "neutral")
    game_end()


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()