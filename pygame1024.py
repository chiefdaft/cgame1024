#!/usr/bin/env python3
""" Pygame version of game of 1024
    Try to move the squares upwards, downwards, to the left or right
    to squares with the same value. These will merge and double their
    value. When you reach 1024 (2^10) you win the the game.
    """
import pygame
from pygame.locals import *
# Get the game1024 class rules
import game1024
import math

# define size of the grid
rows, cols = 4, 4
screen_width, screen_height = 620, 620
padding = 16
off_set_x, off_set_y = 24, 20
screen_bgcolor = (10, 10, 10)
screen_fgcolor = (250,250, 250)

# Define some console colors
W = pygame.Color(255,255,255,1)  # white (normal)
R = pygame.Color(255,0,0,1)  # red
G = pygame.Color(0,255,0,1)  # green
O = pygame.Color(255,127,0,1)  # orange
B = pygame.Color(0,0,255,1)  # blue
P = pygame.Color(128,0,128,1)  # purple
M = pygame.Color(255,0,255,1)  # magenta
C = pygame.Color(0,255,255,1)  # cyan

colors = [C, W, W, R, G, O, B, P, M, G, B]
cell_width = math.floor((screen_width - 2*padding - 2*cols*padding )/cols)
cell_height = math.floor((screen_height - 2*padding- 2*rows*padding )/rows)
empty_cell = pygame.Rect(2*padding, 2*padding, cell_width, cell_height)

class pygame1024(game1024.Game1024):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.dir_transp = {
            "left": (-1, 1),
            "right": (-1, -1),
            "up": (1, 1),
            "down": (1, -1),
        }
        self.rows, self.cols = rows, cols
        self.cells = []
        for x in range(cols):
            col = []
            for y in range(rows):
                # print(x,x*(cell_width + padding), y,y*(cell_height + padding))
                cell = empty_cell.copy()
                x0, y0  = x*(cell_width + padding)+ off_set_x, y*(cell_height + padding) + off_set_y
                # Add rectangles to the list of cells
                col.append({"x0y0": (x0, y0), "cell": cell.move(x0,y0), "bg_color": colors[0]})
            self.cells.append(col)
    
    def print_grid(self, background, font_game):
        for x in range(cols):
            for y in range(rows):
                val = self.squares[x][y]
                pygame.draw.rect(background, colors[val],self.cells[x][y]["cell"])
                if val > 0:
                    num = font_game.render(str(val), 1, (10, 10, 10))
                    numpos = num.get_rect()
                    numpos.centerx = self.cells[x][y]["cell"].centerx
                    numpos.centery = self.cells[x][y]["cell"].centery
                    background.blit(num, numpos)

    def run(self, dir, background, font_game):
        self.squares = self.step(dir)
        self.print_grid(background, font_game)
        return self.squares


def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Game1024')
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(screen_bgcolor)
    # Display some text on top of the screen
    
    font_file = pygame.font.match_font('gnutypewriter')
    font_screen = pygame.font.Font(font_file, 36)
    font_game = pygame.font.Font(font_file, 120)
    text = font_screen.render("Your score:", 1, screen_fgcolor)
    textpos = text.get_rect()
    textpos.left = off_set_x + 2*padding #background.get_rect().centerx
    background.blit(text, textpos)
    
    # Blit everything to the screen
    # screen.blit(background, (0, 0))
    
    game = pygame1024(rows, cols)
    game.add_random_number(game.squares)
    game.add_random_number(game.squares)

    game.print_grid(background, font_game)
    #pygame.draw.rect(background, (255,0,0), empty_cell)
    
    score_text = font_screen.render(str(game.score), 1, screen_fgcolor)
    score_pos = score_text.get_rect()
    score_pos.left = background.get_rect().centerx
    background.blit(score_text, score_pos)
    screen.blit(background, (0, 0))

    pygame.display.flip()

    dir = "0"
    wis_score = pygame.Rect(score_pos.left, 0, score_pos.width, score_pos.height)

    # Event loop
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    dir = "up"
                else:
                    if event.key == K_DOWN or event.key == K_s:
                        dir = "down"
                    else:
                        if event.key == K_LEFT or event.key == K_a:
                            dir = "left"
                        else:
                            if event.key == K_RIGHT or event.key == K_d:
                                dir = "right"
                            else:
                                dir = "0"

                if dir != "0":
                    game.squares = game.run(dir, background, font_game)
                    pygame.draw.rect(background, screen_bgcolor, wis_score)
                    score_text = font_screen.render(str(game.score), 1, screen_fgcolor)
                    score_pos = score_text.get_rect()
                    score_pos.left = background.get_rect().centerx
                    background.blit(score_text, score_pos)
                    screen.blit(background, (0, 0))
                    
                    pygame.display.flip()
                    wis_score = pygame.Rect(score_pos.left, 0, score_pos.width, score_pos.height)

    # screen.blit(background, (0, 0))
    # pygame.display.flip()
    


if __name__=="__main__":
    # call the main function
    main()