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


def _parse_pair_csv(s: str) -> tuple[int, int]:
    """Parsea 'a,b' -> (int(a), int(b)). Lanza ValueError si es inválido."""
    if s is None or s == "":
        raise ValueError("Valor vacío")
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError("Formato inválido: se espera 'a,b'")
    try:
        a = int(parts[0].strip())
        b = int(parts[1].strip())
    except Exception:
        raise ValueError("Valores no numéricos en 'a,b'")
    return a, b


def _parse_move_str(s: str) -> tuple[int, int]:
    """Parsea 'origin,pip' -> (int, int)."""
    return _parse_pair_csv(s)


def _roll_from_arg(s: str) -> tuple[int, int]:
    a, b = _parse_pair_csv(s)
    # valida rango 1..6
    if not (1 <= a <= 6 and 1 <= b <= 6):
        raise ValueError("--roll a,b requiere enteros entre 1 y 6")
    return (a, b)


def _print_status(game: BackgammonGame):
    print("Estado:")
    cur = game.current_player()
    color = getattr(cur, "get_color", lambda: getattr(cur, "_Player__color__", "unknown"))()
    print(f"Jugador: {color}")
    print(f"Dados: {game.last_roll()}")
    print(f"Pips: {game.pips()}")


def _print_history(game: BackgammonGame):
    print("History:")
    # turn_history: (origin, dest|None, color_int, pip, kind)
    for (o, d, _, pip, kind) in game.turn_history():
        if kind == "enter":   # -1 -> d
            print(f"BAR->{d} (pip {pip})")
        elif kind == "off":   # o -> OFF
            print(f"{o}->OFF (pip {pip})")
        else:                 # move normal
            print(f"{o}->{d} (pip {pip})")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="backgammon-cli")
    parser.add_argument("--setup", action="store_true", help="Inicializa el tablero estándar")
    parser.add_argument("--roll", type=str, help="Usa tirada fija a,b (ej: 3,4)")
    parser.add_argument("--list-moves", action="store_true", help="Lista movimientos legales")
    parser.add_argument("--move", action="append", help="Aplica movimiento origin,pip (repetible)")
    parser.add_argument("--bear-off", action="append",
                        help="Retira ficha (bear-off) origin,pip (repetible, requiere todas en home)")
    parser.add_argument("--end-turn", action="store_true", help="Finaliza turno si no quedan pips")
    parser.add_argument("--auto-end-turn", action="store_true",
                        help="Rota turno automáticamente si no hay jugadas legales")
    parser.add_argument("--history", action="store_true", help="Muestra el historial del turno")
    parser.add_argument("--status", action="store_true", help="Muestra el estado actual")
    parser.add_argument("--save", type=str, help="Guarda la partida en JSON en la ruta indicada")
    parser.add_argument("--load", type=str, help="Carga la partida desde JSON en la ruta indicada")

    args = parser.parse_args(argv)

    # juego base
    game = BackgammonGame()
    game.add_player("White", "white")
    game.add_player("Black", "black")

    # cargar partida si corresponde (antes de setup/roll)
    if args.load:
        p = Path(args.load)
        if not p.exists():
            raise ValueError(f"Archivo a cargar no existe: {args.load}")
        data = json.loads(p.read_text(encoding="utf-8"))
        game = BackgammonGame.from_dict(data)

    if args.setup:
        game.setup_board()
        print(format_board_summary(game.board()))

    # Tirada fija / automática si se piden acciones de turno
    if args.roll is not None:
        roll = _roll_from_arg(args.roll)  # puede lanzar ValueError
        game.start_turn(roll)
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")
    else:
        # Si no hay roll explícito pero se piden acciones que requieren pips,
        # iniciamos turno automático.
        needs_turn = any([args.list_moves, args.move, args.bear_off, args.end_turn, args.auto_end_turn])
        if needs_turn and game.last_roll() is None:
            game.start_turn()
            # coherencia de salida con tests previos
            print(f"Dados: {game.last_roll()}")
            print(f"Pips: {game.pips()}")

    # Listar movimientos
    if args.list_moves:
        print("Legal moves:")
        for (o, d, pip) in game.legal_moves():
            if o == -1:
                print(f"  BAR->{d} (pip {pip})")
            else:
                print(f"  {o}->{d} (pip {pip})")
        # Bear-off disponibles
        offs = game.legal_bear_off_moves()
        if offs:
            print("Bear-off moves:")
            for (o, pip) in offs:
                print(f"  {o}->OFF (pip {pip})")

    # Aplicar movimientos (puede lanzar ValueError si inválidos)
    if args.move:
        for m in args.move:
            origin, pip = _parse_move_str(m)  # valida formato
            real_dest = game.apply_move(origin, pip)  # puede ser None si bear-off
            if real_dest is None:
                # por si alguien pasa -1,2 en move con all-in-home (no debería)
                print(f"Bear-off: {origin} (pip {pip})")
            else:
                print(f"Move: {origin}->{real_dest} (pip {pip})")
            # coherencia de salida esperada en tests
            print(f"Dados: {game.last_roll()}")
            print(f"Pips: {game.pips()}")

    # Bear-off explícito
    if args.bear_off:
        for m in args.bear_off:
            origin, pip = _parse_move_str(m)
            game.bear_off(origin, pip)
            print(f"Bear-off: {origin} (pip {pip})")
            print(f"Dados: {game.last_roll()}")
            print(f"Pips: {game.pips()}")

    # Auto end-turn
    if args.auto_end_turn:
        ok = game.auto_end_turn()
        if ok:
            print("Sin jugadas → turno rotado.")
        else:
            print("Aún hay jugadas; no se rota.")
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")

    # Cerrar turno (puede lanzar ValueError si quedan pips)
    if args.end_turn:
        game.end_turn()
        print("Turno finalizado.")
        print(f"Dados: {game.last_roll()}")
        print(f"Pips: {game.pips()}")
        # Mostrar siguiente jugador
        nxt = game.current_player()
        ncolor = getattr(nxt, "get_color", lambda: getattr(nxt, "_Player__color__", "unknown"))()
        print(f"Turno ahora: {ncolor}")

        # Chequear victoria del jugador anterior
        prev_idx = (game._BackgammonGame__current_player_index__ - 1) % game.num_players()
        prev = game.players()[prev_idx]
        prev_color = getattr(prev, "get_color", lambda: getattr(prev, "_Player__color__", "unknown"))()
        prev_int = Board.WHITE if prev_color == "white" else Board.BLACK
        if game.has_won(prev_int):
            print(f"¡Victoria de {prev_color}!")

    # History
    if args.history:
        _print_history(game)

    # Status
    if args.status:
        _print_status(game)

    # Guardar partida (al final, con estado actual)
    if args.save:
        p = Path(args.save)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = game.to_dict()
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        # salida amigable
        # (no es requerido por tests, pero útil)
        # print(f"Guardado en {p}")


if __name__ == "__main__":
    main()
