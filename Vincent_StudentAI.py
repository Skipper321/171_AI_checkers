from random import randint
from BoardClasses import Move
from BoardClasses import Board
import copy

class StudentAI():
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()

        self.color = 2  
        self.opponent = {1: 2, 2: 1}
        # Adjustable
        self.search_depth = 3

    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            # If this is the first move (no opponent move received), we choose to be player 1 (Black)
            self.color = 1

        # Get all possible moves for our current turn.
        moves_nested = self.board.get_all_possible_moves(self.color)
        # Gather all moves into a list
        all_moves = [m for sublist in moves_nested for m in sublist]

        # If no moves are available, return an empty move.
        if not all_moves:
            return Move([])

        best_move = None
        best_score = float('-inf')

        # Minimax
        for m in all_moves:
            new_board = self.simulate_move(self.board, m, self.color)
            score = self.minimax(new_board, self.search_depth - 1, False, self.color, float('-inf'), float('inf'))
            if score > best_score:
                best_score = score
                best_move = m

        # Make the actual move on our board and return it.
        self.board.make_move(best_move, self.color)
        return best_move

    def simulate_move(self, board, move, player):
        """
        Returns a deep-copied board after applying move for player.
        """
        new_board = copy.deepcopy(board)
        try:
            new_board.make_move(move, player)
        except Exception as e:
            # Should not happen because we only simulate valid moves.
            pass
        return new_board

    def minimax(self, board, depth, maximizingPlayer, ai_player, alpha, beta):
        """
        Performs minimax search with alpha-beta pruning.
        Parameters:
            board: current board state
            depth: search depth remaining
            maximizingPlayer: bool, True if it is the AI’s turn, False for opponent
            ai_player: our player number (1 or 2)
            alpha, beta: bounds for pruning
        Returns:
            a numeric evaluation score
        """
        # Determine whose turn it is.
        current_player = ai_player if maximizingPlayer else self.opponent[ai_player]
        # For board.is_win, we need to supply a color string.
        current_color = 'B' if current_player == 1 else 'W'
        win_status = board.is_win(current_color)
        # win_status returns:
        #   -1 if tie, 0 if game not over, or the winning player number (1 or 2).
        if win_status != 0:
            if win_status == ai_player:
                return 10000  
            elif win_status == -1:
                return 0      # Tie is neutral.
            else:
                return -10000 
        # If we have reached the search depth, evaluate the board.
        if depth == 0:
            return self.evaluate_board(board, ai_player)

        moves_nested = board.get_all_possible_moves(current_player)
        all_moves = [m for sublist in moves_nested for m in sublist]
        if not all_moves:
            return self.evaluate_board(board, ai_player)

        if maximizingPlayer:
            max_eval = float('-inf')
            for m in all_moves:
                new_board = self.simulate_move(board, m, current_player)
                eval_score = self.minimax(new_board, depth - 1, False, ai_player, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cut-off
            return max_eval
        else:
            min_eval = float('inf')
            for m in all_moves:
                new_board = self.simulate_move(board, m, current_player)
                eval_score = self.minimax(new_board, depth - 1, True, ai_player, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cut-off
            return min_eval

    def evaluate_board(self, board, ai_player):
        """
        A simple evaluation function that sums the values of pieces.
        Adjust the piece values as desired.
        """
        # Define colors for our AI and our opponent.
        my_color = 'B' if ai_player == 1 else 'W'
        opp_color = 'W' if ai_player == 1 else 'B'
        score = 0
        # Loop through every cell on the board.
        for row in board.board:
            for cell in row:
                if cell.color == my_color:
                    score += 15 if cell.is_king else 10
                elif cell.color == opp_color:
                    score -= 15 if cell.is_king else 10
        return score
