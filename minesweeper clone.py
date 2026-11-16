import pygame as py
from random import *
import math
import time
import sys
sys.setrecursionlimit(5000)

BLACK = (0, 0, 0)

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800

TILE_COLOR = (210, 210, 210)
UNCLICKED_TILE_COLOR = (80, 80, 80)
BOARDER_COLOR = (240, 240, 240)

BOUNDARY = 2


def main():
    global SCREEN, TIME
    global NUMBER_COLS
    
    py.init()
    SCREEN = py.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    grid_sizes = dict([("beginner", [9, 9, 10]), ("intermediate", [16, 16, 40]), ("expert", [30, 16, 99]), ("evil", [30, 30, 250]), ("custom", "custom")])
    LOSE_SHIMMER_TIMER = -99999999 #used to track a lost state
    TIME = time.time()
    SCREEN.fill(BLACK)
    grid_data = None #grid metadata
    x,y,w,z,a,b = [None]*6
    r = None
    while grid_data == None:
        grid_data = grid_sizes.get(input("Difficulty (beginner, intermediate, expert, evil, or custom): ").lower())
        if grid_data == "custom":
            w = int(input("Width of the board?: "))
            h = int(input("Height of the board?: "))
            b = int(input("Number of mines?: "))
            grid_data = [w, h, b]
            print(grid_data)
            if (w > 35 or h > 35) and grid_data != [67,67,67]:
                print("The maximum supported board size is 35x35")
                grid_data = None
                    
        bomb_data = [] #[[0]*row]*col isn't working: once again python is screwing with my pointers in ways I cannot control explicitly. Great language!!!
        unclicked_tiles = [] #keeps track of which tiles are not revealed
        flagged_tiles = [] #0 = unflagged, 1 = flagged
        for i in range(grid_data[1]):
            row = []
            row2 = []
            row3 = []
            for j in range(grid_data[0]):
                row.append(0)
                row2.append(1)
                row3.append(0) #need a row3 due to ONCE MORE python being stupid with pointers
            bomb_data.append(row)
            flagged_tiles.append(row3)
            unclicked_tiles.append(row2)
        bomb_locations = []
        while len(bomb_locations) < min(grid_data[2], grid_data[0]*grid_data[1]): #place the mines
            x = randint(1, grid_data[1])
            y = randint(1, grid_data[0])
            if [x, y] not in bomb_locations:
                bomb_data[x-1][y-1] = 9 #0, ..., 8 used to represent tiles with 0..8 bombs, 9 is used to represent bombs
                bomb_locations.append([x,y])
        #easter_egg_boards using garbage custom grid data as flags for nonsensical boards

        EIGHT_LOCATE = []
        for i in range(grid_data[1]): #place the numbers
            for j in range(grid_data[0]):
                if bomb_data[i][j] != 9:
                    bomb_data[i][j] = count_bombs(bomb_data, i, j)
                    if bomb_data[i][j] == 8:
                        EIGHT_LOCATE.append([i,j])
        first_click = True
        block_size = 20 #magic number :(
        global FONT
        FONT = py.font.SysFont('consolas', block_size-4)
        #some funnies
        if grid_data[2] == grid_data[0]*grid_data[1]-1:
            draw_text(SCREEN, FONT, "LETS GO GAMBLING!", [WINDOW_WIDTH//2-300, 100], (255, 255, 255))
        if grid_data[2] == grid_data[0]*grid_data[1]:
            draw_text(SCREEN, FONT, "LETS GO DYING!", [WINDOW_WIDTH//2-300, 100], (255, 255, 255))
        if grid_data == [6, 9, 420]:
            print("codes for easter egg boards! Enter a custom board with these numbers to generate the easter egg board")
            print("8, 8, 88: crazy 8s!")
            print("67, 67, 67: very funny!")
        easter_egg_boards = dict([
            [(8, 8, 88), ([3,3,1], [[8,8,8],[8,9,8],[8,8,8]], "crazy 8s!")],
            [(67, 67, 67), ([6,7,1], [[6,7,6,7,6,7],[6,7,6,7,6,7],[6,7,6,7,6,7],[6,7,6,7,6,7],[6,7,6,7,6,7],[6,7,6,7,6,7],[6,7,6,7,9,7]], "very funny! now perish")],
            [(6,9,420), ([5, 6, 10], [[9,2,1,2,9],[1,2,9,3,1],[0,2,3,9,2],[1,2,9,3,2],[9,4,4,4,9],[2,9,9,9,2]],  ":^)")]
                ])
        EE = False
        if easter_egg_boards.get(tuple(grid_data)) is not None:
            EE = True
            if grid_data == [8,8,88]:
                EIGHT_LOCATE = [[0,0], [0,1], [0,2], [1,0], [1,2], [2,0], [2,1], [2,2]]
            E = easter_egg_boards.get(tuple(grid_data))
            print(E[2])
            grid_data = E[0]
            bomb_data = E[1]


        tile_coords = drawGrid(grid_data[0], grid_data[1], block_size)
        completed = False
         #flag if we're on an easter egg grid
        while not completed:
            PHASE = time.time()-TIME
            if first_click:
                TIMER_START = time.time()
                try:
                    BACK_UP
                except NameError:
                    BACK_UP = TIMER_START
            if LOSE_SHIMMER_TIMER < 0:
                py.draw.rect(SCREEN, (0,0,0), py.Rect(tile_coords[0][0][0], tile_coords[0][0][1]-50, 30, 30))
                draw_text(SCREEN, FONT, str(int(time.time()-TIMER_START)), [tile_coords[0][0][0], tile_coords[0][0][1]-50], (240, 40, 40))
                py.draw.rect(SCREEN, (0,0,0), py.Rect(tile_coords[::-1][0][::-1][0][0], tile_coords[0][0][1]-50, 30, 30))
                draw_text(SCREEN, FONT, str(grid_data[2]-sum([sum(r) for r in flagged_tiles])), [tile_coords[::-1][0][::-1][0][0], tile_coords[0][0][1]-50], (240, 40, 40))
            NUMBER_COLS = [TILE_COLOR, (40, 40, 170), (50, 160, 80), (180, 40, 40), (50, 30, 80), (75, 0, 20), (40, 90, 105), (50, 50, 50),
                           (190+40*math.sin(PHASE), 190+40*math.sin(PHASE+math.pi/3), 190+40*math.sin(PHASE+2*math.pi/3)), BLACK]
            for event in py.event.get():
                if event.type == py.QUIT:
                    quit()
                    py.sys.exit()
                if event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        r = findsquare(tile_coords)
                    if event.button == 2 and EE == False: #chording
                        coords = findsquare(tile_coords)
                        if coords != False:
                            a, b = coords
                            if unclicked_tiles[b][a] == 0 and count_flags(flagged_tiles, b, a) == bomb_data[b][a]:
                                for c in range(-1, 2):
                                    for d in range(-1, 2):
                                        try:
                                            if flagged_tiles[b+d][a+c] == 0 and a+c >= 0 and b+d >= 0:
                                                unclicked_tiles = clickSquare(a+c, b+d, block_size, tile_coords, bomb_data, unclicked_tiles, SCREEN)
                                                if bomb_data[b+d][a+c] == 9:
                                                    print("you lost!")
                                                    drawGrid(grid_data[0], grid_data[1], block_size, debug=bomb_data) #reveal the board
                                                    if LOSE_SHIMMER_TIMER < 0:
                                                        LOSE_SHIMMER_TIMER = time.time()
                                                        x, y = a+c, b+d
                                                        break
                                        except IndexError:
                                            pass
                                    if LOSE_SHIMMER_TIMER > 0:
                                        break
                    if event.button == 3 and EE == False:
                        r = False #prevents unintended behaviour by pressing both left and right
                        coords = findsquare(tile_coords)
                        if coords != False and unclicked_tiles[coords[1]][coords[0]] == 1:
                            w, z = coords
                            flagged_tiles[z][w] = 1-flagged_tiles[z][w]
                            if flagged_tiles[z][w] == 1:
                                py.draw.rect(SCREEN, (255,0,0), py.Rect(tile_coords[w][z][0]+block_size/3,
                                                tile_coords[w][z][1]+block_size/3,
                                                block_size/3,
                                                block_size/3))
                            else:
                                tile = py.Rect(tile_coords[w][z][0], tile_coords[w][z][1], block_size-2*BOUNDARY, block_size-2*BOUNDARY)
                                py.draw.rect(SCREEN, UNCLICKED_TILE_COLOR, tile, 0)#mark the flag and draw the tile
                if event.type == py.MOUSEBUTTONUP:
                    r_check = findsquare(tile_coords)
                    if r_check == r and r != False and LOSE_SHIMMER_TIMER < 0 and event.button == 1:
                        x, y = r
                        unclicked_tiles = clickSquare(x, y, block_size, tile_coords, bomb_data, unclicked_tiles, SCREEN, exclude = [])
                        if bomb_data[y][x] == 9: #if the player clicks on a mine
                            print("you lost!")
                            drawGrid(grid_data[0], grid_data[1], block_size, debug=bomb_data) #reveal the board
                            if LOSE_SHIMMER_TIMER < 0:
                                LOSE_SHIMMER_TIMER = time.time
                                first_click = False
            if LOSE_SHIMMER_TIMER > 0:
                py.draw.rect(SCREEN, (0,0,0), py.Rect(tile_coords[0][0][0], tile_coords[0][0][1]-50, 30, 30))
                draw_text(SCREEN, FONT, "X_X", [tile_coords[0][0][0], tile_coords[0][0][1]-50], (240, 40, 40))
                clickSquare(x, y, block_size, tile_coords, bomb_data, unclicked_tiles, SCREEN, exclude = [], color = (100+100*math.sin(PHASE*4), 0, 0)) #shimmer on the clicked mine
                if time.time()-LOSE_SHIMMER_TIMER > 3:
                    completed = True
            for EIGHT in EIGHT_LOCATE: #add the shimmer effect to the 8s
                if unclicked_tiles[EIGHT[1]][EIGHT[0]] == 0:
                    clickSquare(EIGHT[1], EIGHT[0], block_size, tile_coords, bomb_data, unclicked_tiles, SCREEN)
            py.display.update()
            if sum([sum(r) for r in unclicked_tiles]) == grid_data[2] and LOSE_SHIMMER_TIMER <0 and sum([sum(r) for r in unclicked_tiles]) < grid_data[0]*grid_data[1]: #the only unknown tiles are bombs
                print("you win! Final time: {0}".format(round(time.time()-BACK_UP), len(str(int(time.time()-TIMER_START)))+5))
                py.draw.rect(SCREEN, (0,0,0), py.Rect(tile_coords[0][0][0], tile_coords[0][0][1]-50, 30, 30))
                input("press enter to close")
                py.quit()
                completed = True
        completed = False



def draw_rect_centred(screen, colour, x, y, size):
    py.draw.rect(screen, colour, py.Rect(x-size//2, y-size//2, size, size), 1)

def count_bombs(array, x, y):
    T = 0
    for off_x in range(-1, 2):
        for off_y in range(-1, 2):
            try:
                if x+off_x >= 0 and y+off_y >= 0 and array[x+off_x][y+off_y] == 9:
                    T += 1
            except IndexError:
                pass
    return T

def count_flags(array, x, y):
    T = 0
    for off_x in range(-1, 2):
        for off_y in range(-1, 2):
            try:
                if x+off_x >= 0 and y+off_y >= 0 and array[x+off_x][y+off_y] == 1:
                    T += 1
            except IndexError:
                pass
    return T

def findsquare(tile_coords):
    x, y = py.mouse.get_pos()
    for i in range(len(tile_coords)):
        for j in range(len(tile_coords[i])):
            test_coords = tile_coords[i][j]
            if test_coords[0] <= x and x <= test_coords[2] and test_coords[1] <= y and y <= test_coords[3]:
                return i, j
    return False

def clickSquare(x, y, blockSize, tileCoords, bombData, unclickedTiles, Surface, exclude = [], color = []):
        if color == []:
            color = NUMBER_COLS[bombData[y][x]]
        unclickedTiles[y][x] = 0
        start_x = (WINDOW_WIDTH - x*blockSize)//2
        start_y = (WINDOW_HEIGHT - y*blockSize)//2
        cornerpos = [start_x, start_y]
        X, Y = cornerpos[0]+x*(blockSize),cornerpos[1]+y*(blockSize)
        tile = py.Rect(tileCoords[x][y][0], tileCoords[x][y][1], blockSize-2*BOUNDARY, blockSize-2*BOUNDARY)
        if bombData[y][x] == 9:
            py.draw.circle(SCREEN, color, [tileCoords[x][y][0]-BOUNDARY+blockSize/2,tileCoords[x][y][1]-BOUNDARY+blockSize/2], blockSize/math.sqrt(2*math.pi))
        if bombData[y][x] < 9:
            py.draw.rect(SCREEN, color, tile, 0)
            if bombData[y][x] > 0:  
                draw_text(SCREEN, FONT, str(bombData[y][x]), [tileCoords[x][y][0]+4, tileCoords[x][y][1]+1], (255, 255, 255))
        if bombData[y][x] == 0:
            for off_x in range(-1, 2):
                for off_y in range(-1, 2):
                    try:
                        if x+off_x >= 0 and y+off_y >= 0 and [x+off_x, y+off_y] not in exclude:
                            exclude.append([x, y])
                            unclickedTiles = clickSquare(x+off_x, y+off_y, blockSize, tileCoords, bombData, unclickedTiles, exclude)
                    except IndexError:
                        pass
        return unclickedTiles
        

def drawGrid(width, height, blockSize, debug = None): #pass bombdata in through debug var. to display full grid
    start_x = (WINDOW_WIDTH - width*blockSize)//2
    start_y = (WINDOW_HEIGHT - height*blockSize)//2
    cornerpos = [start_x, start_y]
    tile_coords = []
    for x in range(width):
        row = []
        for y in range(height):
            X, Y = cornerpos[0]+x*(blockSize),cornerpos[1]+y*(blockSize)
            row.append([X+BOUNDARY, Y+BOUNDARY, X+blockSize-BOUNDARY, Y+blockSize-BOUNDARY]) #tile coords
            rect = py.Rect(X, Y, blockSize, blockSize)
            tile = py.Rect(X+BOUNDARY, Y+BOUNDARY, blockSize-2*BOUNDARY, blockSize-2*BOUNDARY)
            py.draw.rect(SCREEN, BOARDER_COLOR, rect, BOUNDARY)
            py.draw.rect(SCREEN, UNCLICKED_TILE_COLOR, tile, 0)
            if debug is not None:
                if debug[y][x] == 8:
                    PHASE = time.time()-TIME
                    py.draw.rect(SCREEN, (
                        NUMBER_COLS[debug[y][x]][0]+40*math.sin(PHASE),
                        NUMBER_COLS[debug[y][x]][1]+40*math.sin(PHASE+math.pi/3),
                        NUMBER_COLS[debug[y][x]][2]+40*math.sin(PHASE+2*math.pi/3)
                        ), tile, 0)
                elif debug[y][x] == 9:
                    py.draw.rect(SCREEN, NUMBER_COLS[0], tile, 0)
                    py.draw.circle(SCREEN, NUMBER_COLS[debug[y][x]],
                                   [X+blockSize/2,Y+blockSize/2], blockSize/math.sqrt(2*math.pi))
                else:
                    py.draw.rect(SCREEN, NUMBER_COLS[debug[y][x]], tile, 0)
        tile_coords.append(row)
    return tile_coords

def draw_text(surface, font, text, coords, color):
    textSurface = font.render(text, True, color)
    surface.blit(textSurface, coords)

for i in range(3):
    print(" ")
print('''
Welcome to my minesweeper clone!
================================
Left click to clear a tile
Right click to flag a tile
Middle click on a cleared+flagged tile to chord!

================================

Top left is your time, top right is the number of flags you have left
REMEMBER: The goal is to clear all squares, not flag every mine!

================================

There are some goofy easter eggs that can be 
found by inputting particuarly silly numbers
for custom boards

Have fun!

================================


''')


main()
quit()
