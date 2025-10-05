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

    # gestión de jugadores / turno 
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

    # listado de movimientos posibles 
    def legal_moves(self) -> list[tuple[int, int, int]]:
        """Lista (origin, pip, dest) posibles para el jugador actual con los pips restantes."""
        color = self._color_sign()
        return self.__board__.legal_moves(color, list(self.__pips_left__))

    def has_any_move(self) -> bool:
        """True si el jugador actual puede mover con los pips restantes."""
        return len(self.legal_moves()) > 0

    # cierre/rotación de turnos 
    def is_turn_over(self) -> bool:
        """True si no quedan pips por jugar en el turno actual."""
        return len(self.__pips_left__) == 0

    def end_turn(self) -> None:
        """
        Finaliza el turno solo si no quedan pips. Rota al siguiente jugador
        y limpia el estado de tirada.
        """
        if not self.is_turn_over():
            raise ValueError("Aún quedan pips por jugar")
        self.next_turn()
        self.__last_roll__ = None
        self.__pips__ = tuple()
        self.__pips_left__.clear()

    def can_auto_end(self) -> bool:
        """True si hay pips restantes pero no existe ninguna jugada legal."""
        return len(self.__pips_left__) > 0 and not self.has_any_move()

    def auto_end_turn(self) -> bool:
        """
        Si no hay jugadas legales con los pips restantes, consume los pips y cierra el turno.
        Retorna True si se cerró automáticamente, False en caso contrario.
        """
        if not self.can_auto_end():
            return False
        self.__pips_left__.clear()
        self.end_turn()
        return True

    def current_player_label(self) -> str:
        """Nombre y color del jugador actual (útil para CLI)."""
        cp = self.current_player()
        if cp is None:
            return "N/A"
        name = cp.get_name() if hasattr(cp, "get_name") else getattr(cp, "__name__", "?")
        color = cp.get_color() if hasattr(cp, "get_color") else getattr(cp, "__color__", "?")
        return f"{name} ({color})"
