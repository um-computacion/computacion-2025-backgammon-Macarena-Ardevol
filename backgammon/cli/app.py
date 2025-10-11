import argparse
from backgammon.core.game import BackgammonGame
from backgammon.core.board import Board

def format_board_summary(board) -> str:
    # Resumen corto de puntos iniciales clave
    spots = {
        "W": [23, 12, 7, 5],
        "B": [0, 11, 16, 18],
    }
    lines = ["Resumen tablero:"]
    for label, idxs in spots.items():
        vals = [board.get_point(i) for i in idxs]
        lines.append(f"{label} {idxs} -> {vals}")
    return "\n".join(lines)


def _parse_roll(roll_str: str) -> tuple[int, int]:
    if roll_str is None:
        raise ValueError("Roll no provisto (interno)")
    if roll_str == "":
        # requerido por tests de errores
        raise ValueError("Formato de --roll vacío")
    parts = roll_str.split(",")
    if len(parts) != 2:
        raise ValueError("Formato de --roll inválido (usar a,b)")
    try:
        a = int(parts[0].strip())
        b = int(parts[1].strip())
    except Exception:
        raise ValueError("Formato de --roll inválido (deben ser enteros)")
    if not (1 <= a <= 6 and 1 <= b <= 6):
        raise ValueError("Valores de --roll fuera de rango (1..6)")
    return (a, b)


def _parse_move(move_str: str) -> tuple[int, int]:
    # "origin,pip"
    if move_str is None or move_str == "":
        raise ValueError("Formato de --move vacío")
    parts = move_str.split(",")
    if len(parts) != 2:
        raise ValueError("Formato de --move inválido (usar origin,pip)")
    try:
        origin = int(parts[0].strip())
        pip = int(parts[1].strip())
    except Exception:
        raise ValueError("Formato de --move inválido (deben ser enteros)")
    if pip <= 0:
        raise ValueError("Pip debe ser positivo")
    return origin, pip


def _parse_enter(enter_str: str) -> int:
    if enter_str is None or enter_str == "":
        raise ValueError("Formato de --enter vacío")
    try:
        pip = int(enter_str.strip())
    except Exception:
        raise ValueError("Formato de --enter inválido (debe ser entero)")
    if pip <= 0:
        raise ValueError("Pip de --enter debe ser positivo")
    return pip


def _player_color_label(game: BackgammonGame) -> str:
    p = game.current_player()
    if p is None:
        return "White"
    if hasattr(p, "get_color") and callable(p.get_color):
        c = p.get_color()
    else:
        c = getattr(p, "_Player__color__", getattr(p, "color", "white"))
    return c


def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    parser.add_argument("--move", action="append", help="Aplica movimiento origin,pip (puede repetirse)")
    parser.add_argument("--enter", type=str, help="Reingresar desde barra usando pip (equivale a move -1,pip)")
    parser.add_argument("--list-moves", action="store_true", help="Lista movimientos legales")
    parser.add_argument("--end-turn", action="store_true", help="Finaliza el turno (si no quedan pips)")
    parser.add_argument("--auto-end-turn", action="store_true", help="Rota si no hay jugadas posibles")
    parser.add_argument("--history", action="store_true", help="Muestra el historial del turno")
    parser.add_argument("--status", action="store_true", help="Muestra estado resumido")
    args = parser.parse_args(argv)

    game = BackgammonGame()
    game.add_player("White", "white")
    game.add_player("Black", "black")

    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

    # Tirada (fija o automática)
    if args.roll is not None:
        roll = _parse_roll(args.roll)  # puede lanzar ValueError (tests lo esperan)
        game.start_turn(roll)
    else:
        game.start_turn()

    # Listar movimientos (antes de aplicar)
    if args.list_moves:
        moves = game.legal_moves()
        print("Dados:", game.last_roll())
        print("Pips:", game.pips())
        print("Legal moves:")
        for origin, dest, pip in moves:
            o_label = "bar" if origin == -1 else str(origin)
            print(f"  {o_label}->{dest} (pip {pip})")

    # Reingreso desde barra (opcional)
    if args.enter is not None:
        pip = _parse_enter(args.enter)
        # preferimos API unificada: apply_move(-1, pip)
        dest = game.apply_move(-1, pip)
        print(f"Enter: -1->{dest} (pip {pip})")
        print("Pips:", game.pips())

    # Aplicar movimientos secuenciales
    if args.move:
        for mv in args.move:
            origin, pip = _parse_move(mv)
            dest = game.apply_move(origin, pip)
            print(f"Move: {origin}->{dest} (pip {pip})")
            print("Pips:", game.pips())

    # Historial del turno
    if args.history:
        print("History:")
        for (o, d, color, pip) in game.turn_history():
            o_label = "bar" if o == -1 else str(o)
            who = "W" if color == Board.WHITE else "B"
            print(f"  {who}: {o_label}->{d} (pip {pip})")

    # Estado (resumen)
    if args.status:
        print("Estado:")
        print("Jugador:", _player_color_label(game))
        print("Dados:", game.last_roll())
        print("Pips:", game.pips())

    # Fin de turno
    if args.end_turn:
        game.end_turn()
        print("Turno finalizado.")
        print("Turno ahora:", _player_color_label(game))
        print("Dados:", game.last_roll())
        print("Pips:", game.pips())

    # Auto fin si no hay jugadas
    if args.auto_end_turn:
        if game.auto_end_turn():
            print("Sin jugadas → turno rotado.")
            print("Turno ahora:", _player_color_label(game))
        else:
            print("Aún hay jugadas legales disponibles.")
        print("Dados:", game.last_roll())
        print("Pips:", game.pips())

    # Salida estándar al final (coherente con tests previos)
    if not (args.end_turn or args.auto_end_turn or args.history or args.status or args.list_moves or args.move or args.enter):
        print(f"Datos: {game.last_roll()}")
        print(f"Pips: {game.pips()}")
    else:
        # Siempre mostrar el estado final mínimo al terminar
        print("Dados:", game.last_roll())
        print("Pips:", game.pips())


if __name__ == "__main__":
    main()
