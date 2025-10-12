import argparse
import json
from pathlib import Path
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
    # Validación estricta para tests de errores (incluye vacío)
    if roll_str is None:
        return None  # type: ignore
    s = roll_str.strip()
    if s == "":
        raise ValueError("Formato de --roll vacío")
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError("Formato de --roll inválido, usar a,b")
    try:
        a = int(parts[0]); b = int(parts[1])
    except Exception:
        raise ValueError("Formato de --roll no numérico")
    if not (1 <= a <= 6 and 1 <= b <= 6):
        raise ValueError("Valores de --roll fuera de rango (1..6)")
    return (a, b)


def _parse_move_str(move_str: str) -> tuple[int, int]:
    s = move_str.strip()
    if "," not in s:
        raise ValueError("Formato de --move inválido, usar origen,pip")
    o, p = s.split(",", 1)
    try:
        origin = int(o); pip = int(p)
    except Exception:
        raise ValueError("Valores de --move no numéricos")
    if origin < -1 or not (1 <= pip <= 6):
        raise ValueError("Valores de --move fuera de rango")
    return origin, pip


def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    parser.add_argument("--move", action="append", help="Aplica movimiento origen,pip (ej: 7,3). Repetible.")
    parser.add_argument("--list-moves", action="store_true", help="Lista movimientos legales")
    parser.add_argument("--end-turn", action="store_true", help="Cierra el turno si no quedan pips")
    parser.add_argument("--auto-end-turn", action="store_true", help="Cierra el turno si no hay jugadas legales")
    parser.add_argument("--history", action="store_true", help="Muestra historial del turno")
    parser.add_argument("--status", action="store_true", help="Muestra estado actual")
    parser.add_argument("--save", type=str, help="Guarda la partida en JSON (ruta)")
    parser.add_argument("--load", type=str, help="Carga la partida desde JSON (ruta)")
    args = parser.parse_args(argv)

    # Validación anticipada de --roll para que tests de errores capten ValueError
    roll_tuple = None
    if args.roll is not None:
        roll_tuple = _parse_roll(args.roll)  # puede levantar ValueError

    # Crear/cargar juego
    game = BackgammonGame()
    if args.load:
        path = Path(args.load)
        if not path.exists():
            raise ValueError("Archivo a cargar inexistente")
        data = json.loads(path.read_text(encoding="utf-8"))
        game = BackgammonGame.from_dict(data)

    # setup básico y jugadores si no viene desde load()
    if args.load is None:
        game.add_player("White", "white")
        game.add_player("Black", "black")

    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

    # Tirada (fija o automática si más abajo hace falta y no hay)
    if roll_tuple is not None:
        game.start_turn(roll_tuple)

    # --list-moves
    if args.list_moves:
        # Si no hay tirada, tirar autom.
        if game.last_roll() is None:
            game.start_turn()
        moves = game.legal_moves()
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")
        print("Legal moves:")
        for (o, d, pip) in moves:
            if o == -1:
                print(f"  bar->{d} (pip {pip})")
            else:
                print(f"  {o}->{d} (pip {pip})")

    # --move (puede venir varias veces)
    if args.move:
        if game.last_roll() is None:
            # Si no hubo tirada previa, tirar automática
            game.start_turn()
        for m in args.move:
            origin, pip = _parse_move_str(m)
            real_dest = game.apply_move(origin, pip)
            print(f"Move: {origin}->{real_dest} (pip {pip})")
            # Mostrar dados y pips luego de cada move (para satisfacer el test que busca "Dados: (3, 4)")
            print(f"Dados: {game.last_roll()}")
            print(f"Pips: {game.pips()}")

    # --end-turn
    if args.end_turn:
        game.end_turn()
        cp = game.current_player()
        cur = getattr(cp, "get_color", lambda: getattr(cp, "_Player__color__", "unknown"))()
        print("Turno finalizado.")
        print(f"Turno ahora: {cur}")
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")

    # --auto-end-turn
    if args.auto_end_turn:
        ok = game.auto_end_turn()
        print("Auto end-turn:", "rotado" if ok else "aún hay jugadas")
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")

    # --history
    if args.history:
        print("History:")
        for (o, d, color, pip) in game.turn_history():
            lbl = "WHITE" if color == Board.WHITE else "BLACK"
            if o == -1:
                print(f"  bar->{d} (pip {pip}) [{lbl}]")
            else:
                print(f"  {o}->{d} (pip {pip}) [{lbl}]")

    # --status
    if args.status:
        cp = game.current_player()
        cur = getattr(cp, "get_color", lambda: getattr(cp, "_Player__color__", "unknown"))()
        print("Estado:")
        print(f"Turno de: {cur}")
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")

    # --save (al final para capturar el estado actual)
    if args.save:
        path = Path(args.save)
        data = game.to_dict()
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Guardado en: {path}")


if __name__ == "__main__":
    main()
