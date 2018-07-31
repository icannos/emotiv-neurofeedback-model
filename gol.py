from tkinter import *
from random import randint
from time import sleep

# --------GAME OF LIFE--------


# ----Parameters

grid_size = 250  # number of blocks on the grid
block_size = 5  # size of a block (pixels)

dt = 5  # pause duration
step = 10  # pause duration increase / decrease step size

cell_color = 'pink' # Alive
cell_skeleton_color = 'gray' # Skeletons
background_color = 'white'

DeathLonelyness = 2
DeathTooMuch = 4
Spawn = 3
stepbystep = 0

# ------- States
global begin
begin = 0


# ----Functions

def init_grid(grid):
    "Intializes the grid with random values."
    global begin
    for i in range(0, grid_size):
        for j in range(0, grid_size):
            grid[i][j] = 0

    begin = 0


def numb_neighbours(i, j, grid):
    """Returns the number of alive niehgbours of the cell (i,j)."""
    res = 0
    for k in range(-1, 2):
        for l in range(-1, 2):
            if grid[(i + k) % grid_size][(j + l) % grid_size] == 1:
                res += 1
    if grid[i][j] == 1: res -= 1  # in case the center is counted

    return res


def update(grid, grid_cpy):
    """Updates the grid, applying death and birth condition."""
    for i in range(grid_size):  # copies the grid
        for j in range(grid_size):
            grid_cpy[i][j] = grid[i][j]

    for i in range(grid_size):
        for j in range(grid_size):
            nb_neighb = numb_neighbours(i, j, grid_cpy)  # use the grid copy !

            if (grid_cpy[i][j] == 0) and nb_neighb == Spawn:  # birth rule
                grid[i][j] = 1
            elif grid_cpy[i][j] and (nb_neighb < DeathLonelyness or DeathTooMuch < nb_neighb):  # death rules
                grid[i][j] = 2


def animationLoop(grid, grid_cpy):
    """Renders the blocks."""
    global dt
    global begin

    if begin:
        update(grid, grid_cpy)
        can.delete(ALL)

        posx = 0  # x coordinate of the drawing cursor
        posy = 0  # y coordinate of the drawing cursor
        for i in range(grid_size):
            posx = 0
            for j in range(grid_size):
                if grid[i][j] == 1:
                    can.create_rectangle(posx, posy, posx + block_size, posy + block_size, fill=cell_color)
                if grid[i][j] == 2:
                    can.create_rectangle(posx, posy, posx + block_size, posy + block_size, fill=cell_skeleton_color)
                posx += block_size  # moves the cursor for the next block
            posy += block_size  # new line

        if not stepbystep:
            root.after(dt, animationLoop, grid, grid_cpy)


    else:
        # sleep(0.1)
        can.delete(ALL)

        posx = 0  # x coordinate of the drawing cursor
        posy = 0  # y coordinate of the drawing cursor
        for i in range(grid_size):
            posx = 0
            for j in range(grid_size):
                if grid[i][j] == 1:
                    can.create_rectangle(posx, posy, posx + block_size, posy + block_size, fill=cell_color)
                if grid[i][j] == 2:
                    can.create_rectangle(posx, posy, posx + block_size, posy + block_size, fill=cell_skeleton_color)
                posx += block_size  # moves the cursor for the next block
            posy += block_size  # new line


        root.after(5, animationLoop, grid, grid_cpy)


# ----Keyboard events

def reset(event=0):
    """Resets the grid."""
    global grid
    init_grid(grid)


def start(event):
    """Resets the grid."""
    global begin
    begin = 1


def faster(event):
    """Accelerates the animation."""
    global dt
    if dt - step > 1:
        dt -= step
    else:
        dt = 1


def slower(event):
    """Slows the animation."""
    global dt
    dt += step

def togglestepbystep(event):
    """Slows the animation."""
    global stepbystep
    if stepbystep == 0:
        stepbystep = 1
    else:
        stepbystep = 0
        root.after(dt, animationLoop, grid, grid_cpy)

