__author__ = 'Cyril de Vogelaere : 2814-11-00 & Thuin florian : 0656-11-00'

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

def readGridFromFile(Texte):
    with open(Texte, "r") as file:
        data_read = file.read()
        grid = data_read.split("\n")
        #Remove empty line
        grid.pop()
        #Remove last line
        grid.pop()
        #Remove first line
        grid.pop(0)
        #Truncate first and last collumn
        for i in range(0, len(grid)):
            grid[i] = grid[i][1 : len(grid[i])-1]
        return grid

# Read goal file and return a grid containing the goal_pos [(),()]
def readStateFromGoal(goal):

    grid = readGridFromFile(goal)
    goal_pos = [] #Orginal position of boxes
    i = 0
    for line in grid:
        for j in range(0, len(line)):
            if line[j] == ".":
                #Avatar
                goal_pos.append((i, j))
        i+=1
    return goal_pos

# Read init file and return a state containing the data
def readStateFromInit(init):
    with open(init, "r") as file:
        # Lecture du fichier
        grid = readGridFromFile(init)
        # Creation d'un tableau equivalent au probleme
        curr_pos = (0,0) #Original position of the avatar
        boxes_pos = [] #Orginal position of boxes
        #Read grid for important elem
        i = 0
        for line in grid:
            for j in range(0, len(line)):
                if line[j] == "@":
                    #Avatar
                    curr_pos = (i, j)
                elif line[j] == "$":
                    #Box
                    boxes_pos.append((i, j))
            i+=1
        print(grid)
    return State(grid, boxes_pos, curr_pos)



#################
# Problem class #
#################

class Sokoban(Problem):
    def __init__(self, init):
        # Extract state from file
        global goal_pos
        goal_pos = readStateFromGoal(init + ".goal")
        initState = readStateFromInit(init + ".init")
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

            if inBounds(state.grid, (direction_checked[0], direction_checked[1])):
                if state.grid[direction_checked[0]][direction_checked[1]] == ' ' or (state.grid[direction_checked[0]][direction_checked[1]] == '$' and boxPush(state.grid, state.curr_pos, (direction_checked[0],direction_checked[1])) and boxOk(state, direction, direction_checked)):
                    movements.append(direction)  

        return movements    

    def result(self, state, action):
        new_state = deepcopy(state)
        #Calculate new avatar pos
        new_state.curr_pos = (state.curr_pos[0] + action[0], state.curr_pos[1] + action[1])
        #Clear old pos in grid, update avatar pos in state
        new_state.grid[state.curr_pos[0]] = new_state.grid[state.curr_pos[0]][:state.curr_pos[1]] + " " + new_state.grid[state.curr_pos[0]][state.curr_pos[1]+1:]
        if(new_state.grid[new_state.curr_pos[0]][new_state.curr_pos[1]] == "$"):
            #Move box_pos before updating avatar in grid
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
def isKOState(state, box_pos):
    #Check direction in which i can push
    if box_pos in goal_pos :
        # If box_pos on goal state, it's never a KO state
        return False
    #Test LEFT AND RIGHT
    freedom = 0
    for x in range(0, 2):
        i = box_pos[0] + directions[x][0]
        j = box_pos[1] + directions[x][1]
        if inBounds(state.grid, (i, j)) and (state.grid[i][j] == " " or state.grid[i][j] == "@"):
            freedom += 1
    if freedom == 2:
        return False
    #Test LEFT AND RIGHT
    freedom = 0
    for x in range(2, 4):
        i = box_pos[0] + directions[x][0]
        j = box_pos[1] + directions[x][1]
        if inBounds(state.grid, (i, j)) and (state.grid[i][j] == " " or state.grid[i][j] == "@"):
            freedom += 1
    if freedom == 2:
        return False
    return False

# Check if pushing box_pos will lead to a KO state
# Pre : box_pos is pushable
def boxOk(state, direction, direction_checked):
    result = False
    side_checked=[0,0]
    state.grid[direction_checked[0]] = state.grid[direction_checked[0]][:direction_checked[1]] + " " + state.grid[direction_checked[0]][direction_checked[1]+1:]

    side_checked[0] = direction_checked[0] + direction[0]
    side_checked[1] = direction_checked[1] + direction[1]

    state.grid[side_checked[0]] = state.grid[side_checked[0]][:side_checked[1]] + "$" + state.grid[side_checked[0]][side_checked[1]+1:]
    result = not isKOState(state, (side_checked[0], side_checked[1]))

    state.grid[side_checked[0]] = state.grid[side_checked[0]][:side_checked[1]] + " " + state.grid[side_checked[0]][side_checked[1]+1:]
    state.grid[direction_checked[0]] = state.grid[direction_checked[0]][:direction_checked[1]] + "$" + state.grid[direction_checked[0]][direction_checked[1]+1:]
    
    return result

#Check if curr_pos can push the box_pos from this position
def boxPush(grid, curr_pos, box_pos):
    if abs(curr_pos[0] - box_pos[0])+ abs(curr_pos[1] - box_pos[1]) == 1:
        i = 2*box_pos[0] - curr_pos[0]
        j = 2*box_pos[1] - curr_pos[1]
        if inBounds(grid, (i, j)) and grid[i][j] == " ":
            return True
    return False

#Calculate the minimum position from the avatar to a box_pos
def distFromBox(state):
    best_pos = len(state.grid) + len(state.grid[0])
    for box_pos in state.boxes_pos:
        best_pos = min(best_pos, (abs(box_pos[0] - state.curr_pos[0]) + abs(box_pos[1] - state.curr_pos[1])))
    return best_pos

# Return the minimum hamilton distance to reach a goal
def boxGoalMinDistance(state, box_pos):
    best_pos = len(state.grid) + len(state.grid[0])
    for goal in goal_pos:
        best_pos = min(best_pos, (abs(goal[0] - box_pos[0]) + abs(goal[1] - box_pos[1])))
    return best_pos

# Heuristic function
# Minimal value will be explored first !!!
def Heuristic(node):
    score = 0
    for box_pos in node.state.boxes_pos:
        score += boxGoalMinDistance(node.state, box_pos) * len(node.state.grid) # Passes everything
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