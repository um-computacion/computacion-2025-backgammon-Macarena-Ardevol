class Board:
    """Tablero de Backgammon: 24 puntos y administración de fichas."""
    NUM_POINTS = 24

    def __init__(self):
        self.__points__ = [0] * self.NUM_POINTS
