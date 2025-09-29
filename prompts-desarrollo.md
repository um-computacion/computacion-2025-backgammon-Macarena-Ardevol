## Prompt para helpers de movimiento y flag --move en CLI
Herramienta usada: IA – ChatGPT
Prompt utilizado:
“Necesito helpers mínimos en Board (owner_at, count_at, is_blocked, dest_from) para validar movimientos
y luego exponer un flag `--move origen,pip` en CLI que consuma un pip del turno. Dame la firma y precondiciones.”

Respuesta IA:
- Sugerencias de firmas y precondiciones para:
  - Board.can_move(origin, pip, color) → True/False
  - Board.move(origin, pip, color) → aplica y retorna destino
- Validación CLI:
  - `--move` con formato `origen,pip` (enteros), error en caso inválido.

Uso en el proyecto:
Se usó parcialmente (firmas y validaciones) y se completó la implementación a mano.

Archivos actualizados:
- backgammon/core/board.py (helpers y can_move/move)
- backgammon/cli/app.py (flag --move)
