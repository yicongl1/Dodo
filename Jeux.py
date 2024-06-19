import time
import ast
import random
from typing import Callable, List, Tuple, Any, Dict, NamedTuple, Union
import requests

# Types de base utilisés par l'arbitre
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell] # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int # 1 ou 2
State = list[tuple[Cell, Player]] # État du jeu pour la boucle de jeu
Score = int
Time = int
Env = Environment = Dict[str, Union[Dict[Cell, Player], int, str]]
Game = int

class GameInfo(NamedTuple):
    game: Game
    player: Player
    clocktime: Time
    state: State
    grid_size: int
    token: str


class FinishInfo(NamedTuple):
    finished: bool
    winner: Player
    final_score: int


InitCallback = Callable[[str, State, Player, int, Time], Env]
StrategyCallback = Callable[[Env, State, Player, Time], Tuple[Env, Action]]
FinalCallback = Callable[[State, Score, Player], None]

GOPHER: Game = 0
DODO: Game = 1

GOPHER_STR: str = "gopher"
DODO_STR: str = "dodo"

EMPTY: Player = 0
RED: Player = 1
BLUE: Player = 2

CODE_ILLEGAL_ACTION = 310

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
    if game == GOPHER_STR:
        environment['state'] = initialize_board_dodo(hex_size)
    elif game == DODO_STR:
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
        

        
### Fonction de jeu
# Cette fonction est la strategie que vous utilisez pour jouer. Cette fonction est lancée à chaque fois que c'est à votre joueur de jouer.
def strategy(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
   pass


def is_within_bounds(cell: Cell, hex_size: int) -> bool:
    q, r = cell
    return -hex_size < q < hex_size and -hex_size < r < hex_size and -hex_size < q + r < hex_size


def player_opponent(player: Player) -> Player:
    if player == 1:
        return 2
    else:
        return 1


def minmax_dodo(state: State, depth: int, maximizing_player: bool, player: Player, hex_size: int) -> int:
    if depth == 0:
        return evaluation_dodo(state, player)
    
    opponent = player_opponent(player)
    
    if maximizing_player:
        max_eval = float('-inf')
        for action in legals_dodo(state, player, hex_size):
            new_state = apply_action_dodo(state, action, player)
            eval = minmax_dodo(new_state, depth - 1, False, player, hex_size)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for action in legals_dodo(state, opponent, hex_size):
            new_state = apply_action_dodo(state, action, opponent)
            eval = minmax_dodo(new_state, depth - 1, True, player, hex_size)
            min_eval = min(min_eval, eval)
        return min_eval


def minmax_gopher(state: State, depth: int, maximizing_player: bool, player: Player, hex_size: int) -> int:
    if depth == 0:
        return evaluation_gopher(state, player)
    
    opponent = player_opponent(player)
    
    if maximizing_player:
        max_eval = float('-inf')
        for action in legals_gopher(state, player, hex_size):
            new_state = apply_action_gopher(state, action, player)
            eval = minmax_gopher(new_state, depth - 1, False, player, hex_size)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for action in legals_gopher(state, opponent, hex_size):
            new_state = apply_action_gopher(state, action, opponent)
            eval = minmax_gopher(new_state, depth - 1, True, player, hex_size)
            min_eval = min(min_eval, eval)
        return min_eval


def apply_action_dodo(state: State, action: ActionDodo, player: Player) -> State:
    # Créer une copie de l'état actuel pour le modifier
    new_state = list(state)
    start, end = action
    new_state.remove((start, player))
    new_state.append((end, player))
    
    return new_state


def apply_action_gopher(state: State, action: ActionGopher, player: Player) -> State:
    # Créer une copie de l'état actuel pour le modifier
    new_state = list(state)
    new_state.append((action, player))
    
    return new_state


def neighbors_list(state: State, cell: Cell) -> State:
    neighbors = []
    directions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]

    for dq, dr in directions:
        neighbor = (cell[0] + dq, cell[1] + dr)
        for pos, player in state:
            if pos == neighbor:
                neighbors.append((pos, player))
    
    return neighbors


def count_neighbors(state: State, cell: Cell, player: Player = 0) -> int:
    neighbors = neighbors_list(state, cell)
    count = 0

    if player == 0:
        count = len(neighbors)
    else:
        for pos, cell_player in neighbors:
            if cell_player == player:
                count += 1
   
    return count


