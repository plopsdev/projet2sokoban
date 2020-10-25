import time
import sys
import search
from search import *
from copy import deepcopy

class State:
    def __init__(self, grid, curr_pos, goal_pos, curr_ok):
        self.grid=grid
        self.curr_pos=curr_pos #position of the @
        self.goal_pos=goal_pos #array of the position(s) of .
        self.curr_ok=curr_ok #number of $ at the spot .

class Sokoban(Problem):
    def __init__(self, initial):
        #todo : ouverture des deux fichiers pour remplir grid et curr_pos
        self.initial = State(grid, curr_pos, goal_pos, 0) #note on peut calculer le nb de curr_ok selon le grid initial mais dans aucun des cas il y a un ok dès le début
    def actions(self, state):
        directions= [[1, 0], [-1, 0], [0, -1], [0, 1]]

        #filtres en fonction des murs

        for direction in directions:
            direction_checked[0] = state.curr_pos[0] + direction [0]
            direction_checked[1] = state.curr_pos[1] + direction [1]

            if state.grid[direction_checked[0]][direction_checked[1]] == "#":
                directions.remove(direction)
        
        #filtres en fonction des boites
        #note d'optimisation: réunir tous les if dans un seul for direction in directions
        for direction in directions:
            direction_checked[0] = state.curr_pos[0] + direction [0]
            direction_checked[1] = state.curr_pos[1] + direction [1]

            if state.grid[direction_checked[0]][direction_checked[1]] == "$": #todo: ajouter un indicateur pour communiquer à result qu'une boite à été déplacée -> ajouter une lettre 
                for side in directions: #check around the box
                    side_checked[0]=pos_checked[0]+side[0]
                    side_checked[1]=pos_checked[1]+side[1]

                    if (state.grid[side_checked[0]][direction_checked[1]] == "#" or "$") and (side == direction): #si une boite est présente ou un mur autour de la boite initial, vérifie que ca soit dans la meme direction, et annule l'action auquel cas
                        directions.remove(direction)

            
        
    def result(self, state, action):
        #todo
    def goal_test(self, state):
        #todo

