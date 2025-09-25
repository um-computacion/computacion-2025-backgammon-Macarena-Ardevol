import unittest
from backgammon.core.board import Board
from backgammon.core.game import BackgammonGame
from backgammon.cli.app import main as cli_main


class TestErroresCore(unittest.TestCase):
    # ---- Board: índices fuera de rango / tipo incorrecto 
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
        # Comparación 0 <= "0" dispara TypeError
        with self.assertRaises(TypeError):
            b.get_point("0")  

    def test_board_set_point_indice_no_entero(self):
        b = Board()
        with self.assertRaises(TypeError):
            b.set_point(1.2, 1)  

    # ---- Game.start_turn: tuplas inválidas / tipos inválidos 
    def test_game_start_turn_roll_tupla_con_un_elemento(self):
        g = BackgammonGame()
        g.add_player("A", "white")
        g.add_player("B", "black")
        with self.assertRaises(ValueError):
            g.start_turn((3,))  

    def test_game_start_turn_roll_tupla_con_tres_elementos(self):
        g = BackgammonGame()
        g.add_player("A", "white")
        g.add_player("B", "black")
        with self.assertRaises(ValueError):
            g.start_turn((3, 4, 5)) 

    def test_game_start_turn_roll_string_en_vez_de_tupla(self):
        g = BackgammonGame()
        g.add_player("A", "white")
        g.add_player("B", "black")
        with self.assertRaises(ValueError):
            g.start_turn("3,4") 

    # ---- CLI: --roll con formatos inválidos ----
    def test_cli_roll_no_numerico(self):
        with self.assertRaises(ValueError):
            cli_main(["--roll", "x,y"])  

    def test_cli_roll_sin_coma(self):
        with self.assertRaises(ValueError):
            cli_main(["--roll", "34"])  

    def test_cli_roll_tres_valores(self):
        with self.assertRaises(ValueError):
            cli_main(["--roll", "3,4,5"])  
    def test_cli_roll_vacio(self):
        with self.assertRaises(ValueError):
            cli_main(["--roll", ""])  

    # (Opcional) Falta de argumento
    def test_cli_roll_falta_argumento_lanza_systemexit(self):
        with self.assertRaises(SystemExit):
            cli_main(["--roll"]) 

    def test_board_is_blocked_color_invalido(self):
        b = Board()
        with self.assertRaises(ValueError):
            b.is_blocked(0, 0)  # color inválido

    def test_board_dest_from_fuera_del_tablero(self):
        b = Board()
        # WHITE desde 1 con pip 2 sale por debajo de 0
        with self.assertRaises(ValueError):
            b.dest_from(1, 2, Board.WHITE)
        # BLACK desde 22 con pip 3 sale por encima de 23
        with self.assertRaises(ValueError):
            b.dest_from(22, 3, Board.BLACK)
