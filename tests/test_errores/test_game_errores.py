import unittest
from backgammon.core.board import Board
from backgammon.core.game import BackgammonGame

class TestGameErrores(unittest.TestCase):
    def test_game_start_turn_roll_tupla_con_un_elemento(self):
        g = BackgammonGame()
        g.add_player("A", "white"); g.add_player("B", "black")
        with self.assertRaises(ValueError):
            g.start_turn((3,))

    def test_game_start_turn_roll_tupla_con_tres_elementos(self):
        g = BackgammonGame()
        g.add_player("A", "white"); g.add_player("B", "black")
        with self.assertRaises(ValueError):
            g.start_turn((3, 4, 5))

    def test_game_start_turn_roll_string_en_vez_de_tupla(self):
        g = BackgammonGame()
        g.add_player("A", "white"); g.add_player("B", "black")
        with self.assertRaises(ValueError):
            g.start_turn("3,4")

    def test_game_can_play_move_sin_turno_devuelve_false(self):
        g = BackgammonGame()
        g.add_player("A", "white"); g.add_player("B", "black")
        g.setup_board()
        self.assertFalse(g.can_play_move(7, 3))

    def test_game_has_any_move_false_si_sin_pips(self):
        g = BackgammonGame()
        g.add_player("A", "white"); g.add_player("B", "black")
        g.setup_board()
        g.start_turn((3, 4))
        g.apply_move(7, 3)  # 7->4 usando 3
        g.apply_move(5, 4)  # 5->1 usando 4
        self.assertEqual(g.pips(), ())
        self.assertFalse(g.has_any_move())

    def test_game_end_turn_con_pips_pendientes_levanta(self):
        g = BackgammonGame()
        g.add_player("A", "white"); g.add_player("B", "black")
        g.setup_board()
        g.start_turn((3, 4))
        with self.assertRaises(ValueError):
            g.end_turn()

    def setUp(self):
        self.g = BackgammonGame()
        self.g.add_player("A", "white")
        self.g.add_player("B", "black")
        self.g.setup_board()

    def test_enter_blocked_levanta(self):
        b = self.g.board()
        # Mandar una blanca a barra
        b.set_point(8, 1)   # blanca blot en idx 8
        b.set_point(7, -1)  # negra en idx 7
        b.move(7, 1, Board.BLACK)  # golpe
        self.assertEqual(b.bar_count(Board.WHITE), 1)

        # WHITE quiere entrar con pip=6 -> idx 18 (24-6)
        # bloquear 18 con 2 negras
        b.set_point(18, -2)
        self.g.start_turn((6, 2))
        self.assertFalse(self.g.can_enter(6))
        with self.assertRaises(ValueError):
            self.g.enter_from_bar(6)

    def test_apply_move_con_barra_levanta(self):
        b = self.g.board()
        # blanca a barra
        b.set_point(5, 1); b.set_point(4, -1)
        b.move(4, 1, Board.BLACK)
        self.g.start_turn((3,4))
        with self.assertRaises(ValueError):
            self.g.apply_move(7, 3)  # no puede mover normal con barra pendiente


if __name__ == "__main__":
    unittest.main()
