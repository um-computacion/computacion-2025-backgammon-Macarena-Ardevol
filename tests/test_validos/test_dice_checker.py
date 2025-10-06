import unittest
from backgammon.core.dice import Dice
from backgammon.core.checker import Checker
from backgammon.core.player import Player

class TestDiceCheckerPlayerValidos(unittest.TestCase):
    def test_dice_roll_tuple_range(self):
        dice = Dice()
        a, b = dice.roll()
        self.assertIn(a, range(1, 7))
        self.assertIn(b, range(1, 7))
        self.assertIsInstance(dice.is_double(), bool)

    def test_checker_creation(self):
        checker = Checker("black")
        self.assertEqual(checker.__color__, "black")

    def test_player_creation(self):
        player = Player("Alice", "white")
        self.assertEqual(player.__name__, "Alice")
        self.assertEqual(player.__color__, "white")
        self.assertEqual(player.__checkers__, 15)

if __name__ == "__main__":
    unittest.main()
