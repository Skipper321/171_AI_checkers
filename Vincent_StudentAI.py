import copy
import math 
import random
import time
from BoardClasses import Board, InvalidMoveError, InvalidParameterError
from Move import Move

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
        # Count total moves available for the current player
        return len(self.children) >= sum(len(moves) for moves in valid_moves)

    def best_child(self, exploration_weight=1.4):
        remaining_pieces = sum(
            1 for row in self.board.board for piece in row if piece and piece.color in ["B", "W"]
        )

        # **Reduce exploration as the game progresses**
        if remaining_pieces <= 6:  
            exploration_weight = 0.5  # Less random exploration in endgame

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
        # Added cache for board moves to speed up simulation
        self.move_cache = {}

    def board_signature(self, board):
        """Generates a unique string signature for the board state."""
        sig = []
        for row in board.board:
            for cell in row:
                if cell is None:
                    sig.append("X")
                else:
                    sig.append(cell.get_color())
        return ''.join(sig)

    def get_move(self, move):
        """Determines the AI's move using MCTS"""

        print(f"🔍 AI is playing as: {self.color} (1 = Black, 2 = White)")
        print(f"🔍 Opponent is playing as: {self.opponent[self.color]}")
        print(f"🔍 Board Memory Address BEFORE Opponent Move: {id(self.board)}")
        print("📌 Board BEFORE applying opponent move:")
        self.board.show_board()

        if len(move) != 0:
            try:
                self.board.make_move(move, self.opponent[self.color])
                print("📌 Board AFTER applying opponent move:")
                self.board.show_board()
            except InvalidMoveError:
                print("⚠️ WARNING: Invalid opponent move attempted!")
                return Move([])
        else: 
            self.color = 1

        # 🚨 Force update self.board reference to ensure opponent's move is applied
        self.board = self.board  # Ensures AI isn't working with a stale copy
        print(f"🔍 Board Memory Address AFTER Opponent Move: {id(self.board)}")

        best_move = self.mcts_search(self.board, self.simulation_time)

        # **NEW: Fallback if MCTS returns an empty move.**
        valid_moves_nested = self.board.get_all_possible_moves(self.color)
        all_valid_moves = [m for sublist in valid_moves_nested for m in sublist]
        if best_move is None or len(best_move.seq) == 0:
            if all_valid_moves:
                best_move = random.choice(all_valid_moves)
                print("🔄 Fallback: using a random valid move.")
            else:
                print("⚠️ No valid moves available for AI!")
                return Move([])

        valid_moves = [m.seq for sublist in self.board.get_all_possible_moves(self.color) for m in sublist]
        if best_move.seq not in valid_moves:
            print(f"⚠️ WARNING: AI selected an invalid move: {best_move}")
            return Move([])

        print(f"🎯 AI selects final move: {best_move}")

        try:
            self.board.make_move(best_move, self.color)
        except InvalidMoveError:
            print("❌ AI move was invalid according to game rules!")
            return Move([])

        print("📌 Board AFTER AI move:")
        self.board.show_board()

        return best_move

    def mcts_search(self, board, time_limit=10):
        # Create a deep copy of the board to avoid modifying the real game state 
        root = MCTSNode(copy.deepcopy(board), current_player=self.color)
        start_time = time.time()

        while time.time() - start_time < time_limit:
            node = root

            # **Selection: Traverse down the tree using the best UCT child**
            while node.is_fully_expanded() and node.children:
                node = node.best_child()

            # **Expansion: Pick a new move to explore**
            # Use the node's current player's moves rather than always self.color
            possible_moves = node.board.get_all_possible_moves(node.current_player)

            # 🔥 **Prioritize forced captures (jumps)**
            jump_moves = [m for sublist in possible_moves for m in sublist if len(m.seq) > 1]
            if jump_moves:
                possible_moves = [jump_moves]  # Override with forced jumps

            flattened_moves = [m for sublist in possible_moves for m in sublist]

            if not flattened_moves:
                return None  # No moves available

            move = random.choice(flattened_moves)

            # **Create a fresh deep copy of the board for each move**
            new_board = copy.deepcopy(node.board)
            try:
                # Apply move on new_board using the node's current player
                new_board.make_move(move, node.current_player)
                # **Only create a new node if the move was valid**
                # New node's current player is switched to the opponent.
                new_node = MCTSNode(new_board, move, node, current_player=self.opponent[node.current_player])
                node.children.append(new_node)
                node = new_node
            except InvalidMoveError:
                continue  # Skip invalid moves

            # **Simulation: Run random playouts**
            winner = self.simulate_random_game(new_board, node.current_player)

            # **Backpropagation: Update node statistics**
            while node:
                node.visits += 1
                if winner == self.color or winner == 0:  # 0 means draw
                    node.wins += 1
                node = node.parent

        return root.best_child(exploration_weight=0).move

    def simulate_random_game(self, board, current_player):
        """Simulates a game but stops early if a strong advantage is found."""
        sim_board = copy.deepcopy(board)
        # Increased simulation length from 10 to 20 moves.
        for _ in range(20):
            result = sim_board.is_win("B" if current_player == 1 else "W")
            if result != 0:
                return 0 if result == -1 else result  # -1 is tie, return 0
            # Early stopping: if AI leads by 3 pieces, assume AI will win
            if self.evaluate_board(sim_board, self.color) >= 3:
                return self.color
            # Use cached moves if available
            sig = self.board_signature(sim_board) + "_" + str(current_player)
            if sig in self.move_cache:
                possible_moves_nested = self.move_cache[sig]
            else:
                possible_moves_nested = sim_board.get_all_possible_moves(current_player)
                self.move_cache[sig] = possible_moves_nested
            possible_moves = [move for sublist in possible_moves_nested for move in sublist]
            if not possible_moves:
                return self.opponent[current_player]  # If no moves, opponent wins
            move = random.choice(possible_moves)
            try:
                sim_board.make_move(move, current_player)
            except InvalidMoveError:
                continue  # Skip and retry
            current_player = self.opponent[current_player]
        return 0  # If no decisive outcome, count as a tie

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
