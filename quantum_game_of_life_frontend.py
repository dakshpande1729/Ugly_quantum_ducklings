import pygame, copy, math, random
import numpy as np
import argparse
import json

from dead_and_alive_back import DSQGOL, SQGOL, liveliness

pygame.init()

pixel_size = 9
lw = 4
board_width = 500
board_height = 500
board_interspace = 50
Y_LIMIT = board_width // pixel_size
X_LIMIT = board_height // pixel_size
ALIVE = np.array([1,0])
DEAD = np.array([0,1])
SUPERPOSITION_UP_LIMIT_ARG = 'sp_up'
SUPERPOSITION_UP_LIMIT_VAL = 0.51
SUPERPOSITION_DOWN_LIMIT_ARG = 'sp_down'
SUPERPOSITION_DOWN_LIMIT_VAL = 0.48
FILE_ARG = 'json'

#Update every 2ms
REFRESH = 2
TARGET_FPS = 60

class Grid():
    def __init__(self, *args, **kwargs):
        self.grid = [[DEAD for i in range(Y_LIMIT)] for i in range(X_LIMIT)]

    def setCell(self, x, y, stat):
        self.grid[x][y] = stat

    def getCell(self, x, y):
        return self.grid[x][y]

    def getNeighboursAround(self, x, y):
        neighbors = []

        for sub_x in range(3):
            row = []

            for sub_y in range(3):
                actual_x = x - 1 + sub_x
                if actual_x < 0:
                    actual_x = X_LIMIT + actual_x
                elif actual_x >= X_LIMIT:
                    actual_x -= X_LIMIT

                actual_y = y - 1 + sub_y
                if actual_y < 0:
                    actual_y = Y_LIMIT + actual_y
                elif actual_y >= Y_LIMIT:
                    actual_y -= Y_LIMIT

                cell = self.getCell(actual_x, actual_y)

                row.append(np.array(cell))

            neighbors.append(np.array(row))

        return neighbors

    def countNeighbours(self, x, y):
        neighbours = self.getNeighboursAround(x,y)
        return liveliness(neighbours)

        count = 0
        for x in range(3):
            for y in range(3):
                if x == 1 and y == 1:
                    continue
                count += 1 if (neighbours[x][y] == np.array([0.,1.])).all() else 0

        return count

class debugText():
    def __init__(self, screen, clock, *args, **kwargs):
        self.screen = screen
        self.clock = clock
        self.font = pygame.font.SysFont("Monospaced", 20)

    def printText(self):
        label_frameRate = self.font.render("FPS: " + str(self.clock.get_fps()), 1, (255,255,255))
        self.screen.blit(label_frameRate, (8, 22))

    def update(self, *args, **kwargs):
        self.screen = kwargs.get("screen",self.screen)
        self.clock = kwargs.get("clock",self.clock)

def init_grid_random(sp_up_limit,
                     sp_down_limit,
                     grid,
                     background,
                     grid2,
                     background2,
                     grid_fully_quantum,
                     background_fully_quantum):
    for x in range(X_LIMIT):
        for y in range(Y_LIMIT):
            cell = random_cell(sp_up_limit, sp_down_limit)
            grid.setCell(x, y, cell)
            drawSquare(background, x, y, cell)

            grid_fully_quantum.setCell(x, y, cell)
            drawSquare(background_fully_quantum, x, y, cell)

            if cell[1] >= 0.5:
                grid2.setCell(x, y, DEAD)
                drawSquareClassic(background2, x, y)
            else:
                grid2.setCell(x, y, ALIVE)
                drawSquareClassic(background2, x, y)

def init_grid_file(file_path,
                   grid,
                   background,
                   grid2,
                   background2,
                   grid_fully_quantum,
                   background_fully_quantum):
    with open(file_path) as json_file:
        data = json.load(json_file)

        row_inc = len(data) // 2
        column_inc = len(data[0]) // 2

        grid_x_inc = X_LIMIT // 2
        grid_y_inc = Y_LIMIT // 2

        for r, row in enumerate(data):
            for c, elem in enumerate(row):
                cell = json_cell(elem)
                final_x = grid_x_inc - column_inc + c
                final_y = grid_y_inc - row_inc + r

                grid.setCell(final_x, final_y, cell)
                drawSquare(background, final_x, final_y, cell)

                if cell[1] >= 0.5:
                    grid2.setCell(final_x, final_y, DEAD)
                    drawSquareClassic(background2, final_x, final_y)
                else:
                    grid2.setCell(final_x, final_y, ALIVE)
                    drawSquareClassic(background2, final_x, final_y)

