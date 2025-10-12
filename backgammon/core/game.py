from backgammon.core.board import Board
from backgammon.core.player import Player
from backgammon.core.dice import Dice

class BackgammonGame:
    """Clase principal del juego Backgammon."""
    def __init__(self):
        self.__board__ = Board()
        self.__players__ = []
        self.__current_player_index__ = 0
        self.__dice__ = Dice()
        self.__last_roll__ = None
        self.__pips__ = tuple()
        self.__turn_history__ = []  # [(origin, dest|None, color, pip, kind)] kind: "move"|"enter"|"off"

    # ---------- Setup / acceso ----------
    def add_player(self, name: str, color: str) -> None:
        self.__players__.append(Player(name, color))

    def current_player(self):
        if not self.__players__:
            return None
        return self.__players__[self.__current_player_index__]

    def num_players(self) -> int:
        return len(self.__players__)

    def board(self):
        return self.__board__

    def players(self):
        return tuple(self.__players__)

    def setup_board(self) -> None:
        self.__board__.setup_initial()

    # ---------- Turnos / dados / pips ----------
    def start_turn(self, roll: tuple[int, int] | None = None) -> tuple[int, int]:
        self.__last_roll__ = roll if roll is not None else self.__dice__.roll()
        a, b = self.__last_roll__
        self.__pips__ = (a, a, a, a) if a == b else (a, b)
        self.__turn_history__.clear()
        return self.__last_roll__

    def last_roll(self):
        return self.__last_roll__

    def pips(self):
        return self.__pips__

    def is_turn_over(self) -> bool:
        return len(self.__pips__) == 0

    def next_turn(self) -> None:
        """Compatibilidad: simple rotación (sin validación de pips)."""
        if self.__players__:
            self.__current_player_index__ = (self.__current_player_index__ + 1) % len(self.__players__)

    def end_turn(self) -> None:
        if not self.is_turn_over():
            raise ValueError("Aún quedan pips por jugar")
        self.next_turn()
        self.__last_roll__ = None
        self.__pips__ = tuple()
        self.__turn_history__.clear()

    def auto_end_turn(self) -> bool:
        if self.has_any_move():
            return False
        self.__pips__ = tuple()
        self.end_turn()
        return True

    def turn_history(self):
        return tuple(self.__turn_history__)

    # ---------- Color actual ----------
    def _current_color_int(self) -> int:
        p = self.current_player()
        if p is None:
            return Board.WHITE
        if hasattr(p, "get_color") and callable(p.get_color):
            color = p.get_color()
        else:
            color = getattr(p, "_Player__color__", getattr(p, "color", None))
        return Board.WHITE if color == "white" else Board.BLACK

    # ---------- Barra: API pública ----------
    def bar_count(self, color: int) -> int:
        return self.__board__.bar_count(color)

    def _has_pieces_on_bar(self, color: int) -> bool:
        return self.__board__.bar_count(color) > 0

    def can_enter_from_bar(self, pip: int) -> bool:
        color = self._current_color_int()
        try:
            return self.__board__.can_enter(pip, color)
        except Exception:
            return False

    def enter_from_bar(self, pip: int) -> int:
        color = self._current_color_int()
        dest = self.__board__.enter_from_bar(pip, color)
        pips = list(self.__pips__)
        pips.remove(pip)
        self.__pips__ = tuple(pips)
        self.__turn_history__.append((-1, dest, color, pip, "enter"))
        return dest

    # ---------- Bear-off ----------
    def can_bear_off(self, origin: int, pip: int) -> bool:
        color = self._current_color_int()
        try:
            return self.__board__.can_bear_off(origin, pip, color)
        except Exception:
            return False

    def bear_off(self, origin: int, pip: int) -> None:
        color = self._current_color_int()
        if pip not in self.__pips__:
            raise ValueError("Pip no disponible en este turno")
        self.__board__.bear_off(origin, pip, color)
        pips = list(self.__pips__)
        pips.remove(pip)
        self.__pips__ = tuple(pips)
        self.__turn_history__.append((origin, None, color, pip, "off"))

    def borne_off_count(self, color: int) -> int:
        return self.__board__.borne_off_count(color)

    def has_won(self, color: int) -> bool:
        """Gana quien tiene 15 borne-off."""
        return self.__board__.borne_off_count(color) >= 15

    # ---------- Movimientos normales ----------
    def legal_moves(self):
        """Movimientos normales y, si aplica, sólo entradas desde barra."""
        color = self._current_color_int()
        res = []
        pips = sorted(set(self.__pips__))
        if not pips:
            return res

        if self._has_pieces_on_bar(color):
            for pip in pips:
                if self.can_enter_from_bar(pip):
                    # origen -1 para barra
                    try:
                        dest = self.__board__.entry_index(pip, color)
                        res.append((-1, dest, pip))
                    except Exception:
                        pass
            return res

        # Si todas las fichas en home, sólo listamos normales aquí
        for origin in range(self.__board__.num_points()):
            if self.__board__.owner_at(origin) != color:
                continue
            if self.__board__.count_at(origin) <= 0:
                continue
            for pip in pips:
                try:
                    if self.__board__.can_move(origin, pip, color):
                        dest = self.__board__.dest_from(origin, pip, color)
                        res.append((origin, dest, pip))
                except Exception:
                    continue
        return res

    def legal_bear_off_moves(self):
        """Lista movimientos de bear-off como (origin, pip)."""
        color = self._current_color_int()
        res = []
        pips = sorted(set(self.__pips__))
        if not pips or self._has_pieces_on_bar(color):
            return res
        # Sólo si todas en home
        if not self.__board__.all_in_home(color):
            return res
        for origin in self.__board__.home_indices(color):
            if self.__board__.owner_at(origin) != color or self.__board__.count_at(origin) == 0:
                continue
            for pip in pips:
                if self.__board__.can_bear_off(origin, pip, color):
                    res.append((origin, pip))
        return res

    def has_any_move(self) -> bool:
        return bool(self.legal_moves() or self.legal_bear_off_moves())

    def can_play_move(self, origin: int, pip: int) -> bool:
        color = self._current_color_int()
        if self._has_pieces_on_bar(color):
            return origin == -1 and self.can_enter_from_bar(pip)
        # si está todo en home, puede que sea bear-off
        if self.__board__.all_in_home(color) and self.__board__.can_bear_off(origin, pip, color):
            return True
        try:
            return self.__board__.can_move(origin, pip, color)
        except Exception:
            return False

    def apply_move(self, origin: int, pip: int) -> int | None:
        """Aplica movimiento normal, entrada desde barra o bear-off. Devuelve destino o None si bear-off."""
        color = self._current_color_int()

        if pip not in self.__pips__:
            raise ValueError("Pip no disponible en este turno")

        # barra obliga entrada
        if self._has_pieces_on_bar(color):
            if origin != -1:
                raise ValueError("Debes reingresar desde la barra antes de mover otras fichas")
            dest = self.enter_from_bar(pip)
            return dest

        # bear-off si aplica
        if self.__board__.all_in_home(color) and self.__board__.can_bear_off(origin, pip, color):
            self.bear_off(origin, pip)
            return None

        # movimiento normal
        if not self.__board__.can_move(origin, pip, color):
            raise ValueError("Movimiento inválido para el estado actual del tablero")

        dest = self.__board__.move(origin, pip, color)
        pips = list(self.__pips__)
        pips.remove(pip)
        self.__pips__ = tuple(pips)
        self.__turn_history__.append((origin, dest, color, pip, "move"))
        return dest

    # ---------- Persistencia (CLI/UI) ----------
    def to_dict(self) -> dict:
        return {
            "points": [self.__board__.get_point(i) for i in range(self.__board__.num_points())],
            "white_bar": self.__board__.bar_count(Board.WHITE),
            "black_bar": self.__board__.bar_count(Board.BLACK),
            "white_borne_off": self.__board__.borne_off_count(Board.WHITE),
            "black_borne_off": self.__board__.borne_off_count(Board.BLACK),
            "players": [{"name": getattr(p, "_Player__name__", getattr(p, "name", "")),
                         "color": getattr(p, "get_color", lambda: getattr(p, "_Player__color__", ""))()} for p in self.__players__],
            "current_player_index": self.__current_player_index__,
            "last_roll": self.__last_roll__,
            "pips": list(self.__pips__),
        }

    @staticmethod
    def from_dict(data: dict) -> "BackgammonGame":
        g = BackgammonGame()
        g.__players__ = [Player(p["name"], p["color"]) for p in data.get("players", [])]
        g.__current_player_index__ = data.get("current_player_index", 0)
        # reconstruir tablero
        g.__board__.setup_initial()
        pts = data.get("points", [0]*24)
        for i, v in enumerate(pts):
            g.__board__.set_point(i, v)
        # barra y borne-off
        # (ajustar counters privados vía “parche” aplicando diferencias)
        # Como Board no expone setters directos, derivar de totales:
        # truco simple: restar lo necesario del conteo total ideal (15) para cada color
        # borne_off = 15 - (en_tablero + en_barra)
        white_on_board = g.__board__.count_total(Board.WHITE)
        black_on_board = g.__board__.count_total(Board.BLACK)
        w_bar = data.get("white_bar", 0)
        b_bar = data.get("black_bar", 0)
        w_off = data.get("white_borne_off", max(0, 15 - white_on_board - w_bar))
        b_off = data.get("black_borne_off", max(0, 15 - black_on_board - b_bar))
        # “inyectar” counters privados (compatibilidad pragmática)
        g.__board__._Board__white_bar__ = w_bar
        g.__board__._Board__black_bar__ = b_bar
        g.__board__._Board__white_borne_off__ = w_off
        g.__board__._Board__black_borne_off__ = b_off

        g.__last_roll__ = tuple(data.get("last_roll")) if data.get("last_roll") else None
        g.__pips__ = tuple(data.get("pips", ()))
        return g
