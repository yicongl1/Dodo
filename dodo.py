from typing import Tuple, Dict

class Hex:
    def __init__(self, q: int, r: int):
        self.q = q
        self.r = r
        self.s = -q - r

    def __eq__(self, other: 'Hex') -> bool:
        return self.q == other.q and self.r == other.r and self.s == other.s

    def __hash__(self) -> int:
        return hash((self.q, self.r, self.s))

Grid = Tuple[Tuple[int, ...], ...]
State = Grid
Action = Tuple[Hex, Hex]
Player = str
Score = float

class DodoGame:
    def __init__(self):
        self.size = 4
        self.board = self.initialize_board(4)
        self.current_player = 'Blue'

    def initialize_board(self, size: int) -> Dict[Hex, Player]:
        board = {}
        red_coordinates = [(-3, 3), (-3, 2), (-3, 1), (-3, 0), (-2, 3), (-2, 2), (-2, 1), (-2, 0), (-1, 3), (-1, 2), (-1, 1), (0, 3), (0, 2)]
        blue_coordinates = [(3, 0), (3, -1), (3, -2), (3, -3), (2, 0), (2, -1), (2, -2), (2, -3), (1, -1), (1, -2), (1, -3), (0, -2), (0, -3)]
 
        for q in range(-size + 1, size):
            for r in range(-size + 1, size):
                if -size + 1 <= q + r < size:
                    if (q, r) in red_coordinates:
                        board[Hex(q, r)] = 'Red'
                    elif (q, r) in blue_coordinates:
                        board[Hex(q, r)] = 'Blue'
        return board

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

    def make_move(self, move: Action) -> None:
        start, end = move
        self.board[end] = self.board[start]
        del self.board[start]

    def switch_player(self) -> None:
        self.current_player = 'Red' if self.current_player == 'Blue' else 'Blue'

    def play(self) -> None:
        while True:
            self.display_board()
            print(f"{self.current_player}'s turn")
            print("Make your move.")
            start_q = int(input('Enter the start Q coordinate: '))
            start_r = int(input('Enter the start R coordinate: '))
            end_q = int(input('Enter the end Q coordinate: '))
            end_r = int(input('Enter the end R coordinate: '))
            start_hex = Hex(start_q, start_r)
            end_hex = Hex(end_q, end_r)
            move = (start_hex, end_hex)
            self.make_move(move)
            self.switch_player()

game = DodoGame()
game.play()
