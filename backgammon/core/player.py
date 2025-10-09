class Player:
    """Representa un jugador de Backgammon."""
    def __init__(self, name: str, color: str):
        self.__name__ = name
        self.__color__ = color
        self.__checkers__ = 15

    def get_name(self) -> str:
        return self.__name__

    def get_color(self) -> str:
        return self.__color__

    def get_checkers(self) -> int:
        return self.__checkers__
