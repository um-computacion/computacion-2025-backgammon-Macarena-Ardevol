# Backgammon — Computación 2025
### Macarena Ardevol

Implementación del juego **Backgammon** en Python para la cátedra de Computación 2025.  
El proyecto prioriza **POO + SOLID**, pruebas automatizadas y mejora continua.  
Incluye una **CLI funcional** y una interfaz visual mínima con **Pygame**.

## Descripción breve
- **Core del juego**: tablero, jugadores, dados, turnos, barra (capturas), bear-off (retirar fichas) y condición de victoria.
- **CLI**: setup del tablero, tiradas fijas o automáticas, listar/aplicar movimientos, entrar desde barra, bear-off, historial, estado, guardar/cargar, cierre y auto-cierre de turno.
- **Pygame UI**: interfaz visual mínima con selección por click, panel lateral de estado/ayuda e interacción básica por teclado.
- **Testing**: separación entre *tests válidos* y *tests de errores*, integrados con CI en GitHub Actions.

## Estructura del proyecto
backgammon/
  core/
    board.py
    dice.py
    player.py
    checker.py
    game.py

  cli/
    app.py
    __main__.py        (entrada para `python -m backgammon.cli`)
  pygame_ui/
    __main__.py        (entrada para `python -m backgammon.pygame_ui`)

assets/
requirements.txt

tests/
  test_validos/
    test_board.py
    test_game.py
    test_cli.py
    test_dice_checker_player.py

  test_errores/
    test_board_errores.py
    test_game_errores.py
    test_cli_errores.py

README.md
CHANGELOG.md
JUSTIFICACION.md
prompts-desarrollo.md
prompts-testing.md
prompts-documentacion.md
.github/workflows/ci.yml

## Requisitos
- Python 3.10+
- pip actualizado

## Instalación de dependencias
python -m pip install --upgrade pip
pip install -r backgammon/requirements.txt

## Uso en modo CLI

### Inicializar tablero y usar una tirada fija
python -m backgammon.cli --setup --roll 3,4

`--roll a,b` acepta enteros entre 1 y 6. Formatos inválidos o valores vacíos generan `ValueError`.

### Tirada automática (sin --roll explícito)
python -m backgammon.cli

### Listar movimientos legales del turno
python -m backgammon.cli --setup --roll 3,4 --list-moves

### Mover (uno o más movimientos origin,pip)
python -m backgammon.cli --setup --roll 3,4 --move 7,3 --move 5,4

### Entrar desde barra (si tenés fichas capturadas)
# ejemplo genérico (el parseo es origin,pip; para barra se usa origin=-1)
python -m backgammon.cli --setup --roll 3,1 --move -1,3

### Bear-off (retirar fichas cuando todas están en el home)
python -m backgammon.cli --setup --roll 6,5 --bear-off 5,5 --bear-off 5,6
Notas:
- Retiro exacto: pip que “salta” exactamente fuera del tablero.
- Retiro inexacto: permitido si no quedan fichas en puntos más alejados del home.

### Historial del turno
python -m backgammon.cli --setup --roll 3,4 --move 7,3 --history

### Mostrar estado actual
python -m backgammon.cli --status

### Finalizar turno (requiere que no queden pips)
python -m backgammon.cli --setup --roll 3,4 --move 7,3 --move 5,4 --end-turn

### Auto-cerrar turno si no hay jugadas legales
python -m backgammon.cli --setup --roll 1,1 --auto-end-turn

### Guardar y cargar partida (JSON)
python -m backgammon.cli --setup --roll 3,4 --move 7,3 --save partida.json
python -m backgammon.cli --load partida.json --status

## Interfaz Pygame (base mínima)
Requiere instalación local de Pygame (no se incluye en CI).

Instalar:
pip install pygame

Ejecutar:
python -m backgammon.pygame_ui

Controles principales:
- ESPACIO: tirar dados | F: tirada fija (3,4)
- Click: seleccionar ORIGEN → DESTINO (usa un pip disponible)
- U: deshacer jugada | C: cancelar turno a inicio de tirada
- E: fin de turno (si no hay pips) | A: auto-end si no hay jugadas
- G: guardar partida | L: cargar partida | R: resetear
- S: captura de pantalla | ESC/Q: salir
Panel lateral: estado (jugador, dados, pips), ayuda y lista de jugadas del turno.

## Cómo correr los tests

### Ejecutar todos
python -m unittest discover

### Ejecutar un archivo específico
python -m unittest tests/test_validos/test_game.py

### Interpretación de resultados
Todos OK:
..
Ran N tests in X.XXXs
OK

Falla:
.F
FAIL: test_algo (tests.test_validos.test_game.TestGame)
AssertionError: ...

Error en ejecución:
E
ERROR: test_error (tests.test_errores.test_game_errores.TestGameErrores)
ValueError: Movimiento inválido para el estado actual del tablero

## Cobertura de tests (opcional)
Instalar:
python -m pip install coverage

Ejecutar cobertura:
coverage run -m unittest discover
coverage report -m

HTML:
coverage html
# abrir htmlcov/index.html

Sugerencia .coveragerc:
[run]
branch = True
source = backgammon
omit =
  */tests/*
  */venv/*
  */.venv/*

[report]
exclude_lines =
  pragma: no cover
  if __name__ == .__main__.:

## Convenciones
- Atributos privados con formato `self.__nombre__`.
- Docstrings en clases y métodos.
- Cambios incrementales y trazables.
- Enfoque TDD: pruebas primero, luego implementación.

## Estado actual
- Core estable (`Board`, `Game`, `Player`, `Dice`, `Checker`)
- CLI completa: `--setup`, `--roll`, `--list-moves`, `--move`, `--bear-off`, `--end-turn`, `--auto-end-turn`, `--history`, `--status`, `--save`, `--load`
- Tests divididos por categoría (válidos / errores)
- UI Pygame base operativa
- Próximo sprint: mejoras visuales, efectos y menú de inicio