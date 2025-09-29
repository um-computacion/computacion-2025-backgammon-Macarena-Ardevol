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

    def test_board_move_invalido_levanta(self):
        b = Board()
        b.setup_initial()
        # Movimiento bloqueado: WHITE 12 -> 11 (negro x5)
        with self.assertRaises(ValueError):
            b.move(12, 1, Board.WHITE)

    def test_board_can_move_origen_sin_fichas(self):
        b = Board()
        b.setup_initial()
        # Punto vacío, no se puede mover
        self.assertFalse(b.can_move(10, 1, Board.WHITE))

    def test_game_can_play_move_sin_turno_devuelve_false(self):
        g = BackgammonGame()
        g.add_player("A", "white"); g.add_player("B", "black")
        g.setup_board()
        # Sin start_turn no hay pips disponibles
        self.assertFalse(g.can_play_move(7, 3))

    def test_cli_move_formato_invalido(self):
        from backgammon.cli.app import main as cli_main
        with self.assertRaises(ValueError):
            cli_main(["--setup", "--roll", "3,4", "--move", "7;3"])  # mal separador

    def test_cli_move_bloqueado_levanta(self):
        from backgammon.cli.app import main as cli_main
        # WHITE 12->11 está bloqueado al inicio (negro x5 en 11)
        with self.assertRaises(ValueError):
            cli_main(["--setup", "--roll", "1,2", "--move", "12,1"])

    def test_game_has_any_move_false_si_sin_pips(self):
        g = BackgammonGame()
        g.add_player("A", "white"); g.add_player("B", "black")
        g.setup_board()
        g.start_turn((3, 4))
    # Consumir ambos pips con jugadas legales:
    # WHITE: 7->4 usando 3
        g.apply_move(7, 3)
    # WHITE: 5->1 usando 4 (1 está vacío al inicio)
        g.apply_move(5, 4)
    # Ya no quedan pips
        self.assertEqual(g.pips(), ())
    # Sin pips, no debería haber movimientos disponibles
        self.assertFalse(g.has_any_move())
