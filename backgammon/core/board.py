class Board:
    """
    Tablero de Backgammon:
    - 24 puntos indexados 0..23
    - WHITE (=1) se mueve hacia índices menores (origin - pip); su "home" es 0..5
    - BLACK (=-1) se mueve hacia índices mayores (origin + pip); su "home" es 18..23
    - Barra por color (fichas capturadas)
    - Borne-off / Off por color (fichas retiradas)
    """
    NUM_POINTS = 24
    WHITE = 1
    BLACK = -1

    def __init__(self):
        self.__points__ = [0] * self.NUM_POINTS
        # Barra y borne-off
        self.__white_bar__ = 0
        self.__black_bar__ = 0
        # Nombres "off" modernos; algunos tests/compat podrían buscar "borne_off"
        self.__white_off__ = 0
        self.__black_off__ = 0

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

    def owner_at(self, idx: int) -> int:
        self.__check_index__(idx)
        v = self.__points__[idx]
        if v > 0: return self.WHITE
        if v < 0: return self.BLACK
        return 0

    def count_at(self, idx: int) -> int:
        self.__check_index__(idx)
        return abs(self.__points__[idx])

    def count_total(self, color: int) -> int:
        """Total de fichas del color en tablero (excluye barra y off)."""
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

    # ---------- borne-off / off ----------
    def off_count(self, color: int) -> int:
        if color == self.WHITE:
            return self.__white_off__
        elif color == self.BLACK:
            return self.__black_off__
        raise ValueError("Color inválido")

    # alias de compatibilidad
    def borne_off_count(self, color: int) -> int:
        return self.off_count(color)

    def _inc_off(self, color: int, n: int = 1) -> None:
        if color == self.WHITE:
            self.__white_off__ += n
        elif color == self.BLACK:
            self.__black_off__ += n
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
        self.__white_off__ = 0
        self.__black_off__ = 0

    # ---------- reglas de bloqueo ----------
    def is_blocked(self, idx: int, mover_color: int) -> bool:
        """Punto bloqueado si tiene 2+ fichas del rival."""
        self.__check_index__(idx)
        if mover_color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        v = self.__points__[idx]
        if mover_color == self.WHITE:
            return v <= -2  # bloquean negras 2+
        else:
            return v >= 2   # bloquean blancas 2+

    # ---------- destinos / movimiento normal ----------
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
            return False  # mientras haya fichas en barra, no se mueven otras
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
        Punto de entrada desde barra:
          - WHITE entra en 23..18 => 24 - pip
          - BLACK entra en 0..5   => pip - 1
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

    # ---------- home / bear-off ----------
    def home_indices(self, color: int):
        """Indices de home por color (para reglas de bear-off)."""
        if color == self.WHITE:
            return range(0, 6)
        elif color == self.BLACK:
            return range(18, 24)
        raise ValueError("Color inválido")

    # alias de compatibilidad (algunos códigos esperan "home_range")
    def home_range(self, color: int):
        return self.home_indices(color)

    def all_in_home(self, color: int) -> bool:
        """¿Todas las fichas del color están en su home (y no en barra)?"""
        if self.bar_count(color) > 0:
            return False
        total = self.count_total(color)
        if total == 0:
            # Si no hay fichas en tablero, o están todas borne-off, también vale
            return True
        rng = self.home_indices(color)
        home_total = 0
        for i in rng:
            v = self.get_point(i)
            if color == self.WHITE and v > 0:
                home_total += v
            elif color == self.BLACK and v < 0:
                home_total += -v
        return home_total == total

    def can_bear_off(self, origin: int, pip: int, color: int) -> bool:
        """
        Regla estándar:
        - Solo si all_in_home(color)
        - Exacto: si origin±pip sale del tablero, permite off.
        - No exacto: si no hay fichas en puntos más alejados (más "lejanos" a la banda de salida)
        """
        if color not in (self.WHITE, self.BLACK):
            raise ValueError("Color inválido")
        if not isinstance(pip, int) or pip <= 0:
            raise ValueError("Pip inválido")

        # debe tener ficha propia en origin
        if self.owner_at(origin) != color or self.count_at(origin) == 0:
            return False
        if not self.all_in_home(color):
            return False

        try:
            # si el destino cae fuera del tablero en dirección de salida -> exacto
            _ = self.dest_from(origin, pip, color)
            # si no cae fuera, es que quedaría en tablero. Para bear-off exacto,
            # únicamente se podría si ese destino fuera "más allá" (pero aquí no lo es)
            return False
        except ValueError:
            #significa "cae fuera", puede ser off exacto o no-exacto
            pass

        # no-exacto: permitido si no hay fichas en puntos más alejados
        if color == self.WHITE:
            # WHITE sale por debajo de 0; puntos "más alejados" son los de mayor índice dentro de home
            # Si saco desde 'origin', no debe haber fichas en indices > origin dentro de [0..5]
            higher_has = any(self.owner_at(i) == self.WHITE and self.count_at(i) > 0 for i in range(origin + 1, 6))
            return not higher_has
        else:
            # BLACK sale por encima de 23; puntos "más alejados" son los de menor índice dentro de home
            # No debe haber fichas en indices < origin dentro de [18..23]
            lower_has = any(self.owner_at(i) == self.BLACK and self.count_at(i) > 0 for i in range(18, origin))
            return not lower_has

    def bear_off(self, origin: int, pip: int, color: int) -> None:
        if not self.can_bear_off(origin, pip, color):
            raise ValueError("No se puede hacer bear-off desde ese origen/pip")
        # quitar del origin
        v = self.get_point(origin)
        if color == self.WHITE:
            self.set_point(origin, v - 1)
            self._inc_off(self.WHITE, 1)
        else:
            self.set_point(origin, v + 1)
            self._inc_off(self.BLACK, 1)

