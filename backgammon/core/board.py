class Board:
    """Tablero de Backgammon: 24 puntos y administración de fichas."""
    NUM_POINTS = 24
    WHITE = 1
    BLACK = -1

    def __init__(self):
        self.__points__ = [0] * self.NUM_POINTS
        # contadores de barra (no se incluyen en count_total())
        self.__white_bar__ = 0
        self.__black_bar__ = 0

    # --- getters auxiliares existentes/previos ---
    def num_points(self) -> int:
        return self.NUM_POINTS

    def __check_index__(self, idx: int):
        if not isinstance(idx, int):
            raise TypeError("El índice debe ser int")
        if not (0 <= idx < self.NUM_POINTS):
            raise ValueError("Índice fuera de rango")

    def get_point(self, idx: int) -> int:
        self.__check_index__(idx)
        return self.__points__[idx]

    def set_point(self, idx: int, value: int) -> None:
        self.__check_index__(idx)
        self.__points__[idx] = int(value)

    def count_total(self, color: int) -> int:
        """Total de fichas de ese color en el tablero (excluye barra)."""
        if color == self.WHITE:
            return sum(v for v in self.__points__ if v > 0)
        elif color == self.BLACK:
            return sum(-v for v in self.__points__ if v < 0)
        raise ValueError("Color inválido")

    # NUEVO: barra
    def bar_count(self, color: int) -> int:
        if color == self.WHITE:
            return self.__white_bar__
        elif color == self.BLACK:
            return self.__black_bar__
        raise ValueError("Color inválido")

    def _inc_bar(self, color: int) -> None:
        if color == self.WHITE:
            self.__white_bar__ += 1
        elif color == self.BLACK:
            self.__black_bar__ += 1
        else:
            raise ValueError("Color inválido")

    # --- setup inicial que ya usábamos ---
    def setup_initial(self) -> None:
        P = [0] * 24
        # Blancas: 24(=idx 23):2, 13(12):5, 8(7):3, 6(5):5
        P[23] = 2; P[12] = 5; P[7] = 3; P[5] = 5
        # Negras: 1(0):-2, 12(11):-5, 17(16):-3, 19(18):-5
        P[0] = -2; P[11] = -5; P[16] = -3; P[18] = -5
        self.__points__ = P
        self.__white_bar__ = 0
        self.__black_bar__ = 0

    # --- utilidades que ya veníamos usando en tests ---
    def owner_at(self, idx: int) -> int:
        self.__check_index__(idx)
        v = self.__points__[idx]
        if v > 0: return self.WHITE
        if v < 0: return self.BLACK
        return 0

    def count_at(self, idx: int) -> int:
        self.__check_index__(idx)
        v = self.__points__[idx]
        return abs(v)

    def is_blocked(self, idx: int, mover_color: int) -> bool:
        """Punto bloqueado si tiene 2+ fichas del rival."""
        self.__check_index__(idx)
        own = self.WHITE if mover_color == self.WHITE else self.BLACK
        opp = self.BLACK if own == self.WHITE else self.WHITE
        v = self.__points__[idx]
        # bloqueado si hay 2+ del rival
        return (v >= 2 and opp == self.WHITE) or (v <= -2 and opp == self.BLACK)

    def dest_from(self, origin: int, pip: int, mover_color: int) -> int:
        self.__check_index__(origin)
        if not isinstance(pip, int) or pip <= 0:
            raise ValueError("Pip inválido")
        if mover_color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        if mover_color == self.WHITE:
            dest = origin - pip
        else:
            dest = origin + pip
        if not (0 <= dest < self.NUM_POINTS):
            raise ValueError("Destino fuera de tablero")
        return dest

    def can_move(self, origin: int, pip: int, mover_color: int) -> bool:
        """Permite mover a vacío, propio o blot rival (1). Bloqueado (rival≥2) = False."""
        self.__check_index__(origin)
        if mover_color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        # Debe haber ficha propia en origin
        if self.owner_at(origin) != mover_color or self.count_at(origin) <= 0:
            return False
        try:
            dest = self.dest_from(origin, pip, mover_color)
        except Exception:
            return False
        # bloqueado por 2+ del rival
        if self.is_blocked(dest, mover_color):
            return False
        return True  # vacío, propio o blot rival (1) son válidos

    def move(self, origin: int, pip: int, mover_color: int) -> int:
        """Aplica el movimiento y gestiona 'hit' si el destino tiene 1 del rival."""
        if not self.can_move(origin, pip, mover_color):
            raise ValueError("Movimiento inválido para el estado actual del tablero")
        dest = self.dest_from(origin, pip, mover_color)

        # Quitar del origen
        v = self.__points__[origin]
        if mover_color == self.WHITE:
            self.__points__[origin] = v - 1
        else:
            self.__points__[origin] = v + 1

        # Gestionar destino (hit si blot rival)
        dv = self.__points__[dest]
        if mover_color == self.WHITE:
            if dv == -1:
                # golpear negra -> va a barra negra
                self.__points__[dest] = 1
                self._inc_bar(self.BLACK)
            else:
                self.__points__[dest] = dv + 1
        else:
            if dv == 1:
                # golpear blanca -> va a barra blanca
                self.__points__[dest] = -1
                self._inc_bar(self.WHITE)
            else:
                self.__points__[dest] = dv - 1

        return dest
