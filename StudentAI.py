from BoardClasses import Board, InvalidMoveError, InvalidParameterError
from Move import Move
import random
import copy # for using deepcopy()

# HOW TO RUN: 

# Need to cd into Tools folder
# cd /home/ics-home/Checkers_Student/Checkers_Student-1/Tools

# Then run this in terminal: 
# python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Random_AI/main.py


class StudentAI:
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2  # AI plays as Player 2
        self.opponent = {1: 2, 2: 1}

    

    def get_move(self, move):
        #print(f"DEBUG: Received move in get_move(): {move}")  
        #print(f"DEBUG: AI is playing as color {self.color}")  

        # Ensure move is a Move object before processing
        if len(move) != 0:
            if not isinstance(move, Move):
                print(f"ERROR: Move {move} is not a Move object! Converting...")
                #Convert BoardClasses.Move to Move
                if hasattr(best_move, 'seq'):  
                    move = Move(move.seq)  # Force conversion
                    
                else:  # Handle move strings if needed
                    move = Move.from_str(str(move))  

            # Get all possible moves BEFORE making the move
            legal_moves = self.board.get_all_possible_moves(self.opponent[self.color])
            #print(f"DEBUG: Legal moves BEFORE making move for opponent ({self.opponent[self.color]}): {legal_moves}")

            # Check if the move is in the legal moves list
            if move.seq not in [m.seq for sublist in legal_moves for m in sublist]:
                print(f"WARNING: Move {move} is NOT in the legal moves list! Skipping execution.")
            else:
                try:
                    self.board.make_move(move, self.opponent[self.color])
                    #print(f"DEBUG: Successfully made move: {move}")
                except InvalidMoveError:
                    #print(f"ERROR: Move {move} is invalid according to make_move()!")
                    return Move([])  

        else:
            self.color = 1  

        # AI selects its move using Minimax
        best_move = self.minimax_decision(self.board, self.color, depth=3)

        #Ensure best_move is a valid Move object
        if hasattr(best_move, 'seq'):  
            #print(f"DEBUG: best_move is a BoardClasses.Move. Converting to Move.")
            best_move = Move(best_move.seq)  

        elif not isinstance(best_move, Move):  
            #print(f"ERROR: best_move is NOT a Move object! Converting... {best_move}")  
            best_move = Move(best_move)  

        # Validate best_move sequence before returning
        if not best_move or not isinstance(best_move.seq, list) or len(best_move.seq) == 0:
            #print("ERROR: best_move.seq is empty or incorrect format! Returning an empty move.")
            return Move([])

        # FINAL DEBUGGING BEFORE RETURN
        #print(f"DEBUG: AI is about to return move: {best_move} (type: {type(best_move)})")
        #print(f"DEBUG: AI move as string: {str(best_move)}")

        self.board.make_move(best_move, self.color)
        return best_move  # Ensure we always return a properly formatted Move object



    def minimax_decision(self, board, color, depth=3):
        """Chooses the best move using Minimax with Alpha-Beta Pruning."""
        best_move = None
        best_value = float('-inf')

        legal_moves = board.get_all_possible_moves(color)
        #print(f"DEBUG: Legal moves for AI (color {color}): {legal_moves}")
        if not legal_moves:
            return Move([])  # Empty Move List if - No moves available

        for move_list in legal_moves:
            for move in move_list:
                new_board = copy.deepcopy(board)
                new_board.make_move(move, color)

                value = self.minimax(new_board, depth - 1, False, self.opponent[color], float('-inf'), float('inf'))

                if value > best_value:
                    best_value = value
                    best_move = move

        if best_move is None:
            #print("ERROR: AI failed to select a valid move!")
            return Move([])  

        #print(f"DEBUG: AI selected move (validated): {best_move}")

        # Ensure minimax decision always returns a Move object
        if isinstance(best_move, tuple) or isinstance(best_move, list):
            #print("ERROR: best_move is a tuple/list instead of Move! Converting...")
            best_move = Move(best_move)

        return best_move

    def minimax(self, board, depth, is_maximizing, color, alpha, beta):
        """Minimax algorithm with Alpha-Beta Pruning."""
        if depth == 0 or board.is_win(color) != 0:
            return self.evaluate_board(board, color)

        possible_moves = board.get_all_possible_moves(color)
        if not possible_moves:
            return -1000 if is_maximizing else 1000  # Assign large loss values

        if is_maximizing:
            max_eval = float('-inf')
            for move_set in possible_moves:
                for move in move_set:
                    new_board = copy.deepcopy(board)
                    new_board.make_move(move, color)

                    eval = self.minimax(new_board, depth - 1, False, self.opponent[color], alpha, beta)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)

                    if beta <= alpha:
                        break  # Alpha-Beta Pruning
            return max_eval
        else:
            min_eval = float('inf')
            for move_set in possible_moves:
                for move in move_set:
                    new_board = copy.deepcopy(board)
                    new_board.make_move(move, color)

                    eval = self.minimax(new_board, depth - 1, True, self.opponent[color], alpha, beta)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)

                    if beta <= alpha:
                        break  # Alpha-Beta Pruning
            return min_eval

    def evaluate_board(self, board, color):
        """Simple heuristic: AI pieces - Opponent pieces."""
        my_pieces = sum(1 for row in board.board for piece in row if piece and piece.color == color)
        opponent_pieces = sum(1 for row in board.board for piece in row if piece and piece.color == self.opponent[color])
        
        return my_pieces - opponent_pieces  # Simple piece advantage heuristic
