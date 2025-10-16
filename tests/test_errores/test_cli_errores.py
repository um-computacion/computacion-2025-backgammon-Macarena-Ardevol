import unittest
from backgammon.cli.app import main as cli_main

class TestCLIErrores(unittest.TestCase):
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

    def test_cli_roll_falta_argumento_lanza_systemexit(self):
        with self.assertRaises(SystemExit):
            cli_main(["--roll"])

    def test_cli_move_formato_invalido(self):
        with self.assertRaises(ValueError):
            cli_main(["--setup", "--roll", "3,4", "--move", "7;3"])

    def test_cli_move_bloqueado_levanta(self):
        with self.assertRaises(ValueError):
            cli_main(["--setup", "--roll", "1,2", "--move", "12,1"])

    def test_cli_load_inexistente_levanta(self):
        with self.assertRaises(ValueError):
            cli_main(["--load", "no_existe_abc123.json"])

    def test_cli_end_turn_con_pips_pendientes_levanta(self):
        from backgammon.cli.app import main as cli_main
    # Con pips sin consumir, --end-turn debe levantar ValueError
        with self.assertRaises(ValueError):
            cli_main(["--setup", "--roll", "3,4", "--end-turn"])


if __name__ == "__main__":
    unittest.main()
