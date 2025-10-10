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

def parse_roll(roll_str: str) -> tuple[int, int]:
    if roll_str is None:
        return None
    if "," not in roll_str:
        raise ValueError("--roll debe ser 'a,b'")
    a_str, b_str = roll_str.split(",", 1)
    if not a_str or not b_str:
        raise ValueError("Valores vacíos en --roll")
    a, b = int(a_str), int(b_str)
    if not (1 <= a <= 6 and 1 <= b <= 6):
        raise ValueError("Valores en --roll fuera de 1..6")
    return (a, b)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    parser.add_argument("--move", action="append", help="Mover 'origen,pip' (puede repetirse)")
    parser.add_argument("--list-moves", action="store_true", help="Lista movimientos legales")
    parser.add_argument("--end-turn", action="store_true", help="Finaliza el turno si no hay pips")
    parser.add_argument("--auto-end-turn", action="store_true", help="Cierra turno si no hay jugadas")
    parser.add_argument("--history", action="store_true", help="Muestra historial del turno actual")
    parser.add_argument("--status", action="store_true", help="Muestra estado actual")
    args = parser.parse_args(argv)

    # Juego
    game = BackgammonGame()
    game.add_player("White", "white")
    game.add_player("Black", "black")

    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

    # Tirada (fija u automática)
    if args.roll is not None:
        r = parse_roll(args.roll)
        game.start_turn(r)
    else:
        game.start_turn()

    print(f"Dados: {game.last_roll()}")
    print(f"Pips: {game.pips()}")

    # list moves
    if args["list-moves"] if isinstance(args, dict) else args.list_moves:
        moves = game.legal_moves()
        print("Legal moves:")
        for o, d, p in moves:
            print(f"  {o}->{d} (pip {p})")

    # aplicar --move múltiples
    if args.move:
        for mv in args.move:
            if "," not in mv:
                raise ValueError("--move debe ser 'origen,pip'")
            o_str, pip_str = mv.split(",", 1)
            origin = int(o_str); pip = int(pip_str)

            # snapshot de barra del rival (para detectar hit)
            cur = game.current_player()
            color = Board.WHITE if cur.get_color() == "white" else Board.BLACK
            rival = Board.BLACK if color == Board.WHITE else Board.WHITE
            bar_antes = game.bar_count(rival)

            real_dest = game.apply_move(origin, pip)
            print(f"Move: {origin}->{real_dest} (pip {pip})")

            bar_despues = game.bar_count(rival)
            if bar_despues > bar_antes:
                print("Hit!")

        print(f"Pips: {game.pips()}")

    # history
    if args.history:
        print("History:")
        for h in game.turn_history():
            print(f"  {h}")

    # end-turn
    if args.end_turn:
        game.end_turn()
        print("Turno finalizado.")
        print(f"Turno ahora: {game.current_player().get_color()}")

    # auto-end-turn
    if args.auto_end_turn:
        if game.auto_end_turn():
            print("Sin jugadas → turno rotado")
        else:
            print("Aún hay jugadas disponibles")

    # status
    if args.status:
        print("Estado:")
        print(f"  Jugador: {game.current_player().get_color()}")
        print(f"  Dados: {game.last_roll()}")
        print(f"  Pips:  {game.pips()}")

if __name__ == "__main__":
    main()