def step(event):
    if stepbystep == 1:
        root.after(dt, animationLoop, grid, grid_cpy)


def click(event):
    global grid
    global grid_cpy
    if not begin:
        grid[event.y // block_size][event.x // block_size] = 1
        grid_cpy[event.y // block_size][event.x // block_size] = 1


def updateDeathTooMuch(event):
    w = event.widget

    global DeathTooMuch
    DeathTooMuch = int(w.get(ANCHOR))


def updateDeathLonelyness(event):
    w = event.widget
    global DeathLonelyness
    DeathLonelyness = int(w.get(ANCHOR))


def updateSpawn(event):
    w = event.widget

    global Spawn
    Spawn = int(w.get(ANCHOR))


# ----Initialization

grid = [[0 for j in range(grid_size)] for i in range(grid_size)]
grid_cpy = [[0 for j in range(grid_size)] for i in range(grid_size)]

root = Tk()
root.title("Game of life")

can = Canvas(root, height=grid_size * block_size, width=grid_size * block_size, bg=background_color)
frame = Frame(root, width=250 * 5, height=300)
frame.pack(side=LEFT)

# ----Controle

LabelSpawn = Label(frame, text="Nombre de voisins pour naître")
LabelSpawn.pack()

SpawnRules = Listbox(frame, selectmode=SINGLE)
SpawnRules.insert(0, 1)
SpawnRules.insert(1, 2)
SpawnRules.insert(2, 3)
SpawnRules.insert(3, 4)
SpawnRules.insert(4, 5)
SpawnRules.insert(5, 6)
SpawnRules.insert(6, 7)
SpawnRules.insert(7, 8)
SpawnRules.pack()

LabelDeathLonely = Label(frame, text="Nombre de voisins min pour survivre")
LabelDeathLonely.pack()

DeathRulesLonelyness = Listbox(frame, selectmode=SINGLE)
DeathRulesLonelyness.insert(0, 0)
DeathRulesLonelyness.insert(1, 1)
DeathRulesLonelyness.insert(2, 2)
DeathRulesLonelyness.insert(3, 3)
DeathRulesLonelyness.insert(4, 4)
DeathRulesLonelyness.insert(5, 5)
DeathRulesLonelyness.insert(6, 6)
DeathRulesLonelyness.insert(7, 7)
DeathRulesLonelyness.insert(8, 8)
DeathRulesLonelyness.pack()

LabelDeathTooMuch = Label(frame, text="Nombre de voisins max pour survivre")
LabelDeathTooMuch.pack()

DeathRulesTooMuch = Listbox(frame, selectmode=SINGLE)
DeathRulesTooMuch.insert(0, 0)
DeathRulesTooMuch.insert(1, 1)
DeathRulesTooMuch.insert(2, 2)
DeathRulesTooMuch.insert(3, 3)
DeathRulesTooMuch.insert(4, 4)
DeathRulesTooMuch.insert(5, 5)
DeathRulesTooMuch.insert(6, 6)
DeathRulesTooMuch.insert(7, 7)
DeathRulesTooMuch.insert(8, 8)
DeathRulesTooMuch.pack()

# ---- Binding actions

DeathRulesLonelyness.bind("<<ListboxSelect>>", updateDeathLonelyness)
DeathRulesTooMuch.bind("<<ListboxSelect>>", updateDeathTooMuch)
SpawnRules.bind("<<ListboxSelect>>", updateSpawn)

root.bind("<r>", reset)
root.bind("<f>", faster)
root.bind("<s>", slower)

root.bind("<Return>", start)
root.bind("<b>", start)

root.bind("<p>", togglestepbystep)
root.bind("<n>", step)

can.bind("<Button-1>", click)

can.focus_set()
can.pack()
animationLoop(grid, grid_cpy)

print("----Game Of Life----")
print(" Press Enter to start.")
print(" Press R to reset.")
print(" Press P to toggle stepbystep mode.")
print(" Press N to go process next step when in stepbystep mode")
print(" Press F to increase the animation speed.")
print(" press S to decrease the animation speed.")

reset()
root.mainloop()
