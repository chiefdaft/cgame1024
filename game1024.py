#!/usr/bin/env python3
""" Console game of 1024
    Try to move the squares upwards, downwards, to the left or right
    to squares with the same value. These will merge and double their
    value. When you reach 1024 (2^10) you win the the game.
    """

import random
from random import choice

class Game1024:
    def __init__(self, rows, cols) -> None:
        self.rows = rows
        self.cols = cols
        self.squares = [[0] * cols for i in range(rows)]
        self.score= 0
        
        self.transl_dir = {
            "a": "left",
            "L": "left",
            "w": "up",
            "U": "up",
            "d": "right",
            "R": "right",
            "s": "down",
            "D": "down",
        }
        self.dir_transp = {
            "left": (1, 1),
            "right": (1, -1),
            "up": (-1, 1),
            "down": (-1, -1),
        }

    def transpose(self, mx):
        """Transpose a matrix, a list with lists"""
        # print("transpose",mx)
        mx_w, mx_h = len(mx[0]), len(mx)
        transResult = [[0] * mx_h for i in range(mx_w)]
        for a in range(mx_h):
            for b in range(mx_w):
                transResult[b][a] = mx[a][b]
        return transResult


    def mirror_v(self, mx):
        """Miror a matrix vertically"""
        w, h = len(mx[0]), len(mx)
        mirror_mx = [[0] * w for i in range(h)]
        for rowi in range(w):
            mirror_mx[rowi] = mx[rowi][::-1]
        return mirror_mx

    def end(self):
        quit()

    def over(self):
        """ End the game and tell the user it's over """
        self.end()

    def won(self):
        """ End the game and tell the user he/she has won """
        self.end()

    def get_random_empty_cell(self, cells):
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
            self.over()

    def add_random_number(self, cells):
        """ Add a random 1 or 2 to a random empty square """
        try:
            rndcell = self.get_random_empty_cell(cells)
            (cells[rndcell[0]])[rndcell[1]] = random.randint(1, 2)
            return cells
        except ValueError:
            self.over()

    def merge_cells_in_trow(self, trow):
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
                self.score += 2**srow[m]
                if m == 10:
                    self.won()
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


    def move_cells(self, dir):
        """Move all cells in the indicated direction and merge equally valued cells"""
        if dir not in self.dir_transp.keys():
            return
        temp_sqrs = self.squares
        # in case of up or down, transpose
        if self.dir_transp[dir][0] == -1:
            temp_sqrs = self.transpose(self.squares)
        # in case of right or down, mirror
        if self.dir_transp[dir][1] == -1:
            temp_sqrs = self.mirror_v(temp_sqrs)
        merged_cells = []
        for row in temp_sqrs:
            merged_cells.append(self.merge_cells_in_trow(row))
        if self.dir_transp[dir][1] == -1:
            # mirror back
            merged_cells = self.mirror_v(merged_cells)
        if self.dir_transp[dir][0] == -1:
            # transpose back
            merged_cells = self.transpose(merged_cells)
        return merged_cells

    def get_dir(self, inp):
        try:
            return self.transl_dir[inp]
        except KeyError:
            return "neutral"

    def step(self, dir):
        if dir not in self.dir_transp.keys():
            return self.squares
        self.squares = self.move_cells(dir)
        self.squares = self.add_random_number(self.squares)
        return self.squares

    def init(self):
        self.squares = self.add_random_number(self.squares)
        self.squares = self.add_random_number(self.squares)

