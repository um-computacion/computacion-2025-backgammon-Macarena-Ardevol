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

    def test_game_has_board_and_no_players(self):
        game = BackgammonGame()
        self.assertEqual(len(game.__players__), 0)

    def test_game_add_player(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        self.assertEqual(len(game.__players__), 1)
        self.assertEqual(game.current_player().__color__, "white")

    def test_game_turn_rotation(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        self.assertEqual(game.current_player().__color__, "white")
        game.next_turn()
        self.assertEqual(game.current_player().__color__, "black")
        game.next_turn()
        self.assertEqual(game.current_player().__color__, "white")

    def test_board_initial_setup_totals_and_spots(self):
        board = Board()
        board.setup_initial()
        # Totales
        self.assertEqual(board.count_total(Board.WHITE), 15)
        self.assertEqual(board.count_total(Board.BLACK), 15)
        # Spots clave (convención de índices 0..23)
        self.assertEqual(board.get_point(23), 2)    # blancas
        self.assertEqual(board.get_point(12), 5)
        self.assertEqual(board.get_point(7), 3)
        self.assertEqual(board.get_point(5), 5)
        self.assertEqual(board.get_point(0), -2)    # negras
        self.assertEqual(board.get_point(11), -5)
        self.assertEqual(board.get_point(16), -3)
        self.assertEqual(board.get_point(18), -5)

    def test_game_start_turn_with_fixed_roll(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        r = game.start_turn((3, 4))
        self.assertEqual(r, (3, 4))
        self.assertEqual(game.pips(), (3, 4))

    def test_game_start_turn_double_generates_four_pips(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        game.start_turn((5, 5))
        self.assertEqual(game.pips(), (5, 5, 5, 5))

if __name__ == "__main__":
    unittest.main()
