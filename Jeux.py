from typing import Tuple, Dict, List, Optional
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
        
### Fonction de jeu
# Cette fonction est la strategie que vous utilisez pour jouer. Cette fonction est lancée à chaque fois que c'est à votre joueur de jouer.
"""def strategy(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    pass

def legals_dodo(state: State, player: Player) -> List[ActionDodo]:
    legals = []
    directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]  # Six directions for moving
    
    for cell, cell_player in state:
        if cell_player == player:
            for direction in directions:
                new_cell = (cell[0] + direction[0], cell[1] + direction[1])
                if new_cell not in [c[0] for c in state]:  # Check if the new cell is unoccupied
                    legals.append((cell, new_cell))
    
    return legals
"""
def minmax(state: State, depth: int, maximizing_player: bool, player: Player, hex_size: int) -> int:
    if depth == 0:
        return heuristic(state, player)
    
    opponent = 1 if player == 2 else 2
    
    if maximizing_player:
        max_eval = float('-inf')
        for action in generate_actions(state, player, hex_size):
            new_state = apply_action(state, action, player)
            eval = minmax(new_state, depth - 1, False, player, hex_size)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for action in generate_actions(state, opponent, hex_size):
            new_state = apply_action(state, action, opponent)
            eval = minmax(new_state, depth - 1, True, player, hex_size)
            min_eval = min(min_eval, eval)
        return min_eval
    
def generate_actions(state: State, player: Player, hex_size: int) -> List[ActionDodo]:
    return legals_dodo(state, player, hex_size)

def apply_action(state: State, action: ActionDodo, player: Player) -> State:
    # Créer une copie de l'état actuel pour le modifier
    new_state = list(state)
    start, end = action
    new_state.remove((start, player))
    new_state.append((end, player))
    return new_state


def count_neighbors(state: State, cell: Cell) -> int:
    directions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    neighbors = 0
    for dq, dr in directions:
        neighbor = (cell[0] + dq, cell[1] + dr)
        if neighbor in [pos for pos, player in state]:
            neighbors += 1
    return neighbors

def heuristic(state: State, player: Player) -> int:
    opponent = 1 if player == 2 else 2
    score = 0
    for cell, p in state:
        if p == opponent:
            score -= count_neighbors(state, cell)
    return score

def strategy(env: Environment, state: State, player: Player, time_left: Time) -> Tuple[Environment, ActionDodo]:
    best_action = None
    best_value = float('-inf')
    depth = 3  # Profondeur de recherche
    
    for action in generate_actions(state, player, env['hex_size']):
        new_state = apply_action(state, action, player)
        move_value = minmax(new_state, depth - 1, False, player, env['hex_size'])
        if move_value > best_value:
            best_value = move_value
            best_action = action
    
    return env, best_action

def legals_dodo(state: State, player: Player, hex_size: int) -> List[ActionDodo]: #Il faut régler le problème que les joeurs peuvent "reculer" dans les legals moves (regarder la boucle en bas du programme)
    legals = []
    directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]  # Six directions for moving
    
    for cell, cell_player in state:
        if cell_player == player:
            for direction in directions:
                new_cell = (cell[0] + direction[0], cell[1] + direction[1])
                if is_within_bounds(new_cell, hex_size) and new_cell not in [c[0] for c in state]:  # Check if the new cell is within bounds and unoccupied
                    legals.append((cell, new_cell))
    
    return legals

def is_within_bounds(cell: Cell, hex_size: int) -> bool:
    q, r = cell
    return -hex_size < q < hex_size and -hex_size < r < hex_size and -hex_size < q + r < hex_size

env = initialize("Dodo", [], 1, 4, 10)
env['state'] = initialize_board_dodo(env['hex_size'])
display_board(env["state"], env["hex_size"])

state = env['state']
player = env['player']
time_left = env['total_time']
for i in range(9) :
    if player == 1:
        env, best_action = strategy(env, state, player, time_left)
        print(f"Best action: {best_action}")

        state = apply_action(state, best_action, player)
        display_board(state, env["hex_size"])
        player = 2
    else : 
        env, best_action = strategy(env, state, player, time_left)
        print(f"Best action: {best_action}")

        state = apply_action(state, best_action, player)
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


