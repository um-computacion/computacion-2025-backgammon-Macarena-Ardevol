import argparse
from backgammon.core.game import BackgammonGame

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

def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    args = parser.parse_args(argv)

    game = BackgammonGame()
    game.add_player("White", "white")
    game.add_player("Black", "black")

    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

    if args.roll:
        a_str, b_str = args.roll.split(",")
        a, b = int(a_str), int(b_str)
        game.start_turn((a, b))
    else:
        game.start_turn()

    print(f"Dados: {game.last_roll()}")
    print(f"Pips: {game.pips()}")

if __name__ == "__main__":
    main()
