from BoardClasses import Move, Board, InvalidMoveError, InvalidParameterError
import random

class StudentAI:
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2  # AI plays as Player 2
        self.opponent = {1: 2, 2: 1}

    def copy_board(self, board):
        """Manually creates a deep copy of the board."""
        new_board = Board(self.col, self.row, self.p)  # Create a new board
        new_board.board = [row[:] for row in board.board]  # Copy board state
        new_board.turn = board.turn  # Copy turn information
        return new_board

    def get_move(self, move):
        print(f"DEBUG: Received move in get_move(): {move}")  

        if len(move) != 0:
            if not isinstance(move, Move):
                print(f"ERROR: Move {move} is not a Move object! Converting...")
                move = Move(move)  

            # **Check legal moves BEFORE making the move**
            legal_moves = self.board.get_all_possible_moves(self.opponent[self.color])
            print(f"DEBUG: Legal moves BEFORE making move: {legal_moves}")

            if move.seq not in [m.seq for sublist in legal_moves for m in sublist]:
                print(f"ERROR: Move {move} is NOT in legal moves list!")
                return Move([])

            try:
                self.board.make_move(move, self.opponent[self.color])
            except InvalidMoveError:
                print(f"ERROR: Move {move} is invalid according to make_move()!")
                return Move([])  

        else:
            self.color = 1  

        # AI selects its move
        best_move = self.minimax_decision(self.board, self.color, depth=3)
    
        if not best_move or not isinstance(best_move, Move):
            print("ERROR: AI returned an invalid move! Returning an empty move.")
            return Move([])  

        print(f"DEBUG: AI selected move (raw): {best_move}")  
        self.board.make_move(best_move, self.color)
        return best_move


    def minimax_decision(self, board, color, depth=3):
        """Chooses the best move using Minimax with Alpha-Beta Pruning."""
        best_move = None
        best_value = float('-inf')

        possible_moves = board.get_all_possible_moves(color)
        if not possible_moves:
            return None  # No moves available

        for move_set in possible_moves:
            for move in move_set:
                new_board = self.copy_board(board)
                new_board.make_move(move, color)

                value = self.minimax(new_board, depth - 1, False, self.opponent[color], float('-inf'), float('inf'))

                if value > best_value:
                    best_value = value
                    best_move = move

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
                    new_board = board.copy_board()
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
                    new_board = board.copy_board()
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
