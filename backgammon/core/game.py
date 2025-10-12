from backgammon.core.board import Board
from backgammon.core.player import Player
from backgammon.core.dice import Dice
import json
from pathlib import Path


class BackgammonGame:
    """Clase principal del juego Backgammon."""
    def __init__(self):
        self.__board__ = Board()
        self.__players__ = []
        self.__current_player_index__ = 0
        self.__dice__ = Dice()
        self.__last_roll__ = None
        self.__pips__ = tuple()
        self.__turn_history__ = []  # [(origin, dest, color, pip)]

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

    def last_roll(self) -> tuple[int, int] | None:
        return self.__last_roll__

    def pips(self) -> tuple[int, ...]:
        return self.__pips__

    def is_turn_over(self) -> bool:
        return len(self.__pips__) == 0

    def next_turn(self) -> None:
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

    # ---------- Barra ----------
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

    def can_enter(self, pip: int) -> bool:
        return self.can_enter_from_bar(pip)

    def enter_from_bar(self, pip: int) -> int:
        color = self._current_color_int()
        dest = self.__board__.enter_from_bar(pip, color)
        pips = list(self.__pips__)
        pips.remove(pip)
        self.__pips__ = tuple(pips)
        self.__turn_history__.append((-1, dest, color, pip))
        return dest

    # ---------- Movimientos ----------
    def legal_moves(self):
        color = self._current_color_int()
        res = []
        pips = sorted(set(self.__pips__))
        if not pips:
            return res

        if self._has_pieces_on_bar(color):
            for pip in pips:
                try:
                    if self.__board__.can_enter(pip, color):
                        dest = self.__board__.entry_index(pip, color)
                        res.append((-1, dest, pip))
                except Exception:
                    continue
            return res

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

    def has_any_move(self) -> bool:
        return len(self.legal_moves()) > 0

    def can_play_move(self, origin: int, pip: int) -> bool:
        # Debe existir el pip (cubre “sin start_turn”)
        if pip not in self.__pips__:
            return False

        color = self._current_color_int()

        if self._has_pieces_on_bar(color):
            return origin == -1 and self.can_enter_from_bar(pip)

        try:
            return self.__board__.can_move(origin, pip, color)
        except Exception:
            return False

    def apply_move(self, origin: int, pip: int) -> int:
        color = self._current_color_int()
        if self._has_pieces_on_bar(color) and origin != -1:
            raise ValueError("Debes reingresar desde la barra antes de mover otras fichas")

        pips = list(self.__pips__)
        if pip not in pips:
            raise ValueError("Pip no disponible en este turno")

        if origin == -1:
            return self.enter_from_bar(pip)

        if not self.__board__.can_move(origin, pip, color):
            raise ValueError("Movimiento inválido para el estado actual del tablero")

        dest = self.__board__.move(origin, pip, color)
        pips.remove(pip)
        self.__pips__ = tuple(pips)
        self.__turn_history__.append((origin, dest, color, pip))
        return dest

    # ---------- Serialización ----------
    def to_dict(self) -> dict:
        return {
            "board": self.__board__.to_dict(),
            "players": [
                {
                    "name": getattr(p, "get_name", lambda: getattr(p, "_Player__name__", getattr(p, "name", "")))(),
                    "color": getattr(p, "get_color", lambda: getattr(p, "_Player__color__", getattr(p, "color", "")))(),
                }
                for p in self.__players__
            ],
            "current_player_index": int(self.__current_player_index__),
            "last_roll": tuple(self.__last_roll__) if self.__last_roll__ is not None else None,
            "pips": list(self.__pips__),
            "turn_history": [
                {"origin": o, "dest": d, "color": c, "pip": pip}
                for (o, d, c, pip) in self.__turn_history__
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BackgammonGame":
        g = cls()
        g.__board__ = Board.from_dict(data["board"])
        g.__players__.clear()
        for pd in data.get("players", []):
            g.add_player(pd.get("name", ""), pd.get("color", "white"))
        g.__current_player_index__ = int(data.get("current_player_index", 0))
        lr = data.get("last_roll", None)
        g.__last_roll__ = tuple(lr) if lr is not None else None
        g.__pips__ = tuple(int(x) for x in data.get("pips", []))
        g.__turn_history__.clear()
        for md in data.get("turn_history", []):
            g.__turn_history__.append((
                int(md.get("origin", -1)),
                int(md.get("dest", 0)),
                int(md.get("color", Board.WHITE)),
                int(md.get("pip", 1)),
            ))
        return g

    # Helpers de archivo (para CLI/tests)
    def save(self, path: str | Path) -> str:
        p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return str(p)

    @classmethod
    def load(cls, path: str | Path) -> "BackgammonGame":
        p = Path(path)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
