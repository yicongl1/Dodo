class Hex:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.s = -q - r

    def __eq__(self, other):
        return self.q == other.q and self.r == other.r and self.s == other.s

    def __hash__(self):
        return hash((self.q, self.r, self.s))

    def neighbors(self):
        directions = [
            Hex(1, 0), Hex(1, -1), Hex(0, -1),
            Hex(-1, 0), Hex(-1, 1), Hex(0, 1)
        ]
        return [self.add(direction) for direction in directions]

    def add(self, other):
        return Hex(self.q + other.q, self.r + other.r)

class DodoGame:
    def __init__(self, size):
        self.size = size
        self.board = self.initialize_board(size)
        self.current_player = 'Red'

    def initialize_board(self, size):
        board = {}
        for r in range(size):
            board[Hex(0, r)] = 'R'
            board[Hex(size-1, r)] = 'B'
        return board

    def display_board(self):
        min_q = min(hex.q for hex in self.board.keys())
        max_q = max(hex.q for hex in self.board.keys())
        min_r = min(hex.r for hex in self.board.keys())
        max_r = max(hex.r for hex in self.board.keys())

        print("   ", end="")
        for q in range(min_q, max_q + 1):
            print(f" {q:2}", end="")
        print()
        
        for r in range(min_r, max_r + 1):
            print(f"{r:2} ", end="")
            print(" " * (r - min_r), end="")
            for q in range(min_q, max_q + 1):
                hex = Hex(q, r)
                if hex in self.board:
                    print(f" {self.board[hex]} ", end="")
                else:
                    print(" . ", end="")
            print()

    def get_moves(self, player):
        moves = []
        for hex, occupant in self.board.items():
            if occupant == player[0]:
                for neighbor in hex.neighbors():
                    if neighbor not in self.board and self.is_within_bounds(neighbor):
                        moves.append((hex, neighbor))
        return moves

    def is_within_bounds(self, hex):
        return 0 <= hex.q < self.size and 0 <= hex.r < self.size

    def make_move(self, move):
        start, end = move
        self.board[end] = self.board[start]
        del self.board[start]

    def switch_player(self):
        self.current_player = 'Blue' if self.current_player == 'Red' else 'Red'

    def play(self):
        while True:
            self.display_board()
            moves = self.get_moves(self.current_player)
            if not moves:
                print(f'{self.current_player} has no moves available and wins!')
                break

            print(f"Available moves for {self.current_player}:")
            for move in moves:
                start, end = move
                print(f"({start.q},{start.r}) -> ({end.q},{end.r})")

            while True:
                try:
                    start_q = int(input(f'{self.current_player}, enter the start Q coordinate: '))
                    start_r = int(input(f'{self.current_player}, enter the start R coordinate: '))
                    end_q = int(input(f'Enter the end Q coordinate: '))
                    end_r = int(input(f'Enter the end R coordinate: '))
                    start_hex = Hex(start_q, start_r)
                    end_hex = Hex(end_q, end_r)
                    if (start_hex, end_hex) in moves:
                        move = (start_hex, end_hex)
                        break
                    else:
                        print("Invalid move. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter valid coordinates.")

            self.make_move(move)
            self.switch_player()

# Initialize the game with a board size of 5
game = DodoGame(5)
game.play()
