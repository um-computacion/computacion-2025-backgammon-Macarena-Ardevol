import unittest
from backgammon.core.board import Board

class TestBoardErrores(unittest.TestCase):
    def test_board_get_point_indice_negativo(self):
        b = Board()
        with self.assertRaises(ValueError):
            b.get_point(-1)

    def test_board_get_point_indice_fuera_superior(self):
        b = Board()
        with self.assertRaises(ValueError):
            b.get_point(24)

    def test_board_set_point_indice_negativo(self):
        b = Board()
        with self.assertRaises(ValueError):
            b.set_point(-1, 1)

    def test_board_set_point_indice_fuera_superior(self):
        b = Board()
        with self.assertRaises(ValueError):
            b.set_point(24, 1)

    def test_board_get_point_indice_no_entero(self):
        b = Board()
        with self.assertRaises(TypeError):
            b.get_point("0")

    def test_board_set_point_indice_no_entero(self):
        b = Board()
        with self.assertRaises(TypeError):
            b.set_point(1.2, 1)

    def test_board_is_blocked_color_invalido(self):
        b = Board()
        with self.assertRaises(ValueError):
            b.is_blocked(0, 0)

    def test_board_dest_from_fuera_del_tablero(self):
        b = Board()
        with self.assertRaises(ValueError):
            b.dest_from(1, 2, Board.WHITE)   # < 0
        with self.assertRaises(ValueError):
            b.dest_from(22, 3, Board.BLACK)  # > 23

    def test_board_move_invalido_levanta(self):
        b = Board()
        b.setup_initial()
        with self.assertRaises(ValueError):
            b.move(12, 1, Board.WHITE)

    def test_board_can_move_origen_sin_fichas(self):
        b = Board()
        b.setup_initial()
        self.assertFalse(b.can_move(10, 1, Board.WHITE))

    def test_bear_off_falla_sin_all_in_home_unittest():
        from backgammon.core.board import Board
        b = Board(); b.setup_initial()
        assert not b.all_in_home(Board.WHITE)
        with unittest.TestCase().assertRaises(Exception):
         b.bear_off(5, 6, Board.WHITE)


if __name__ == "__main__":
    unittest.main()
