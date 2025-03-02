from BoardClasses import Board, InvalidMoveError, InvalidParameterError
from Move import Move
import random
import copy # for using deepcopy()
import math 
import time

# Commands 
# python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Random_AI/main.py
# python3 AI_Runner.py 8 8 2 n ../src/checkers-python/main.py

# cd /home/ics-home/Checkers_Student/Checkers_Student-1/Tools

# Running against poor AI: 
# python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Poor_AI/main.py

# Black is player 1, White is player 2 

# Idea to improve MCTS would be could you cache certain paths of high winrate moves to make the AI faster
# at making these moves? 


# MCTSNode Class for Monte Carlo Tree Search
class MCTSNode:
    """Represents a node in the Monte Carlo Tree Search (MCTS) Tree."""
    
    def __init__(self, board, move=None, parent=None, current_player=1):
        self.board = copy.deepcopy(board)
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.current_player = current_player

    def is_fully_expanded(self):
        """Returns True if all possible moves have been explored."""
        valid_moves = self.board.get_all_possible_moves(self.current_player)
        return len(self.children) >= sum(len(m) for m in valid_moves)

    def best_child(self, exploration_weight=1.4):
        """Selects the child node with the highest UCT value."""
        return max(self.children, key=lambda node: 
                   (node.wins / (node.visits + 1)) + 
                   exploration_weight * math.sqrt(math.log(self.visits + 1) / (node.visits + 1)))

class StudentAI:
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2
        self.opponent = {1: 2, 2: 1}
        self.current_player = 1
        self.base_time = 480
        self.simulation_time = self.base_time / 60 

    def get_move(self, move):
        """Determines the AI's move using MCTS"""

        if len(move) != 0:
            try:
                self.board.make_move(move, self.opponent[self.color])
            except InvalidMoveError:
                return Move([])

        valid_moves = self.board.get_all_possible_moves(self.color)
        if not valid_moves:
            return Move([])

        best_move = self.mcts_search(self.board, self.simulation_time)

        if best_move is None or best_move.seq not in [m.seq for sublist in valid_moves for m in sublist]:
            return Move([])

        self.board.make_move(best_move, self.color)
        return best_move

    def mcts_search(self, board, time_limit=10):
        """Performs MCTS to determine the best move."""
        root = MCTSNode(board, current_player=self.color)
        start_time = time.time()

        while time.time() - start_time < time_limit:
            node = root

            while node.is_fully_expanded() and node.children:
                node = node.best_child()

            possible_moves = node.board.get_all_possible_moves(self.color)
            if not possible_moves:
                return None

            if not node.is_fully_expanded():
                move = random.choice([m for sublist in possible_moves for m in sublist])

                valid_moves = [m.seq for sublist in node.board.get_all_possible_moves(self.color) for m in sublist]
                if move.seq not in valid_moves:
                    continue

                new_board = copy.deepcopy(node.board)
                try:
                    new_board.make_move(move, self.color)
                except InvalidMoveError:
                    continue

                new_node = MCTSNode(new_board, move, node, self.color)
                node.children.append(new_node)
                node = new_node

            winner = self.simulate_random_game(node.board)

            while node:
                node.visits += 1
                if winner == self.color or winner == 0:
                    node.wins += 1
                node = node.parent

        best_child = root.best_child(exploration_weight=0)

        if best_child and best_child.move.seq in [m.seq for sublist in root.board.get_all_possible_moves(self.color) for m in sublist]:
            return best_child.move

        return None

    def simulate_random_game(self, board):
        """Simulates a random game from the given board state until a winner is found."""
        sim_board = copy.deepcopy(board)
        current_player = self.color

        while True:
            result = sim_board.is_win(current_player)
            if result != 0:
                return 0 if result == -1 else result

            possible_moves_nested = sim_board.get_all_possible_moves(current_player)
            possible_moves = [move for sublist in possible_moves_nested for move in sublist]

            if not possible_moves:
                return self.opponent[current_player]  # If no moves, the opponent wins

            max_attempts = 5
            for _ in range(max_attempts):  # Try up to 5 moves
                move = random.choice(possible_moves)
                try:
                    sim_board.make_move(move, current_player)
                    break  # Exit loop if move is successful
                except InvalidMoveError:
                    possible_moves.remove(move)  # Remove invalid move and retry
                    if not possible_moves:
                        return self.opponent[current_player]  # No valid moves left

            current_player = self.opponent[current_player]

    def get_estimated_remaining_moves(self):
        """Estimates the number of remaining moves in the game based on the number of pieces left."""
        total_pieces = sum(
            1 for row in self.board.board for piece in row if piece and piece.color in ["B", "W"]
        )
        return max(10, total_pieces * 3)

    def evaluate_board(self, board, color):
        """Simple heuristic function: calculates material advantage."""
        my_pieces = sum(1 for row in board.board for piece in row if piece and piece.color == color)
        opponent_pieces = sum(1 for row in board.board for piece in row if piece and piece.color == self.opponent[color])
        
        return my_pieces - opponent_pieces
