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
        self.__last_roll__ = None          # tuple[int,int] | None
        self.__pips__ = tuple()            # tuple[int,...]
        self.__turn_history__ = []         # [(origin, dest, color, pip)]
        self.__turn_started__ = False      # para validar “hay tirada activa”

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
        """Devuelve el tablero actual (solo lectura)."""
        return self.__board__

    def players(self):
        """Devuelve una tupla con los jugadores (solo lectura)."""
        return tuple(self.__players__)

    def setup_board(self) -> None:
        self.__board__.setup_initial()

    # ---------- Turnos / dados / pips ----------
    def start_turn(self, roll: tuple[int, int] | None = None) -> tuple[int, int]:
        """Inicia el turno tirando dados (o usando un roll fijo para test)."""
        self.__last_roll__ = roll if roll is not None else self.__dice__.roll()
        a, b = self.__last_roll__
        self.__pips__ = (a, a, a, a) if a == b else (a, b)
        self.__turn_history__.clear()
        self.__turn_started__ = True
        return self.__last_roll__

    def last_roll(self) -> tuple[int, int] | None:
        return self.__last_roll__

    def pips(self) -> tuple[int, ...]:
        return self.__pips__

    def is_turn_over(self) -> bool:
        return len(self.__pips__) == 0

    def end_turn(self) -> None:
        if not self.is_turn_over():
            raise ValueError("Aún quedan pips por jugar")
        if self.__players__:
            self.__current_player_index__ = (self.__current_player_index__ + 1) % len(self.__players__)
        # limpiar estado de turno
        self.__last_roll__ = None
        self.__pips__ = tuple()
        self.__turn_history__.clear()
        self.__turn_started__ = False

    def next_turn(self) -> None:
        """Alias histórico usado en algunos tests: rota el jugador sin validar pips."""
        if self.__players__:
            self.__current_player_index__ = (self.__current_player_index__ + 1) % len(self.__players__)

    def auto_end_turn(self) -> bool:
        """Rota el turno automáticamente si no hay jugadas legales con los pips actuales."""
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
            return Board.WHITE  # por defecto, no rompe
        # Usar getter si está disponible; si no, caer a atributo interno o público
        if hasattr(p, "get_color") and callable(p.get_color):
            color = p.get_color()
        else:
            color = getattr(p, "_Player__color__", getattr(p, "color", None))
        return Board.WHITE if color == "white" else Board.BLACK

    # ---------- Barra: API pública de Game sobre Board ----------
    def bar_count(self, color: int) -> int:
        return self.__board__.bar_count(color)

    def _has_pieces_on_bar(self, color: int) -> bool:
        return self.__board__.bar_count(color) > 0

    def can_enter_from_bar(self, pip: int) -> bool:
        """¿Puedo entrar desde la barra usando este pip?"""
        color = self._current_color_int()
        try:
            return self.__board__.can_enter(pip, color)
        except Exception:
            return False

    # Alias esperado por algunos tests
    def can_enter(self, pip: int) -> bool:
        return self.can_enter_from_bar(pip)

    def enter_from_bar(self, pip: int) -> int:
        """Entra una ficha desde la barra usando este pip. Devuelve el destino."""
        color = self._current_color_int()
        dest = self.__board__.enter_from_bar(pip, color)
        # consumir pip
        pips = list(self.__pips__)
        pips.remove(pip)
        self.__pips__ = tuple(pips)
        # registrar en historia (origen especial: -1)
        self.__turn_history__.append((-1, dest, color, pip))
        return dest

    # ---------- Movimientos ----------
    def legal_moves(self):
        """Devuelve una lista de movimientos legales como (origin, dest, pip).
        Si hay fichas en barra, solo lista entradas desde barra."""
        color = self._current_color_int()
        res = []
        pips = sorted(set(self.__pips__))
        if not pips:
            return res

        if self._has_pieces_on_bar(color):
            for pip in pips:
                if self.can_enter_from_bar(pip):
                    try:
                        dest = self.__board__.dest_from_bar(pip, color)
                        res.append((-1, dest, pip))
                    except Exception:
                        pass
            return res

        # movimientos normales
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
        """Devuelve False si no hay tirada activa o si el movimiento no es legal."""
        if not self.__turn_started__ or not self.__pips__:
            return False
        color = self._current_color_int()
        # si hay fichas en barra, sólo se permiten entradas desde barra
        if self._has_pieces_on_bar(color):
            return origin == -1 and self.can_enter_from_bar(pip)
        try:
            return self.__board__.can_move(origin, pip, color)
        except Exception:
            return False

    def apply_move(self, origin: int, pip: int) -> int:
        """Aplica un movimiento usando `pip`. Devuelve el índice destino."""
        color = self._current_color_int()

        if not self.__turn_started__:
            raise ValueError("No hay tirada activa")

        # si hay fichas en barra, obligar entrada
        if self._has_pieces_on_bar(color) and origin != -1:
            raise ValueError("Debes reingresar desde la barra antes de mover otras fichas")

        # consumir pip si el movimiento es válido
        pips = list(self.__pips__)
        if pip not in pips:
            raise ValueError("Pip no disponible en este turno")

        if origin == -1:
            # entrada desde barra
            dest = self.enter_from_bar(pip)
            return dest

        # movimiento normal
        if not self.__board__.can_move(origin, pip, color):
            raise ValueError("Movimiento inválido para el estado actual del tablero")

        dest = self.__board__.move(origin, pip, color)
        pips.remove(pip)
        self.__pips__ = tuple(pips)
        self.__turn_history__.append((origin, dest, color, pip))
        return dest

    # ---------- Serialización (para guardado/carga) ----------
    def to_dict(self) -> dict:
        """Estado serializable de la partida (para JSON)."""
        # Jugadores
        players = []
        for p in self.__players__:
            if hasattr(p, "get_name") and callable(p.get_name):
                name = p.get_name()
            else:
                name = getattr(p, "_Player__name__", getattr(p, "name", ""))
            if hasattr(p, "get_color") and callable(p.get_color):
                color = p.get_color()
            else:
                color = getattr(p, "_Player__color__", getattr(p, "color", "white"))
            players.append({"name": name, "color": color})

        # Tablero (usar snapshot público)
        snap = self.__board__.snapshot()

        return {
            "players": players,
            "current_player_index": self.__current_player_index__,
            "board": snap,
            "last_roll": list(self.__last_roll__) if self.__last_roll__ else None,
            "pips": list(self.__pips__),
            "turn_history": list(self.__turn_history__),
            "turn_started": bool(self.__turn_started__),
        }

    @staticmethod
    def from_dict(data: dict) -> "BackgammonGame":
        """Crea una partida desde un dict (complemento de to_dict)."""
        g = BackgammonGame()
        # jugadores
        for pl in data.get("players", []):
            g.add_player(pl.get("name", ""), pl.get("color", "white"))
        # índice actual
        g.__current_player_index__ = int(data.get("current_player_index", 0))
        # tablero
        board_snap = data.get("board", {})
        g.__board__.restore(board_snap)
        # turno
        lr = data.get("last_roll", None)
        g.__last_roll__ = tuple(lr) if lr is not None else None
        g.__pips__ = tuple(int(x) for x in data.get("pips", []))
        g.__turn_history__ = [tuple(x) for x in data.get("turn_history", [])]
        g.__turn_started__ = bool(data.get("turn_started", False))
        return g
