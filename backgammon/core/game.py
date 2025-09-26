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
        self.__pips_left__ = []

    # --- gestión de jugadores / turno ---
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

    # acceso a objetos internos (solo lectura) 
    def board(self):
        return self.__board__

    def players(self):
        return tuple(self.__players__)

    # configuración inicial
    def setup_board(self) -> None:
        self.__board__.setup_initial()

    # dados / pips
    def start_turn(self, roll: tuple[int, int] | None = None) -> tuple[int, int]:
        """Inicia el turno tirando dados (o usando un roll fijo para test)."""
        self.__last_roll__ = roll if roll is not None else self.__dice__.roll()
        a, b = self.__last_roll__
        base = (a, a, a, a) if a == b else (a, b)
        self.__pips__ = base
        self.__pips_left__ = list(base)
        return self.__last_roll__

    def last_roll(self) -> tuple[int, int] | None:
        return self.__last_roll__

    def pips(self) -> tuple[int, ...]:
        """Pips restantes por jugar en el turno actual."""
        return tuple(self.__pips_left__)

    # helpers de reglas
    def _color_sign(self) -> int:
        """WHITE -> +1, BLACK -> -1 en términos del Board."""
        cp = self.current_player()
        if cp is None:
            raise ValueError("No hay jugadores")
        color = cp.get_color().lower() if hasattr(cp, "get_color") else cp.__color__.lower()
        if color == "white":
            return Board.WHITE
        if color == "black":
            return Board.BLACK
        raise ValueError("Color de jugador inválido")

    # validar / aplicar movimientos
    def can_play_move(self, origin: int, pip: int) -> bool:
        """True si el pip está disponible y el tablero permite el movimiento."""
        if pip not in self.__pips_left__:
            return False
        try:
            color = self._color_sign()
        except Exception:
            return False
        return self.__board__.can_move(origin, pip, color)

    def apply_move(self, origin: int, pip: int) -> int:
        """
        Aplica un movimiento del jugador actual consumiendo un pip.
        Retorna el índice de destino. Lanza ValueError si no se puede.
        """
        if pip not in self.__pips_left__:
            raise ValueError("Pip no disponible para este turno")
        color = self._color_sign()
        dest = self.__board__.move(origin, pip, color)
        self.__pips_left__.remove(pip)
        return dest
