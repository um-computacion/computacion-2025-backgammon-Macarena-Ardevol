# Changelog
Todas las modificaciones relevantes de este proyecto se documentarán aquí.  
Formato: Keep a Changelog.

> Convención de este repositorio: **orden cronológico ascendente**
> (0.1.0 → 0.1.1 → 0.2.0).  
> La sección **Unreleased** se ubica al final.

---

## [0.1.0] - 2025-08-26
### Added
- Creación de la estructura inicial del proyecto:
  - Carpetas: `core/`, `cli/`, `pygame_ui/`, `assets/`, `tests/`
  - Archivos: `README.md`, `CHANGELOG.md`, `JUSTIFICACION.md`, `requirements.txt`
  - Archivos de prompts vacíos:  
    `prompts-desarrollo.md`, `prompts-testing.md`, `prompts-documentacion.md`

---

## [0.1.1] - 2025-08-26
### Added
- Organización de los tests:
  - Se agregaron subcarpetas dentro de `tests/`:
    - `test_validos/`: pruebas de comportamiento esperado.
    - `test_errores/`: pruebas de manejo de excepciones y casos límite.

---

## [0.2.0] - 2025-09-24
### Added
- **Board:** `setup_initial()`, `count_total(color)`, `get_point()/set_point()` con validación, `num_points()`.
- **Game:** `start_turn(roll)`, `last_roll()`, `pips()` (manejo de dobles), `setup_board()`.
- **CLI:** flags `--setup` y `--roll a,b`; entrypoint `python -m backgammon.cli`.

### Changed
- Encapsulamiento con `self.__atributos__`.
- Tests actualizados para usar la API pública del modelo.

### Fixed
- `NUM_POINTS` y validaciones de rango corregidas.

---

## [Unreleased] — Sprint 4
### Added
- **Tests de errores:** índices fuera de rango en `Board`; formato inválido en `CLI --roll`.
- **Documentación:** 
  - README reordenado con CLI completa y guía de uso detallada.
  - JUSTIFICACION completada (atributos, excepciones, testing, SOLID).
  - Ejemplo de `--move` y `--end-turn` en README.
- **CLI:**
  - Flags `--list-moves`, `--end-turn`, `--auto-end-turn`, `--history`, `--status`.
  - Soporte para guardar (`--save`) y cargar (`--load`) partidas en formato JSON.
  - Comando `--bear-off` para retirada de fichas (borne-off).
- **Core:**
  - `Game.turn_history()`, `Game.auto_end_turn()` y `Game.to_dict()/from_dict()`.
  - Incorporación de barra (`bar_count`, `can_enter_from_bar`, `enter_from_bar`).
- **Pygame UI:**
  - Versión mínima (`python -m backgammon.pygame_ui`) con ventana funcional, 24 puntos y totales.
  - Hover con información de punto, selección por click y barra lateral de estado.
  - Etiquetas de índices (0..23), contador de FPS y atajos de teclado (H, ESC, Q).
  - Simulación de movimientos por click (origen→destino).
  - Alternancia de color (T), deshacer (U) y reset del tablero (R).

### Changed
- **CLI:**
  - Validación estricta de `--roll` (vacío o incorrecto → `ValueError`).
  - Soporte para múltiples `--move` en una misma ejecución.
- **Core:**
  - Mejoras en `Board.legal_moves()` y `Game.has_any_move()`.
  - Ajustes en `apply_move()` y validaciones de barra.
- **Documentación:**
  - Revisión de estilo y estructura del README.
  - Corrección de saltos, sangrías y formato uniforme de comandos.

---

© 2025 — Macarena Ardevol — Universidad de Mendoza — Facultad de Ingeniería
