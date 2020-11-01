# Author Jonathan Miel 16013 & Charles Vandermies 15123

import time
import sys
from copy import deepcopy
from os import listdir, system
from search import *

# LEFT RIGHT UP DOWN
directions = [[0, -1], [0, 1], [-1, 0], [1, 0]]
global goal_pos

###############
# My function #
###############


#################
# Problem class #
#################

class Sokoban(Problem):
    def __init__(self, initial):

        pathInit = str(initial + ".init")
        pathGoal = str(initial + ".goal")
        boxes_pos = [] #Orginal position of boxes
        goal_pos = [] #Final supposed position of boxes
        
        with open(pathGoal, "r") as file:
            data_read = file.read()
            grid_go = data_read.split("\n")
            grid_go.pop(0)
            grid_go.pop()
            grid_go.pop()
            for i in range(0, len(grid_go)):
                grid_go[i] = grid_go[i][1 : len(grid_go[i])-1]

            i = 0
            for line in grid_go:
                for j in range(0, len(line)):
                    if line[j] == ".":
                        #Avatar
                        goal_pos.append((i, j))
                i+=1
                
        with open(pathInit, "r") as file:
            data_read = file.read()
            grid_in = data_read.split("\n")
            #Remove the first line and the two last ones
            grid_in.pop(0)
            grid_in.pop()
            grid_in.pop()
            #Truncate first and last collumn
            for i in range(0, len(grid_in)):
                grid_in[i] = grid_in[i][1 : len(grid_in[i])-1]

            curr_pos = (0,0) #Original position of the avatar
            #Read grid for important elem
            i = 0
            for line in grid_in:
                for j in range(0, len(line)):
                    if line[j] == "@":
                        #Avatar
                        curr_pos = (i, j)
                    elif line[j] == "$":
                        #Box
                        boxes_pos.append((i, j))
                i+=1

        initState = State(grid_in, boxes_pos, curr_pos)
        # Extend super init
        super().__init__(initState)

    def goal_test(self, state):
        for elem in goal_pos:
            if not elem in state.boxes_pos:
                return False
        return True
    
    def actions(self, state):
        direction_checked=[0, 0]
        movements=[]

        for direction in directions:
            direction_checked[0] = state.curr_pos[0] + direction[0]
            direction_checked[1] = state.curr_pos[1] + direction[1]

            if inBounds(state.grid, (direction_checked[0], direction_checked[1])) and (state.grid[direction_checked[0]][direction_checked[1]] == ' ' or (state.grid[direction_checked[0]][direction_checked[1]] == '$' and canPushBox(state.grid, state.curr_pos, (direction_checked[0],direction_checked[1])) and isPushingOK(state, direction, direction_checked[0], direction_checked[1]))):
                movements.append(direction)  

        return movements    

    def result(self, state, action):
        new_state = deepcopy(state)
        #Calculate new avatar pos
        new_state.curr_pos = (state.curr_pos[0] + action[0], state.curr_pos[1] + action[1])
        #Clear old pos in grid, update avatar pos in state
        print(new_state.grid[state.curr_pos[0]][state.curr_pos[1]])
        new_state.grid[state.curr_pos[0]] = new_state.grid[state.curr_pos[0]][:state.curr_pos[1]] + " " + new_state.grid[state.curr_pos[0]][state.curr_pos[1]+1:]
        print(new_state.grid)
        if(new_state.grid[new_state.curr_pos[0]][new_state.curr_pos[1]] == "$"):
            #Move box before updating avatar in grid
            for index in range(0, len(new_state.boxes_pos)):
                if (new_state.curr_pos[0], new_state.curr_pos[1]) == new_state.boxes_pos[index]:
                    #Calculate new coordinate
                    newX = action[0] + new_state.curr_pos[0]
                    newY = action[1] + new_state.curr_pos[1]
                    new_state.boxes_pos[index] = (newX, newY)
                    new_state.grid[newX] = new_state.grid[newX][:newY] + "$" + new_state.grid[newX][newY+1:]
        #Update avatar in grid
        new_state.grid[new_state.curr_pos[0]] = new_state.grid[new_state.curr_pos[0]][:new_state.curr_pos[1]] + "@" + new_state.grid[new_state.curr_pos[0]][new_state.curr_pos[1]+1:]
        return new_state

