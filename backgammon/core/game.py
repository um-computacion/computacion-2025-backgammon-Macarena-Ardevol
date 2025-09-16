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

    def start_turn(self, roll: tuple[int, int] | None = None) -> tuple[int, int]:
        """Inicia el turno tirando dados (o usando un roll fijo para test)."""
        self.__last_roll__ = roll if roll is not None else self.__dice__.roll()
        a, b = self.__last_roll__
        self.__pips__ = (a, a, a, a) if a == b else (a, b)
        return self.__last_roll__

    def last_roll(self) -> tuple[int, int] | None:
        return self.__last_roll__

    def pips(self) -> tuple[int, ...]:
        return self.__pips__

    def setup_board(self) -> None:
        self.__board__.setup_initial()
