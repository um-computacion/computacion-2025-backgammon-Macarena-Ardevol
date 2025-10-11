import argparse
from backgammon.core.game import BackgammonGame
from backgammon.core.board import Board

def format_board_summary(board) -> str:
    spots = {"W": [23, 12, 7, 5], "B": [0, 11, 16, 18]}
    lines = ["Resumen tablero:"]
    for label, idxs in spots.items():
        vals = [board.get_point(i) for i in idxs]
        lines.append(f"{label} {idxs} -> {vals}")
    return "\n".join(lines)

def parse_roll(s: str) -> tuple[int, int]:
    if s is None:
        raise ValueError("Se esperaba un valor para --roll (formato a,b).")
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError("Formato inválido para --roll. Use a,b")
    try:
        a = int(parts[0]); b = int(parts[1])
    except Exception:
        raise ValueError("Roll no numérico. Use enteros.")
    if not (1 <= a <= 6 and 1 <= b <= 6):
        raise ValueError("Cada dado debe estar entre 1 y 6.")
    return (a, b)

def parse_move(s: str) -> tuple[int, int]:
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError("Formato inválido para --move. Use origin,pip")
    try:
        origin = int(parts[0]); pip = int(parts[1])
    except Exception:
        raise ValueError("Move no numérico. Use enteros.")
    if pip <= 0:
        raise ValueError("pip debe ser positivo.")
    return origin, pip

def _current_color_label(game: BackgammonGame) -> str:
    cur = game.current_player()
    if hasattr(cur, "get_color") and callable(cur.get_color):
        return cur.get_color()
    return getattr(cur, "_Player__color__", getattr(cur, "color", "?"))

def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    parser.add_argument("--move", action="append", help="Juega un movimiento origin,pip (puede repetirse)")
    parser.add_argument("--list-moves", action="store_true", help="Lista jugadas legales disponibles")
    parser.add_argument("--end-turn", action="store_true", help="Finaliza el turno si no quedan pips")
    parser.add_argument("--auto-end-turn", action="store_true", help="Cierra turno si no hay jugadas legales")
    parser.add_argument("--history", action="store_true", help="Muestra historial del turno")
    parser.add_argument("--status", action="store_true", help="Muestra estado actual")
    parser.add_argument("--enter", type=str, help="Reingresa desde barra usando pip X (ej: --enter 3)")
    args = parser.parse_args(argv)

    game = BackgammonGame()
    game.add_player("White", "white")
    game.add_player("Black", "black")

    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

    # IMPORTANTE: chequear None (no truthiness) para que "" dispare error
    if args.roll is not None:
        a, b = parse_roll(args.roll)
        game.start_turn((a, b))
    else:
        game.start_turn()

    if args.list_moves:
        moves = game.legal_moves()
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")
        print("Legal moves:")
        for (origin, dest, pip) in moves:
            if origin == -1:
                print(f"  BAR->{dest} (pip {pip})")
            else:
                print(f"  {origin}->{dest} (pip {pip})")

    if args.enter is not None:
        try:
            pip = int(args.enter)
        except Exception:
            raise ValueError("--enter requiere un entero (ej: --enter 3)")
        cur_color = Board.WHITE if _current_color_label(game) == "white" else Board.BLACK
        if game.bar_count(cur_color) <= 0:
            raise ValueError("No hay fichas en barra para el jugador actual.")
        if not game.can_enter(pip):
            raise ValueError("No es posible entrar desde barra con ese pip.")
        dest = game.enter_from_bar(pip)
        print(f"Enter: BAR->{dest} (pip {pip})")
        print(f"Pips: {game.pips()}")

    if args.move:
        for mv in args.move:
            origin, pip = parse_move(mv)
            real_dest = game.apply_move(origin, pip)
            print(f"Move: {origin}->{real_dest} (pip {pip})")
            print(f"Pips: {game.pips()}")

    if args.auto_end_turn:
        ok = game.auto_end_turn()
        if ok:
            print("Sin jugadas legales → turno rotado.")
            print(f"Turno ahora: {_current_color_label(game)}")
            print(f"Pips: {game.pips()}")
        else:
            print("Aún hay jugadas legales; no se rota.")

    if args.end_turn:
        game.end_turn()
        print("Turno finalizado.")
        print(f"Turno ahora: {_current_color_label(game)}")
        print(f"Pips: {game.pips()}")

    if args.history:
        print("History:")
        for (o, d, color, pip) in game.turn_history():
            lbl = "W" if color == Board.WHITE else "B"
            if o == -1:
                print(f"  BAR->{d} (pip {pip}, {lbl})")
            else:
                print(f"  {o}->{d} (pip {pip}, {lbl})")

    if args.status:
        cur_lbl = _current_color_label(game)
        print("Estado:")
        print(f"  Turno de: {cur_lbl}")
        print(f"  Dados: {game.last_roll()}")
        print(f"  Pips: {game.pips()}")
        print(f"  Bar W/B: {game.bar_count(Board.WHITE)}/{game.bar_count(Board.BLACK)}")

    print(f"Dados: {game.last_roll()}")
    print(f"Pips: {game.pips()}")

if __name__ == "__main__":
    main()
