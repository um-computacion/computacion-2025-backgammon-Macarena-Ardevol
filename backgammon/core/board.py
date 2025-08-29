class Board:
    """
    Representa el tablero de Backgammon.
    Contiene 24 puntos y administra las fichas de los jugadores.
    """
    def __init__(self):
        self.points = [0] * 24
