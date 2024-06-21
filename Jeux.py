import ast
from typing import Callable, List, Tuple, Any, Dict, NamedTuple, Union

Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]  # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int  # 1 ou 2
State = list[tuple[Cell, Player]]  # État du jeu pour la boucle de jeu
Score = int
Time = int

Environment = Dict[str, Union[Dict[Cell, Player], int, str]]
Game = int

GOPHER: Game = 0
DODO: Game = 1

GOPHER_STR: str = "gopher"
DODO_STR: str = "dodo"

EMPTY: Player = 0
RED: Player = 1
BLUE: Player = 2

CODE_ILLEGAL_ACTION = 310

class GameInfo(NamedTuple):
    game: str
    player: Player
    clocktime: Time
    state: State
    grid_size: int
    token: str

### Fonction d'initialisation
def initialize(game: str, state: State, player: Player, hex_size: int, total_time: Time) -> Environment:
    # Initialisation de l'environnement
    environment = {
        'state': initialize_board(hex_size, game),  # État initial du jeu
        'player': player,  # Le joueur qui commence
        'hex_size': hex_size,  # Taille du plateau
        'game': game,  # Nom du jeu
        'total_time': total_time  # Temps total pour chaque joueur
    }
    
    print("Init complete")
    return environment

#création des coordonnées utilisées plus tard sur le plateau
def generate_coordinates(size: int, game: str, color: int) -> List[Cell]:
    coordinates = []
    if game == DODO_STR:
        if color == RED:
            for x in range(-size + 1, 1):
                for y in range(-size + 1, 1):
                    if abs(y) >= size - 2 + x:
                        coordinates.append((x, y))
        elif color == BLUE:
            for x in range(size):
                for y in range(size):
                    if x >= size - 2 - y:
                        coordinates.append((x, y))
    return coordinates

#initialisation du plateau
def initialize_board(size: int, game: str) -> State:
    state = []
    for x in range(-size + 1, size):
        for y in range(-size + 1, size):
            if -size < x < size and -size < y < size and -size < -x + y < size:
                state.append(((x, y), EMPTY))
    
    if game == DODO_STR:
        blue_coordinates = generate_coordinates(size, game, BLUE)
        red_coordinates = generate_coordinates(size, game, RED)
        for coord in blue_coordinates:
            state[state.index((coord, EMPTY))] = (coord, BLUE)
        for coord in red_coordinates:
            state[state.index((coord, EMPTY))] = (coord, RED)

    return state

"""
def display_board(state: State, hex_size: int) -> None:
    min_x = -hex_size + 1
    max_x = hex_size - 1
    min_y = -hex_size + 1
    max_y = hex_size - 1

    board_dict = {cell: player for cell, player in state}

    print(" x" + " "*(2*hex_size-2) + "y", end="")
    for y in range(min_y, max_y + 1):
        print(f" {y:2}", end="")
    print()

    for x in range(min_x, max_x + 1):
        print(f"{x:2} ", end="")
        print(" " * (- x - min_x), end="")
        for y in range(min_y, max_y + 1):
            cell = (x, y)
            if cell in board_dict:
                player = board_dict[cell]
                print(f" {player} ", end="")
            elif min_y <= - x + y <= max_y:
                print(" . ", end="")
            else:
                print("   ", end="")
        print()
"""

### Fonction de jeu
def strategy(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, Action]:
    if env['game'] == DODO_STR: #si le jeu est dodo, appliquer la strategie pour le dodo
        return strategy_dodo(env, state, player, time_left)
    elif env['game'] == GOPHER_STR: #si le jeu est dodo, appliquer la strategie pour le dodo
        return strategy_gopher(env, state, player, time_left)


def is_within_bounds(cell: Cell, hex_size: int) -> bool: #vérifie que la cellule est bel est bien dans la grille
    x, y = cell
    return -hex_size < x < hex_size and -hex_size < y < hex_size and -hex_size < - x + y < hex_size


def player_opponent(player: Player) -> Player: #facilite l'utilisation de l'adversaire dans le reste du code
    if player == RED:
        return BLUE
    else:
        return RED


# def memoize(f: Callable[[State, int, bool, Player, int, str], int]) -> Callable[[State, int, bool, Player, int, str], int]:
#     cache = {}  #cache

#     def memoized_minmax(state: State, depth: int, maximizing_player: bool, player: Player, hex_size: int, game: str):
#         #conversion en tuple pour le cache
#         state_key = tuple((cell, player) for cell, player in state)
#         key = (state_key, depth, maximizing_player, player, hex_size, game)

#         if key in cache: #si le cas est reconnu dans le cache, alors on renvoie le resultat déjà calculé
#             return cache[key]
        
