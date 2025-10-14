class Board:
    """Tablero de Backgammon: 24 puntos, barra y borne-off."""
    NUM_POINTS = 24
    WHITE = 1
    BLACK = -1

    def __init__(self):
        self.__points__ = [0] * self.NUM_POINTS
        # Barra (capturas)
        self.__white_bar__ = 0
        self.__black_bar__ = 0
        # Fichas borne-off (retiradas)
        self.__white_borne_off__ = 0
        self.__black_borne_off__ = 0

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
        """Total de fichas del color en los 24 puntos (excluye barra y borne-off)."""
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

    # ---------- borne-off ----------
    def borne_off_count(self, color: int) -> int:
        if color == self.WHITE:
            return self.__white_borne_off__
        elif color == self.BLACK:
            return self.__black_borne_off__
        raise ValueError("Color inválido")

    def _inc_borne_off(self, color: int) -> None:
        if color == self.WHITE:
            self.__white_borne_off__ += 1
        elif color == self.BLACK:
            self.__black_borne_off__ += 1
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
        self.__white_borne_off__ = 0
        self.__black_borne_off__ = 0

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
            return v <= -2  # negras 2+
        else:
            return v >= 2   # blancas 2+

    # ---------- homes y helpers ----------
    def home_indices(self, color: int) -> range:
        if color == self.WHITE:
            return range(0, 6)     # 0..5
        elif color == self.BLACK:
            return range(18, 24)   # 18..23
        else:
            raise ValueError("Color inválido")

    def all_in_home(self, color: int) -> bool:
        """¿Todas las fichas de 'color' están en su home (sin contar barra)?"""
        if color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        if self.bar_count(color) > 0:
            return False
        home = set(self.home_indices(color))
        if color == self.WHITE:
            # no debe haber blancas fuera de 0..5
            return all((v <= 0) or (i in home) for i, v in enumerate(self.__points__))
        else:
            # no debe haber negras fuera de 18..23
            return all((v >= 0) or (i in home) for i, v in enumerate(self.__points__))

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
        if self.bar_count(mover_color) > 0:
            return False
        if self.owner_at(origin) != mover_color or self.count_at(origin) == 0:
            return False
        try:
            dest = self.dest_from(origin, pip, mover_color)
        except Exception:
            return False
        if self.is_blocked(dest, mover_color):
            return False
        return True

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
        if not isinstance(pip, int) or pip <= 0:
            raise ValueError("Pip inválido")
        if color == self.WHITE:
            dest = 24 - pip            # 23..18
        elif color == self.BLACK:
            dest = pip - 1             # 0..5
        else:
            raise ValueError("Color inválido")
        if not (0 <= dest < self.NUM_POINTS):
            raise ValueError("Destino fuera de tablero")
        return dest

    def can_enter(self, pip: int, color: int) -> bool:
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
        if not self.can_enter(pip, color):
            raise ValueError("No se puede entrar con ese pip/color")
        dest = self.entry_index(pip, color)
        dv = self.__points__[dest]
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

    # ---------- bear-off (retirar fichas) ----------
    def _has_higher_in_home(self, origin: int, color: int) -> bool:
        """¿Hay fichas propias en posiciones 'más altas' dentro del home?
        WHITE: índices mayores (origin+1..5).  BLACK: índices menores (18..origin-1)."""
        if color == self.WHITE:
            rng = range(origin + 1, 6)
            return any(self.owner_at(i) == self.WHITE and self.count_at(i) > 0 for i in rng)
        else:
            rng = range(18, origin)
            return any(self.owner_at(i) == self.BLACK and self.count_at(i) > 0 for i in rng)

    def can_bear_off(self, origin: int, pip: int, color: int) -> bool:
        if color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        if not isinstance(pip, int) or pip <= 0:
            raise ValueError("Pip inválido")
        if self.owner_at(origin) != color or self.count_at(origin) == 0:
            return False
        if not self.all_in_home(color):
            return False

        # Exacto o mayor sin fichas "más altas"
        try:
            if color == self.WHITE:
                dest = origin - pip
                if dest == -1:  # exacto (salir del tablero)
                    return True
                if dest < 0:
                    return not self._has_higher_in_home(origin, color)
                # si dest dentro tablero, entonces no es bear-off sino move normal
                return False
            else:
                dest = origin + pip
                if dest == 24:
                    return True
                if dest > 23:
                    return not self._has_higher_in_home(origin, color)
                return False
        except Exception:
            return False

    def bear_off(self, origin: int, pip: int, color: int) -> None:
        if not self.can_bear_off(origin, pip, color):
            raise ValueError("No se puede retirar esa ficha (bear-off)")
        # Quitar una ficha del origen
        v = self.__points__[origin]
        if color == self.WHITE:
            self.__points__[origin] = v - 1
        else:
            self.__points__[origin] = v + 1
        self._inc_borne_off(color)