def evaluation_dodo(state: State, player: Player) -> int:
    opponent = player_opponent(player)
    score = 0
    for cell, p in state:
        if p == opponent:
            score -= count_neighbors(state, cell)
    
    return score


def evaluation_gopher(state: State, player: Player, hex_size: int) -> int:
    return len(legals_gopher(state, player, hex_size))


def legals_dodo(state: State, player: Player, hex_size: int) -> List[ActionDodo]: #Il faut régler le problème que les joeurs peuvent "reculer" dans les legals moves (regarder la boucle en bas du programme)
    legals = []
    blue_directions = [(1, 0), (1, -1), (0, -1)]  # three directions for moving
    red_directions = [(-1, 0), (-1, 1), (0, 1)]
    
    if player == B:
        directions = blue_directions
    else:
        directions = red_directions

    for cell, cell_player in state:
        if cell_player == player:
            for direction in directions:
                new_cell = (cell[0] + direction[0], cell[1] + direction[1])
                if is_within_bounds(new_cell, hex_size) and new_cell not in [c[0] for c in state]:  # Check if the new cell is within bounds and unoccupied
                    legals.append((cell, new_cell))
    
    return legals


def legals_gopher(state: State, player: Player, hex_size: int) -> List[ActionGopher]: #Il faut régler le problème que les joeurs peuvent "reculer" dans les legals moves (regarder la boucle en bas du programme)
    legals = []
    directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
    opponent = player_opponent(player)

    for cell, cell_player in state:
        if cell_player == opponent:
            for direction in directions:
                new_cell = (cell[0] + direction[0], cell[1] + direction[1])
                if is_within_bounds(new_cell, hex_size) and new_cell not in [c[0] for c in state] and count_neighbors(state, new_cell, player) > 0:  # Check if the new cell is within bounds and unoccupied
                    legals.append((cell, new_cell))

    return legals


def strategy_dodo(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, ActionDodo]:
    best_action = None
    best_value = float('-inf')
    depth = 3  # Profondeur de recherche
    
    for action in legals_dodo(state, player, env['hex_size']):
        new_state = apply_action_dodo(state, action, player)
        move_value = minmax_dodo(new_state, depth - 1, False, player, env['hex_size'])
        if move_value > best_value:
            best_value = move_value
            best_action = action
    
    return env, best_action

def strategy_gopher(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, ActionDodo]:
    best_action = None
    best_value = float('-inf')
    depth = 3  # Profondeur de recherche
    
    for action in legals_gopher(state, player, env['hex_size']):
        new_state = apply_action_gopher(state, action, player)
        move_value = minmax_gopher(new_state, depth - 1, False, player, env['hex_size'])
        if move_value > best_value:
            best_value = move_value
            best_action = action
    
    return env, best_action

def strategy_brain(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    print("New state ", state)
    print("Time remaining ", time_left)
    print("What's your play ? ", end="")
    s = input()
    print()
    t = ast.literal_eval(s)
    return (env, t)

env = initialize(GOPHER_STR, [], 1, 4, 10)

state = env['state']
player = env['player']
time_left = env['total_time']
for i in range(100) :
    if player == 1:
        env, best_action = strategy_gopher(env, state, player, time_left)
        print(f"Best action: {best_action}")

        state = apply_action_gopher(state, best_action, player)
        display_board(state, env["hex_size"])
        player = 2
    else : 
        env, best_action = strategy_gopher(env, state, player, time_left)
        print(f"Best action: {best_action}")

        state = apply_action_gopher(state, best_action, player)
        display_board(state, env["hex_size"])
        player = 1


### Resultat de la partie
# Cette fonction est appelée à la fin du jeu et revoie le joueur gagnant, l'état final et le score.

def final_result(state: State, score: Score, player: Player):
    pass


def final_dodo(state: State, player: Player) -> Score:
    if not legals_dodo(state, player):
        if player == B:  # Blue wins
            print("Blue wins!")
            return 1
        else:  # Red wins
            print("Red wins!")
            return -1
    else:
        return 0  # Game continues


def final_gopher(state: State, player: Player) -> Score:
    if not legals_gopher(state, player):
        if player == B:  # Blue wins
            print("Blue wins!")
            return 1
        else:  # Red wins
            print("Red wins!")
            return -1
    else:
        return 0  # Game continues