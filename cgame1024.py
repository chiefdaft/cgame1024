#!/usr/bin/env python3
""" Console game of 1024
    Try to move the squares upwards, downwards, to the left or right
    to squares with the same value. These will merge and double their
    value. When you reach 1024 (2^10) you win the the game.
    """
import os, math, random #, keyboard
from random import randint

# define size of the grid
cols, rows = 4, 4
score = 0
# begin values and global variables
legecell = "[{0:1}]"

squares = [[0] * cols for i in range(rows)]

# Get the size
# of the terminal
size = os.get_terminal_size()

def clear_console():
    os.system("cls" if os.name in ("nt", "dos") else "clear")

margins = {
    "top": math.floor((size.lines - rows) / 2) if size.lines > rows else 0,
    "left": math.floor((size.columns - (cols * 3)) / 2) 
    if size.columns > 3 * cols
    else 0,
}

def print_top_margin():
    for l in range(margins["top"] - 2):
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
                c = " "
            else:
                c = cell
            print(legecell.format(c), end="")
        else:
            print_left_margin()

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
    "left": (1,1),
    "right": (1,-1),
    "up": (-1,1),
    "down": (-1,-1),
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
def game_over():
    """ End the game and tell the user it's over """
    print("        GAME OVER!")
    quit()

def you_won():
    """ End the game and tell the user he/she has won """
    print("        Y O U   H A V E  W O N ! !  Score = ", score)

def get_random_empty_cell(cells):
    """ Find the squares with value 0, these are the empty ones """
    ecls = []
    w, h = len(cells[0]), len(cells)
    for x in range(w):
        for y in range(h):
            if cells[x][y] == 0:
                ecls.append([x, y])
    rcn = random.randint(0, len(ecls) - 1)
    return ecls[rcn]

def add_random_number(cells):
    """ Add a random 1 or 2 to a random empty square """
    try:
        rndcell = get_random_empty_cell(cells)
        (cells[rndcell[0]])[rndcell[1]] = random.randint(1, 2)
        return cells
    except ValueError:
        game_over()

def merge_cells_in_trow(trow):
    """Move all cells>0 to the left, and fill up with zero's on the right.
    Add the merged cell values to the score"""
    srow = list(filter(lambda c: c != 0, trow ))
    ls = len(srow)
    m, l  = 0 , 1
    while l < ls:
        if srow[m] == srow[l]:
            srow[m] += 1
            if m == 10 :
                you_won()
            srow[l] = 0
            global score 
            score += 2**srow[m]
            m += 2
            l += 2
        else:
            m += 1
            l += 1
    srow += [0 for i in range(len(trow) - ls)]
    return srow

def move_cells (squares, dir):
    """Move all cells in the indicated direction and merge equally valued cells"""
    if dir not in dir_transp.keys() :
        return
    tempSqrs = squares[:]
    # in case of up or down, transpose
    if dir_transp[dir][0] == -1 :
        tempSqrs = transpose(squares)
    # in case of right or down, mirror
    if dir_transp[dir][1] == -1 :
        tempSqrs = mirror_v(tempSqrs)
        # print("tempSqrs mirror 1", tempSqrs)
    merged_cells = []
    for row in tempSqrs:
        merged_cells.append(merge_cells_in_trow(row))
    if dir_transp[dir][1] == -1 :
        # mirror back
        merged_cells = mirror_v(merged_cells)
        # print("merged_cells mirror 2", merged_cells)
    if dir_transp[dir][0] == -1 :
        # transpose back
        merged_cells = transpose(merged_cells)
    return merged_cells

# print(squares)

squares = add_random_number(squares)


def get_dir(inp):
    try:
        return transl_dir[inp]
    except KeyError:
        return "neutral"

def run_game(squares, inp=""):
    dir = get_dir(inp)
    clear_console()
    print_top_margin()
    
    # print("1", squares)
    if dir in dir_transp.keys() :
        squares = move_cells(squares, dir)
        # print("moved etc:", squares)
        squares = add_random_number(squares)
    print_left_margin()
    print_grid(squares)
    print_left_margin(0.5)
    print("Up = U, Down = D, Left = L, Right = R  | SCORE = ", score, " | > Direction =", dir)
    print_bottom_margin()
    return squares

keystr = "start"
run_game(squares)
while keystr != "X":
    keystr = input("?> (Druk X om af te breken)")
    if keystr in transl_dir.keys():
        squares = run_game(squares,keystr)
    else:
        squares = run_game(squares,"neutral")
quit()
