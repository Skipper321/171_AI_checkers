from BoardClasses import Move, Board
import random


class StudentAI:
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = 2
        self.opponent = {1: 2, 2: 1}

    def move_to_string(self, move):
        """Convert a Move object to the expected string format."""
        if not move.seq:
            return "[-1]"  # No move case

        move_str = "-".join([f"({x},{y})" for x, y in move.seq])
        return f"[{move_str}]"  # Ensure brackets


    def get_move(self, move):
        """Select the best move using Minimax with Alpha-Beta Pruning."""

        print("get_move function entered")


        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1  # AI starts as player 1 if no move exists

        best_move = self.minimax_decision(self.board, self.color, depth=3)
        

        if not best_move or not isinstance(best_move, Move):
            print("ERROR: AI returned an invalid move!")
            return Move([])  # Return a no-op move to prevent crashing
    
        # Convert move to required string format
        move_str = self.move_to_string(best_move)
        print(f"DEBUG: AI selected move: {move_str}")  # Debugging output

        self.board.make_move(best_move, self.color)
        return best_move

    def minimax_decision(self, board, color, depth=3):
        """Choose the best move using Minimax with Alpha-Beta Pruning."""
        best_move = None
        best_value = float('-inf')

        possible_moves = board.get_all_possible_moves(color)
        for move_set in possible_moves:
            for move in move_set:
                new_board = board.clone()  # Clone board to simulate move
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
        if is_maximizing:
            max_eval = float('-inf')
            for move_set in possible_moves:
                for move in move_set:
                    new_board = board.clone()
                    new_board.make_move(move, color)

                    eval = self.minimax(new_board, depth - 1, False, self.opponent[color], alpha, beta)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)

                    if beta <= alpha:  # Alpha-Beta Pruning: Stop searching this branch
                        break
            return max_eval
        else:
            min_eval = float('inf')
            for move_set in possible_moves:
                for move in move_set:
                    new_board = board.clone()
                    new_board.make_move(move, color)

                    eval = self.minimax(new_board, depth - 1, True, self.opponent[color], alpha, beta)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)

                    if beta <= alpha:  # Alpha-Beta Pruning: Stop searching this branch
                        break
            return min_eval

    def evaluate_board(self, board, color):
        """Basic heuristic evaluation function."""
        my_pieces = 0
        opponent_pieces = 0
        my_kings = 0
        opponent_kings = 0

        for row in board.board:
            for piece in row:
                if piece.color == color:
                    my_pieces += 1
                    if piece.is_king:
                        my_kings += 1
                elif piece.color == self.opponent[color]:
                    opponent_pieces += 1
                    if piece.is_king:
                        opponent_kings += 1

        return (my_pieces - opponent_pieces) + (2 * (my_kings - opponent_kings))
