class Player:
    """
    Representa un jugador de Backgammon.
    Cada jugador tiene un color y un conjunto de fichas.
    """
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.checkers = 15
