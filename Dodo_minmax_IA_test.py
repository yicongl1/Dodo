# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 15:40:36 2024

@author: micha
"""

from typing import Tuple, Dict, List, Optional

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

    def is_within_bounds(self, hex: Hex) -> bool:
        return -self.size + 1 <= hex.q <= self.size - 1 and -self.size + 1 <= hex.r <= self.size - 1 and -self.size + 1 <= hex.q + hex.r <= self.size - 1

    def get_neighbors(self, hex: Hex) -> List[Hex]:
        directions = [
            (1, 0, -1), (1, -1, 0), (0, -1, 1),
            (-1, 0, 1), (-1, 1, 0), (0, 1, -1)
        ]
        neighbors = []
        for dq, dr, ds in directions:
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
        if self.current_player == 'Red' and (end.r > start.r or (end.q != start.q and end.r == start.r)):
            return False
        if self.current_player == 'Blue' and (end.r < start.r or (end.q != start.q and end.r == start.r)):
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

    def evaluate_board(self) -> int:  # we have to change this in order to have a better IA 
        # Simple evaluation function: count the pieces of each player
        red_count = sum(1 for player in self.board.values() if player == 'Red')
        blue_count = sum(1 for player in self.board.values() if player == 'Blue')
        return blue_count - red_count if self.current_player == 'Blue' else red_count - blue_count

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

    def play(self) -> None:
        while True:
            self.display_board()
            print(f"{self.current_player}'s turn")
            print("AI is thinking...")
            
            possible_moves = self.get_all_possible_moves(self.current_player)
            if not possible_moves:
                print(f"No moves possible for {self.current_player}.")
                break

            _, best_move = self.minimax(3, True)
            if best_move:
                self.make_move(best_move)
                self.switch_player()

        
        print(f"{self.current_player} Lost!")
        self.switch_player()
        print(f"{self.current_player} Win!")
        

game = DodoGame()
game.play()