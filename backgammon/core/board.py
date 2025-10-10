class Board:
    """Tablero de Backgammon: 24 puntos y administración de fichas."""
    NUM_POINTS = 24
    WHITE = 1
    BLACK = -1

    def __init__(self):
        self.__points__ = [0] * self.NUM_POINTS
        # Barra por color (no cuenta en count_total)
        self.__white_bar__ = 0
        self.__black_bar__ = 0

    # ---------- utilidades básicas ----------
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
        """Total de fichas del color en los 24 puntos (excluye barra)."""
        if color == self.WHITE:
            return sum(v for v in self.__points__ if v > 0)
        elif color == self.BLACK:
            return sum(-v for v in self.__points__ if v < 0)
        raise ValueError("Color inválido")

    # ---------- barra ----------
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

    def _dec_bar(self, color: int) -> None:
        if color == self.WHITE:
            if self.__white_bar__ <= 0:
                raise ValueError("Barra blanca vacía")
            self.__white_bar__ -= 1
        elif color == self.BLACK:
            if self.__black_bar__ <= 0:
                raise ValueError("Barra negra vacía")
            self.__black_bar__ -= 1
        else:
            raise ValueError("Color inválido")

    # ---------- setup ----------
    def setup_initial(self) -> None:
        P = [0] * 24
        # Blancas: 24(=idx 23):2, 13(12):5, 8(7):3, 6(5):5
        P[23] = 2; P[12] = 5; P[7]  = 3; P[5]  = 5
        # Negras: 1(0):-2, 12(11):-5, 17(16):-3, 19(18):-5
        P[0]  = -2; P[11] = -5; P[16] = -3; P[18] = -5
        self.__points__ = P
        self.__white_bar__ = 0
        self.__black_bar__ = 0

    # ---------- consultas de punto ----------
    def owner_at(self, idx: int) -> int:
        self.__check_index__(idx)
        v = self.__points__[idx]
        if v > 0: return self.WHITE
        if v < 0: return self.BLACK
        return 0

    def count_at(self, idx: int) -> int:
        self.__check_index__(idx)
        return abs(self.__points__[idx])

    def is_blocked(self, idx: int, mover_color: int) -> bool:
        """Punto bloqueado si tiene 2+ fichas del rival."""
        self.__check_index__(idx)
        if mover_color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        v = self.__points__[idx]
        if mover_color == self.WHITE:
            # bloquean negras con 2+
            return v <= -2
        else:
            # bloquean blancas con 2+
            return v >= 2

    # ---------- destinos, movimiento normal ----------
    def dest_from(self, origin: int, pip: int, mover_color: int) -> int:
        self.__check_index__(origin)
        if not isinstance(pip, int) or pip <= 0:
            raise ValueError("Pip inválido")
        if mover_color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        dest = origin - pip if mover_color == self.WHITE else origin + pip
        if not (0 <= dest < self.NUM_POINTS):
            raise ValueError("Destino fuera de tablero")
        return dest

    def can_move(self, origin: int, pip: int, mover_color: int) -> bool:
        if mover_color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        # si hay fichas en barra, no se puede mover normal
        if self.bar_count(mover_color) > 0:
            return False
        # Debe haber ficha propia en origin
        if self.owner_at(origin) != mover_color or self.count_at(origin) == 0:
            return False
        try:
            dest = self.dest_from(origin, pip, mover_color)
        except Exception:
            return False
        if self.is_blocked(dest, mover_color):
            return False
        return True  # vacío, propio o blot rival (1)

    def move(self, origin: int, pip: int, mover_color: int) -> int:
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
                self.__points__[dest] = 1
                self._inc_bar(self.BLACK)
            else:
                self.__points__[dest] = dv + 1
        else:
            if dv == 1:
                self.__points__[dest] = -1
                self._inc_bar(self.WHITE)
            else:
                self.__points__[dest] = dv - 1

        return dest

    # ---------- entrada desde barra ----------
    def entry_index(self, pip: int, color: int) -> int:
        """
        Punto de entrada desde barra según color y pip.
        Convención de índices 0..23:
          - WHITE entra en el home de BLACK (top), que es 23..18.
            Fórmula: dest = 24 - pip  -> índices 23..18
          - BLACK entra en el home de WHITE (bottom), que es 0..5.
            Fórmula: dest = pip - 1   -> índices 0..5
        """
        if not isinstance(pip, int) or pip <= 0:
            raise ValueError("Pip inválido")
        if color == self.WHITE:
            dest = 24 - pip
        elif color == self.BLACK:
            dest = pip - 1
        else:
            raise ValueError("Color inválido")
        if not (0 <= dest < self.NUM_POINTS):
            raise ValueError("Destino fuera de tablero")
        return dest

    def can_enter(self, pip: int, color: int) -> bool:
        """Se puede entrar si hay ficha en barra y el punto de entrada no está bloqueado."""
        if color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        if self.bar_count(color) <= 0:
            return False
        try:
            dest = self.entry_index(pip, color)
        except Exception:
            return False
        if self.is_blocked(dest, color):
            return False
        return True

    def enter_from_bar(self, pip: int, color: int) -> int:
        """
        Entra una ficha desde la barra usando 'pip'.
        Captura si hay blot rival en el destino.
        Devuelve el índice destino.
        """
        if not self.can_enter(pip, color):
            raise ValueError("No se puede entrar con ese pip/color")
        dest = self.entry_index(pip, color)
        dv = self.__points__[dest]

        # sale de barra
        self._dec_bar(color)

        if color == self.WHITE:
            if dv == -1:
                self.__points__[dest] = 1
                self._inc_bar(self.BLACK)
            else:
                self.__points__[dest] = dv + 1
        else:
            if dv == 1:
                self.__points__[dest] = -1
                self._inc_bar(self.WHITE)
            else:
                self.__points__[dest] = dv - 1
        return dest
