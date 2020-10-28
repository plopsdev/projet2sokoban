import time
import sys
import search
from search import *
from copy import deepcopy

class State:
    def __init__(self, grid, curr_pos, goal_pos, boxes_pos, curr_ok):
        self.grid=grid
        self.curr_pos=curr_pos #position of the @
        self.goal_pos=goal_pos #tuple of the position(s) of .
        self.curr_ok=curr_ok #number of $ at the spot .
        self.boxes_pos=boxes_pos

class Sokoban(Problem):
    def __init__(self, initial):
        #todo : ouverture des deux fichiers pour remplir grid, curr_pos et goal_pos
        self.initial = State(grid, curr_pos, goal_pos, boxes_pos, 0) #note on peut calculer le nb de curr_ok selon le grid initial mais dans aucun des cas il y a un ok dès le début
    
    def goal_test(self, state):
        return state.curr_ok == len(state.goal_pos)
    
    def actions(self, state):
        directions= [[1, 0], [-1, 0], [0, -1], [0, 1]] #DOWN UP LEFT RIGHT
        direction_checked=[0, 0]

        for direction in directions:
            direction_checked[0] = state.curr_pos[0] + direction [0]
            direction_checked[1] = state.curr_pos[1] + direction [1]

            if state.grid[direction_checked[0]][direction_checked[1]] == "#": #filtres en fonction des murs
                directions.remove(direction)

            if state.grid[direction_checked[0]][direction_checked[1]] == "$": #todo: ajouter un indicateur pour communiquer à result qu'une boite à été déplacée -> ajouter une lettre 
                side_checked=[0, 0]

                for side in directions: #check around the box
                    side_checked[0]=direction_checked[0]+side[0]
                    side_checked[1]=direction_checked[1]+side[1]

                    if (state.grid[side_checked[0]][direction_checked[1]] == "#" or "$") and (side == direction): #si une boite est présente ou un mur autour de la boite initial, vérifie que ca soit dans la meme direction, et annule l'action auquel cas
                        directions.remove(direction)

        return directions
        
    def result(self, state, action):
        #si la nouvelle position du personnage coincide avec la position d'une caisse, c'est que ce déplacement a été validée, il s'agit donc de la translater dans le même sens
        new_state = deepcopy(state)
        
        new_state.grid[state.curr_pos[0]][state.curr_pos[1]]=" " #remplace le slot avant déplacement par du rien

        new_state.curr_pos[0]=state.curr_pos[0]+action[0]  #met à jour la current position en ajoutant la direction "action" (ex: [0, -1])
        new_state.curr_pos[1]=state.curr_pos[1]+action[1]

        new_state.grid[new_state.curr_pos[0]][new_state.curr_pos[1]] = "@" #remplace le slot où le personnage va par @ -> déplacement

        if state.grid[new_state.curr_pos[0]][new_state.curr_pos[1]] == "$": #si il y avait une caisse là où le personnage se déplace, (on check l'ancien state)
            new_state.grid[new_state.curr_pos[0]+action[0]][new_state.curr_pos[1]+action[1]] = "$" #immite le déplacement de la caisse en allant écrire $ un déplacent plus loin dans la direction d'action
        
        
        #boucle de calcul de boite à leur place -> TODO faire une fonction
        new_state.curr_ok=0
        for goal_pos in state.goal_pos:
            if new_state.grid[goal_pos[0]][goal_pos[1]]=="$": #vérifier si une des position de fin correspond à un $  
                new_state.curr_ok+=1    #on augmente le nombre de boite trouvées

        return State(new_state.grid, new_state.curr_pos, state.goal_pos, new_state.curr_ok)
        


####################
# Launch the search#
####################

tic = time.process_time()
problem = Sokoban(sys.argv[1])
solution = search.breadth_first_tree_search(problem)
for n in solution.path():
    print(n.state)
toc = time.process_time()
print("Le programme s'est exécuté en "+str(toc-tic)+" secondes.")