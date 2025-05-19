# -*- coding: utf-8 -*-

import argparse
import os
import json
import random
import time
import copy
import numpy as np

# Enable command line history
#import readline
#readline.parse_and_bind('tab: complete')

FACTEUR_DISQUALIFICATION = 0.5


class Joueur:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, etat, fct_but, fct_transitions, str_joueur, int_tempsMaximal):
        return self.func(etat, fct_but, fct_transitions, str_joueur, int_tempsMaximal)


def joueur_humain(etat, fct_but, fct_transitions, str_joueur, int_tempsMaximal):
    actions_str = '; '.join([a.__str__() for a in fct_transitions(etat).keys()])
    action = input('Entrer un choix d\'action puis appuyer sur Enter.\nChoisir parmi: {' + actions_str + '}\n')

    action_ret = None
    while True:
        try:
            action_ret = int(action)
            if action_ret in fct_transitions(etat):
                break
            else:
                action = input('L\'action n\'est pas valide. Réessayer à nouveau, puis appuyer sur Enter\n')
        except ValueError:
            action = input('L\'action n\'est pas valide. Veuillez entrer un nombre, puis appuyer sur Enter\n')

    return action_ret


def joueur_aleatoire(etat, fct_but, fct_transitions, str_joueur, int_tempsMaximal):
    action, etat = random.choice(fct_transitions(etat).items())
    return action


class Jeu:

    """
    Classe de jeu.

    Initialize à partir de la fonction but,
    fonction transitions et l'état inital du jeu.

    La méthode "jouer_partie" simule une partie
    où un joueur Max (les 'X') et un joueur Min (les 'O')
    s'affrontent.
    """
    def __init__(self, etat_initial, fct_but, fct_transitions, verbose=True, tempsMaximal=np.inf, json_file=None):
        self.but = fct_but
        self.transitions = fct_transitions
        self.etat_initial = etat_initial
        self.verbose = verbose
        self.tempsMaximal = tempsMaximal
        self.resultat = None
        self.vainqueur = ''
        self.json_file = json_file
        self.player_turn = ''

    def resultat_partie(self):
        if self.resultat > 0:
            self.vainqueur = 'X'
            return 'Joueur X a gagné'

        if self.resultat < 0:
            self.vainqueur = 'O'
            return 'Joueur O a gagné'

        self.vainqueur = ''
        return 'Partie nulle'

    def afficher(self, str):
        if self.verbose:
            print(str)

    def dump_json(self, etat, action, temps, msg=None):
        if self.json_file is None:
            return

        data = {}
        if os.path.isfile(self.json_file):
            data = json.loads(open(self.json_file).read())

        data['moves'].append({'column': action,
                              'row': etat.n_rangees - np.sum(etat.tableau.T[action] != ' '),
                              'time': round(temps, 1),
                              'message': msg
                              })

        if self.vainqueur != '':
            data['win'] = self.vainqueur == 'X'

        with open(self.json_file, 'w') as json_out:
            json_out.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

    def jouer_partie(self, joueur_max, joueur_min):
        etat = copy.deepcopy(self.etat_initial)
        self.afficher(etat)

        tempsAlloueX = self.tempsMaximal
        tempsAlloueO = self.tempsMaximal

        msg = None
        
        if self.json_file is not None:
            with open(self.json_file, 'w') as json_out:
                json_out.write(json.dumps({'moves': []}, sort_keys=True, indent=4, separators=(',', ': ')))

        while True:
            ### X ###
            self.afficher("Joueur X a {0} sec. pour se décider".format(tempsAlloueX))
            self.player_turn = 'X'

            start = time.time()
            action = joueur_max(copy.deepcopy(etat), self.but, self.transitions, 'X', tempsAlloueX)
            tempsUtilise = time.time() - start

            tempsAlloueX = min(self.tempsMaximal, tempsAlloueX + (self.tempsMaximal - tempsUtilise))

            if tempsAlloueX < FACTEUR_DISQUALIFICATION * self.tempsMaximal:
                self.afficher("Joueur X a pris trop de temps: " + str(tempsUtilise))
                msg = "Temps expiré!"
                self.resultat = -1
                self.afficher(self.resultat_partie())
                break

            etat = self.transitions(etat)[action]
            self.afficher("X: " + str(tempsUtilise))
            self.afficher(etat)
            self.resultat = self.but(etat)

            if self.resultat is not None:         
                self.afficher(self.resultat_partie())
                break

            self.dump_json(etat, action, tempsUtilise, msg)

            ### O ###
            self.afficher("Joueur O a {0} sec. pour se décider".format(tempsAlloueO))
            self.player_turn = 'O'

            start = time.time()
            action = joueur_min(copy.deepcopy(etat), self.but, self.transitions, 'O', tempsAlloueO)
            tempsUtilise = time.time() - start

            tempsUtilise = time.time() - start
            tempsAlloueO = min(self.tempsMaximal, tempsAlloueO + (self.tempsMaximal - tempsUtilise))

            if tempsAlloueO < FACTEUR_DISQUALIFICATION * self.tempsMaximal:
                self.afficher("Joueur O a pris trop de temps: " + str(tempsUtilise))
                msg = "Temps expiré!"
                self.resultat = 1
                self.afficher(self.resultat_partie())
                break

            etat = self.transitions(etat)[action]
            self.afficher("O: " + str(tempsUtilise))
            self.afficher(etat)
            self.resultat = self.but(etat)

            if self.resultat is not None:
                self.afficher(self.resultat_partie())
                break

            self.dump_json(etat, action, tempsUtilise, msg)

        # Gagnant
        self.afficher(self.resultat_partie())
        self.dump_json(etat, action, tempsUtilise, msg)


