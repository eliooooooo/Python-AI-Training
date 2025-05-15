from __future__ import annotations
import csv
import copy

###################################################
################## Utilitaires ####################
###################################################

# Fonction pour le calcul de la valeur absolue
# x: Entier
# Retourne |x|
def abs(x) -> int: 
    if(x<0): return -x
    return x

# Fonction pour le calcul d'intervalle de caractères
# c1: Caractère de départ
# c2: Caractère de fin
# Retourne la liste des caractères entre c1 et c2 inclus
def char_range(c1:str, c2:str):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

############################################
############### Classe Etat ################
############################################
# Classe représentant les états possibles de la table
class Etat:
    # Fonction d'initialisation, appelée à la construction d'un objet Etat
    def __init__(self):
        # On place les invités dans un certain ordre, sans prise en compte des contraintes
        self.table = [  ['A','B','C','D','E','F'],
                        ['G','H','I','J','K','L']]
        # Récupération du tableau de contraintes
        # Dans le fichier CSV: 
        # * 1 en ligne i, colonne j signifie que i veut être à côté (ou en face) de j
        # * -1 en ligne i, colonne j signifie que i ne veut pas être à côté (ou en face) de j
        # * 0 signifie qu'il n'y a pas de contrainte
        # * 9 permet de repérer la diagonale (sur laquelle on ne peut pas avoir de contrainte)

        # Les contraintes encodées dans le fichier de base sont les suivantes
        # - A ne veut pas être à côté de B ni à côté de J
        # - B veut être à côté de I et L
        # - C refuse de s'asseoir près de D
        # - D ne veut pas voir B ni C
        # - E souhaite pouvoir discuter avec H
        # - F n'aime ni C ni E
        # - G veut absolument être à proximité de K
        # - I apprécie A mais n'aime pas D
        # - J veut juste rester proche de C
        # - K demande une place à côté de B
        # - L en veut à F
        self.contraintes=[]
        # @TODO: Changer le chemin vers le fichier CSV si besoin
        with open("./contraintes.csv",newline='') as gridfile:
            reader = csv.reader(gridfile, delimiter=',',quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                self.contraintes.append(row)
        
    # Fonction pour copier un état et échanger deux places
    # self: Etat courant
    # i,j: Numéros de places à échanger
    # Retourne l'état avec les places échangées
    def copie_avec_echange(self,i:int,j:int)->Etat:
        copie = Etat()
        copie.table = copy.deepcopy(self.table)
        copie.echanger(i,j)
        copie.contraintes=self.contraintes

        return copie

    # Fonction pour tester si deux personnes sont voisines
    # self: Etat courant
    # i,j: Personnes à vérifier
    # Retourne True si les personnes sont côte à côte ou face à face
    def voisins(self,i:str,j:str) -> bool:
        place_i=-1
        place_j=-1
        for p in range(0,12):
            if (self.table[p//6][p%6]==i): place_i=p
            if (self.table[p//6][p%6]==j): place_j=p
        return (abs(place_i-place_j)==1     # Côte à côte
             or abs(place_i-place_j)==6)    # Face à face

    # Fonction pour calculer le nombre de personnes dont les demandes ne sont pas respectées
    # self: Etat courant
    # Retourne entre 0 et 12 personnes insatisfaites
    def nb_insatisfaits(self) -> int:
        insatisfaits = 0
        for i in char_range('A','L'):
            if (not self.satisfait(i)): 
                insatisfaits=insatisfaits+1
        return insatisfaits
    
    # Fonction pour tester si une personne est satisfaite de sa place
    # self: Etat courant
    # i: Personne à vérifier
    # Retourne True si la personne voit ses demandes résolues
    def satisfait(self,i:str) -> bool:
        for j in char_range('A','L'):
            if (i==j): continue
            if (self.contrainte(i,j)==-1 and self.voisins(i,j)):      return False    # Est à côté de quelqu'un qu'il n'aime pas
            if (self.contrainte(i,j)==1 and not self.voisins(i,j)):   return False    # Veut un voisin et ne l'a pas
        return True
    
    # Fonction pour interpréter les contraintes d'après le tableau
    # self: Etat courant
    # i,j: Personnes à vérifier
    # 0,1 ou -1 selon l'encodage de la contrainte
    def contrainte(self,i:str,j:str)->int:
        return self.contraintes[ord(i)-65][ord(j)-65]

    # Fonction pour échanger deux places
    # self: Etat à modifier
    # i,j: Numéros de places à échanger
    def echanger(self,i:int,j:int)->None:
        tmp=self.table[i//6][i%6]
        self.table[i//6][i%6]=self.table[j//6][j%6]
        self.table[j//6][j%6]=tmp

    # Fonction pour afficher l'état
    # self: Etat courant
    def __str__(self) -> str:
        res = "Plan de table:\n"
        res += " "+ self.table[0][0] +" "+ self.table[0][1] +" "+ self.table[0][2] +" "+ self.table[0][3] +" "+ self.table[0][4] +" "+ self.table[0][5] +"\n"
        res += "█████████████\n"
        res += " "+ self.table[1][0] +" "+ self.table[1][1] +" "+ self.table[1][2] +" "+ self.table[1][3] +" "+ self.table[1][4] +" "+ self.table[1][5] +"\n"

        nb_ins = self.nb_insatisfaits()
        res = res + "\nNombre d'insatisfaits : "+str(nb_ins)

        if (nb_ins>0):
            res += " ("
            for i in char_range('A','L'):
                if (not self.satisfait(i)): res += i + ""
            res += ")"


        return res

# Fonction pour faire la descente de gradient
def descente_gradient():
    etat = Etat()
    nb_ins = etat.nb_insatisfaits()
    meilleure_solution = etat
    meilleur_nb_ins = nb_ins

    while True:
        amelioration = False
        for i in range(12):
            for j in range(i+1, 12):
                nouvel_etat = meilleure_solution.copie_avec_echange(i, j)
                nb_ins_nouveau = nouvel_etat.nb_insatisfaits()
                if nb_ins_nouveau < meilleur_nb_ins:
                    meilleur_nb_ins = nb_ins_nouveau
                    amelioration = True
                    meilleure_nouvelle_solution = nouvel_etat
        if not amelioration:
            break
        else:
            meilleure_solution = meilleure_nouvelle_solution

    print(meilleure_solution)

#########################################
########### Exécution du code ###########
#########################################
descente_gradient()