from typing import Tuple, Dict, List, Optional, Union
import random

# Types de base utilisés par l'arbitre
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int # 1 ou 2
State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int
Environment = Dict[str, Union[Dict[Cell, Player], int, str]]

# Quelques constantes
DRAW = 0
EMPTY = 0
B = 1
R = 2

### Fonction d'initialisation
# Cette fonction est lancée au début du jeu. Elle dit à quel jeu on joue, le joueur que l'on est et renvoie l'environnement, c'est-à-dire la structure de donnée (objet, dictionnaire, etc.) que vous utiliserez pour jouer.
def initialize(game: str, state: State, player: Player, hex_size: int, total_time: Time) -> Environment:
    # Initialisation de l'environnement
    environment = {
        'state': [],  # État initial du jeu
        'player': player,  # Le joueur qui commence
        'hex_size': hex_size,  # Taille du plateau
        'game': game,  # Nom du jeu
        'total_time': total_time  # Temps total pour chaque joueur
    }
    
    # Initialiser le plateau en fonction du jeu
    if game == "Dodo":
        environment['state'] = initialize_board_dodo(hex_size)
    elif game == "Gopher":
        environment['state'] = initialize_board_gopher(hex_size)
    
    return environment

def generate_blue_coordinates_dodo(size: int) -> List[Cell]:
    blue_coordinates = []
    for r in range(size - 1, -1, -1):
        for q in range(-size + 1, 1):
            if abs(q) >= size - 2 - abs(r):
                blue_coordinates.append((q, r))
    return blue_coordinates

def generate_red_coordinates_dodo(size: int) -> List[Cell]:
    red_coordinates = []
    for r in range(-size + 1, 1):
        for q in range(size):
            if abs(r) >= size -2 - q:
                red_coordinates.append((q, r))
    return red_coordinates

def initialize_board_dodo(size: int) -> State:
    state = []
    blue_coordinates = generate_blue_coordinates_dodo(size)
    red_coordinates = generate_red_coordinates_dodo(size)
    
    for coord in blue_coordinates:
        state.append((coord, 1))
    for coord in red_coordinates:
        state.append((coord, 2))
    
    return state

def initialize_board_gopher(size: int) -> State:
    # Initialisation d'un plateau vide pour le jeu Gopher
    return []

def display_board(state: State, hex_size: int) -> None:
    min_q = -hex_size + 1
    max_q = hex_size - 1
    min_r = -hex_size + 1
    max_r = hex_size - 1

    board_dict = {cell: player for cell, player in state}

    print(" r     q ", end="")
    for q in range(min_q, max_q + 1):
        print(f" {q:2}", end="")
    print()

    for r in range(max_r, min_r - 1, -1):
        print(f"{r:2} ", end="")
        print(" " * (r - min_r), end="")
        for q in range(min_q, max_q + 1):
            cell = (q, r)
            if cell in board_dict:
                player = board_dict[cell]
                print(f" {player} ", end="")
            elif min_q <= q + r <= max_q:
                print(" . ", end="")
            else:
                print("   ", end="")
        print()

env = initialize("Dodo", State, 1, 5, 10)
display_board(env["state"], env["hex_size"])