"""
class DodoGame:
    def __init__(self):
        self.size = 4
        self.board = self.initialize_board()
        self.current_player = 'Blue'



    def display_board(self) -> None:
        min_q = min(hex.q for hex in self.board.keys())
        max_q = max(hex.q for hex in self.board.keys())
        min_r = min(hex.r for hex in self.board.keys())
        max_r = max(hex.r for hex in self.board.keys())

        print(" r     q ", end="")
        for q in range(min_q, max_q + 1):
            print(f" {q:2}", end="")
        print()
        
        for r in range(max_r, min_r - 1, -1):
            print(f"{r:2} ", end="")
            print(" " * (r - min_r), end="")
            for q in range(min_q, max_q + 1):
                hex = Hex(q, r)
                if hex in self.board:
                    print(f" {self.board[hex][0]} ", end="")
                elif -4 < q + r < 4:
                    print(" . ", end="")
                else:
                    print("   ", end="")
            print()

    def is_within_bounds(self, hex: Hex) -> bool:
        return (-self.size + 1 <= hex.q <= self.size - 1) and (-self.size + 1 <= hex.r <= self.size - 1) and (-self.size + 1 <= hex.q + hex.r <= self.size - 1)

    def get_neighbors(self, hex: Hex) -> List[Hex]:
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        neighbors = []
        for dq, dr in directions:
            neighbor = Hex(hex.q + dq, hex.r + dr)
            if self.is_within_bounds(neighbor):
                neighbors.append(neighbor)
        return neighbors

    def is_valid_move(self, start: Hex, end: Hex) -> bool:
        if start not in self.board:
            return False
        if self.board[start] != self.current_player:
            return False
        if end in self.board:
            return False
        if not self.is_within_bounds(end):
            return False
        if end not in self.get_neighbors(start):
            return False

        # Check movement direction based on player
        if self.current_player == 'Red' and (end.r < start.r or (end.q > start.q and end.r == start.r)):
            return False
        if self.current_player == 'Blue' and (end.r > start.r or (end.q < start.q and end.r == start.r)):
            return False

        return True

    def make_move(self, move: Action) -> bool:
        start, end = move
        if self.is_valid_move(start, end):
            self.board[end] = self.board[start]
            del self.board[start]
            return True
        return False

    def switch_player(self) -> None:
        self.current_player = 'Red' if self.current_player == 'Blue' else 'Blue'

    def evaluate_board(self) -> int:
        # Evaluation function considering only the opponent's move possibilities
        opponent = 'Red' if self.current_player == 'Blue' else 'Blue'
        opponent_possible_moves = sum(len(self.get_neighbors(hex)) for hex, piece in self.board.items() if piece == opponent)
        return -opponent_possible_moves

    def get_all_possible_moves(self, player: Player) -> List[Action]:
        moves = []
        for hex, piece in self.board.items():
            if piece == player:
                for neighbor in self.get_neighbors(hex):
                    if neighbor not in self.board and self.is_valid_move(hex, neighbor):
                        moves.append((hex, neighbor))
        return moves

    def minimax(self, depth: int, maximizing_player: bool) -> Tuple[int, Optional[Action]]:
        if depth == 0 or not self.get_all_possible_moves(self.current_player):
            return self.evaluate_board(), None

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            for move in self.get_all_possible_moves(self.current_player):
                start, end = move
                self.board[end] = self.board[start]
                del self.board[start]
                self.switch_player()
                eval, _ = self.minimax(depth - 1, False)
                self.switch_player()
                self.board[start] = self.board[end]
                del self.board[end]
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in self.get_all_possible_moves(self.current_player):
                start, end = move
                self.board[end] = self.board[start]
                del self.board[start]
                self.switch_player()
                eval, _ = self.minimax(depth - 1, True)
                self.switch_player()
                self.board[start] = self.board[end]
                del self.board[end]
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def random_move(self) -> Optional[Action]:
        possible_moves = self.get_all_possible_moves(self.current_player)
        if not possible_moves:
            return None
        return random.choice(possible_moves)

    def play(self) -> None:
        while True:
            self.display_board()
            print(f"{self.current_player}'s turn")
            
            possible_moves = self.get_all_possible_moves(self.current_player)
            if not possible_moves:
                print(f"No moves possible for {self.current_player}.")
                break

            if self.current_player == 'Blue':
                print("Blue AI (Minimax) is thinking...")
                _, best_move = self.minimax(4, True)
                if best_move:
                    self.make_move(best_move)
            else:
                print("Red AI (Random) is thinking...")
                random_move = self.random_move()
                if random_move:
                    self.make_move(random_move)

            self.switch_player()

        print(f"{self.current_player} Win!")
        self.switch_player()
        print(f"{self.current_player} Lost!")

game = DodoGame()
game.play()

"""