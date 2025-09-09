import unittest
from backgammon.core.game import BackgammonGame
from backgammon.core.board import Board
from backgammon.core.player import Player
from backgammon.core.dice import Dice
from backgammon.core.checker import Checker

class TestCore(unittest.TestCase):
    def test_game_instance(self):
        game = BackgammonGame()
        self.assertIsInstance(game, BackgammonGame)

    def test_board_points(self):
        board = Board()
        self.assertEqual(len(board.__points__), 24)

    def test_player_creation(self):
        player = Player("Alice", "white")
        self.assertEqual(player.__name__, "Alice")
        self.assertEqual(player.__color__, "white")
        self.assertEqual(player.__checkers__, 15)

    def test_dice_roll_tuple_range(self):
        dice = Dice()
        a, b = dice.roll()
        self.assertIn(a, range(1, 7))
        self.assertIn(b, range(1, 7))
        self.assertIsInstance(dice.is_double(), bool)

    def test_checker_creation(self):
        checker = Checker("black")
        self.assertEqual(checker.__color__, "black")

if __name__ == "__main__":
    unittest.main()
