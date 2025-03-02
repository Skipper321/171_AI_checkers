import unittest
from BoardClasses import Board, InvalidMoveError
from StudentAI import StudentAI
from Move import Move


class TestOpponentMoveApplication(unittest.TestCase):

    def setUp(self):
        """Initialize game and AI before each test."""
        self.ai = StudentAI(8, 8, 2)
        self.board = self.ai.board

    def test_opponent_move_is_applied(self):
        """Ensure AI correctly applies the opponent's move before making its move."""
        opponent_move = Move([(2, 1), (3, 2)])  # Example valid move for opponent

        try:
            self.ai.get_move(opponent_move)  # Apply opponent's move
        except InvalidMoveError:
            self.fail("AI failed to apply opponent’s move correctly!")

        # Verify opponent's piece moved
        new_state = self.ai.board
        self.assertIsNotNone(new_state.board[3][2], "Opponent’s piece did not move correctly.")
        self.assertIsNone(new_state.board[2][1], "Opponent’s old position was not cleared.")

if __name__ == '__main__':
    unittest.main()

class TestMCTSMoveGeneration(unittest.TestCase):

    def setUp(self):
        """Initialize game and AI before each test."""
        self.ai = StudentAI(8, 8, 2)

    def test_mcts_generates_valid_moves(self):
        """Ensure MCTS only generates valid moves."""
        best_move = self.ai.mcts_search(self.ai.board, time_limit=2)

        valid_moves = [m.seq for sublist in self.ai.board.get_all_possible_moves(self.ai.color) for m in sublist]
        self.assertIn(best_move.seq, valid_moves, f"MCTS generated an invalid move: {best_move}")

if __name__ == '__main__':
    unittest.main()


class TestAIMoveApplication(unittest.TestCase):

    def setUp(self):
        """Initialize game and AI before each test."""
        self.ai = StudentAI(8, 8, 2)

    def test_ai_applies_own_move(self):
        """Ensure AI applies the move it selects."""
        move = self.ai.get_move([])  # AI selects move

        try:
            self.ai.board.make_move(move, self.ai.color)  # AI applies move
        except InvalidMoveError:
            self.fail("AI failed to apply its own move!")

        # Verify AI's move was applied correctly
        new_state = self.ai.board
        self.assertIsNotNone(new_state.board[move.seq[-1][0]][move.seq[-1][1]], "AI's piece did not move correctly.")
        self.assertIsNone(new_state.board[move.seq[0][0]][move.seq[0][1]], "AI's old position was not cleared.")

if __name__ == '__main__':
    unittest.main()

