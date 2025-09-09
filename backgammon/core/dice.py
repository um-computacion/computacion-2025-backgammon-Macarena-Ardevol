import random

class Dice:
    """
    Representa los dados usados en Backgammon.
    """
    def roll(self):
        return random.randint(1, 6)
