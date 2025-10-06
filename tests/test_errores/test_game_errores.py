import unittest
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

if __name__ == "__main__":
    unittest.main()