#         val = f(state, depth, maximizing_player, player, hex_size, game) #si le cas n'est pas connu, on l'ajoute au cache
#         cache[key] = val
#         return val
    
#     return memoized_minmax

# @memoize
# def minmax(state: State, depth: int, maximizing_player: bool, player: Player, hex_size: int, game: str) -> int:
#     if depth == 0: #lorsque la profondeur devient 0, alors on évalue
#         return evaluation(state, player, game, hex_size)
    
#     opponent = player_opponent(player)
    
#     if maximizing_player: #maximise le coup du joueur
#         max_eval = float('-inf')
#         for action in legals(state, player, hex_size, game):
#             new_state = apply_action(state, action, player, game)
#             eval = minmax(new_state, depth - 1, False, player, hex_size, game)
#             max_eval = max(max_eval, eval)
#         return max_eval
#     else: #minimise le coup de l'adversaire
#         min_eval = float('inf')
#         for action in legals(state, opponent, hex_size, game):
#             new_state = apply_action(state, action, opponent, game)
#             eval = minmax(new_state, depth - 1, True, player, hex_size, game)
#             min_eval = min(min_eval, eval)
#         return min_eval

def memoize(f: Callable[[State, int, bool, Player, int, str, float, float], int]) -> Callable[[State, int, bool, Player, int, str, float, float], int]:
    cache = {} #cache

    def memoized_minmax(state: State, depth: int, maximizing_player: bool, player: Player, hex_size: int, game: str, alpha: float, beta: float) -> int:
        #conversion en tuple pour le cache
        state_key = tuple((cell, player) for cell, player in state)
        key = (state_key, depth, maximizing_player, player, hex_size, game, alpha, beta)

        if key in cache: #si le cas est reconnu dans le cache, alors on renvoie le resultat déjà calculé
            return cache[key]
        
        val = f(state, depth, maximizing_player, player, hex_size, game, alpha, beta) #si le cas n'est pas connu, on l'ajoute au cache
        cache[key] = val
        return val
    
    return memoized_minmax

@memoize
def minmax(state: State, depth: int, maximizing_player: bool, player: Player, hex_size: int, game: str, alpha: float, beta: float) -> int:
    if depth == 0: #lorsque la profondeur devient 0, alors on évalue
        return evaluation(state, player, game, hex_size)
    
    opponent = player_opponent(player)
    
    if maximizing_player: #maximise le coup du joueur
        max_eval = float('-inf')
        for action in legals(state, player, hex_size, game):
            new_state = apply_action(state, action, player, game)
            eval = minmax(new_state, depth - 1, False, player, hex_size, game, alpha, beta)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else: #minimise le coup de l'adversaire
        min_eval = float('inf')
        for action in legals(state, opponent, hex_size, game):
            new_state = apply_action(state, action, opponent, game)
            eval = minmax(new_state, depth - 1, True, player, hex_size, game, alpha, beta)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def apply_action(state: State, action: Action, player: Player, game: str) -> State:
    if not action: #si pas d'action alors on retourne le meme etat
        return state

    new_state = list(state)
    if game == DODO_STR: #Lorsque le jeu est dodo, on applique l'action choisie et change l'état
        start, end = action
        new_state[new_state.index((start, player))] = (start, EMPTY) #Ici on change la nouvelle position du pion et enlève l'ancien
        new_state[new_state.index((end, EMPTY))] = (end, player)
    elif game == GOPHER_STR: #Lorsque le jeu est gopher, on applique l'action choisie et change l'état
        new_state[new_state.index((action, EMPTY))] = (action, player) #on rajoute le pion dans le nouvel état
    
    return new_state


def neighbors_list(state: State, cell: Cell) -> State: #effectue la liste des voisins de la cellule en question (uniquement si le voisin est un joueur et non pas une celulle vide)
    neighbors = []
    directions = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]

    for dx, dy in directions:
        neighbor = (cell[0] + dx, cell[1] + dy)
        for pos, player in state:
            if pos == neighbor and player != EMPTY:
                neighbors.append((pos, player))
    
    return neighbors


def count_neighbors(state: State, cell: Cell, player: Player = EMPTY) -> int: #Compte le nombre de voisins de la cellule en question 
    neighbors = neighbors_list(state, cell)
    count = 0

    if player == EMPTY:
        count = len(neighbors)
    else:
        for pos, cell_player in neighbors:
            if cell_player == player:
                count += 1
   
    return count


