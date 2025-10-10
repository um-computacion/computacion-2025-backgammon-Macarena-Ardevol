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
        self.__turn_history__ = []  # strings tipo "7->4 (pip 3)" del turno actual

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
        """Devuelve el tablero actual (solo lectura)."""
        return self.__board__

    def players(self):
        """Devuelve una tupla con los jugadores (solo lectura)."""
        return tuple(self.__players__)

    # --- dados / pips ---
    def start_turn(self, roll: tuple[int, int] | None = None) -> tuple[int, int]:
        """
        Inicia el turno tirando dados (o usando un roll fijo).
        Valida formato del roll si viene fijado externamente.
        """
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

    # --- barra (NUEVO accessor) ---
    def bar_count(self, color: int) -> int:
        """Cantidad de fichas en barra para el color dado (Board.WHITE/BLACK)."""
        return self.__board__.bar_count(color)

    # --- movimientos a nivel Game ---
    def _current_color_int(self) -> int:
        p = self.current_player()
        # Soporta getters o atributo interno
        color = p.get_color() if hasattr(p, "get_color") else getattr(p, "_Player__color__", getattr(p, "color", None))
        return Board.WHITE if color == "white" else Board.BLACK

    def can_play_move(self, origin: int, pip: int) -> bool:
        if not self.__pips__:
            return False
        color = self._current_color_int()
        return self.__board__.can_move(origin, pip, color)

    def legal_moves(self):
        """Devuelve lista de triples (origin, dest, pip) para los pips disponibles."""
        color = self._current_color_int()
        res = []
        pips_set = sorted(set(self.__pips__))
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
        """
        Aplica un movimiento legal, consume el pip usado y registra en historia.
        Devuelve el destino real.
        """
        if pip not in self.__pips__:
            raise ValueError("Pip no disponible en el turno actual")
        color = self._current_color_int()
        dest = self.__board__.move(origin, pip, color)
        # consumir solo una ocurrencia del pip
        pips_list = list(self.__pips__)
        pips_list.remove(pip)
        self.__pips__ = tuple(pips_list)
        self.__turn_history__.append(f"{origin}->{dest} (pip {pip})")
        return dest

    def has_any_move(self) -> bool:
        return bool(self.legal_moves())

    def is_turn_over(self) -> bool:
        return len(self.__pips__) == 0

    def end_turn(self) -> None:
        """Finaliza turno: sólo si no quedan pips. Rota al siguiente jugador."""
        if not self.is_turn_over():
            raise ValueError("Aún quedan pips por jugar")
        self.next_turn()
        self.__last_roll__ = None
        self.__pips__ = tuple()
        self.__turn_history__.clear()

    # utilidades opcionales ya usadas en CLI/tests
    def turn_history(self):
        return tuple(self.__turn_history__)

    def auto_end_turn(self) -> bool:
        """
        Si no hay jugadas legales o no hay pips, cierra el turno automáticamente.
        Devuelve True si rotó, False si aún hay jugadas.
        """
        if not self.__pips__ or not self.has_any_move():
            # sin pips o sin jugadas → cerrar
            if not self.is_turn_over():
                # Si quedan pips pero no hay jugadas, los descartamos (regla simplificada)
                self.__pips__ = tuple()
            self.end_turn()
            return True
        return False
