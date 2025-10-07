def main():
    # Import lazy para no romper CI si no está pygame
    try:
        import pygame
    except ImportError:
        print("Pygame no está instalado. Instalá con: pip install pygame")
        return

    from backgammon.core.board import Board

    # Config 
    W, H = 800, 600
    MARGIN = 40
    TRI_H = 120
    BG = (240, 240, 240)
    TOP_CLR = (50, 90, 160)
    BOT_CLR = (160, 90, 50)
    TXT = (20, 20, 20)
    HILIGHT = (240, 200, 60)
    OUTLINE = (30, 30, 30)

    def tri_polygon_top(i, col_w):
        x0 = MARGIN + i * col_w
        x1 = x0 + col_w
        return [(x0, MARGIN), (x1, MARGIN), ((x0 + x1) / 2, MARGIN + TRI_H)]

    def tri_polygon_bottom(i, col_w):
        x0 = MARGIN + i * col_w
        x1 = x0 + col_w
        return [(x0, H - MARGIN), (x1, H - MARGIN),
                ((x0 + x1) / 2, H - MARGIN - TRI_H)]

    def hover_index(mx, my, col_w):
        # Top band
        if MARGIN <= my <= MARGIN + TRI_H:
            i = int((mx - MARGIN) // col_w)
            if 0 <= i < 12 and MARGIN <= mx <= MARGIN + 12 * col_w:
                return i  # 0..11
        # Bottom band
        if (H - MARGIN - TRI_H) <= my <= (H - MARGIN):
            i = int((mx - MARGIN) // col_w)
            if 0 <= i < 12 and MARGIN <= mx <= MARGIN + 12 * col_w:
                return 12 + i  # 12..23
        return None

    # Init 
    pygame.init()
    try:
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Backgammon - UI mínima")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 24)

        board = Board()
        board.setup_initial()

        width = W - 2 * MARGIN
        col_w = width / 12

        running = True
        while running:
            # Eventos básicos (cerrar/ESC)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # Fondo
            screen.fill(BG)

            mx, my = pygame.mouse.get_pos()
            idx = hover_index(mx, my, col_w)

            # Triángulos superiores (puntos 0..11)
            for i in range(12):
                poly = tri_polygon_top(i, col_w)
                color = HILIGHT if idx == i else TOP_CLR
                pygame.draw.polygon(screen, color, poly)
                # contorno si está resaltado
                if idx == i:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=2)

            # Triángulos inferiores (puntos 12..23)
            for i in range(12):
                poly = tri_polygon_bottom(i, col_w)
                pt_index = 12 + i
                color = HILIGHT if idx == pt_index else BOT_CLR
                pygame.draw.polygon(screen, color, poly)
                if idx == pt_index:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=2)

            # Totales de fichas
            white_total = board.count_total(Board.WHITE)
            black_total = board.count_total(Board.BLACK)
            info = font.render(f"White: {white_total} | Black: {black_total}", True, TXT)
            screen.blit(info, (MARGIN, MARGIN - 28))

            # Tooltip simple de hover (índice, dueño, cantidad)
            if idx is not None:
                try:
                    owner = board.owner_at(idx)
                    cnt = board.count_at(idx)
                    owner_lbl = "White" if owner == Board.WHITE else ("Black" if owner == Board.BLACK else "Empty")
                    tip = font.render(f"Point {idx} | {owner_lbl} x{cnt}", True, TXT)
                    # Mostrar arriba si el punto es top, abajo si es bottom
                    tip_y = MARGIN + TRI_H + 8 if idx <= 11 else (H - MARGIN - TRI_H - 28)
                    screen.blit(tip, (MARGIN, tip_y))
                except Exception:
                    # Si algo raro pasa con índices (no debería), ignoramos el tooltip
                    pass

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
