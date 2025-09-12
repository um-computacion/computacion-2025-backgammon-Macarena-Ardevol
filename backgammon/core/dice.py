import random

class Dice:
    """Representa los dados usados en Backgammon."""
    def __init__(self):
        self.__last_roll__ = None

    def roll(self) -> tuple[int, int]:
        a = random.randint(1, 6)
        b = random.randint(1, 6)
        self.__last_roll__ = (a, b)
        return self.__last_roll__

    def is_double(self) -> bool:
        if self.__last_roll__ is None:
            return False
        a, b = self.__last_roll__
        return a == b
