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
        self.__turn_history__ = []  # strings tipo "7->4 (pip 3)"

    # --- jugadores / tablero ---
    def add_player(self, name: str, color: str) -> None:
        self.__players__.append(Player(name, color))

    def current_player(self):
        if not self.__players__:
            return None
        return self.__players__[self.__current_player_index__]

    def num_players(self) -> int:
        return len(self.__players__)

    def next_turn(self) -> None:
        if self.__players__:
            self.__current_player_index__ = (self.__current_player_index__ + 1) % len(self.__players__)

    def setup_board(self) -> None:
        self.__board__.setup_initial()

    def board(self):
        return self.__board__

    def players(self):
        return tuple(self.__players__)

    # --- dados / pips ---
    def start_turn(self, roll: tuple[int, int] | None = None) -> tuple[int, int]:
        if roll is not None:
            if (not isinstance(roll, tuple)) or len(roll) != 2:
                raise ValueError("roll debe ser una tupla (a,b)")
            a, b = roll
            if not (isinstance(a, int) and isinstance(b, int)):
                raise ValueError("roll inválido: ambos valores deben ser enteros")
            if not (1 <= a <= 6 and 1 <= b <= 6):
                raise ValueError("roll inválido: valores fuera de rango 1..6")
            self.__last_roll__ = (a, b)
        else:
            self.__last_roll__ = self.__dice__.roll()

        a, b = self.__last_roll__
        self.__pips__ = (a, a, a, a) if a == b else (a, b)
        self.__turn_history__.clear()
        return self.__last_roll__

    def last_roll(self) -> tuple[int, int] | None:
        return self.__last_roll__

    def pips(self) -> tuple[int, ...]:
        return self.__pips__

    # --- barra (expuestos) ---
    def bar_count(self, color: int) -> int:
        return self.__board__.bar_count(color)

    # --- helpers de color ---
    def _current_color_int(self) -> int:
        p = self.current_player()
        color = p.get_color() if hasattr(p, "get_color") else getattr(p, "_Player__color__", getattr(p, "color", None))
        return Board.WHITE if color == "white" else Board.BLACK

    # --- legalidad / preferencia: si hay barra, se debe entrar primero ---
    def has_bar(self) -> bool:
        return self.bar_count(self._current_color_int()) > 0

    def can_enter(self, pip: int) -> bool:
        return self.__board__.can_enter(pip, self._current_color_int())

    def enter_from_bar(self, pip: int) -> int:
        if pip not in self.__pips__:
            raise ValueError("Pip no disponible en este turno")
        dest = self.__board__.enter_from_bar(pip, self._current_color_int())
        p = list(self.__pips__); p.remove(pip); self.__pips__ = tuple(p)
        self.__turn_history__.append(f"bar->{dest} (pip {pip})")
        return dest

    def can_play_move(self, origin: int, pip: int) -> bool:
        # si hay barra, no se permite mover normal
        if self.has_bar():
            return False
        if not self.__pips__:
            return False
        return self.__board__.can_move(origin, pip, self._current_color_int())

    def legal_moves(self):
        color = self._current_color_int()
        res = []
        pips_set = sorted(set(self.__pips__))

        # prioridad: entrada desde barra
        if self.bar_count(color) > 0:
            for pip in pips_set:
                if self.__board__.can_enter(pip, color):
                    dest = self.__board__.entry_index(pip, color)
                    res.append(("bar", dest, pip))
            return res

        # si no hay barra, movimientos normales
        for origin in range(self.__board__.num_points()):
            if self.__board__.owner_at(origin) != color or self.__board__.count_at(origin) == 0:
                continue
            for pip in pips_set:
                try:
                    dest = self.__board__.dest_from(origin, pip, color)
                    if self.__board__.can_move(origin, pip, color):
                        res.append((origin, dest, pip))
                except Exception:
                    continue
        return res

    def apply_move(self, origin: int, pip: int) -> int:
        if self.has_bar():
            raise ValueError("Debes reingresar desde barra antes de mover")
        if pip not in self.__pips__:
            raise ValueError("Pip no disponible en el turno actual")
        color = self._current_color_int()
        dest = self.__board__.move(origin, pip, color)
        p = list(self.__pips__); p.remove(pip); self.__pips__ = tuple(p)
        self.__turn_history__.append(f"{origin}->{dest} (pip {pip})")
        return dest

    def has_any_move(self) -> bool:
        return bool(self.legal_moves())

    def is_turn_over(self) -> bool:
        return len(self.__pips__) == 0

    def end_turn(self) -> None:
        if not self.is_turn_over():
            raise ValueError("Aún quedan pips por jugar")
        self.next_turn()
        self.__last_roll__ = None
        self.__pips__ = tuple()
        self.__turn_history__.clear()

    def turn_history(self):
        return tuple(self.__turn_history__)

    def auto_end_turn(self) -> bool:
        if not self.__pips__ or not self.has_any_move():
            if not self.is_turn_over():
                self.__pips__ = tuple()
            self.end_turn()
            return True
        return False
