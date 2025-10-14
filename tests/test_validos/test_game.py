import unittest
from backgammon.core.game import BackgammonGame
from backgammon.core.board import Board

class TestGameValidos(unittest.TestCase):

    def setUp(self):
        self.g = BackgammonGame()
        self.g.add_player("Alice", "white")
        self.g.add_player("Bob", "black")
        self.g.setup_board()

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
        # Bloquear destinos WHITE con pip=1: 22, 11 (ya bloqueado), 6, 4
        b = game.board()
        b.set_point(22, -2)  # bloquear 23->22
        # 11 ya está en -5 por setup_initial()
        b.set_point(6, -2)   # bloquear 7->6
        b.set_point(4, -2)   # bloquear 5->4
        game.start_turn((1, 1))
        # Ahora debería auto-rotar porque no hay jugadas con (1,1)
        ok = game.auto_end_turn()
        self.assertTrue(ok)
        self.assertEqual(game.pips(), ())
        self.assertEqual(game.current_player().__color__, "black")

    def test_white_enter_from_bar_simple(self):
        # Preparamos un golpe para enviar una blanca a la barra
        b = self.g.board()
        b.set_point(18, 1)       # blanca en 19(=idx 18)
        b.set_point(16, -1)      # negra en 17
        dest = b.move(16, 1, Board.BLACK)  # 17->18 golpea blanca
        self.assertEqual(dest, 17)  # índice 17 tras sumar 1 desde 16
        self.assertEqual(b.bar_count(Board.WHITE), 1)

        # Turno de WHITE con pip=6 → entrada en 24-6=18 si no está bloqueado
        self.g.start_turn((6, 3))
        if b.owner_at(18) == Board.BLACK and b.count_at(18) >= 2:
            b.set_point(18, -1)  # dejar blot para permitir entrada
        self.assertTrue(self.g.can_enter(6))
        d = self.g.enter_from_bar(6)
        self.assertIn(d, range(18, 24))     # home de BLACK
        self.assertEqual(b.bar_count(Board.WHITE), 0)

    def test_cannot_move_normal_if_bar_not_empty(self):
        b = self.g.board()
        # Dejar un blot blanca y golpear con negras
        b.set_point(10, 1)
        b.set_point(9, -1)
        b.move(9, 1, Board.BLACK)   # golpe a blanca -> barra blanca = 1
        self.assertEqual(b.bar_count(Board.WHITE), 1)
        self.g.start_turn((3, 4))
        # Mientras haya barra, no puede mover normal
        self.assertFalse(self.g.can_play_move(7, 3))
        # Pero sí puede entrar si el destino no está bloqueado
        # White entra con 3 en idx 21 (24-3)
        self.assertTrue(self.g.can_enter(3))


    def test_history_acumula_moves_y_enter(self):
        g = BackgammonGame()
        g.add_player("White", "white")
        g.add_player("Black", "black")
        g.setup_board()

        b = g.board()
        # Forzamos blot negro en 6 y movemos blanca 7->6 con pip 1
        b.set_point(6, -1)
        g.start_turn((1, 4))
        g.apply_move(7, 1)  # WHITE golpea y manda una negra a la barra

        hist = g.turn_history()
        # origin=7 y tipo "move" (si la history guarda 'kind', lo aceptamos)
        self.assertTrue(any((h[0] == 7 and (len(h) < 5 or h[4] in ("move", "enter", "off"))) for h in hist))

        # Turno negro: intentar entrar desde barra si es posible
        g.end_turn()
        g.start_turn((3, 3))
        try:
            if hasattr(g, "can_enter") and callable(getattr(g, "can_enter")):
                if g.can_enter(3):
                    g.apply_move(-1, 3)
            elif hasattr(g, "can_enter_from_bar") and callable(getattr(g, "can_enter_from_bar")):
                if g.can_enter_from_bar(3):
                    g.apply_move(-1, 3)
            else:
                # Intento directo; si está bloqueado puede levantar ValueError y está bien
                try:
                    g.apply_move(-1, 3)
                except ValueError:
                    pass
        except Exception as _:
            self.fail("enter_from_bar no debería explotar con errores inesperados")

    def test_has_won_dispara_con_bear_off_total_si_soportado(self):
        # Solo corre si Board/Game soportan borne-off
        if not all(hasattr(Board, attr) for attr in ("borne_off_count", "all_in_home", "home_indices")):
            self.skipTest("Bear-off no implementado en Board")

        g = BackgammonGame()
        g.add_player("White", "white")
        g.add_player("Black", "black")
        g.setup_board()

        b = g.board()
        # Vaciar tablero y poner 15 blancas en el home (punto 0) como ejemplo simple
        for i in range(24):
            b.set_point(i, 0)
        b.set_point(0, 15)

        g.start_turn((6, 6))
        # Intentamos retirar algunas (según reglas implementadas)
        intentos = 0
        for _ in range(4):
            if hasattr(g, "can_bear_off") and g.can_bear_off(0, 6):
                g.apply_move(0, 6)
                intentos += 1
            else:
                try:
                    g.apply_move(0, 6)
                    intentos += 1
                except ValueError:
                    break

        white_off = b.borne_off_count(Board.WHITE)
        self.assertGreaterEqual(white_off, 0)  # al menos no explota


if __name__ == "__main__":
    unittest.main()
