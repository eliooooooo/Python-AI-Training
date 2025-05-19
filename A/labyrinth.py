#########################
#####    Imports    #####
#########################
import time             # Pour temporiser l'affichage
from enum import Enum   # Classes énumération
import os               # Accès aux commandes systèmes
import sys              # Accès aux options système
import csv              # Lecture de fichiers CSV

# Énumération pour définir les directions possibles
Direction = Enum('Direction', ['LEFT', 'BOTTOM', 'RIGHT', 'TOP'])

#########################
####  Initialisation ####
#########################
# Objet global pour la grille
grid = None

# Initialisation de la grille avec des valeurs par défaut
# - 0 est utilisé pour marquer une case accessible
# - 1 est utilisé pour marquer un mur
# - 2 est utilisé pour marquer l'objectif
# - 3 est utilisé pour marquer le départ
def grid_init(): 
    global grid  # L'objet grid utilisé est la variable globale
    grid=[]
    # @TODO: Changer le chemin de fichier si besoin. Par défaut, vous pouvez tester avec le labyrinthe 1, puis tester les 2 et 3 
    with open("./labyrinth3.csv",newline='') as gridfile:
        reader = csv.reader(gridfile, delimiter=',',quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            grid.append(row)

# Trouve la case de départ
# - Si aucune case n'est trouvée pour le départ, commence sur la case en haut à gauche
def maze_starting_cell():
    global grid  # L'objet grid utilisé est la variable globale

    # Rechercher toute la grille pour trouver une case marquée 3
    for i in range(0,len(grid)):
        for j in range(0,len(grid[0])):
            if (grid[i][j]==3): return (i,j)

    # Si rien n'est trouvé après parcours complet, renvoyer la case en haut à gauche (1,1)
    return (1,1)

# Démarre la résolution
def maze_solve():
    global grid  # L'objet grid utilisé est la variable globale

    # Partir de la case de départ
    (i_start,j_start) = maze_starting_cell()
    grid[i_start][j_start] = 0
    maze_solve_depth(i_start,j_start)
    
#########################
##### Algorithme A* #####
#########################

# Recherche en profondeur par algorithme A*
# - i,j: Case en cours de validation
# Renvoie
# - Vrai si l'arrivée est atteinte
# - Faux si on tombe sur une impasse
def maze_solve_depth(i,j):
    global grid  # L'objet grid utilisé est la variable globale

    # Vérifier les bornes
    if i < 0 or i >= len(grid) or j < 0 or j >= len(grid[0]):
        return False
    
    # Si c'est un mur ou déjà visité, on arrête
    if grid[i][j] == 1 or grid[i][j] == 4:
        return False
    # Si c'est l'arrivée
    if grid[i][j] == 2:
        path_show()
        return True

    # Marquer la case comme visitée (4)
    temp = grid[i][j]
    grid[i][j] = 4
    path_show()

    # Explorer les 4 directions : gauche, bas, droite, haut
    directions = [(-1,0), (0,1), (1,0), (0,-1)]
    for di, dj in directions:
        ni, nj = i + di, j + dj
        if maze_solve_depth(ni, nj):
            return True

    # Backtrack : remettre la case à son état initial
    grid[i][j] = temp
    path_show()
    return False


#########################
#####   Affichage   #####
#########################
# Transformation d'une valeur de case en caractère pour affichage
def path_int_to_char(n):
    match n:
        case 0: return ' '
        case 1: return '█'
        case 2: return '$'
        case 3: return '·'
        case 4: return 'o'

# Effaçage de la console
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# Affiche le labyrinthe avec le chemin suivi
def path_show():
    global grid
    cls()
    for i in range(0,len(grid)):
        for j in range(0,len(grid[0])):
            print(path_int_to_char(grid[i][j]),end='')
        print('')
    # time.sleep(0.1) 

# Main
def main():
    sys.setrecursionlimit(5000) # Pour accepter de chercher en profondeur sans risquer la boucle infinie
    grid_init()
    path_show()
    maze_solve()

main()