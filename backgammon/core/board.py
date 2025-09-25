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

    # --- Helpers de movimiento y consulta ---

    def _validate_index(self, index: int) -> None:
        if not (0 <= index < self.NUM_POINTS):
            raise ValueError("Índice de punto fuera de rango")

    def _validate_color(self, color: int) -> None:
        if color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido (use Board.WHITE o Board.BLACK)")

    def owner_at(self, index: int) -> int:
        """Devuelve Board.WHITE, Board.BLACK o 0 si el punto está vacío."""
        self._validate_index(index)
        v = self.__points__[index]
        if v > 0:
            return self.WHITE
        if v < 0:
            return self.BLACK
        return 0

    def count_at(self, index: int) -> int:
        """Cantidad de fichas (valor absoluto) en el punto."""
        self._validate_index(index)
        return abs(self.__points__[index])

    def is_blocked(self, index: int, mover_color: int) -> bool:
        """True si el punto está bloqueado para 'mover_color' (2+ fichas rivales)."""
        self._validate_index(index)
        self._validate_color(mover_color)
        owner = self.owner_at(index)
        if owner == 0 or owner == mover_color:
            return False
        return self.count_at(index) >= 2

    def dest_from(self, origin: int, pip: int, mover_color: int) -> int:
        """
        Calcula destino desde 'origin' con 'pip' según el color:
        - WHITE: decrece índices (hacia 0)
        - BLACK: crece índices (hacia 23)
        Lanza ValueError si queda fuera del tablero o parámetros inválidos.
        """
        self._validate_index(origin)
        self._validate_color(mover_color)
        if not isinstance(pip, int) or pip <= 0:
            raise ValueError("pip inválido (debe ser entero positivo)")
        dest = origin - pip if mover_color == self.WHITE else origin + pip
        if not (0 <= dest < self.NUM_POINTS):
            raise ValueError("Destino fuera del tablero")
        return dest
