# JUSTIFICACION - Backgammon Computación 2025

### Diseño general
El proyecto está diseñado con separación clara entre lógica central (**core**), interfaz de línea de comandos (**CLI**) e interfaz gráfica con **Pygame** (`pygame_ui`).  
Este diseño facilita mantener las **reglas del juego independientes de la presentación** y evolucionar cada capa de forma incremental.

### Clases elegidas
- **BackgammonGame**: coordina el flujo del juego (jugadores, turno actual), inicializa el tablero y gestiona tiradas/pips (`start_turn`, `last_roll`, `pips`, `setup_board`).  
- **Board**: representa el tablero con sus 24 puntos y provee API pública mínima (`num_points`, `get_point`, `set_point`, `setup_initial`, `count_total`).  
- **Player**: representa a cada jugador (nombre, color, cantidad de fichas) con getters públicos.  
- **Dice**: lógica de tiradas (dos dados de seis caras) y detección de dobles (`is_double`).  
- **Checker**: representa cada ficha (color) con getter público.  
- **CLI**: interfaz de texto para operaciones básicas (mostrar tirada y pips; flags `--setup` y `--roll a,b`).  
- **PygameUI**: interfaz gráfica (pendiente de implementación).

### Atributos
Se usa **encapsulamiento estricto** con `self.__atributo__` para proteger el estado interno y obligar el acceso vía métodos:
- **Board**: `__points__` (lista de 24 enteros), constantes `WHITE = +1`, `BLACK = -1`.  
  Justificación: mantener conteos por punto y distinguir color por signo facilita validar movimientos y sumar totales.  
- **Dice**: `__last_roll__` (tupla `(a, b)`), para exponer `is_double()` y permitir pruebas deterministas.  
- **Player**: `__name__`, `__color__`, `__checkers__ = 15`, con getters para evitar acceso directo.  
- **Checker**: `__color__`, con getter.  
- **BackgammonGame**: `__board__`, `__players__` (lista), `__current_player_index__`, `__dice__`, `__last_roll__`, `__pips__`.  
  Justificación: separar orquestación (Game) del estado del tablero (Board) y de la fuente de aleatoriedad (Dice) respeta SRP y facilita tests.

### Decisiones de diseño relevantes
- **Convención de signos en Board**: positivos = blancas (`WHITE`), negativos = negras (`BLACK`). Simplifica `count_total` y verificaciones.  
- **`setup_initial`**: disposición estándar de Backgammon cargada de una vez para iniciar partidas y tests.  
- **Pips a partir de tirada**: dobles → 4 pips, caso contrario 2 pips; `start_turn(roll)` acepta tirada fija para tests reproducibles.  
- **API mínima**: se evitan accesos a `__points__` desde fuera; se expone `get_point/set_point` con validación.  
- **Separación core/CLI**: la CLI solo orquesta y muestra datos; la lógica vive en core.

### Excepciones y manejo de errores
- **Board**: `get_point/set_point` validan rango `[0..23]` y lanzan `ValueError` si es inválido.  
- **CLI**: `--roll a,b` convierte a enteros; formatos inválidos generan `ValueError`.  
- (Pendiente) Al avanzar con reglas de movimiento, se evaluará introducir **excepciones específicas** (por ejemplo, movimientos ilegales, bloqueo, reingreso desde bar).

### Estrategia de testing
- **Unit tests** por clase (Board, Dice, Player/Checker, Game) y **tests de errores** (rangos inválidos, roll mal formado).  
- Tests de CLI (import/formatter y rutas básicas sin subprocesos).  
- **Determinismo**: `start_turn(roll)` permite fijar tiradas en tests.  
- **Cobertura**: meta ≥ **90%** en core para la entrega final; seguimiento en CI (GitHub Actions) y servicio externo (Coveralls/CodeClimate) cuando esté activado.

### Principios SOLID
- **S (Single Responsibility)**: cada clase tiene una responsabilidad clara (ej., `Dice` solo gestiona dados).  
- **O (Open/Closed)**: `Board`/`Game` permiten extender reglas (movimientos, bar, bearing off) sin romper la API actual.  
- **L (Liskov Substitution)**: sin jerarquías por ahora; se preservará al introducir interfaces/abstracciones.  
- **I (Interface Segregation)**: APIs pequeñas y enfocadas; no se exponen métodos que no se usan.  
- **D (Dependency Inversion)**: `Game` depende de componentes del core; a futuro se podrá invertir dependencias (p. ej., estrategias de IA o fuentes de aleatoriedad) si se requiere.

### Diagramas UML
Pendiente adjuntar **diagrama de clases** (Board, Dice, Player, Checker, BackgammonGame; CLI/PygameUI como capas externas).  
Se incorporará cuando se consolide la base de movimientos.
