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
    HILIGHT = (240, 200, 60)   # hover
    SELECT = (120, 200, 120)   # seleccionado
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
        # Banda superior  (0..11)
        if MARGIN <= my <= MARGIN + TRI_H:
            i = int((mx - MARGIN) // col_w)
            if 0 <= i < 12 and MARGIN <= mx <= MARGIN + 12 * col_w:
                return i
        # Banda inferior (12..23)
        if (H - MARGIN - TRI_H) <= my <= (H - MARGIN):
            i = int((mx - MARGIN) // col_w)
            if 0 <= i < 12 and MARGIN <= mx <= MARGIN + 12 * col_w:
                return 12 + i
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

        selected_idx = None

        running = True
        while running:
            mx, my = pygame.mouse.get_pos()
            idx_hover = hover_index(mx, my, col_w)

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # ESC: limpiar selección o salir si no hay selección
                    if selected_idx is not None:
                        selected_idx = None
                    else:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Click izquierdo: seleccionar/deseleccionar
                    if idx_hover is not None:
                        if selected_idx == idx_hover:
                            selected_idx = None
                        else:
                            selected_idx = idx_hover
                    else:
                        selected_idx = None

            # Fondo
            screen.fill(BG)

            # Dibujar triángulos superiores (0..11)
            for i in range(12):
                poly = tri_polygon_top(i, col_w)
                if selected_idx == i:
                    color = SELECT
                    border_w = 3
                elif idx_hover == i:
                    color = HILIGHT
                    border_w = 2
                else:
                    color = TOP_CLR
                    border_w = 0
                pygame.draw.polygon(screen, color, poly)
                if border_w:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=border_w)

            # Dibujar triángulos inferiores (12..23)
            for i in range(12):
                poly = tri_polygon_bottom(i, col_w)
                pt_index = 12 + i
                if selected_idx == pt_index:
                    color = SELECT
                    border_w = 3
                elif idx_hover == pt_index:
                    color = HILIGHT
                    border_w = 2
                else:
                    color = BOT_CLR
                    border_w = 0
                pygame.draw.polygon(screen, color, poly)
                if border_w:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=border_w)

            # Totales
            white_total = board.count_total(Board.WHITE)
            black_total = board.count_total(Board.BLACK)
            info = font.render(f"White: {white_total} | Black: {black_total}", True, TXT)
            screen.blit(info, (MARGIN, MARGIN - 28))

            # Tooltip hover
            if idx_hover is not None:
                try:
                    owner = board.owner_at(idx_hover)
                    cnt = board.count_at(idx_hover)
                    owner_lbl = "White" if owner == Board.WHITE else ("Black" if owner == Board.BLACK else "Empty")
                    tip = font.render(f"Hover: {idx_hover} | {owner_lbl} x{cnt}", True, TXT)
                    tip_y = MARGIN + TRI_H + 8 if idx_hover <= 11 else (H - MARGIN - TRI_H - 28)
                    screen.blit(tip, (MARGIN, tip_y))
                except Exception:
                    pass

            # Barra de estado selección
            status_msg = "Sin selección"
            if selected_idx is not None:
                try:
                    owner = board.owner_at(selected_idx)
                    cnt = board.count_at(selected_idx)
                    owner_lbl = "White" if owner == Board.WHITE else ("Black" if owner == Board.BLACK else "Empty")
                    status_msg = f"Seleccionado: {selected_idx} | {owner_lbl} x{cnt}   (ESC para limpiar)"
                except Exception:
                    status_msg = f"Seleccionado: {selected_idx}"
            status = font.render(status_msg, True, TXT)
            screen.blit(status, (MARGIN, H - MARGIN + 6 - 24))  # justo arriba del margen inferior

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