def json_cell(a):
    b = math.sqrt(1 - a**2)
    return np.array([a,b])

def random_cell(up_limit, down_limit):
    a = random.random()
    b = math.sqrt(1 - a**2)
    if b >= up_limit:
        b = 1.
        a = 0.
    elif b <= down_limit:
        b = 0.
        a = 1.

    return np.array([a,b])

def drawSquare(background, x, y, array):
    #Cell colour
    value = 255.0 - np.floor((array[1]**2)*255)
    colour = value, value, value
    pygame.draw.rect(background, colour, (x * pixel_size, y * pixel_size, pixel_size, pixel_size), lw)

def drawBlankSpace(background, x, y):
    #Random cell colour
    colour = 40,40,40
    pygame.draw.rect(background, colour, (x * pixel_size, y * pixel_size, pixel_size, pixel_size))

def drawSquareClassic(background, x, y):
    colour = 255, 255, 255
    pygame.draw.rect(background, colour, (x * pixel_size, y * pixel_size, pixel_size, pixel_size), lw)

def main(sp_up_limit, sp_down_limit, file_path):
    print(file_path)
    screen = pygame.display.set_mode((2*board_width+board_interspace, 2*board_height+board_interspace))

    background_Final = pygame.Surface(screen.get_size())

    rect_classical = pygame.Rect(0,0,board_width,board_height)
    background_classical = background_Final.subsurface(rect_classical)
    background_classical = background_classical.convert()
    background_classical.fill((0, 0, 0))

    rect_interspace = pygame.Rect(board_width+board_interspace,0,board_interspace,board_height)
    interspace = background_Final.subsurface(rect_interspace)
    interspace = interspace.convert()
    interspace.fill((0, 0, 0))

    for x in range(0, board_interspace // pixel_size):
        for y in range(Y_LIMIT):
            drawBlankSpace(interspace, x, y)

    rect_quantum = pygame.Rect(board_width+board_interspace,0,board_width,board_height)
    background_quantum = background_Final.subsurface(rect_quantum)
    background_quantum = background_quantum.convert()
    background_quantum.fill((0, 0, 0))

    rect_interspace_horizontal = pygame.Rect(0,board_height,2*board_width+board_interspace,board_interspace)
    interspace_horizontal = background_Final.subsurface(rect_interspace_horizontal)
    interspace_horizontal = interspace_horizontal.convert()
    interspace_horizontal.fill((0, 0, 0))

    for x in range(0, (2*board_width+board_interspace) // pixel_size):
        for y in range(0, board_interspace // pixel_size):
            drawBlankSpace(interspace_horizontal, x, y)

    rect_fully_quantum = pygame.Rect(0,0,board_width,board_height)
    background_fully_quantum = background_Final.subsurface(rect_quantum)
    background_fully_quantum = background_fully_quantum.convert()
    background_fully_quantum.fill((0, 0, 0))

    clock = pygame.time.Clock()

    isActive = True
    actionDown = False

    final = pygame.time.get_ticks()
    grid_quantum = Grid()
    grid_classical = Grid()
    grid_fully_quantum = Grid()
    debug = debugText(screen, clock)

    #Create the orginal grid pattern randomly
    if file_path is None:
        init_grid_random(sp_up_limit,
                         sp_down_limit,
                         grid_quantum,
                         background_quantum,
                         grid_classical,
                         background_classical,
                         grid_fully_quantum,
                         background_fully_quantum)
    else:
        init_grid_file(file_path,
                       grid_quantum,
                       background_quantum,
                       grid_classical,
                       background_classical,
                       grid_fully_quantum,
                       background_fully_quantum)

    screen.blit(background_classical, (0, 0))
    screen.blit(interspace, (board_width, 0))
    screen.blit(background_quantum, (board_width+board_interspace, 0))
    screen.blit(interspace_horizontal, (0, board_height))
    screen.blit(background_quantum, (board_width/2+board_interspace/2, board_height+board_interspace))
    pygame.display.flip()

    while isActive:
        clock.tick(TARGET_FPS)
        newgrid_quantum = Grid()
        newgrid_classical = Grid()
        newgrid_fully_quantum = Grid()

        if pygame.time.get_ticks() - final > REFRESH:
            background_quantum.fill((0, 0, 0))
            background_classical.fill((0, 0, 0))

            for x in range(0, X_LIMIT):
                for y in range(0, Y_LIMIT):
                    subgrid = grid_quantum.getNeighboursAround(x, y)
                    newgrid_quantum.setCell(x, y, SQGOL(subgrid))
                    drawSquare(background_quantum, x, y, newgrid_quantum.getCell(x,y))
					#Classic game of life
                    if (grid_classical.getCell(x, y) == ALIVE).all():
                        count = grid_classical.countNeighbours(x, y)
                        if count < 2:
                            newgrid_classical.setCell(x, y, DEAD)

                        elif count <= 3:
                            newgrid_classical.setCell(x, y, ALIVE)
                            drawSquareClassic(background_classical, x, y)

                        elif count >= 4:
                            newgrid_classical.setCell(x, y, DEAD)
                    else:
                        if grid_classical.countNeighbours(x, y) == 3:
                            newgrid_classical.setCell(x, y, ALIVE)
                            drawSquareClassic(background_classical, x, y)

                    subgrid_fully_quantum = grid_fully_quantum.getNeighboursAround(x, y)
                    newgrid_fully_quantum.setCell(x, y, DSQGOL(subgrid_fully_quantum))
                    drawSquare(background_fully_quantum, x, y, newgrid_fully_quantum.getCell(x,y))

            final = pygame.time.get_ticks()

        else:
            newgrid_quantum = grid_quantum
            newgrid_classical = grid_classical
            newgrid_fully_quantum = grid_fully_quantum

        debug.update()

        actionDown = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isActive = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                actionDown = True

                while actionDown:
                    x = pygame.mouse.get_pos()[0] // pixel_size
                    y = pygame.mouse.get_pos()[1] // pixel_size
                    newgrid_classical.setCell(x, y, ALIVE)
                    newgrid_quantum.setCell(x,y,random_cell(sp_up_limit, sp_down_limit))
                    newgrid_fully_quantum.setCell(x,y,random_cell(sp_up_limit, sp_down_limit))

                    drawSquareClassic(background_classical, x, y)
                    drawSquare(background_quantum, x, y, newgrid_quantum.getCell(x,y))
                    # drawSquare for fully quantum version left

                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONUP:
                            actionDown = False

                    screen.blit(background_classical, (0, 0))
                    screen.blit(background_quantum, (board_width+100, 0))
                    pygame.display.flip()

        #Draws the new grid
        grid_quantum = newgrid_quantum
        grid_classical = newgrid_classical
        grid_fully_quantum = newgrid_fully_quantum

        #Updates screen
        screen.blit(background_classical, (0, 0))
        screen.blit(interspace, (board_width, 0))
        screen.blit(background_quantum, (board_width+board_interspace, 0))
        screen.blit(interspace_horizontal, (0, board_height))
        screen.blit(background_fully_quantum, (board_width/2+board_interspace/2, board_height+board_interspace))
        debug.update()
        debug.printText()
        pygame.display.flip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Quantum Game of Life')
    parser.add_argument('--{}'.format(SUPERPOSITION_UP_LIMIT_ARG),
                        type=float,
                        default=SUPERPOSITION_UP_LIMIT_VAL,
                        help='Superposition UP limit (default: {})'.format(SUPERPOSITION_UP_LIMIT_VAL))
    parser.add_argument('--{}'.format(SUPERPOSITION_DOWN_LIMIT_ARG),
                        type=float,
                        default=SUPERPOSITION_DOWN_LIMIT_VAL,
                        help='Superposition DOWN limit (default: {})'.format(SUPERPOSITION_DOWN_LIMIT_VAL))
    parser.add_argument('--{}'.format(FILE_ARG),
                        help='Path to JSON file with pre-configured seed',
                        default=None)
    args = vars(parser.parse_args())

    main(args[SUPERPOSITION_UP_LIMIT_ARG],
         args[SUPERPOSITION_DOWN_LIMIT_ARG],
         args[FILE_ARG])