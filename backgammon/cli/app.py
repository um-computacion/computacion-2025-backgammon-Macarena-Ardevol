import argparse
import json
from pathlib import Path
from backgammon.core.game import BackgammonGame
from backgammon.core.board import Board


def format_board_summary(board) -> str:
    spots = {"W": [23, 12, 7, 5], "B": [0, 11, 16, 18]}
    lines = ["Resumen tablero:"]
    for label, idxs in spots.items():
        vals = [board.get_point(i) for i in idxs]
        lines.append(f"{label} {idxs} -> {vals}")
    return "\n".join(lines)


def parse_roll(raw: str) -> tuple[int, int]:
    if raw is None or raw == "":
        raise ValueError("--roll vacío")
    parts = raw.split(",")
    if len(parts) != 2:
        raise ValueError("--roll debe ser 'a,b'")
    try:
        a = int(parts[0]); b = int(parts[1])
    except ValueError:
        raise ValueError("--roll debe ser numérico")
    if not (1 <= a <= 6 and 1 <= b <= 6):
        raise ValueError("--roll fuera de rango (1..6)")
    return (a, b)


def parse_move(raw: str) -> tuple[int, int]:
    parts = raw.split(",")
    if len(parts) != 2:
        raise ValueError("--move debe ser 'origen,pip'")
    try:
        origin = int(parts[0]); pip = int(parts[1])
    except ValueError:
        raise ValueError("--move debe ser numérico (origen,pip)")
    return origin, pip


def color_label(game: BackgammonGame) -> str:
    p = game.current_player()
    if hasattr(p, "get_color") and callable(p.get_color):
        c = p.get_color()
    else:
        c = getattr(p, "_Player__color__", getattr(p, "color", "white"))
    return "White" if c == "white" else "Black"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    parser.add_argument("--move", action="append", help="Aplica un movimiento 'origen,pip'. Repetible.")
    parser.add_argument("--list-moves", action="store_true", help="Lista movimientos legales")
    parser.add_argument("--end-turn", action="store_true", help="Finaliza el turno (si no quedan pips)")
    parser.add_argument("--auto-end-turn", action="store_true", help="Finaliza si no hay jugadas legales")
    parser.add_argument("--history", action="store_true", help="Muestra movimientos del turno")
    parser.add_argument("--status", action="store_true", help="Muestra estado actual (jugador/dados/pips)")

    # NUEVO: persistencia desde CLI
    parser.add_argument("--save", type=str, help="Guarda el estado en un archivo JSON")
    parser.add_argument("--load", type=str, help="Carga el estado desde un archivo JSON")

    args = parser.parse_args(argv)

    # Crear juego
    game = BackgammonGame()

    # Si hay --load, cargar primero
    if args.load:
        path = Path(args.load)
        if not path.exists():
            raise ValueError(f"No existe el archivo para cargar: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        game = BackgammonGame.from_dict(data)

    # Asegurar jugadores y tablero en un estado razonable si no viene de un load
    if game.num_players() == 0:
        game.add_player("White", "white")
        game.add_player("Black", "black")
    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

    # Tirada (opcionalmente fija)
    if args.roll:
        roll = parse_roll(args.roll)
        game.start_turn(roll)
    elif args.setup:
        # Si se pidió setup pero no roll, tirada automática
        game.start_turn()
    # Si no hay setup ni roll, se permite usar sólo comandos de introspección (status/history)
    # o list-moves (si ya se había cargado un estado con pips)

    # Listar movimientos
    if args.list_moves:
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")
        moves = game.legal_moves()
        print("Legal moves:")
        for (o, d, pip) in moves:
            if o == -1:
                # entrada desde barra
                print(f"  bar->{d} (pip {pip})")
            else:
                print(f"  {o}->{d} (pip {pip})")

    # Movimientos (pueden venir múltiples --move)
    if args.move:
        for raw in args.move:
            origin, pip = parse_move(raw)
            real_dest = game.apply_move(origin, pip)
            if origin == -1:
                print(f"Enter: bar->{real_dest} (pip {pip})")
            else:
                print(f"Move: {origin}->{real_dest} (pip {pip})")
            print(f"Pips: {game.pips()}")

    # Cierre de turno
    if args.end_turn:
        game.end_turn()
        print("Turno finalizado.")
        print(f"Turno ahora: {color_label(game)}")
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")

    if args.auto_end_turn:
        if game.auto_end_turn():
            print("Sin jugadas legales → turno rotado.")
            print(f"Turno ahora: {color_label(game)}")
        else:
            print("Aún hay jugadas disponibles → no rota.")

    # Historia y estado
    if args.history:
        hist = game.turn_history()
        print("History:")
        for (o, d, c, pip) in hist:
            if o == -1:
                print(f"  bar->{d} (pip {pip})")
            else:
                print(f"  {o}->{d} (pip {pip})")

    if args.status:
        print("Estado:")
        print(f"Turno ahora: {color_label(game)}")
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")

    # Guardar al final si se pidió
    if args.save:
        path = Path(args.save)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(game.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"Guardado: {path}")


if __name__ == "__main__":
    main()
