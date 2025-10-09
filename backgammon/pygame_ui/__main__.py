def main():
    # Import lazy para no romper CI si no está pygame
    try:
        import pygame
    except ImportError:
        print("Pygame no está instalado. Instalá con: pip install pygame")
        return

    from backgammon.core.board import Board
    from backgammon.core.game import BackgammonGame
    import time
    from pathlib import Path

    # --- Config ---
    W, H = 800, 600
    MARGIN = 40
    TRI_H = 120
    PANEL_W = 260
    BG = (240, 240, 240)
    BG_PANEL = (230, 234, 244)
    SEP = (200, 200, 210)
    TOP_CLR = (50, 90, 160)
    BOT_CLR = (160, 90, 50)
    TXT = (20, 20, 20)
    HILIGHT = (240, 200, 60)
    SELECT = (120, 200, 120)
    LEGAL = (60, 190, 140)
    OUTLINE = (30, 30, 30)

    CHECKER_WHITE = (250, 250, 250)
    CHECKER_BLACK = (30, 30, 30)
    CHECKER_EDGE  = (10, 10, 10)
    R = 10
    GAP = 2
    BADGE_R = 10

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

    def tri_center(idx, col_w):
        cx = BOARD_LEFT + (idx % 12) * col_w + col_w / 2
        cy = (MARGIN + TRI_H / 2) if idx <= 11 else (H - MARGIN - TRI_H / 2)
        return (int(cx), int(cy))

    def hover_index(mx, my, col_w):
        if not (BOARD_LEFT <= mx <= BOARD_RIGHT):
            return None
        if MARGIN <= my <= MARGIN + TRI_H:
            i = int((mx - BOARD_LEFT) // col_w)
            return i if 0 <= i < 12 else None
        if (H - MARGIN - TRI_H) <= my <= (H - MARGIN):
            i = int((mx - BOARD_LEFT) // col_w)
            return 12 + i if 0 <= i < 12 else None
        return None

    # --- Helpers de juego/UI ----
    def owner_label(owner):
        return "White" if owner == Board.WHITE else ("Black" if owner == Board.BLACK else "Empty")

    def current_color_int(game):
        p = game.current_player()
        # Player tiene getter en tu proyecto
        return Board.WHITE if p.get_color() == "white" else Board.BLACK

    def snapshot_points(b: Board):
        return tuple(b.get_point(i) for i in range(24))

    def restore_points(b: Board, snap):
        for i, v in enumerate(snap):
            b.set_point(i, v)

    def snapshot_game(game, board):
        # guardamos tablero + pips + last_roll (mangling controlado)
        return (snapshot_points(board), game.pips(), game.last_roll())

    def restore_game(game, board, snap):
        pts, pips, last_roll = snap
        restore_points(board, pts)
        # Restaurar estado del turno (setter privado; aceptable en UI)
        game._BackgammonGame__pips__ = tuple(pips)
        game._BackgammonGame__last_roll__ = last_roll

    def compute_legal_dests_with_pips(b: Board, origin: int, color: int, pips):
        """Devuelve lista de (dest, pip) sólo para pips disponibles del turno."""
        res = []
        for pip in sorted(set(pips)):
            try:
                dest = b.dest_from(origin, pip, color)
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
        font_badge = pygame.font.SysFont(None, 14)

        # Juego real
        game = BackgammonGame()
        game.add_player("White", "white")
        game.add_player("Black", "black")
        game.setup_board()
        board = game.board()

        col_w = BOARD_W / 12

        # Estado UI
        origin_idx = None
        selected_idx = None
        legal_dests = []     # [(dest, pip)]
        last_move = None     # (origin, dest, color, pip)
        history = []         # snapshots para U (sólo dentro del turno)
        message = ""
        show_help = True

        running = True
        while running:
            mx, my = pygame.mouse.get_pos()
            idx_hover = hover_index(mx, my, col_w)
            cur_color = current_color_int(game)
            pips = game.pips()

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

                    elif event.key == pygame.K_SPACE:
                        game.start_turn()  # tirada random
                        origin_idx = selected_idx = None
                        legal_dests = []
                        history.clear()
                        last_move = None
                        message = f"Dados: {game.last_roll()} | Pips: {game.pips()}"

                    elif event.key == pygame.K_f:
                        game.start_turn((3, 4))  # tirada fija útil para pruebas
                        origin_idx = selected_idx = None
                        legal_dests = []
                        history.clear()
                        last_move = None
                        message = f"Dados: {game.last_roll()} | Pips: {game.pips()}"

                    elif event.key == pygame.K_e:
                        # Fin de turno si no quedan pips
                        from backgammon.core.game import BackgammonGame as _G  # solo para hints
                        try:
                            game.end_turn()
                            origin_idx = selected_idx = None
                            legal_dests = []
                            history.clear()
                            last_move = None
                            message = "Turno finalizado"
                        except ValueError as ex:
                            message = str(ex)

                    elif event.key == pygame.K_a:
                        # Auto end si no hay jugadas legales
                        if hasattr(game, "auto_end_turn"):
                            ok = game.auto_end_turn()
                            if ok:
                                origin_idx = selected_idx = None
                                legal_dests = []
                                history.clear()
                                last_move = None
                                message = "Sin jugadas → turno rotado"
                            else:
                                message = "Aún hay jugadas; no se rota"

                    elif event.key == pygame.K_u:
                        if history:
                            snap = history.pop()
                            restore_game(game, board, snap)
                            origin_idx = selected_idx = None
                            legal_dests = []
                            message = "Deshacer: se restauró la última jugada"
                        else:
                            message = "No hay jugadas para deshacer"

                    elif event.key == pygame.K_r:
                        # Reset total (nuevo juego)
                        game = BackgammonGame()
                        game.add_player("White", "white")
                        game.add_player("Black", "black")
                        game.setup_board()
                        board = game.board()
                        origin_idx = selected_idx = None
                        legal_dests = []
                        history.clear()
                        last_move = None
                        message = "Tablero reseteado"

                    elif event.key == pygame.K_s:
                        Path("screens").mkdir(parents=True, exist_ok=True)
                        fn = f"screens/snap-{time.strftime('%Y%m%d-%H%M%S')}.png"
                        pygame.image.save(screen, fn)
                        message = f"Captura guardada: {fn}"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if idx_hover is None:
                        selected_idx = None
                        continue

                    if origin_idx is None:
                        selected_idx = idx_hover
                        origin_idx = idx_hover
                        own = board.owner_at(origin_idx)
                        if own != cur_color:
                            message = f"Origen inválido: {origin_idx} no es de {owner_label(cur_color)}"
                            origin_idx = None
                            legal_dests = []
                        else:
                            cnt = board.count_at(origin_idx)
                            if cnt <= 0:
                                message = f"Origen vacío: {origin_idx}"
                                origin_idx = None
                                legal_dests = []
                            else:
                                if not pips:
                                    message = "Sin pips. Tirar dados con ESPACIO."
                                    legal_dests = []
                                else:
                                    legal_dests = compute_legal_dests_with_pips(board, origin_idx, cur_color, pips)
                                    if not legal_dests:
                                        message = "Sin destinos legales para los pips actuales"
                                    else:
                                        message = f"Origen: {origin_idx} | Pips: {pips}"

                    else:
                        # Sólo permitimos destinos que estén en legal_dests
                        legal_set = {d for (d, _) in legal_dests}
                        if not legal_dests or idx_hover not in legal_set:
                            message = f"No permitido: {origin_idx}->{idx_hover}"
                            continue

                        # Elegir pip correspondiente
                        dest_idx = idx_hover
                        pip = next((p for (d, p) in legal_dests if d == dest_idx), None)
                        if pip is None:
                            message = "Error interno: pip no encontrado"
                            continue

                        # Snapshot para deshacer dentro del turno
                        history.append(snapshot_game(game, board))
                        # Aplicar jugada real en Game (consume pip)
                        real_dest = game.apply_move(origin_idx, pip)
                        last_move = (origin_idx, real_dest, cur_color, pip)
                        message = f"Move: {origin_idx}->{real_dest} (pip {pip}) | Pips ahora: {game.pips()}"

                        origin_idx = None
                        selected_idx = None
                        legal_dests = []

            # ---- Dibujo ----
            screen.fill(BG)
            col_w = BOARD_W / 12

            # Triángulos
            for i in range(12):
                poly = tri_polygon_top(i, col_w)
                color = SELECT if i == origin_idx else (HILIGHT if i == idx_hover else TOP_CLR)
                border_w = 3 if i == origin_idx else (2 if i == idx_hover else 0)
                pygame.draw.polygon(screen, color, poly)
                if border_w:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=border_w)

            for i in range(12):
                idx = 12 + i
                poly = tri_polygon_bottom(i, col_w)
                color = SELECT if idx == origin_idx else (HILIGHT if idx == idx_hover else BOT_CLR)
                border_w = 3 if idx == origin_idx else (2 if idx == idx_hover else 0)
                pygame.draw.polygon(screen, color, poly)
                if border_w:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=border_w)

            # Destinos legales (borde + badge)
            if origin_idx is not None and legal_dests:
                for (d, pip) in legal_dests:
                    poly = tri_polygon_top(d, col_w) if d <= 11 else tri_polygon_bottom(d - 12, col_w)
                    pygame.draw.polygon(screen, LEGAL, poly, width=3)
                    bx, by = tri_center(d, col_w)
                    by = by - 16 if d <= 11 else by + 16
                    pygame.draw.circle(screen, LEGAL, (bx, by), BADGE_R)
                    txt = font_badge.render(str(pip), True, (255, 255, 255))
                    screen.blit(txt, txt.get_rect(center=(bx, by)))

            # Totales
            white_total = board.count_total(Board.WHITE)
            black_total = board.count_total(Board.BLACK)
            info = font.render(f"White: {white_total} | Black: {black_total}", True, TXT)
            screen.blit(info, (BOARD_LEFT, MARGIN - 28))

            # Etiquetas 0..23
            for i in range(12):
                cx = BOARD_LEFT + i * col_w + col_w / 2
                screen.blit(font_small.render(str(i), True, TXT),
                            font_small.render(str(i), True, TXT).get_rect(center=(cx, MARGIN + TRI_H + 10)))
                idxb = 12 + i
                screen.blit(font_small.render(str(idxb), True, TXT),
                            font_small.render(str(idxb), True, TXT).get_rect(center=(cx, H - MARGIN - TRI_H - 12)))

            # Fichas (máx 5 visibles + "+n")
            def draw_stack(i_idx, top_band: bool):
                owner = board.owner_at(i_idx)
                cnt = board.count_at(i_idx)
                if cnt == 0:
                    return
                color_fill = CHECKER_WHITE if owner == Board.WHITE else CHECKER_BLACK
                cx = BOARD_LEFT + (i_idx % 12) * col_w + col_w / 2
                if top_band:
                    for k in range(min(cnt, 5)):
                        cy = MARGIN + R + k * (2 * R + GAP)
                        pygame.draw.circle(screen, color_fill, (int(cx), int(cy)), R)
                        pygame.draw.circle(screen, CHECKER_EDGE, (int(cx), int(cy)), R, width=1)
                    if cnt > 5:
                        extra = font_small.render(f"+{cnt-5}", True, TXT)
                        screen.blit(extra, extra.get_rect(center=(cx, MARGIN + TRI_H - 10)))
                else:
                    for k in range(min(cnt, 5)):
                        cy = H - MARGIN - R - k * (2 * R + GAP)
                        pygame.draw.circle(screen, color_fill, (int(cx), int(cy)), R)
                        pygame.draw.circle(screen, CHECKER_EDGE, (int(cx), int(cy)), R, width=1)
                    if cnt > 5:
                        extra = font_small.render(f"+{cnt-5}", True, TXT)
                        screen.blit(extra, extra.get_rect(center=(cx, H - MARGIN - TRI_H + 10)))

            for i in range(12):
                draw_stack(i, True)
            for i in range(12, 24):
                draw_stack(i, False)

            # Último movimiento
            if last_move is not None:
                o, d, _, _ = last_move
                x0, y0 = tri_center(o, col_w)
                x1, y1 = tri_center(d, col_w)
                pygame.draw.line(screen, (20, 160, 120), (x0, y0), (x1, y1), width=4)

            # Panel lateral
            panel_x = W - MARGIN - PANEL_W
            pygame.draw.rect(screen, BG_PANEL, pygame.Rect(panel_x, MARGIN, PANEL_W, H - 2 * MARGIN), border_radius=8)
            pygame.draw.line(screen, SEP, (panel_x - 6, MARGIN), (panel_x - 6, H - MARGIN), 2)

            fps = clock.get_fps()
            screen.blit(font_small.render(f"{fps:.0f} FPS", True, TXT), (panel_x + PANEL_W - 40, MARGIN + 6))
            screen.blit(font.render("Ayuda", True, TXT), (panel_x + 10, MARGIN + 4))

            help_lines = [
                "- ESPACIO: tirar dados",
                "- F: tirada fija (3,4)",
                "- Click: ORIGEN → DESTINO (usa pip)",
                "- U: deshacer última jugada del turno",
                "- E: fin de turno | A: auto-end",
                "- R: resetear juego | S: captura",
                "- ESC/Q: salir",
            ]
            y = MARGIN + 32
            for line in help_lines:
                surf = font_small.render(line, True, TXT)
                screen.blit(surf, (panel_x + 10, y)); y += 18

            # Estado
            cur_lbl = owner_label(cur_color)
            roll = game.last_roll()
            pips_txt = str(game.pips())
            screen.blit(font_small.render(f"Jugador: {cur_lbl}", True, TXT), (panel_x + 10, H - MARGIN - 68))
            screen.blit(font_small.render(f"Dados: {roll}", True, TXT), (panel_x + 10, H - MARGIN - 50))
            screen.blit(font_small.render(f"Pips:  {pips_txt}", True, TXT), (panel_x + 10, H - MARGIN - 32))
            screen.blit(font_small.render(message or "Listo", True, TXT), (panel_x + 10, H - MARGIN - 14))

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
