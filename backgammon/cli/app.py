import argparse
from backgammon.core.game import BackgammonGame

def format_board_summary(board) -> str:
    spots = {
        "W": [23, 12, 7, 5],
        "B": [0, 11, 16, 18],
    }
    lines = ["Resumen tablero:"]
    for label, idxs in spots.items():
        vals = [board.get_point(i) for i in idxs]
        lines.append(f"{label} {idxs} -> {vals}")
    return "\n".join(lines)

def format_legal_moves(moves: list[tuple[int, int, int]]) -> str:
    if not moves:
        return "Legal moves: ninguno"
    # agrupar por pip
    by_pip: dict[int, list[str]] = {}
    for origin, pip, dest in moves:
        by_pip.setdefault(pip, []).append(f"{origin}->{dest}")
    lines = ["Legal moves:"]
    for pip in sorted(by_pip.keys()):
        lines.append(f"  pip {pip}: " + ", ".join(sorted(by_pip[pip])))
    return "\n".join(lines)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    parser.add_argument("--move", type=str, help="Aplica un movimiento origen,pip (ej: 7,3)")
    parser.add_argument("--list-moves", action="store_true", help="Muestra movimientos legales con los pips actuales")
    args = parser.parse_args(argv)

    game = BackgammonGame()
    game.add_player("White", "white")
    game.add_player("Black", "black")

    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

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

    # listar movimientos legales
    if args.__dict__.get("list_moves", False):
        print(format_legal_moves(game.legal_moves()))

    # Aplicar movimiento desde CLI 
    if args.move is not None:
        value = args.move
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

    print(f"Dados: {game.last_roll()}")
    print(f"Pips: {game.pips()}")

if __name__ == "__main__":
    main()
