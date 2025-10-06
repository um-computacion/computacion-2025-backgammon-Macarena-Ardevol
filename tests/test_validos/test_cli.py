import unittest
import io, contextlib

class TestCLIValidos(unittest.TestCase):
    def test_cli_app_import(self):
        from backgammon.cli.app import main
        self.assertTrue(callable(main))

    def test_cli_format_board_summary(self):
        from backgammon.cli.app import format_board_summary
        from backgammon.core.board import Board
        board = Board(); board.setup_initial()
        s = format_board_summary(board)
        self.assertIn("Resumen tablero:", s)
        self.assertIn("[23, 12, 7, 5]", s)
        self.assertIn("[0, 11, 16, 18]", s)

    def test_cli_entrypoint_exists(self):
        from backgammon.cli.app import main
        self.assertTrue(callable(main))

    def test_cli_list_moves_muestra_posibles(self):
        from backgammon.cli.app import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--setup", "--roll", "3,4", "--list-moves"])
        out = buf.getvalue()
        self.assertIn("Legal moves:", out)
        self.assertIn("pip 3", out)
        self.assertIn("7->4", out)

    def test_cli_move_aplica_y_muestra(self):
        from backgammon.cli.app import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--setup", "--roll", "3,4", "--move", "7,3"])
        out = buf.getvalue()
        self.assertIn("Move: 7->4", out)
        self.assertIn("Dados: (3, 4)", out)
        self.assertIn("Pips: (4,)", out)

    def test_cli_end_turn_rotacion_y_pips_vacios(self):
        from backgammon.cli.app import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--setup", "--roll", "3,4", "--move", "7,3", "--move", "5,4", "--end-turn"])
        out = buf.getvalue()
        self.assertIn("Turno ahora:", out)
        self.assertIn("Pips: ()", out)

    def test_cli_history_muestra_movimientos(self):
        from backgammon.cli.app import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--setup", "--roll", "3,4", "--move", "7,3", "--history"])
        out = buf.getvalue()
        self.assertIn("History:", out)
        self.assertIn("7->4 (pip 3)", out)

    def test_cli_status_refresca_estado(self):
        from backgammon.cli.app import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["--setup", "--roll", "3,4", "--status"])
        out = buf.getvalue()
        self.assertIn("Estado:", out)
        self.assertIn("Dados: (3, 4)", out)
        self.assertIn("Pips: (3, 4)", out)

if __name__ == "__main__":
    unittest.main()
