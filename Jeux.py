import ast
from typing import Callable, List, Tuple, Any, Dict, NamedTuple, Union

# Types de base utilisés par l'arbitre
Cell = Tuple[int, int]
Action = Union[Cell, Tuple[Cell, Cell]]
Player = int  # 1 ou 2
State = List[Tuple[Cell, Player]]  # État du jeu pour la boucle de jeu
Score = int
Time = int
Environment = Dict[str, Union[Dict[Cell, Player], int, str]]

# Quelques constantes
DRAW = 0
EMPTY = 0
B = 1
R = 2

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
        'state': [],  # État initial du jeu
        'player': player,  # Le joueur qui commence
        'hex_size': hex_size,  # Taille du plateau
        'game': game,  # Nom du jeu
        'total_time': total_time  # Temps total pour chaque joueur
    }
    
    # Initialiser le plateau en fonction du jeu
    if game.lower() == "dodo":
        environment['state'] = initialize_board(hex_size, game)
    elif game.lower() == "gopher":
        environment['state'] = initialize_board(hex_size, game)
    
    return environment


def generate_coordinates(size: int, game: str, color: str) -> List[Cell]:
    coordinates = []
    if game == "dodo":
        if color == "blue":
            for r in range(size - 1, -1, -1):
                for q in range(-size + 1, 1):
                    if abs(q) >= size - 2 - abs(r):
                        coordinates.append((q, r))
        elif color == "red":
            for r in range(-size + 1, 1):
                for q in range(size):
                    if abs(r) >= size - 2 - q:
                        coordinates.append((q, r))
    return coordinates


def initialize_board(size: int, game: str) -> State:
    state = []
    if game == "dodo":
        blue_coordinates = generate_coordinates(size, game, "blue")
        red_coordinates = generate_coordinates(size, game, "red")
        for coord in blue_coordinates:
            state.append((coord, B))
        for coord in red_coordinates:
            state.append((coord, R))
    elif game == "gopher":
        state = []
    return state


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
def strategy(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, Action]:
    if env['game'] == "dodo":
        return strategy_dodo(env, state, player, time_left)
    elif env['game'] == "gopher":
        return strategy_gopher(env, state, player, time_left)


def is_within_bounds(cell: Cell, hex_size: int) -> bool:
    q, r = cell
    return -hex_size < q < hex_size and -hex_size < r < hex_size and -hex_size < q + r < hex_size


def player_opponent(player: Player) -> Player:
    if player == R:
        return B
    else:
        return R


def minmax(state: State, depth: int, maximizing_player: bool, player: Player, hex_size: int, game: str) -> int:
    if depth == 0:
        return evaluation(state, player, game)
    
    opponent = player_opponent(player)
    
    if maximizing_player:
        max_eval = float('-inf')
        for action in legals(state, player, hex_size, game):
            new_state = apply_action(state, action, player, game)
            eval = minmax(new_state, depth - 1, False, player, hex_size, game)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for action in legals(state, opponent, hex_size, game):
            new_state = apply_action(state, action, opponent, game)
            eval = minmax(new_state, depth - 1, True, player, hex_size, game)
            min_eval = min(min_eval, eval)
        return min_eval


def apply_action(state: State, action: Action, player: Player, game: str) -> State:
    if not action:
        return state

    new_state = list(state)
    if game == "dodo":
        start, end = action
        new_state.remove((start, player))
        new_state.append((end, player))
    elif game == "gopher":
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


def evaluation(state: State, player: Player, game: str) -> int:
    if game == "dodo":
        opponent = player_opponent(player)
        score = 0
        for cell, p in state:
            if p == opponent:
                score -= count_neighbors(state, cell)
        return score
    elif game == "gopher":
        return len(legals(state, player, env['hex_size'], game))


def legals(state: State, player: Player, hex_size: int, game: str) -> List[Action]:
    legals = []

    if game == "dodo":
        blue_directions = [(1, 0), (1, -1), (0, -1)]
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

    elif game == "gopher":
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        opponent = player_opponent(player)

        if not state:  # State is empty, initial move
            for dq in range(-hex_size, hex_size + 1):
                for dr in range(-hex_size, hex_size + 1):   
                    new_cell = (dq, dr)         
                    if is_within_bounds(new_cell, hex_size):        
                        legals.append(new_cell)
        else:
            for cell, cell_player in state:
                if cell_player == opponent:
                    for direction in directions:
                        new_cell = (cell[0] + direction[0], cell[1] + direction[1])
                        if is_within_bounds(new_cell, hex_size) and new_cell not in [c[0] for c in state] and not count_neighbors(state, new_cell, player):  # Check if the new cell is within bounds and unoccupied
                            legals.append(new_cell)

        # Debug information
    return legals


def strategy_dodo(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, Action]:
    best_action = None
    max_eval = float('-inf')
    
    for action in legals(state, player, env['hex_size'], "dodo"):
        new_state = apply_action(state, action, player, "dodo")
        eval = minmax(new_state, 2, False, player, env['hex_size'], "dodo")
        if eval >= max_eval:
            max_eval = eval
            best_action = action
    
    return env, best_action


def strategy_gopher(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, Action]:
    best_action = None
    max_eval = float('-inf')
    
    if not state:
        best_action = (0, 0)
    else:
        for action in legals(state, player, env['hex_size'], "gopher"):
            new_state = apply_action(state, action, player, "gopher")
            eval = minmax(new_state, 2, False, player, env['hex_size'], "gopher")
            if eval >= max_eval:
                max_eval = eval
                best_action = action
    
    return env, best_action


def final(state: State, player: Player, game: str) -> Score:
    if not legals(state, player, env['hex_size'], game):
        if player == B:  # Blue wins
            print("Blue wins!")
            return -1
        else:  # Red wins
            print("Red wins!")
            return 1
    return 0  # Game continues

# Example usage for Dodo
env = initialize("dodo", [], B, 4, 10)
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

# Example usage for Gopher
env = initialize("gopher", [], B, 4, 10)
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