#####
# Etat, transitions et but pour le Connect4
###
class Connect4Etat:

    def __init__(self):
        self.n_colonnes = 8
        self.n_rangees = 6
        self.tableau = np.array([[' '] * self.n_colonnes] * self.n_rangees)

    def __str__(self):
        ret = ''

        for i, r in enumerate(self.tableau):
            ret += '|' + '|'.join(r) + '|\n'

        ret += '-' * (2 * self.n_colonnes + 1) + '\n'
        ret += ' ' + ' '.join([str(i) for i in range(self.n_colonnes)]) + '\n'

        return ret


def connect4_transitions(etat):
    # Determiner c'est le tour à qui
    if np.sum(etat.tableau == 'X') > np.sum(etat.tableau == 'O'):
        symbol = 'O'
    else:
        symbol = 'X'

    actions = {}
    for i in range(etat.n_colonnes):
        try:
            rangee_pour_i = np.nonzero(etat.tableau.T[i] == ' ')[0].max()
            nouvel_etat = copy.deepcopy(etat)
            nouvel_etat.tableau[rangee_pour_i, i] = symbol
            actions[i] = nouvel_etat
        except:
            pass

    return actions


def connect4_but(etat):
    def symbol_gagne(symbol):
        gagne = False
        # for i in range(etat.n_rangees):
        #    for j in range(etat.n_colonnes):
        if np.sum(etat.tableau == symbol) == 0:
            return False

        x, y = np.nonzero(etat.tableau == symbol)
        for i, j in zip(x, y):
            # Vérifie 4 pareil sur une rangée...
            gagne |= np.sum(etat.tableau[i, j:j + 4] == symbol) == 4
            # ... sur une colonne
            gagne |= np.sum(etat.tableau[i:i + 4, j] == symbol) == 4
            # ... sur une diagonale gauche-droite
            gagne |= np.sum(np.diag(etat.tableau[i:i + 4, j:j + 4]) == symbol) == 4
            # ... sur une diagonale droite-gauche
            gagne |= np.sum(np.diag(etat.tableau[i - 4 + 1:i + 1, j:j + 4][::-1]) == symbol) == 4

            if gagne:
                return gagne

        return gagne

    # Vérifie si X a gagné
    X_gagne = symbol_gagne('X')
    if X_gagne:
        return 100000 + np.sum(etat.tableau == ' ')

    # Vérifie si O a gagné
    O_gagne = symbol_gagne('O')
    if O_gagne:
        return -100000 - np.sum(etat.tableau == ' ')

    # Vérifie si c'est une partie nulle
    if np.sum(etat.tableau != ' ') == etat.n_colonnes * etat.n_rangees:
        return 0

    return None


def player_factory(player):
    if player == 'aleatoire':
        return joueur_aleatoire

    if player == 'humain':
        return joueur_humain

    if player.endswith('.py'):
        import importlib.util
        player = os.path.abspath(player)
        name = player.replace('/', '.').replace('.', '_')
        spec = importlib.util.spec_from_file_location(name, player)
        solution = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(solution)

        # def agent(etat, fct_but, fct_transitions, str_joueur, int_tempsMaximal):
        #     return solution.joueur_connect4(etat, fct_but, fct_transitions, str_joueur, int_tempsMaximal)

        return Joueur(player, solution.joueur_connect4)

    return None


#####
# Execution en tant que script
###
DESCRIPTION = "Lancer une partie de Connect4."


def buildArgsParser():
    p = argparse.ArgumentParser(description=DESCRIPTION,
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Paramètres globaux
    p.add_argument('-joueur1', dest="player1", metavar="JOUEUR", action='store',
                   type=str, required=False, default="./solution_connect4.py",
                   help="'humain', 'aleatoire' ou le fichier contenant votre solution.")

    p.add_argument('-joueur2', dest="player2", metavar="JOUEUR", action='store',
                   type=str, required=False, default="./solution_connect4.py",
                   help="'humain', 'aleatoire' ou le fichier contenant votre solution.")

    p.add_argument('-temps', dest="time_limit", metavar="INT", action='store', type=int, required=False,
                   help="temps disponible pour jouer un coup (en secondes).", default=5)

    p.add_argument('-v', dest='is_verbose', action='store_true', required=False,
                   help='activer le mode verbose')
                   
    p.add_argument('-json', dest='json_file', metavar="FICHIER", action='store', type=str, required=False,
                   help='fichier JSON pour enregistrer les données de la partie', default=None)

    return p


def main():
    parser = buildArgsParser()
    args = parser.parse_args()
    player1 = args.player1
    player2 = args.player2
    time_limit = args.time_limit
    is_verbose = args.is_verbose
    json_file = args.json_file

    if player1 == "humain" or player2 == "humain":
        is_verbose = True  # Afficher les grilles si c'est un joueur humain.

    if player1 not in ['aleatoire', 'humain'] and not player1.endswith('.py'):
        parser.error('Joueur 1 doit être [aleatoire, humain, solution_connect4.py]')

    if player2 not in ['aleatoire', 'humain'] and not player2.endswith('.py'):
        parser.error('Joueur 2 doit être [aleatoire, humain, solution_connect4.py]')

    if player1.endswith('.py') and not os.path.isfile(player1):
        parser.error("-joueur1 '{}' must be an existing file!".format(os.path.abspath(player1)))

    if player2.endswith('.py') and not os.path.isfile(player2):
        parser.error("-joueur2 '{}' must be an existing file!".format(os.path.abspath(player2)))

    # Jouer une partie de Connect4
    connect4 = Jeu(Connect4Etat(), connect4_but, connect4_transitions, verbose=is_verbose, tempsMaximal=time_limit, json_file=json_file)
    connect4.jouer_partie(player_factory(player1), player_factory(player2))

if __name__ == "__main__":
    main()
