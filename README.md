# Backgammon — Computación 2025
### Macarena Ardevol

Implementación del juego **Backgammon** en Python para la cátedra de Computación 2025.  
El proyecto prioriza **POO + SOLID**, pruebas automatizadas y mejora continua.  
Incluye una **CLI funcional** y (próximamente) una interfaz visual con **Pygame**.


## Descripción breve

- **Core del juego:** tablero, jugadores, dados, turnos, barra, borne-off y victoria.  
- **CLI:** operaciones de setup, tiradas fijas o automáticas, movimientos, entradas desde barra y bear-off.  
- **Pygame UI:** interfaz visual mínima, con selección de puntos, animaciones básicas y soporte para eventos del teclado.  
- **Testing:** separación entre *tests válidos* y *tests de errores*, integrados con GitHub Actions.


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
    main.py
  pygame_ui/
    main.py

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

- Python **3.10+**
- `pip` actualizado

## Instalación de dependencias

python -m pip install --upgrade pip
pip install -r backgammon/requirements.txt

## Uso en modo CLI

### Inicializar tablero y usar una tirada fija

python -m backgammon.cli --setup --roll 3,4


`--roll a,b` acepta enteros entre 1 y 6.  
Formatos inválidos o valores vacíos generan `ValueError`.

### Tirada automática (sin setup)

python -m backgammon.cli

### Tirar y mover en un paso

python -m backgammon.cli --setup --roll 3,4 --move 7,3


Inicializa el tablero, fija la tirada (3,4) y mueve una ficha blanca de la posición 7 a la 4 (consume el pip 3).

### Finalizar turno (todos los pips consumidos)

python -m backgammon.cli --setup --roll 3,4 --move 7,3 --move 5,4 --end-turn


### Auto-cerrar turno si no hay jugadas legales

python -m backgammon.cli --setup --roll 1,1 --auto-end-turn


### Ver historial del turno

python -m backgammon.cli --setup --roll 3,4 --move 7,3 --history


### Mostrar estado (jugador actual)

python -m backgammon.cli --status


### Guardar y cargar partidas

python -m backgammon.cli --setup --roll 3,4 --move 7,3 --save partida.json
python -m backgammon.cli --load partida.json --status


### Bear-off (retirar fichas)

python -m backgammon.cli --setup --roll 6,5 --bear-off 5,5 --bear-off 5,6


Retira fichas blancas desde el home si todas están dentro.  
Permite pip mayor si no hay fichas en puntos más altos del home.


## Interfaz Pygame (base mínima)

Requiere instalación local de Pygame (no se incluye en CI).

**Instalar localmente:**

pip install pygame


**Ejecutar la UI:**

python -m backgammon.pygame_ui


**Controles principales:**
- Click: seleccionar ORIGEN y DESTINO (según color actual)
- T: alternar color (White / Black)
- U: deshacer movimiento
- R: resetear tablero
- ESC / Q: salir
- H: mostrar ayuda
- FPS visibles, puntos numerados (0..23)

En la UI mínima se puede pasar el mouse sobre los puntos, ver información, seleccionar fichas y simular jugadas simples.

## Cómo correr los tests

El proyecto incluye un conjunto de **tests automatizados** divididos en dos grupos:

- *Tests válidos:* verifican el comportamiento correcto del sistema.  
- *Tests de errores:* validan la respuesta ante entradas inválidas o situaciones límite.


### Ejecución de todos los tests

python -m unittest discover


### Ejecutar un archivo de tests específico

python -m unittest tests/test_validos/test_game.py


### Interpretación de resultados

#### Todos los tests pasan:

..
Ran 2 tests in 0.001s

OK


#### Un test falla:

.F
FAIL: test_algo (tests.test_validos.test_game.TestGame)
AssertionError: 'A' != 'B'

FAILED (failures=1)


#### Error en ejecución:

E
ERROR: test_error (tests.test_errores.test_game_errores.TestGameErrores)
ValueError: Movimiento inválido para el estado actual del tablero

FAILED (errors=1)

## Convenciones

- Atributos privados con formato `self.__nombre__`.  
- Clases y métodos documentados con docstrings.  
- Cambios incrementales y trazables (máx. 3 commits/día contables).  
- Respeto del principio **TDD**: primero las pruebas, luego la implementación.  
- Código validado con **unittest** y CI en GitHub Actions.


## Estado actual

- Core completo (`Board`, `Game`, `Player`, `Dice`, `Checker`)
- CLI funcional con `--setup`, `--move`, `--end-turn`, `--auto-end-turn`, `--bear-off`, `--save`, `--load`
- Tests divididos por categoría
- UI Pygame base (interactiva)
- Próximo sprint: mejoras visuales, efectos y menú de inicio