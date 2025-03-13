
import copy
import math 
import random
import time
from BoardClasses import Board, InvalidMoveError, InvalidParameterError
from Move import Move

# Commands 
# python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Random_AI/main.py
# python3 AI_Runner.py 8 8 2 n ../src/checkers-python/main.py

# cd /home/ics-home/Checkers_Student/Checkers_Student-1/Tools

# Running against poor AI: 
# python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Poor_AI/main.py

# Running against AverageAI: 
# python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Average_AI/main.py

# python3 AI_Runner.py 7 7 2 l ../src/checkers-python/main.py Sample_AIs/Average_AI/main.py

# Black is player 1, White is player 2 

# Monte Carlo Tree Search Node
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
        return len(self.children) >= sum(len(moves) for moves in valid_moves)

    def best_child(self, exploration_weight=1.4):
        """Selects the best child node using UCB1 formula."""
        remaining_pieces = sum(
            1 for row in self.board.board for piece in row if piece
        )
        # Reduce exploration weight in endgame
        if remaining_pieces <= 6:
            exploration_weight = 0.5
        return max(
            self.children,
            key=lambda node: (node.wins / (node.visits + 1)) +
            exploration_weight * math.sqrt(math.log(self.visits + 1) / (node.visits + 1))
        )


class StudentAI:
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2
        self.opponent = {1: 2, 2: 1}
        self.simulation_time = 10  # Default simulation time
        self.move_cache = {}  # Cache for move evaluations

    def board_signature(self, board):
        """Generates a unique hash signature for a board state."""
        return ''.join(str(piece) if piece else '.' for row in board.board for piece in row)

    def get_move(self, move):
        """Determines the AI's move using MCTS."""
        if len(move) != 0:
            try:
                self.board.make_move(move, self.opponent[self.color])
            except InvalidMoveError:
                return Move([(0, 0)])  # Safe fallback move
        else:
            self.color = 1  # First move, set AI to Player 1

        # Check if legal moves exist before running MCTS.
        legal_moves = [m for sublist in self.board.get_all_possible_moves(self.color) for m in sublist]
        if not legal_moves:
            return Move([(0, 0)])

        best_move = self.mcts_search(self.board, self.simulation_time)

        if best_move is None or best_move.seq not in [m.seq for m in legal_moves]:
            best_move = random.choice(legal_moves) if legal_moves else Move([(0, 0)])  # Safe fallback

        try:
            self.board.make_move(best_move, self.color)
        except InvalidMoveError:
            return Move([(0, 0)])

        return best_move

    def mcts_search(self, board, time_limit=10):
        """Performs Monte Carlo Tree Search to determine the best move."""
        root = MCTSNode(copy.deepcopy(board), current_player=self.color)
        start_time = time.time()

        while time.time() - start_time < time_limit:
            node = root

            # Selection: Traverse the tree
            while node.is_fully_expanded() and node.children:
                node = node.best_child()

            # Expansion: Expand unexplored child nodes
            possible_moves = node.board.get_all_possible_moves(node.current_player)

            # Force captures if available
            jump_moves = [m for sublist in possible_moves for m in sublist if len(m.seq) > 1]
            if jump_moves:
                possible_moves = [jump_moves]

            flattened_moves = [m for sublist in possible_moves for m in sublist]
            if not flattened_moves:
                return random.choice(flattened_moves) if flattened_moves else Move([])

            move = max(flattened_moves, key=lambda m: self.evaluate_board_with_move(node.board, m, node.current_player))

            # Apply move and create a new node
            new_board = copy.deepcopy(node.board)
            try:
                new_board.make_move(move, node.current_player)
                new_node = MCTSNode(new_board, move, node, current_player=self.opponent[node.current_player])
                node.children.append(new_node)
                node = new_node
            except InvalidMoveError:
                continue  # Skip invalid moves

            # Simulation: Run biased rollouts
            winner = self.simulate_random_game(new_board, node.current_player)

            # Backpropagation: Update node statistics
            while node:
                node.visits += 1
                if winner == self.color or winner == 0:  # 0 means draw
                    node.wins += 1
                node = node.parent

        best_child = root.best_child(exploration_weight=0)
        return best_child.move if best_child and best_child.move else random.choice(flattened_moves)

    def simulate_random_game(self, board, current_player):
        """Simulates a biased game rollout."""
        sim_board = copy.deepcopy(board)

        for _ in range(1000):
            result = sim_board.is_win("B" if current_player == 1 else "W")
            if result != 0:
                return 0 if result == -1 else result  # -1 is tie, return 0

            possible_moves_nested = sim_board.get_all_possible_moves(current_player)
            possible_moves = [m for sublist in possible_moves_nested for m in sublist]

            if not possible_moves:
                return self.opponent[current_player]  # If no moves, opponent wins

            move = max(possible_moves, key=lambda m: self.evaluate_board_with_move(sim_board, m, current_player))

            try:
                sim_board.make_move(move, current_player)
            except InvalidMoveError:
                continue  # Skip and retry
            
            current_player = self.opponent[current_player]

        return 0  # If no decisive outcome, count as a tie

    def evaluate_board_with_move(self, board, move, player):
        """Applies a move to a temporary board and evaluates it."""
        new_board = copy.deepcopy(board)
        try:
            new_board.make_move(move, player)
            return self.evaluate_board(new_board, player)
        except InvalidMoveError:
            return -float("inf")  # Assign a very low score to invalid moves

    def evaluate_board(self, board, color):
        """Calculates material and king advantage."""
        my_pieces = sum(1 for row in board.board for piece in row if piece and piece.color == color)
        opponent_pieces = sum(1 for row in board.board for piece in row if piece and piece.color == self.opponent[color])
        return my_pieces - opponent_pieces
