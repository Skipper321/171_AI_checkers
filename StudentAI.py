import copy
import math 
import random
import time
from BoardClasses import Board, InvalidMoveError
from Move import Move

# Commands 
# python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Random_AI/main.py
# python3 AI_Runner.py 8 8 2 n ../src/checkers-python/main.py

# cd /home/ics-home/Checkers_Student/Checkers_Student-1/Tools

# Running against poor AI: 
# python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Poor_AI/main.py

# Black is player 1, White is player 2 

# Monte Carlo Tree Search (MCTS) Node
class MCTSNode:
    def __init__(self, board, move=None, parent=None, current_player=1):
        self.board = board  # No deep copy here, we manage copies externally
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.current_player = current_player
    
    def get_student_ai(self):
        """ Traverse up the tree to find the root StudentAI instance. """
        node = self
        while node.parent is not None:
            node = node.parent
        return node.student_ai  # Assuming we add this reference at root

    def is_fully_expanded(self):
        valid_moves = self.board.get_all_possible_moves(self.current_player)
        return len(self.children) >= sum(len(moves) for moves in valid_moves)

    def best_child(self, exploration_weight=0.7):
        if not self.children:
            return None

        student_ai = self.get_student_ai()  # Get access to StudentAI instance
        return max(self.children, key=lambda node: 
            (node.wins / (node.visits + 1)) + 
            exploration_weight * math.sqrt(math.log(self.visits + 1) / (node.visits + 1)) +
            0.1 * student_ai.evaluate_board(node.board, node.current_player))


