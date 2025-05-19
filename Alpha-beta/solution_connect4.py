# -*- coding: utf-8 -*-

import random
import numpy as np
import time

######################
# Solution Connect 4 #
######################

#####
# joueur_connect4 : Fonction qui calcule le prochain coup optimal pour gagner la
#                   la partie de Connect4 à l'aide d'Alpha-Beta Prunning.
#
# etat: Objet de la classe Connect4Etat indiquant l'état actuel du jeu.
#
# fct_but: Fonction qui prend en entrée un objet de la classe Connect4Etat et
#          qui retourne le score actuel tu plateau. Si le score est positif, les 'X' ont l'avantage
#          si c'est négatif ce sont les 'O' qui ont l'avantage, si c'est 0 la partie est nulle.
#
# fct_transitions: Fonction qui prend en entrée un objet de la classe Connect4Etat et 
#                   qui retourne une liste de tuples actions-états voisins pour l'état donné.
#
# str_joueur: String indiquant c'est à qui de jouer : les 'X' ou 'O'.
#
# int_tempsMaximal: Entier indiquant le temps, en secondes, alloué pour prendre une décision.
#
# retour: Cette fonction retourne l'action optimal à joeur pour le joueur actuel c.-à-d. 'str_joueur'.
###  
def joueur_connect4(etat, fct_but, fct_transitions, str_joueur, int_tempsMaximal):
    
    profondeur_max = 1000
    
    temps_debut = time.time()
    
    def alpha_beta(etat_courant, profondeur, alpha, beta, maximizing_player, temps_debut, temps_max):
        if time.time() - temps_debut > temps_max * 0.95:
            return None
        
        resultat = fct_but(etat_courant)
        if resultat is not None or profondeur == 0:
            if resultat is None:
                tableau = etat_courant.tableau
                score = 0
                
                for i in range(etat_courant.n_rangees):
                    for j in range(etat_courant.n_colonnes):
                        if tableau[i, j] == 'X':
                            score += 1
                        elif tableau[i, j] == 'O':
                            score -= 1
                
                return score
            return resultat
        
        transitions = fct_transitions(etat_courant)
        if not transitions:
            return 0
        
        if maximizing_player:
            v = float('-inf')
            for action, nouvel_etat in transitions.items():
                valeur = alpha_beta(nouvel_etat, profondeur - 1, alpha, beta, False, temps_debut, temps_max)
                if valeur is None:
                    return None
                v = max(v, valeur)
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return v
        else:
            v = float('inf')
            for action, nouvel_etat in transitions.items():
                valeur = alpha_beta(nouvel_etat, profondeur - 1, alpha, beta, True, temps_debut, temps_max)
                if valeur is None:
                    return None
                v = min(v, valeur)
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return v
    
    transitions = fct_transitions(etat)
    meilleure_action = None
    meilleur_score = float('-inf') if str_joueur == 'X' else float('inf')
    
    for action, nouvel_etat in transitions.items():
        if str_joueur == 'X':
            score = alpha_beta(nouvel_etat, profondeur_max - 1, float('-inf'), float('inf'), False, temps_debut, int_tempsMaximal)
            if score is None: 
                break
            if score > meilleur_score:
                meilleur_score = score
                meilleure_action = action
        else: 
            score = alpha_beta(nouvel_etat, profondeur_max - 1, float('-inf'), float('inf'), True, temps_debut, int_tempsMaximal)
            if score is None:
                break
            if score < meilleur_score:
                meilleur_score = score
                meilleure_action = action
        
        if time.time() - temps_debut > int_tempsMaximal * 0.9:
            break
    
    if meilleure_action is None:
        items_list = list(transitions.items())
        meilleure_action, _ = random.choice(items_list)
    
    return meilleure_action
