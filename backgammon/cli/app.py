import argparse
from backgammon.core.game import BackgammonGame

def format_board_summary(board) -> str:
    spots = {"W": [23, 12, 7, 5], "B": [0, 11, 16, 18]}
    lines = ["Resumen tablero:"]
    for label, idxs in spots.items():
        vals = [board.get_point(i) for i in idxs]
        lines.append(f"{label} {idxs} -> {vals}")
    return "\n".join(lines)

def format_legal_moves(moves: list[tuple[int, int, int]]) -> str:
    if not moves:
        return "Legal moves: ninguno"
    by_pip: dict[int, list[str]] = {}
    for origin, pip, dest in moves:
        by_pip.setdefault(pip, []).append(f"{origin}->{dest}")
    lines = ["Legal moves:"]
    for pip in sorted(by_pip.keys()):
        lines.append(f"  pip {pip}: " + ", ".join(sorted(by_pip[pip])))
    return "\n".join(lines)

def format_history(hist: list[tuple[int, int, int]]) -> str:
    if not hist:
        return "History: vacío"
    lines = ["History:"]
    for origin, pip, dest in hist:
        lines.append(f"  {origin}->{dest} (pip {pip})")
    return "\n".join(lines)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    parser.add_argument(
        "--move",
        action="append",
        help="Aplica un movimiento origen,pip (ej: 7,3). Podés repetir el flag."
    )
    parser.add_argument("--list-moves", action="store_true", help="Muestra movimientos legales con los pips actuales")
    parser.add_argument("--end-turn", action="store_true", help="Finaliza el turno si no quedan pips")
    parser.add_argument("--auto-end-turn", action="store_true", help="Cierra el turno si no hay jugadas legales con los pips")
    parser.add_argument("--history", action="store_true", help="Muestra el historial de movimientos del turno")
    parser.add_argument("--status", action="store_true", help="Muestra el jugador actual nuevamente")
    args = parser.parse_args(argv)

    game = BackgammonGame()
    game.add_player("White", "white")
    game.add_player("Black", "black")

    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

    print(f"Turno: {game.current_player_label()}")

    # Validación estricta de --roll
    if args.roll is not None:
        value = args.roll
        parts = value.split(",")
        if len(parts) != 2 or parts[0] == "" or parts[1] == "":
            raise ValueError("--roll debe tener formato a,b (enteros)")
        a_str, b_str = parts
        try:
            a, b = int(a_str), int(b_str)
        except ValueError:
            raise ValueError("--roll debe tener formato a,b (enteros)") from None
        if not (1 <= a <= 6 and 1 <= b <= 6):
            raise ValueError("Valores de --roll fuera de 1..6")
        game.start_turn((a, b))
    else:
        game.start_turn()

    if args.list_moves:
        print(format_legal_moves(game.legal_moves()))

    # Ejecutar TODAS las jugadas indicadas por --move (en orden)
    if args.move:
        for value in args.move:
            parts = value.split(",")
            if len(parts) != 2 or parts[0] == "" or parts[1] == "":
                raise ValueError("--move debe tener formato origen,pip (enteros)")
            o_str, p_str = parts
            try:
                origin, pip = int(o_str), int(p_str)
            except ValueError:
                raise ValueError("--move debe tener formato origen,pip (enteros)") from None
            dest = game.apply_move(origin, pip)
            print(f"Move: {origin}->{dest}")

    # Cierre manual del turno
    if args.end_turn:
        game.end_turn()
        print(f"Turno ahora: {game.current_player_label()}")

    # Auto-cierre si no hay jugadas legales
    if args.auto_end_turn:
        if game.auto_end_turn():
            print(f"Auto-end: turno cerrado. Turno ahora: {game.current_player_label()}")
        else:
            print("Auto-end: hay jugadas o no hay pips; no se cerró el turno.")

    # Historial del turno
    if args.history:
        print(format_history(game.turn_history()))

    # Status (impresión adicional del jugador actual)
    if args.status:
        print(f"Estado: {game.current_player_label()}")

    print(f"Dados: {game.last_roll()}")
    print(f"Pips: {game.pips()}")

if __name__ == "__main__":
    main()
