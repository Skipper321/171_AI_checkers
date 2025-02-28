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


class MCTSNode: 
    """This represents a node in MCTS"""

    def __init__(self, board, move=None, parent=None):
        self.board = copy.deepcopy(board)  # Store board state as deepcopy
        self.move = move  # Move that led to this node
        self.parent = parent  # Parent node
        self.children = []  # Child nodes
        self.visits = 0  # Number of times node has been visited
        self.wins = 0  # Number of wins from this node

    def is_fully_expanded(self):
        """Returns True if all possible moves have been explored."""
        return len(self.children) == len(self.board.get_all_possible_moves(self.board.current_player))

    def best_child(self, exploration_weight=1.4):
        """Selects the child node with the highest UCT value."""
        return max(self.children, key=lambda node: (node.wins / (node.visits + 1)) + 
                   exploration_weight * math.sqrt(math.log(self.visits + 1) / (node.visits + 1)))

class StudentAI:
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2  # AI plays as Player 2
        self.opponent = {1: 2, 2: 1}
        self.simulation_time = 480 # 8 min time in seconds 

    

    def get_move(self, move):
        """Determines the AI's move using MCTS """
    
        # Ensure move is a Move object before processing
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color]) 
        else:
            self.color = 1  

        # Run MCTS to determine the best move
        best_move = self.mcts_search(self.board, self.simulation_time)

        # Ensure move is valid
        if best_move is None:
            return Move([])  # No valid move found

        self.board.make_move(best_move, self.color)
        return best_move  # Ensure we always return a properly formatted Move object


    def mcts_search(self, board, time_limit = 480): 
        """ Determine AI move using MCTS
            board: refers to current game state 
            time_limit: refers to time limit for MCTS (in seconds) in this case 8 min time limit per move 
            returns: best move found 
        """
        # Set root as Node object of current game state 
        root = MCTSNode(board)
        # initailize current start time 
        start_time = time.time() 

        # Current time - start time is less than time limit 
        while time.time() - start_time < time_limit: 
            # start at root 
            node = root 

            # Traverse Tree using UCT formula 
            while node.is_fully_expanded() and node.children: 
                node = node.best_child() 
    
            # First get all possible moves 
            possible_moves = board.get_all_possible_moves(board.current_player)

            # if not a terminal state, expand a new child node 
            if possible_moves and not node.is_fully_expanded():
                move = random.choice(m for sublist in possible_moves for m in sublist)

                # Create deep copy of board and apply the move
                new_board = copy.deepcopy(node.board)
                new_board.make_move(move, new_board.current_player)

                # Create new node for ths move
                new_node = MCTSNode(new_board, move, node)
                node.children.append(new_node)

                node = new_node # move to new node 

            # Simulate a random game to estimate the outcome 
            # HERE: need to implement simulate_random_game function 
            winner = self.simulate_random_game(node.board) 

            # Backpropagation to update win counts for the traversed path 
            while node: 
                node.visits = node.visits + 1 
                # Count ties as wins for the AI as well 
                if winner == board.current_player or winner == 0: 
                    node.wins = node.wins + 1
                # move backwards up the tree 
                node = node.parent

        # Choose the best move 
        best_child = root.best_child(exploration_weight=0)  # Choose most visited node
        
        # return best move 
        return best_child.move if best_child else None

    # Need to implement 
    def simulate_random_game(self, board): 
        """ Simulates random game from given board state until winner is found 
        board: Current Board state
        Return "Winner" where 0 - tie, 1 - player 1 wins, 2 - player 2 wins 
        """
        

















        




