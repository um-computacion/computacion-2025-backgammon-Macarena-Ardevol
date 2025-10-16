import unittest
from backgammon.core.board import Board

class TestBoardValidos(unittest.TestCase):
    def test_board_points(self):
        board = Board()
        self.assertEqual(len(board.__points__), 24)

    def test_board_initial_setup_totals_and_spots(self):
        board = Board()
        board.setup_initial()
        self.assertEqual(board.count_total(Board.WHITE), 15)
        self.assertEqual(board.count_total(Board.BLACK), 15)
        self.assertEqual(board.get_point(23), 2)    # blancas
        self.assertEqual(board.get_point(12), 5)
        self.assertEqual(board.get_point(7), 3)
        self.assertEqual(board.get_point(5), 5)
        self.assertEqual(board.get_point(0), -2)    # negras
        self.assertEqual(board.get_point(11), -5)
        self.assertEqual(board.get_point(16), -3)
        self.assertEqual(board.get_point(18), -5)

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
        self.assertTrue(board.is_blocked(11, Board.WHITE))
        self.assertFalse(board.is_blocked(12, Board.WHITE))
        self.assertTrue(board.is_blocked(12, Board.BLACK))
        self.assertFalse(board.is_blocked(11, Board.BLACK))

    def test_board_dest_from_direction(self):
        board = Board()
        self.assertEqual(board.dest_from(12, 3, Board.WHITE), 9)   # WHITE hacia abajo
        self.assertEqual(board.dest_from(11, 6, Board.BLACK), 17)  # BLACK hacia arriba

    def test_board_can_move_en_vacio_y_propio(self):
        board = Board()
        board.setup_initial()
        self.assertTrue(board.can_move(7, 1, Board.WHITE))   # vacío
        self.assertTrue(board.can_move(7, 2, Board.WHITE))   # propio
        self.assertTrue(board.can_move(16, 1, Board.BLACK))  # vacío
        self.assertTrue(board.can_move(16, 2, Board.BLACK))  # propio

    def test_board_can_move_bloqueado_devuelve_false(self):
        board = Board()
        board.setup_initial()
        self.assertFalse(board.can_move(12, 1, Board.WHITE))  # a 11 (negro x5)
        self.assertFalse(board.can_move(11, 1, Board.BLACK))  # a 12 (blanco x5)

    def test_board_move_aplica_cambios(self):
        board = Board()
        board.setup_initial()
        self.assertEqual(board.get_point(7), 3)
        self.assertEqual(board.get_point(6), 0)
        dest = board.move(7, 1, Board.WHITE)
        self.assertEqual(dest, 6)
        self.assertEqual(board.get_point(7), 2)
        self.assertEqual(board.get_point(6), 1)

    def test_board_move_hit_envia_a_barra(self):
        b = Board()
        b.setup_initial()
        # El destino (9) debe tener un blot negro (-1) para que WHITE haga hit al llegar
        b.set_point(9, -1)        
        self.assertEqual(b.get_point(12), 5)  # origen blanco con fichas
        dest = b.move(12, 3, Board.WHITE)     # 12 - 3 = 9
        self.assertEqual(dest, 9)
        # Ahora en 9 hay blancas (>0) y la negra golpeada fue a la barra negra
        self.assertGreater(b.get_point(9), 0)
        self.assertEqual(b.bar_count(Board.BLACK), 1)

def test_bear_off_white_exact_and_inexact():
    from backgammon.core.board import Board
    b = Board()
    # situar TODAS las blancas (15) en home: 0..5
    P = [0]*24
    P[5] = 2   # dos en el 5
    P[4] = 5
    P[3] = 3
    P[2] = 3
    P[1] = 2
    # total = 15
    for i, v in enumerate(P):
        b.set_point(i, v)
    # no barra ni off
    # exacto: desde 5 con pip=6 -> off permitido
    assert b.all_in_home(Board.WHITE)
    assert b.can_bear_off(5, 6, Board.WHITE)
    b.bear_off(5, 6, Board.WHITE)
    assert b.borne_off_count(Board.WHITE) == 1

    # inexacto: desde 1 con pip=6 -> permitido solo si no hay fichas en >1 (dentro de home)
    # aún quedan fichas en 2,3,4 -> NO permitido
    assert not b.can_bear_off(1, 6, Board.WHITE)


if __name__ == "__main__":
    unittest.main()
