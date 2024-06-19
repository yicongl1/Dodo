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
    
    return environment


def generate_coordinates(size: int, game: str, color: int) -> List[Cell]:
    coordinates = []
    if game == DODO_STR:
        if color == BLUE:
            for r in range(size - 1, -1, -1):
                for q in range(-size + 1, 1):
                    if abs(q) >= size - 2 - abs(r):
                        coordinates.append((r, q))
        elif color == RED:
            for r in range(-size + 1, 1):
                for q in range(size):
                    if abs(r) >= size - 2 - q:
                        coordinates.append((r, q))
    return coordinates


def initialize_board(size: int, game: str) -> State:
    state = []
    if game == DODO_STR:
        blue_coordinates = generate_coordinates(size, game, BLUE)
        red_coordinates = generate_coordinates(size, game, RED)
        for coord in blue_coordinates:
            state.append((coord, BLUE))
        for coord in red_coordinates:
            state.append((coord, RED))
    elif game == GOPHER_STR:
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
            cell = (r, q)
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
    if env['game'] == DODO_STR:
        return strategy_dodo(env, state, player, time_left)
    elif env['game'] == GOPHER_STR:
        return strategy_gopher(env, state, player, time_left)


def is_within_bounds(cell: Cell, hex_size: int) -> bool:
    r, q = cell
    return -hex_size < q < hex_size and -hex_size < r < hex_size and -hex_size < q + r < hex_size


def player_opponent(player: Player) -> Player:
    if player == RED:
        return BLUE
    else:
        return RED


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
    if game == DODO_STR:
        start, end = action
        new_state.remove((start, player))
        new_state.append((end, player))
    elif game == GOPHER_STR:
        new_state.append((action, player))
    return new_state


def neighbors_list(state: State, cell: Cell) -> State:
    neighbors = []
    directions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]

    for dr, dq in directions:
        neighbor = (cell[0] + dr, cell[1] + dq)
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
    if game == DODO_STR:
        opponent = player_opponent(player)
        score = 0
        for cell, p in state:
            if p == opponent:
                score -= count_neighbors(state, cell)
        return score
    elif game == GOPHER_STR:
        return len(legals(state, player, env['hex_size'], game))


def legals(state: State, player: Player, hex_size: int, game: str) -> List[Action]:
    legals = []

    if game == DODO_STR:
        red_directions = [(1, 0), (1, -1), (0, -1)]
        blue_directions = [(-1, 0), (-1, 1), (0, 1)]
        
        if player == BLUE:
            directions = blue_directions
        else:
            directions = red_directions

        for cell, cell_player in state:
            if cell_player == player:
                for direction in directions:
                    new_cell = (cell[0] + direction[0], cell[1] + direction[1])
                    if is_within_bounds(new_cell, hex_size) and new_cell not in [c[0] for c in state]:  # Check if the new cell is within bounds and unoccupied
                        legals.append((cell, new_cell))

    elif game == GOPHER_STR:
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        opponent = player_opponent(player)

        if not state:  # State is empty, initial move
            for dq in range(-hex_size, hex_size + 1):
                for dr in range(-hex_size, hex_size + 1):   
                    new_cell = (dr, dq)         
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
    
    for action in legals(state, player, env['hex_size'], DODO_STR):
        new_state = apply_action(state, action, player, DODO_STR)
        eval = minmax(new_state, 2, False, player, env['hex_size'], DODO_STR)
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
        for action in legals(state, player, env['hex_size'], GOPHER_STR):
            new_state = apply_action(state, action, player, GOPHER_STR)
            eval = minmax(new_state, 2, False, player, env['hex_size'], GOPHER_STR)
            if eval >= max_eval:
                max_eval = eval
                best_action = action
    
    return env, best_action


def final(state: State, player: Player, game: str) -> Score:
    if not legals(state, player, env['hex_size'], game):
        if player == BLUE:  # Blue wins
            print("Blue wins!")
            return -1
        else:  # Red wins
            print("Red wins!")
            return 1
    return 0  # Game continues

# Example usage for Dodo
env = initialize(DODO_STR, [], BLUE, 4, 10)
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