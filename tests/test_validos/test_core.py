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

    def test_cli_app_import(self):
        from backgammon.cli.app import main
        self.assertTrue(callable(main))

    def test_game_setup_board_totals(self):
        game = BackgammonGame()
        game.setup_board()
        self.assertEqual(game.board().count_total(Board.WHITE), 15)
        self.assertEqual(game.board().count_total(Board.BLACK), 15)

    def test_cli_format_board_summary(self):
        from backgammon.cli.app import format_board_summary
        board = Board()
        board.setup_initial()
        s = format_board_summary(board)
        self.assertIn("Resumen tablero:", s)
        self.assertIn("[23, 12, 7, 5]", s)
        self.assertIn("[0, 11, 16, 18]", s)

    def test_cli_entrypoint_exists(self):
        from backgammon.cli.app import main
        self.assertTrue(callable(main))

    def test_board_owner_and_count(self):
        board = Board()
        board.setup_initial()
        self.assertEqual(board.owner_at(23), Board.WHITE)
        self.assertEqual(board.count_at(23), 2)
        self.assertEqual(board.owner_at(0), Board.BLACK)
        self.assertEqual(board.count_at(0), 2)
        self.assertEqual(board.owner_at(10), 0)
        self.assertEqual(board.count_at(10), 0)

    def test_board_is_blocked_rules(self):
        board = Board()
        board.setup_initial()
        # Para WHITE, los puntos negros con 2+ fichas bloquean
        self.assertTrue(board.is_blocked(11, Board.WHITE))
        self.assertFalse(board.is_blocked(12, Board.WHITE))
        # Para BLACK, los puntos blancos con 2+ fichas bloquean
        self.assertTrue(board.is_blocked(12, Board.BLACK))
        self.assertFalse(board.is_blocked(11, Board.BLACK))

    def test_board_dest_from_direction(self):
        board = Board()
        # WHITE se mueve hacia índices menores
        self.assertEqual(board.dest_from(12, 3, Board.WHITE), 9)
        # BLACK se mueve hacia índices mayores
        self.assertEqual(board.dest_from(11, 6, Board.BLACK), 17)

    def test_board_can_move_en_vacio_y_propio(self):
        board = Board()
        board.setup_initial()
        # WHITE: 7 -> 6 (vacío), 7 -> 5 (propio)
        self.assertTrue(board.can_move(7, 1, Board.WHITE))
        self.assertTrue(board.can_move(7, 2, Board.WHITE))
        # BLACK: 16 -> 17 (vacío), 16 -> 18 (propio)
        self.assertTrue(board.can_move(16, 1, Board.BLACK))
        self.assertTrue(board.can_move(16, 2, Board.BLACK))

    def test_board_can_move_bloqueado_devuelve_false(self):
        board = Board()
        board.setup_initial()
        # Destinos con 5 fichas rivales están bloqueados
        self.assertFalse(board.can_move(12, 1, Board.WHITE))  # a 11 (negro x5)
        self.assertFalse(board.can_move(11, 1, Board.BLACK))  # a 12 (blanco x5)

    def test_board_move_aplica_cambios(self):
        board = Board()
        board.setup_initial()
        # WHITE 7 -> 6
        self.assertEqual(board.get_point(7), 3)
        self.assertEqual(board.get_point(6), 0)
        dest = board.move(7, 1, Board.WHITE)
        self.assertEqual(dest, 6)
        self.assertEqual(board.get_point(7), 2)
        self.assertEqual(board.get_point(6), 1)


if __name__ == "__main__":
    unittest.main()
