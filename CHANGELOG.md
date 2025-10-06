# Changelog
Todas las modificaciones relevantes de este proyecto se documentarán aquí.  
Formato: Keep a Changelog.

> Convención de este repo: **orden cronológico ascendente**
> (0.1.0 → 0.1.1 → 0.2.0).  
> La sección **Unreleased** va al final.

## [0.1.0] - 2025-08-26
### Added
- Creación de estructura inicial del proyecto:
  - Carpetas: `core/`, `cli/`, `pygame_ui/`, `assets/`, `tests/`
  - Archivos: `README.md`, `CHANGELOG.md`, `JUSTIFICACION.md`, `requirements.txt`
  - Archivos de prompts vacíos: `prompts-desarrollo.md`, `prompts-testing.md`, `prompts-documentacion.md`

## [0.1.1] - 2025-08-26
### Added
- Organización de tests:
  - Se agregaron subcarpetas dentro de tests/:
    - `test_validos/`: pruebas de comportamiento esperado.
    - `test_errores/`: pruebas de manejo de excepciones y casos límite.

## [0.2.0] - 2025-09-24
### Added
- Board: `setup_initial()`, `count_total(color)`, `get_point()/set_point()` con validación, `num_points()`.
- Game: `start_turn(roll)`, `last_roll()`, `pips()` (manejo de dobles), `setup_board()`.
- CLI: flags `--setup` y `--roll a,b`; entrypoint `python -m backgammon.cli`.

### Changed
- Encapsulamiento con `self.__atributos__` y tests actualizados para usar API pública.

### Fixed
- `NUM_POINTS` y validaciones de rango.

## [Unreleased]

### Added
- Tests de errores: índices fuera de rango en `Board`; formato inválido en `CLI --roll`.
- Documentación: README reordenado; JUSTIFICACION completada (atributos, excepciones, testing, SOLID).
- Documentación: ejemplo de `--move` en README.
- CLI: flags `--list-moves`, `--end-turn`, `--auto-end-turn`, `--history`, `--status`.
- Core: `Game.turn_history()` y `Game.auto_end_turn()`.

### Changed
- CLI: validación estricta de `--roll` (vacío/incorrecto → `ValueError`).
- CLI: soporte para múltiples `--move`.
- Core: `Board.legal_moves()` y `Game.has_any_move()`.
- Ajustes menores de redacción en docs.