def evaluation(state: State, player: Player, game: str, hex_size: int) -> int:
    score = 0
    opponent = player_opponent(player)
    if game == DODO_STR:
        score += len(legals(state, player, hex_size, game))
        # for cell, p in state:
        #     if p == opponent:
        #         score += 0.001 * count_neighbors(state, cell) #on augmente le score si, lors du coup, le nombre de voisins de l'adversaire augmente
    elif game == GOPHER_STR:
        score += len(legals(state, player, hex_size, game)) #retourne le nombre legal de coup
        # for cell, p in state:
        #     if p == player:
        #         score += 0.001 * (abs(cell[0]) + abs(cell[1]))

        #         score -= 0.001 * count_neighbors(state, cell)
    return score


def legals(state: State, player: Player, hex_size: int, game: str) -> List[Action]:
    legals = []

    if game == DODO_STR: #Ensemble des coups legaux pour le dodo
        blue_directions = [(-1, 0), (-1, -1), (0, -1)]
        red_directions = [(1, 0), (1, 1), (0, 1)]
        
        if player == BLUE:
            directions = blue_directions
        else:
            directions = red_directions

        for cell, cell_player in state:
            if cell_player == player:
                for direction in directions:
                    new_cell = (cell[0] + direction[0], cell[1] + direction[1])
                    if is_within_bounds(new_cell, hex_size) and (new_cell, EMPTY) in state:  # vérifie si la nouvelle cellule est bien dans la grille et n'est pas occupée et l'ajoute aux coups legaux
                        legals.append((cell, new_cell))

    elif game == GOPHER_STR:
        directions = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]
        opponent = player_opponent(player)

        for cell, cell_player in state:
            if cell_player == opponent:
                for direction in directions:
                    new_cell = (cell[0] + direction[0], cell[1] + direction[1])
                    if is_within_bounds(new_cell, hex_size) and (new_cell, EMPTY) in state and not count_neighbors(state, new_cell, player) and count_neighbors(state, new_cell, cell_player) == 1:  # vérifie si la nouvelle cellule est bien dans la grille, n'est pas occupée, et ne possède qu'un seul voisin puis l'ajoute aux coups legaux
                        legals.append(new_cell)

    return legals


def strategy_dodo(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, Action]:
    best_action = None
    max_eval = float('-inf')
    
    for action in legals(state, player, env['hex_size'], DODO_STR):
        new_state = apply_action(state, action, player, DODO_STR)
        eval = minmax(new_state, 2, False, player, env['hex_size'], DODO_STR, float('-inf'), float('inf'))
        if eval >= max_eval: #prend la meilleure evaluation
            max_eval = eval
            best_action = action
    
    print(f"Best action: {best_action}")

    return env, best_action


def strategy_gopher(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, Action]:
    best_action = None
    max_eval = float('-inf')
    
    if not legals(state, player, env['hex_size'], GOPHER_STR):
        best_action = (0, 0) #évite les bugs quand c'est notre joueur qui joue en prmeier
    else:
        for action in legals(state, player, env['hex_size'], GOPHER_STR):
            new_state = apply_action(state, action, player, GOPHER_STR)
            eval = minmax(new_state, 2, False, player, env['hex_size'], GOPHER_STR)
            if eval >= max_eval: #Ici aussi, prend la meilleure evaluation
                max_eval = eval
                best_action = action
    print(f"Best action: {best_action}")

    return env, best_action


def final(state: State, score: Score, player: Player):
    print(f"Ending: {player} wins with a score of {score}")
    if player == BLUE :  # le joueur bleu gagne
        print("Blue wins!")
    else:  # le joueur rouge gagne
        print("Red wins!")

"""
# Example usage for Dodo
env = initialize(DODO_STR, [], BLUE, 6, 10)
state = env['state']
player = env['player']
time_left = env['total_time']

# Simulate game loop for Dodo
for i in range(1000):
    print(f"round: {i}")
    print(f"player: {player}")
    env, best_action = strategy(env, state, player, time_left)
    print(f"Best action: {best_action}")

    state = apply_action(state, best_action, player, env['game'])
    display_board(state, env["hex_size"])

    player = player_opponent(player)

    if final(state, player, env['game']) != 0:
        break
"""
"""
# Example usage for Gopher
env = initialize(GOPHER_STR, [], BLUE, 4, 10)
state = env['state']
player = env['player']
time_left = env['total_time']
# Simulate game loop for Gopher
for i in range(100):
    print(f"round: {i}")
    print(f"player: {player}")
    env, best_action = strategy(env, state, player, time_left)
    print(f"Best action: {best_action}")

    state = apply_action(state, best_action, player, env['game'])
    display_board(state, env["hex_size"])

    player = player_opponent(player)

    if final(state, player, env['game']) != 0:
        break
"""
