## Prompt para tests
(1)
Prompt para diseñar tests de errores coherentes con el core y la CLI:

Herramienta usada: IA – ChatGPT
Prompt utilizado:
“Proponé algunos tests de errores coherentes con lo que ya existe: Board.get_point/set_point (rango y tipos) y CLI --roll (formatos inválidos). Quiero funciones de ejemplo que yo pueda extender.”

Respuesta IA:
-------------------------------------
def test_board_get_point_fuera_de_rango_superior(self):
    b = Board()
    with self.assertRaises(ValueError):
        b.get_point(24)

def test_board_set_point_indice_no_entero(self):
    b = Board()
    with self.assertRaises(TypeError):
        b.set_point(1.5, 1)  # índice debe ser int

def test_cli_roll_no_numerico(self):
    with self.assertRaises(ValueError):
        cli_main(["--roll", "x,y"])  # int('x') falla
--------------------------------------

Uso en el proyecto:
Se usó parcialmente y se extendió con más casos (tuplas con un valor, con tres valores, sin coma, vacío, etc.).

Archivo final que incorporó contenido generado por IA:

tests/test_errores/test_core_errores.py