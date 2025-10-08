def main():
    # Import lazy para no romper CI si no está pygame
    try:
        import pygame
    except ImportError:
        print("Pygame no está instalado. Instalá con: pip install pygame")
        return

    from backgammon.core.board import Board

    # --- Config ---
    W, H = 800, 600
    MARGIN = 40
    TRI_H = 120
    PANEL_W = 260  # panel lateral derecho
    BG = (240, 240, 240)
    BG_PANEL = (230, 234, 244)
    SEP = (200, 200, 210)
    TOP_CLR = (50, 90, 160)
    BOT_CLR = (160, 90, 50)
    TXT = (20, 20, 20)
    HILIGHT = (240, 200, 60)   # hover
    SELECT = (120, 200, 120)   # seleccionado
    LEGAL = (60, 190, 140)     # destinos legales
    OUTLINE = (30, 30, 30)

    CHECKER_WHITE = (250, 250, 250)
    CHECKER_BLACK = (30, 30, 30)
    CHECKER_EDGE  = (10, 10, 10)
    R = 10  # radio de ficha dibujada
    GAP = 2 # gap vertical entre fichas

    # Área del tablero (izquierda); panel a la derecha
    BOARD_LEFT = MARGIN
    BOARD_RIGHT = W - MARGIN - PANEL_W
    BOARD_W = BOARD_RIGHT - BOARD_LEFT

    # ---- Helpers geom ----
    def tri_polygon_top(i, col_w):
        x0 = BOARD_LEFT + i * col_w
        x1 = x0 + col_w
        return [(x0, MARGIN), (x1, MARGIN), ((x0 + x1) / 2, MARGIN + TRI_H)]

    def tri_polygon_bottom(i, col_w):
        x0 = BOARD_LEFT + i * col_w
        x1 = x0 + col_w
        return [(x0, H - MARGIN), (x1, H - MARGIN),
                ((x0 + x1) / 2, H - MARGIN - TRI_H)]

    def hover_index(mx, my, col_w):
        # Solo si el mouse está dentro del ancho del tablero
        if not (BOARD_LEFT <= mx <= BOARD_RIGHT):
            return None
        # Banda superior (0..11)
        if MARGIN <= my <= MARGIN + TRI_H:
            i = int((mx - BOARD_LEFT) // col_w)
            if 0 <= i < 12:
                return i
        # Banda inferior (12..23)
        if (H - MARGIN - TRI_H) <= my <= (H - MARGIN):
            i = int((mx - BOARD_LEFT) // col_w)
            if 0 <= i < 12:
                return 12 + i
        return None

    # --- Lógica de simulación/movidas ---
    def pip_from_move(origin, dest, color):
        if color == Board.WHITE:
            return origin - dest
        elif color == Board.BLACK:
            return dest - origin
        return 0

    def owner_label(owner):
        return "White" if owner == Board.WHITE else ("Black" if owner == Board.BLACK else "Empty")

    def snapshot_points(b: Board):
        return tuple(b.get_point(i) for i in range(24))

    def restore_points(b: Board, snap):
        for i, v in enumerate(snap):
            b.set_point(i, v)

    def compute_legal_dests(b: Board, origin: int, color: int):
        """Devuelve lista de (dest, pip) para pips válidos 1..6 desde origin."""
        res = []
        for pip in range(1, 7):
            try:
                dest = b.dest_from(origin, pip, color)
            except Exception:
                continue
            try:
                if b.can_move(origin, pip, color):
                    res.append((dest, pip))
            except Exception:
                continue
        return res

    # --- Init ---
    pygame.init()
    try:
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Backgammon - UI mínima")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 24)
        font_small = pygame.font.SysFont(None, 16)

        board = Board()
        board.setup_initial()

        col_w = BOARD_W / 12

        # Estado UI
        selected_idx = None
        origin_idx = None
        message = ""
        show_help = True
        current_color = Board.WHITE
        history_snaps = []
        legal_dests = []  # lista de (dest, pip) para el origen seleccionado

        running = True
        while running:
            mx, my = pygame.mouse.get_pos()
            idx_hover = hover_index(mx, my, col_w)

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if origin_idx is not None or selected_idx is not None:
                            origin_idx = None
                            selected_idx = None
                            legal_dests = []
                            message = "Selección limpiada"
                        else:
                            running = False
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_h:
                        show_help = not show_help
                    elif event.key == pygame.K_t:
                        current_color = Board.BLACK if current_color == Board.WHITE else Board.WHITE
                        message = f"Color actual: {owner_label(current_color)}"
                        # recomputar legales si hay origen
                        legal_dests = compute_legal_dests(board, origin_idx, current_color) if origin_idx is not None else []
                    elif event.key == pygame.K_r:
                        board.setup_initial()
                        origin_idx = selected_idx = None
                        history_snaps.clear()
                        legal_dests = []
                        message = "Tablero reseteado"
                    elif event.key == pygame.K_u:
                        if history_snaps:
                            snap = history_snaps.pop()
                            restore_points(board, snap)
                            origin_idx = selected_idx = None
                            legal_dests = []
                            message = "Última jugada deshecha"
                        else:
                            message = "No hay jugadas para deshacer"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if idx_hover is None:
                        selected_idx = None
                        continue

                    if origin_idx is None:
                        selected_idx = idx_hover
                        origin_idx = idx_hover
                        own = board.owner_at(origin_idx)
                        if own != current_color:
                            message = f"Origen inválido: {origin_idx} no es de {owner_label(current_color)}"
                            origin_idx = None
                            legal_dests = []
                        else:
                            cnt = board.count_at(origin_idx)
                            if cnt <= 0:
                                message = f"Origen vacío: {origin_idx}"
                                origin_idx = None
                                legal_dests = []
                            else:
                                message = f"Origen: {origin_idx} ({owner_label(own)} x{cnt})"
                                legal_dests = compute_legal_dests(board, origin_idx, current_color)
                                if not legal_dests:
                                    message += " — sin destinos legales"
                    else:
                        dest_idx = idx_hover
                        pip = pip_from_move(origin_idx, dest_idx, current_color)
                        # Validamos contra la lista de legales si existe
                        if legal_dests and all(d != dest_idx for (d, _) in legal_dests):
                            message = f"No permitido: {origin_idx}->{dest_idx}"
                        else:
                            if pip < 1 or pip > 6 or not board.can_move(origin_idx, pip, current_color):
                                message = f"Movimiento bloqueado: {origin_idx}->{dest_idx} (pip {pip})"
                            else:
                                history_snaps.append(snapshot_points(board))
                                real_dest = board.move(origin_idx, pip, current_color)
                                message = f"Move: {origin_idx}->{real_dest} (pip {pip}, {owner_label(current_color)})"
                                origin_idx = None
                                selected_idx = None
                                legal_dests = []

            # Fondo
            screen.fill(BG)

            # ----- Tablero (izquierda) -----
            # Triángulos superiores (0..11)
            for i in range(12):
                poly = tri_polygon_top(i, col_w)
                if i == origin_idx:
                    color = SELECT; border_w = 3
                elif i == selected_idx or i == idx_hover:
                    color = HILIGHT; border_w = 2
                else:
                    color = TOP_CLR; border_w = 0
                pygame.draw.polygon(screen, color, poly)
                if border_w:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=border_w)

            # Triángulos inferiores (12..23)
            for i in range(12):
                poly = tri_polygon_bottom(i, col_w)
                pt_index = 12 + i
                if pt_index == origin_idx:
                    color = SELECT; border_w = 3
                elif pt_index == selected_idx or pt_index == idx_hover:
                    color = HILIGHT; border_w = 2
                else:
                    color = BOT_CLR; border_w = 0
                pygame.draw.polygon(screen, color, poly)
                if border_w:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=border_w)

            # Resaltar destinos legales (borde adicional)
            if origin_idx is not None and legal_dests:
                legal_set = {d for (d, _) in legal_dests}
                for i in range(24):
                    if i == origin_idx or i not in legal_set:
                        continue
                    if i <= 11:
                        poly = tri_polygon_top(i, col_w)
                    else:
                        poly = tri_polygon_bottom(i - 12, col_w)
                    pygame.draw.polygon(screen, LEGAL, poly, width=3)

            # Totales arriba-izquierda
            white_total = board.count_total(Board.WHITE)
            black_total = board.count_total(Board.BLACK)
            info = font.render(f"White: {white_total} | Black: {black_total}", True, TXT)
            screen.blit(info, (BOARD_LEFT, MARGIN - 28))

            # Etiquetas 0..23 centradas por columna
            for i in range(12):
                cx = BOARD_LEFT + i * col_w + col_w / 2
                # superior
                label_top = font_small.render(str(i), True, TXT)
                screen.blit(label_top, label_top.get_rect(center=(cx, MARGIN + TRI_H + 10)))
                # inferior
                idx_b = 12 + i
                label_bot = font_small.render(str(idx_b), True, TXT)
                screen.blit(label_bot, label_bot.get_rect(center=(cx, H - MARGIN - TRI_H - 12)))

            # Dibujar fichas (máx 5 visibles + "+n")
            def draw_stack(i_idx, top_band: bool):
                owner = board.owner_at(i_idx)
                cnt = board.count_at(i_idx)
                if cnt == 0:
                    return
                color_fill = CHECKER_WHITE if owner == Board.WHITE else CHECKER_BLACK
                cx = BOARD_LEFT + (i_idx % 12) * col_w + col_w / 2
                if top_band:
                    # apilar hacia abajo desde la banda superior
                    for k in range(min(cnt, 5)):
                        cy = MARGIN + R + k * (2 * R + GAP)
                        pygame.draw.circle(screen, color_fill, (int(cx), int(cy)), R)
                        pygame.draw.circle(screen, CHECKER_EDGE, (int(cx), int(cy)), R, width=1)
                    if cnt > 5:
                        extra = font_small.render(f"+{cnt-5}", True, TXT)
                        screen.blit(extra, extra.get_rect(center=(cx, MARGIN + TRI_H - 10)))
                else:
                    # apilar hacia arriba desde la banda inferior
                    for k in range(min(cnt, 5)):
                        cy = H - MARGIN - R - k * (2 * R + GAP)
                        pygame.draw.circle(screen, color_fill, (int(cx), int(cy)), R)
                        pygame.draw.circle(screen, CHECKER_EDGE, (int(cx), int(cy)), R, width=1)
                    if cnt > 5:
                        extra = font_small.render(f"+{cnt-5}", True, TXT)
                        screen.blit(extra, extra.get_rect(center=(cx, H - MARGIN - TRI_H + 10)))

            for i in range(12):
                draw_stack(i, top_band=True)
            for i in range(12, 24):
                draw_stack(i, top_band=False)

            # Tooltip hover (sobre tablero)
            if idx_hover is not None:
                try:
                    owner = board.owner_at(idx_hover)
                    cnt = board.count_at(idx_hover)
                    owner_lbl = owner_label(owner)
                    tip = font.render(f"Hover: {idx_hover} | {owner_lbl} x{cnt}", True, TXT)
                    tip_y = MARGIN + TRI_H + 28 if idx_hover <= 11 else (H - MARGIN - TRI_H - 32)
                    screen.blit(tip, (BOARD_LEFT, tip_y))
                except Exception:
                    pass

            # ----- Panel lateral derecho -----
            panel_x = W - MARGIN - PANEL_W
            panel_rect = pygame.Rect(panel_x, MARGIN, PANEL_W, H - 2 * MARGIN)
            pygame.draw.rect(screen, BG_PANEL, panel_rect, border_radius=8)
            pygame.draw.line(screen, SEP, (panel_x - 6, MARGIN), (panel_x - 6, H - MARGIN), 2)

            # FPS y título
            fps = clock.get_fps()
            fps_surf = font_small.render(f"{fps:.0f} FPS", True, TXT)
            screen.blit(fps_surf, (panel_x + PANEL_W - fps_surf.get_width() - 10, MARGIN + 6))
            title = font.render("Ayuda", True, TXT)
            screen.blit(title, (panel_x + 10, MARGIN + 4))

            # Ayuda (toggle con H)
            if show_help:
                help_lines = [
                    "- Click: ORIGEN → DESTINO",
                    "- Destinos legales resaltados en verde",
                    "- T: alternar color (White/Black)",
                    "- U: deshacer última jugada",
                    "- R: resetear tablero inicial",
                    "- H: mostrar/ocultar ayuda",
                    "- ESC: limpiar selección o salir",
                    "- Q: salir",
                ]
                y = MARGIN + 32
                for line in help_lines:
                    surf = font_small.render(line, True, TXT)
                    screen.blit(surf, (panel_x + 10, y))
                    y += 18

            # Lista de destinos legales en el panel
            if origin_idx is not None and legal_dests:
                y = H - MARGIN - 110
                header = font_small.render(f"Legales desde {origin_idx}:", True, TXT)
                screen.blit(header, (panel_x + 10, y)); y += 18
                for (d, pip) in legal_dests[:8]:
                    ln = font_small.render(f"• {origin_idx}->{d} (pip {pip})", True, TXT)
                    screen.blit(ln, (panel_x + 10, y)); y += 16

            # Estado / mensajes
            color_msg = f"Color: {owner_label(current_color)}"
            msg1 = font_small.render(color_msg, True, TXT)
            msg2 = font_small.render(message or "Listo", True, TXT)
            screen.blit(msg1, (panel_x + 10, H - MARGIN - 40))
            screen.blit(msg2, (panel_x + 10, H - MARGIN - 22))

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
