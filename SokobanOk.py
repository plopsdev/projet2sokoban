# Authors Jonathan Miel 16013 & Charles Vandermies 15123

import time
import sys
from copy import deepcopy
from os import listdir, system
from search import *

# LEFT RIGHT UP DOWN
directions = [[0, -1], [0, 1], [-1, 0], [1, 0]]
global goal_pos

#################
# Problem class #
#################

class State:
    def __init__(self, gridInit, boxes_pos, curr_pos):
        # Save state variable
        self.boxes_pos = boxes_pos
        self.curr_pos = curr_pos
        self.grid = gridInit

    def __str__(self):
        string = ""
        for i in range(0, len(self.grid[0])+2):
            string+="#"
        string+="\n"
        for l in self.grid:
            string+="#"
            for c in l:
                string += c
            string+="#"
            string += "\n"
        for i in range(0, len(self.grid[0])+2):
            string+="#"
        string+="\n"
        return string

    def __repr__(self):  # Full representation
        return str((self.curr_pos, self.boxes_pos, self.grid))

    def __eq__(self, other):
        return (other.grid == self.grid)

    def __lt__(self, node):
        return self.grid < node.grid

    def __hash__(self):
        return self.__str__().__hash__()


class Sokoban(Problem):
    def __init__(self, initial):
        global goal_pos
        #Pour run depuis shell vers dossier spécifique, ajouter "./benchsGiven/" + aux deux path ci-dessous
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

        self.initial = State(grid_in, boxes_pos, curr_pos)

    def goal_test(self, state): #counts if there all the box positions correspond to the goal position, compares it to goal_pos size
        ok=0

        for box_pos in state.boxes_pos:
            if box_pos in goal_pos:
                ok+=1

        return ok==len(goal_pos)
    
    def actions(self, state):
        direction_checked=[0, 0]
        movements=[]

        for direction in directions: #check every direction 
            direction_checked[0] = state.curr_pos[0] + direction[0]  #update direction checked based on direction
            direction_checked[1] = state.curr_pos[1] + direction[1]

            if inBounds(state.grid, (direction_checked[0], direction_checked[1])): #checks if in the puzzle area
                if state.grid[direction_checked[0]][direction_checked[1]] == ' ' or (state.grid[direction_checked[0]][direction_checked[1]] == '$' and boxPush(state.grid, state.curr_pos, (direction_checked[0],direction_checked[1])) and boxOk(state, direction, direction_checked)):
                    movements.append(direction) #update an array of possible movement given the state

        return movements    

    def result(self, state, action):
        new_state = deepcopy(state)
        new_state.curr_pos = (state.curr_pos[0] + action[0], state.curr_pos[1] + action[1])
        new_state.grid[state.curr_pos[0]] = new_state.grid[state.curr_pos[0]][:state.curr_pos[1]] + " " + new_state.grid[state.curr_pos[0]][state.curr_pos[1]+1:] #replace the curr_pos before moving with blank

        if(new_state.grid[new_state.curr_pos[0]][new_state.curr_pos[1]] == "$"):

            for index in range(0, len(new_state.boxes_pos)):
                side_checked=[0, 0]

                if (new_state.curr_pos[0], new_state.curr_pos[1]) == new_state.boxes_pos[index]:
                    side_checked[0] = new_state.curr_pos[0] + action[0] #update side checked
                    side_checked[1] = new_state.curr_pos[1] + action[1]
                    new_state.boxes_pos[index] = (side_checked[0], side_checked[1])
                    new_state.grid[side_checked[0]] = new_state.grid[side_checked[0]][:side_checked[1]] + "$" + new_state.grid[side_checked[0]][side_checked[1]+1:]

        new_state.grid[new_state.curr_pos[0]] = new_state.grid[new_state.curr_pos[0]][:new_state.curr_pos[1]] + "@" + new_state.grid[new_state.curr_pos[0]][new_state.curr_pos[1]+1:] #Update curr_pos
        return new_state



######################
# Auxiliary function #
######################

def inBounds(grid, pos): #check if pos is in the area of the puzzle
    return 0 <= pos[0] and pos[0] < len(grid) and 0 <= pos[1] and pos[1] < len(grid[0])

def isNok(state, box_pos):
    if box_pos in goal_pos : #if the destination is a goal, it's a ok state
        return False
    
    possibility = 0
    direction_checked=[0,0]
    for index in range(0, 2): #check horizontal directions
        direction_checked[0] = box_pos[0] + directions[index][0]
        direction_checked[1] = box_pos[1] + directions[index][1]

        if inBounds(state.grid, (direction_checked[0], direction_checked[1])) and (state.grid[direction_checked[0]][direction_checked[1]] == " " or state.grid[direction_checked[0]][direction_checked[1]] == "@"):
            possibility += 1
    if possibility == 2:
        return False
    
    possibility = 0
    for index in range(2, 4): #check vertical directions
        direction_checked[0] = box_pos[0] + directions[index][0]
        direction_checked[1] = box_pos[1] + directions[index][1]
        if inBounds(state.grid, (direction_checked[0], direction_checked[1])) and (state.grid[direction_checked[0]][direction_checked[1]] == " " or state.grid[direction_checked[0]][direction_checked[1]] == "@"):
            possibility += 1
    if possibility == 2:
        return False
    return False


def boxOk(state, direction, direction_checked): #check if the result of the pushed box leads to a deadlock
    result = False
    side_checked=[0,0]
    state.grid[direction_checked[0]] = state.grid[direction_checked[0]][:direction_checked[1]] + " " + state.grid[direction_checked[0]][direction_checked[1]+1:]

    side_checked[0] = direction_checked[0] + direction[0]
    side_checked[1] = direction_checked[1] + direction[1]

    state.grid[side_checked[0]] = state.grid[side_checked[0]][:side_checked[1]] + "$" + state.grid[side_checked[0]][side_checked[1]+1:]
    result = not isNok(state, (side_checked[0], side_checked[1]))

    state.grid[side_checked[0]] = state.grid[side_checked[0]][:side_checked[1]] + " " + state.grid[side_checked[0]][side_checked[1]+1:]
    state.grid[direction_checked[0]] = state.grid[direction_checked[0]][:direction_checked[1]] + "$" + state.grid[direction_checked[0]][direction_checked[1]+1:]
    
    return result

def boxPush(grid, curr_pos, box_pos): #check if it's possible to push the box
    if abs(curr_pos[0] - box_pos[0])+ abs(curr_pos[1] - box_pos[1]) == 1: #check if the box is adjacent

        if inBounds(grid, (2*box_pos[0] - curr_pos[0], 2*box_pos[1] - curr_pos[1])) and grid[2*box_pos[0] - curr_pos[0]][2*box_pos[1] - curr_pos[1]] == " ":
            return True

    return False

def distFromBox(state):
    best_pos = len(state.grid) + len(state.grid[0])
    for box_pos in state.boxes_pos:
        best_pos = min(best_pos, (abs(box_pos[0] - state.curr_pos[0]) + abs(box_pos[1] - state.curr_pos[1])))
    return best_pos

def hamiltonDistance(state, box_pos):
    best_pos = len(state.grid) + len(state.grid[0])
    for goal in goal_pos:
        best_pos = min(best_pos, (abs(goal[0] - box_pos[0]) + abs(goal[1] - box_pos[1])))
    return best_pos

def Heuristic(node):
    score = 0
    for box_pos in node.state.boxes_pos:
        score += hamiltonDistance(node.state, box_pos) * len(node.state.grid)
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