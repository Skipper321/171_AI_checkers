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

        if best_move is None:
            print("⚠️ AI failed to find a valid move!")
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
        """Performs MCTS to determine the best move while ensuring move validity."""

        # Create a deep copy of the board to avoid modifying the real game state
        root = MCTSNode(copy.deepcopy(board), current_player=self.color)
        start_time = time.time()

        while time.time() - start_time < time_limit:
            node = root

            # **Selection: Traverse down the tree using the best UCT child**
            while node.is_fully_expanded() and node.children:
                node = node.best_child()

            # **Expansion: Pick a new move to explore**
            possible_moves = node.board.get_all_possible_moves(self.color)
            flattened_moves = [m for sublist in possible_moves for m in sublist]

            if not flattened_moves:
                #print("⚠️ No valid moves found in MCTS search.")
                return None  # No moves available

            while flattened_moves:
                move = random.choice(flattened_moves)

                # **Create a fresh deep copy of the board for each move**
                new_board = copy.deepcopy(node.board)

                try:
                    new_board.make_move(move, self.color)
                    #print(f"✅ Move {move.seq} applied successfully in MCTS")

                    # **Only create a new node if the move was valid**
                    new_node = MCTSNode(new_board, move, node, self.color)
                    node.children.append(new_node)
                    node = new_node
                    break  # Exit loop if move was valid

                except InvalidMoveError:
                    #print(f"❌ Invalid move: {move.seq}, removing from consideration in copied board.")

                    # **Delete the invalid board to free memory**
                    del new_board

                    # **Remove the invalid move**
                    flattened_moves.remove(move)

                    if not flattened_moves:
                        #print("⚠️ No valid moves left after filtering out invalid ones.")
                        return None  # Prevent further invalid moves

            # **Simulation: Run random playouts**
            winner = self.simulate_random_game(new_board)

            # **Backpropagation: Update node statistics**
            while node:
                node.visits += 1
                if winner == self.color or winner == 0:  # 0 means draw
                    node.wins += 1
                node = node.parent

        # **Select the best move based on highest visit count**
        best_child = root.best_child(exploration_weight=0)

        if best_child:
            all_valid_moves = [m for sublist in board.get_all_possible_moves(self.color) for m in sublist]
            
            if best_child.move in all_valid_moves:
                #print(f"🎯 AI selects final move: {best_child.move.seq}")
                return best_child.move
            #else:
                #print("❌ ERROR: Move selected by MCTS is no longer valid. Searching for fallback move...")

        # **Fallback: Return a valid move from the real game board if MCTS fails**
        valid_moves = board.get_all_possible_moves(self.color)
        if valid_moves:
            fallback_move = random.choice(valid_moves[0])
            #print(f"🔄 Using fallback move: {fallback_move.seq}")
            return fallback_move

        #print("❌ ERROR: No valid move found by AI.")
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