class State:
    def __init__(self, gridInit, boxes_pos, curr_pos):
        # Save state variable
        self.boxes_pos = boxes_pos
        self.curr_pos = curr_pos
        self.grid = gridInit

    def __str__(self):
        string = ""
        for l in self.grid:
            for c in l:
                string += c
            string += "\n"
        return string

    def __repr__(self):  # Full representation
        return str((self.curr_pos, self.boxes_pos, self.grid))

    def __eq__(self, other):
        return (other.grid == self.grid)

    def __lt__(self, node):
        return self.grid < node.grid

    def __hash__(self):
        return self.__str__().__hash__()

######################
# Auxiliary function #
######################

#Add a line of wall
def addALineOfWall(string, length):
    for i in range (0, length+2):
        string += "#"
    string += "\n"
    return string

#Check if position is inbound
def inBounds(grid, pos):
    return 0 <= pos[0] and pos[0] < len(grid) and 0 <= pos[1] and pos[1] < len(grid[0])

#Check if the state is a KO state
def isKOState(state, box):
    #Check direction in which i can push
    if box in goal_pos :
        # If box on goal state, it's never a KO state
        return False
    #Test LEFT AND RIGHT
    freedom = 0
    for x in range(0, 2):
        i = box[0] + directions[x][0]
        j = box[1] + directions[x][1]
        if inBounds(state.grid, (i, j)) and (state.grid[i][j] == " " or state.grid[i][j] == "@"):
            freedom += 1
    if freedom == 2:
        return False
    #Test LEFT AND RIGHT
    freedom = 0
    for x in range(2, 4):
        i = box[0] + directions[x][0]
        j = box[1] + directions[x][1]
        if inBounds(state.grid, (i, j)) and (state.grid[i][j] == " " or state.grid[i][j] == "@"):
            freedom += 1
    if freedom == 2:
        return False
    return False

# Check if pushing box will lead to a KO state
# Pre : box is pushable
def isPushingOK(state, dir, x, y):
    result = False
    state.grid[x] = state.grid[x][:y] + " " + state.grid[x][y+1:]
    newBoxX = x + dir[0]
    newBoxY = y + dir[1]
    state.grid[newBoxX] = state.grid[newBoxX][:newBoxY] + "$" + state.grid[newBoxX][newBoxY+1:]
    result = not isKOState(state, (newBoxX, newBoxY))
    state.grid[newBoxX] = state.grid[newBoxX][:newBoxY] + " " + state.grid[newBoxX][newBoxY+1:]
    state.grid[x] = state.grid[x][:y] + "$" + state.grid[x][y+1:]
    return result

#Check if two position are adjacent
def isAdjacent(posA, posB):
    distI = abs(posA[0] - posB[0])
    distJ = abs(posA[1] - posB[1])
    return (distI + distJ) < 2

#Check if char can push the box from this position
def canPushBox(grid, char, box):
    if isAdjacent(char, box):
        i = 2*box[0] - char[0]
        j = 2*box[1] - char[1]
        if inBounds(grid, (i, j)) and grid[i][j] == " ":
            return True
    return False

#Calculate the minimum position from the avatar to a box
def distFromBox(state):
    best = len(state.grid) + len(state.grid[0])
    for box in state.boxes_pos:
        best = min(best, (abs(box[0] - state.curr_pos[0]) + abs(box[1] - state.curr_pos[1])))
    return best

# Return the minimum hamilton distance to reach a goal
def boxGoalMinDistance(state, box):
    best = len(state.grid) + len(state.grid[0])
    for goal in goal_pos:
        best = min(best, (abs(goal[0] - box[0]) + abs(goal[1] - box[1])))
    return best

# Heuristic function
# Minimal value will be explored first !!!
def Heuristic(node):
    score = 0
    for box in node.state.boxes_pos:
        score += boxGoalMinDistance(node.state, box) * len(node.state.grid) # Passes everything
    score += distFromBox(node.state)
    return score

#####################
# Launch the search #
#####################

tic = time.process_time()
problem = Sokoban(sys.argv[1])
solution = astar_search(problem, Heuristic) #todo insérer ici une fonction heuristique h en paramètre
for n in solution.path():
    print(n.state)

#Afficher le temps d'exécution écoulé
toc = time.process_time()
print("Le programme s'est exécuté en "+str(toc-tic)+" secondes.")