class StudentAI:
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.global_board = copy.deepcopy(self.board)  # Store the global board state
        self.color = 2
        self.opponent = {1: 2, 2: 1}
        self.base_time = 480
        self.simulation_time = self.base_time/6

        self.turn_count = 0

        # Cache for winnable states
        self.state_cache = {}
        self.cache_limit = 500  # Prevent excessive memory usage


    def board_signature(self, board):
        """Creates a unique hashable signature for a board state."""
        return ''.join(str(piece) if piece else '.' for row in board.board for piece in row)

    def store_winning_state(self, board, move=None):
        """Stores a board state if it's a winning position for the AI."""
        board_hash = self.board_signature(board)
        self.state_cache[board_hash] = move if move else True

        # Remove old entries if cache size exceeds limit
        if len(self.state_cache) > self.cache_limit:
            self.state_cache.pop(next(iter(self.state_cache)))  

    # Apparently MCTS already does this so we can maybe remove this function?  (but we also now pick the best move in MCTS rather than a random move) 
    def filter_best_moves(self, board, possible_moves):
        """Prioritize moves that force PoorAI into bad trades."""
        
        capturing_moves = [m for m in possible_moves if len(m.seq) > 1]
        if capturing_moves:
            return capturing_moves  # Always prioritize jumps

        king_promotion_moves = [m for m in possible_moves if self.can_promote(m)]
        if king_promotion_moves:
            return king_promotion_moves

        # Force PoorAI into a bad trade
        forcing_moves = []
        for move in possible_moves:
            new_board = copy.deepcopy(board)
            try:
                new_board.make_move(move, self.color)
                if self.exposes_to_capture(new_board, move):
                    forcing_moves.append(move)  # Moves that force PoorAI to respond
            except InvalidMoveError:
                continue

        if forcing_moves:
            return forcing_moves  # Prioritize forcing the opponent into a bad position

        # Avoid unsafe moves
        safe_moves = []
        for move in possible_moves:
            new_board = copy.deepcopy(board)
            try:
                new_board.make_move(move, self.color)
                if not self.exposes_to_capture(new_board, move):  # Only keep safe moves
                    safe_moves.append(move)
            except InvalidMoveError:
                continue

        if safe_moves:
            possible_moves = safe_moves  # Replace with safe moves only

        # Select the best 50% of safe moves
        scored_moves = [(move, self.evaluate_board(board, self.color)) for move in possible_moves]
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [move[0] for move in scored_moves[:len(scored_moves)//2]]

    # Apparently MCTS already does this so we can maybe remove this function? 
    def exposes_to_capture(self, board, move):
        """Checks if the piece's new position is threatened after the move."""
        new_board = copy.deepcopy(board)
        try:
            new_board.make_move(move, self.color)
        except InvalidMoveError:
            return False  # If move is invalid, assume it's safe

        # Get opponent moves after the move is made
        opponent_moves = [m for sublist in new_board.get_all_possible_moves(self.opponent[self.color]) for m in sublist]

        # Check if the move's new position is in any capture sequence
        new_pos = move.seq[-1]  # The final position of the moved piece
        return any(new_pos in m.seq for m in opponent_moves if len(m.seq) > 1)

            
    # Apparently MCTS already does this so we can maybe remove this function? 
    def can_promote(self, move):
        last_row = 0 if self.color == 1 else self.row - 1
        return any(pos[0] == last_row for pos in move.seq)


    def get_move(self, move):
        """Determines the AI's move using Opening Book or MCTS with move filtering."""
        
        if len(move) != 0:
            try:
                self.board.make_move(move, self.opponent[self.color])
            except InvalidMoveError:
                return Move([])  # Skip move if it's invalid
        else: 
            self.color = 1

        self.global_board = copy.deepcopy(self.board)  # Store the global board state

        self.turn_count += 1  # Update turn count

        # Filter moves first 
        possible_moves = [m for sublist in self.board.get_all_possible_moves(self.color) for m in sublist]
        best_moves = self.filter_best_moves(self.board, possible_moves)
        
        best_move = self.mcts_search(self.global_board, self.simulation_time, best_moves)

        # Fallback: If MCTS fails, pick a valid move randomly
        if best_move is None:
            best_move = random.choice(best_moves) if best_moves else Move([])

        try:
            self.board.make_move(best_move, self.color)
        except InvalidMoveError:
            return Move([])

        

        return best_move

    def mcts_search(self, board, num_simulations=1000, possible_moves=None):
        """Performs Monte Carlo Tree Search with dynamic simulation count."""
        
        board_hash = self.board_signature(board)

        # If seen this board before and won from it, return a known good move
        if board_hash in self.state_cache:
            if possible_moves:
                return random.choice(possible_moves)  # Pick a move from cache
            return None

        # Create root node
        root = MCTSNode(copy.deepcopy(board), current_player=self.color)
        root.student_ai = self  # Reference to StudentAI
        start_time = time.time()

        # **Dynamic Simulation Count** based on game state
        # If few pieces left, increase simulations
        num_pieces = sum(1 for row in board.board for piece in row if piece)
        if num_pieces < 6:  
            num_simulations = 1500  # More accurate endgame play
        elif num_pieces < 12:
            num_simulations = 1200
        else:
            num_simulations = max(200, min(1000, len(board.get_all_possible_moves(self.color)) * 100))

        for _ in range(num_simulations):
            node = root

            # Selection: Traverse down the tree
            while node.is_fully_expanded() and node.children:
                node = node.best_child()

            # Expansion
            possible_moves = node.board.get_all_possible_moves(node.current_player)
            if not possible_moves:
                return None

            flattened_moves = [m for sublist in possible_moves for m in sublist]
            if not flattened_moves:
                return None

            move = max(flattened_moves, key=lambda m: self.evaluate_board_with_move(node.board, m, node.current_player))


            # Simulate move
            new_board = copy.deepcopy(node.board)
            try:
                new_board.make_move(move, node.current_player)
                new_node = MCTSNode(new_board, move, node, current_player=self.opponent[node.current_player])
                node.children.append(new_node)
                node = new_node
            except InvalidMoveError:
                continue

            # Simulation
            winner = self.simulate_random_game(new_board)

            # Store winning board states in cache
            if winner == self.color:
                self.store_winning_state(new_board)

            # Backpropagation
            while node:
                node.visits += 1
                if winner == self.color or winner == 0:  # 0 means draw
                    node.wins += 1
                node = node.parent

        return root.best_child(exploration_weight=0).move

    def evaluate_board(self, board, color):
        """Enhanced evaluation: considers material, kinging potential, mobility, and board control."""
        
        my_score = 0
        opponent_score = 0
        my_kings = 0
        opponent_kings = 0
        my_mobility = 0
        opponent_mobility = 0
        my_endgame_bonus = 0

        for r, row in enumerate(board.board):
            for c, piece in enumerate(row):
                if piece:
                    value = 5 if piece.is_king else 1  # Kings are stronger
                    position_bonus = 0
                    endgame_bonus = 0
                    
                    # Favor central control
                    if 2 <= r <= 5 and 2 <= c <= 5:
                        position_bonus += 0.5  

                    # Encourage kinging
                    king_bonus = (7 - r if color == 1 else r) * 0.3  
                    
                    # Kings in endgame should dominate the board
                    if piece.is_king:
                        value += 2  # Boost king value
                        if 0 < r < 7 and 0 < c < 7:
                            endgame_bonus += 1  # Kings in the center are more powerful
                        my_kings += 1 if piece.color == color else 0
                        opponent_kings += 1 if piece.color != color else 0

                    # Mobility Bonus: Reward pieces that can move
                    mobility_bonus = 0.1 * len(board.get_all_possible_moves(color))

                    # Penalty for being stuck at the edges (columns 0 and 7)
                    edge_penalty = -0.5 if c == 0 or c == 7 else 0  

                    if piece.color == color:
                        my_score += value + position_bonus + king_bonus + mobility_bonus + edge_penalty
                    else:
                        opponent_score += value + position_bonus + king_bonus + mobility_bonus + edge_penalty

        # Late game: if both players have kings, emphasize restriction
        if my_kings > 2 and opponent_kings > 0:
            my_score += my_endgame_bonus * 2  # More control in endgame = better

        # Penalize if the opponent has way more mobility
        if opponent_mobility > my_mobility:
            my_score -= (opponent_mobility - my_mobility) * 0.1 

        return my_score - opponent_score  # Higher score favors AI

    def evaluate_board_with_move(self, board, move, player):
        """Applies a move to a temporary board and evaluates it."""
        new_board = copy.deepcopy(board)  # Make a copy to avoid modifying original
        try:
            new_board.make_move(move, player)
            return self.evaluate_board(new_board, player)  # Evaluate board after move
        except InvalidMoveError:
            return -float("inf")  # Assign a very low score to invalid moves



    def simulate_random_game(self, board):
        sim_board = copy.deepcopy(board)
        current_player = self.color

        for _ in range(20):  # Max simulation depth
            result = sim_board.is_win(current_player)
            if result != 0:
                return result  # Game over

            possible_moves = [m for sublist in sim_board.get_all_possible_moves(current_player) for m in sublist]
            if not possible_moves:
                return self.opponent[current_player]

            # **Choose the best move instead of random**
            best_move = max(possible_moves, key=lambda m: self.evaluate_board(sim_board, current_player))
            try:
                sim_board.make_move(best_move, current_player)
                current_player = self.opponent[current_player]
            except InvalidMoveError:
                continue

        return 0  # Draw if no winner

