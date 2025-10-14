import unittest
import io, contextlib, json, os
from pathlib import Path


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

    def test_cli_save_and_load_roundtrip(self):
        from backgammon.cli.app import main as cli_main

        tmpdir = Path("tmp_tests"); tmpdir.mkdir(exist_ok=True)
        savefile = tmpdir / "partida.json"

        try:
            # Guardar luego de una jugada
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                cli_main(["--setup", "--roll", "3,4", "--move", "7,3", "--save", str(savefile)])
            self.assertTrue(savefile.exists())

            data = json.loads(savefile.read_text(encoding="utf-8"))
            self.assertIn("board", data)
            self.assertIn("players", data)

            # Cargar y consultar status (no debe explotar)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                cli_main(["--load", str(savefile), "--status"])
            out = buf.getvalue()
            self.assertIn("Estado:", out)
            self.assertIn("Pips:", out)
        finally:
            # Limpieza
            try:
                if savefile.exists():
                    savefile.unlink()
                if tmpdir.exists():
                    os.rmdir(tmpdir)
            except Exception:
                pass

    def test_cli_list_moves_y_status_con_roll_auto(self):
      # Sin --roll explícito pero pidiendo acciones → turno automático
        from backgammon.cli.app import main
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
          main(["--setup", "--list-moves"])
        out = buf.getvalue()
        self.assertIn("Legal moves:", out)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
          main(["--status"])
        out = buf.getvalue()
        self.assertIn("Estado:", out)
        self.assertIn("Pips:", out)

    def test_cli_guardar_y_cargar_roundtrip(self):
        from backgammon.cli.app import main
        import io, contextlib, json, os
        from pathlib import Path

        tmp = Path("tmp_tests_cli"); tmp.mkdir(exist_ok=True)
        savefile = tmp / "partida.json"

      # Guardar tras una jugada
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
           main(["--setup", "--roll", "3,4", "--move", "7,3", "--save", str(savefile)])
        self.assertTrue(savefile.exists())

        data = json.loads(savefile.read_text(encoding="utf-8"))
        self.assertIn("board", data)
        self.assertIn("players", data)

    # Cargar y consultar estado
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
           main(["--load", str(savefile), "--status"])
        out = buf.getvalue()
        self.assertIn("Estado:", out)
        self.assertIn("Pips:", out)

    # Limpieza
        try:
            savefile.unlink()
            tmp.rmdir()
        except Exception:
             pass


if __name__ == "__main__":
    unittest.main()
