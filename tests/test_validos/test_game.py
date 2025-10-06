import unittest
from backgammon.core.game import BackgammonGame
from backgammon.core.board import Board

class TestGameValidos(unittest.TestCase):
    def test_game_instance(self):
        game = BackgammonGame()
        self.assertIsInstance(game, BackgammonGame)

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

    def test_game_setup_board_totals(self):
        game = BackgammonGame()
        game.setup_board()
        self.assertEqual(game.board().count_total(Board.WHITE), 15)
        self.assertEqual(game.board().count_total(Board.BLACK), 15)

    def test_game_can_play_move_y_apply_move_consumen_pip(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        game.setup_board()
        game.start_turn((3, 4))
        self.assertTrue(game.can_play_move(7, 3))
        pips_antes = game.pips()
        dest = game.apply_move(7, 3)
        self.assertEqual(dest, 4)
        self.assertEqual(game.board().get_point(7), 2)
        self.assertEqual(game.board().get_point(4), 1)
        self.assertEqual(len(game.pips()), len(pips_antes) - 1)
        self.assertNotIn(3, game.pips())

    def test_game_apply_move_pip_inexistente_levanta(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        game.setup_board()
        game.start_turn((3, 4))
        with self.assertRaises(ValueError):
            game.apply_move(7, 6)

    def test_game_apply_move_bloqueado_levanta(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        game.setup_board()
        game.start_turn((1, 2))
        with self.assertRaises(ValueError):
            game.apply_move(12, 1)

    def test_game_legal_moves_incluye_al_menos_un_par_esperado(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        game.setup_board()
        game.start_turn((3, 4))
        moves = game.legal_moves()
        self.assertTrue(any(m == (7, 3, 4) for m in moves))
        self.assertTrue(any(m == (7, 4, 3) for m in moves))

    def test_game_end_turn_rota_si_no_quedan_pips(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        game.setup_board()
        game.start_turn((3, 4))
        game.apply_move(7, 3)
        game.apply_move(5, 4)
        self.assertTrue(game.is_turn_over())
        self.assertEqual(game.current_player().__color__, "white")
        game.end_turn()
        self.assertEqual(game.current_player().__color__, "black")

    def test_game_auto_end_turn_bloqueado_rota(self):
        game = BackgammonGame()
        game.add_player("Alice", "white")
        game.add_player("Bob", "black")
        game.setup_board()
        b = game.board()
        b.set_point(22, -2)  # bloquear 23->22
        b.set_point(6, -2)   # bloquear 7->6
        b.set_point(4, -2)   # bloquear 5->4
        game.start_turn((1, 1))
        self.assertTrue(game.can_auto_end())
        ok = game.auto_end_turn()
        self.assertTrue(ok)
        self.assertEqual(game.pips(), ())
        self.assertEqual(game.current_player().__color__, "black")

if __name__ == "__main__":
    unittest.main()
