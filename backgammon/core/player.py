class Player:
    """Representa un jugador de Backgammon."""
    def __init__(self, name: str, color: str):
        self.__name__ = name
        self.__color__ = color
        self.__checkers__ = 15
