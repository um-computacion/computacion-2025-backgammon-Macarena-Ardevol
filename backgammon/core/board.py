class Board:
    """Tablero de Backgammon: 24 puntos y administración de fichas."""
    NUM_POINTS = 24
    WHITE = 1
    BLACK = -1

    def __init__(self):
        self.__points__ = [0] * self.NUM_POINTS

    def num_points(self) -> int:
        return len(self.__points__)

    def get_point(self, index: int) -> int:
        if not (0 <= index < self.NUM_POINTS):
            raise ValueError("Índice de punto fuera de rango")
        return self.__points__[index]

    def set_point(self, index: int, value: int) -> None:
        if not (0 <= index < self.NUM_POINTS):
            raise ValueError("Índice de punto fuera de rango")
        self.__points__[index] = value

    def setup_initial(self) -> None:
        """Coloca las fichas en posiciones iniciales estándar."""
        self.__points__ = [0] * self.NUM_POINTS
        # Blancas (positivas)
        self.__points__[23] = 2 * self.WHITE   # 24-point
        self.__points__[12] = 5 * self.WHITE   # 13-point
        self.__points__[7]  = 3 * self.WHITE   # 8-point
        self.__points__[5]  = 5 * self.WHITE   # 6-point
        # Negras (negativas)
        self.__points__[0]  = 2 * self.BLACK   # 1-point
        self.__points__[11] = 5 * self.BLACK   # 12-point
        self.__points__[16] = 3 * self.BLACK   # 17-point
        self.__points__[18] = 5 * self.BLACK   # 19-point

    def count_total(self, color: int) -> int:
        """Cantidad de fichas totales de un color (WHITE=+1, BLACK=-1)."""
        if color == self.WHITE:
            return sum(v for v in self.__points__ if v > 0)
        if color == self.BLACK:
            return -sum(v for v in self.__points__ if v < 0)
        raise ValueError("Color inválido")
