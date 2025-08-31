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
        self.assertEqual(len(board.points), 24)

    def test_player_creation(self):
        player = Player("Alice", "white")
        self.assertEqual(player.name, "Alice")
        self.assertEqual(player.color, "white")
        self.assertEqual(player.checkers, 15)

    def test_dice_roll_range(self):
        dice = Dice()
        roll = dice.roll()
        self.assertIn(roll, range(1, 7))

    def test_checker_creation(self):
        checker = Checker("black")
        self.assertEqual(checker.color, "black")

if __name__ == "__main__":
    unittest.main()
