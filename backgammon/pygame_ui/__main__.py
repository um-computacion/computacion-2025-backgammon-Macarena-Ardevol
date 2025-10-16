def main():
    # Import lazy para no romper CI si no está pygame
    try:
        import pygame
    except ImportError:
        print("Pygame no está instalado. Instalá con: pip install pygame")
        return

    from backgammon.core.board import Board
    from backgammon.core.game import BackgammonGame
    import time, json
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

    # Colores para trails
    LAST_MOVE_CLR   = (20, 160, 120)   # última jugada mía (verde)
    RIVAL_TURN_CLR  = (160, 80, 200)   # jugadas del turno anterior (violeta)

    # --- Helpers geom ---
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

    # --- Helpers de juego/UI ---
    def owner_label(owner):
        return "White" if owner == Board.WHITE else ("Black" if owner == Board.BLACK else "Empty")

    def current_color_int(game):
        p = game.current_player()
        # Soporta Player con getters o atributo interno
        if hasattr(p, "get_color") and callable(p.get_color):
            color = p.get_color()
        else:
            color = getattr(p, "_Player__color__", getattr(p, "color", None))
        return Board.WHITE if color == "white" else Board.BLACK

    def snapshot_points(b: Board):
        return tuple(b.get_point(i) for i in range(24))

    def restore_points(b: Board, snap):
        for i, v in enumerate(snap):
            b.set_point(i, v)

    def snapshot_game(game, board):
        return (snapshot_points(board), game.pips(), game.last_roll())

    def restore_game(game, board, snap):
        pts, pips, last_roll = snap
        restore_points(board, pts)
        game._BackgammonGame__pips__ = tuple(pips)
        game._BackgammonGame__last_roll__ = last_roll

    def compute_legal_dests_with_pips(b: Board, origin: int, color: int, pips):
        res = []
        for pip in sorted(set(pips)):
            try:
                dest = b.dest_from(origin, pip, color)
                if b.can_move(origin, pip, color):
                    res.append((dest, pip))
            except Exception:
                continue
        return res

    # ---------- escena de juego (reusa tu loop existente) ----------
    def run_game_loop(screen, clock, font, font_small, font_badge):
        nonlocal LAST_MOVE_CLR, RIVAL_TURN_CLR, LEGAL, OUTLINE
        nonlocal BOARD_W, BOARD_LEFT, MARGIN, TRI_H, PANEL_W, BG, BG_PANEL, SEP, TOP_CLR, BOT_CLR, TXT
        nonlocal R, GAP, BADGE_R, BOARD_RIGHT, W, H

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
        legal_dests = []      # [(dest, pip)]
        last_move = None      # (origin, dest, color, pip)

        # Historial/turnos
        history = []                 # snapshots para U
        turn_start_snap = None
        turn_moves_text = []         # ["7->4 (pip 3)", ...]
        turn_moves_struct = []       # [(o,d,color,pip), ...]
        last_completed_turn_struct = []  # jugadas del turno anterior (del rival)
        show_rival_trail = True      # toggle con 'V'

        message = ""

        def start_turn_and_reset_ui(roll_tuple=None):
            nonlocal origin_idx, selected_idx, legal_dests, last_move
            nonlocal history, turn_start_snap, turn_moves_text, turn_moves_struct, message
            if roll_tuple:
                game.start_turn(roll_tuple)
            else:
                game.start_turn()
            origin_idx = selected_idx = None
            legal_dests = []
            last_move = None
            history.clear()
            turn_moves_text.clear()
            turn_moves_struct.clear()
            turn_start_snap = snapshot_game(game, board)
            message = f"Dados: {game.last_roll()} | Pips: {game.pips()}"

        # Guardar / Cargar
        SAVEDIR = Path("saves"); SAVEDIR.mkdir(exist_ok=True)
        SAVEFILE = SAVEDIR / "last.json"

        def save_game():
            data = game.to_dict()
            with open(SAVEFILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return str(SAVEFILE)

        def load_game():
            if not SAVEFILE.exists():
                return None
            with open(SAVEFILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return BackgammonGame.from_dict(data)

        running = True
        while running:
            mx, my = pygame.mouse.get_pos()
            idx_hover = hover_index(mx, my, col_w)
            cur_color = current_color_int(game)
            pips = game.pips()

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # volver al menú en lugar de cerrar la app por completo
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if origin_idx is not None or selected_idx is not None:
                            origin_idx = None
                            selected_idx = None
                            legal_dests = []
                            message = "Selección limpiada"
                        else:
                            # ESC desde juego → volver al menú
                            running = False

                    elif event.key == pygame.K_q:
                        running = False

                    elif event.key == pygame.K_v:
                        show_rival_trail = not show_rival_trail
                        message = "Resaltado del turno rival: " + ("ON" if show_rival_trail else "OFF")

                    elif event.key == pygame.K_SPACE:
                        start_turn_and_reset_ui()

                    elif event.key == pygame.K_f:
                        start_turn_and_reset_ui((3, 4))

                    elif event.key == pygame.K_e:
                        try:
                            # Guardamos las jugadas del turno actual como "turno anterior"
                            last_completed_turn_struct = list(turn_moves_struct)
                            game.end_turn()
                            # limpiar selección/estado de UI
                            origin_idx = selected_idx = None
                            legal_dests = []
                            history.clear()
                            turn_moves_text.clear()
                            turn_moves_struct.clear()
                            last_move = None
                            message = "Turno finalizado"
                        except ValueError as ex:
                            message = str(ex)

                    elif event.key == pygame.K_a:
                        if hasattr(game, "auto_end_turn"):
                            # Si rota, el turno anterior pasa a ser lo que se jugó (si algo se jugó)
                            rotated = game.auto_end_turn()
                            if rotated:
                                last_completed_turn_struct = list(turn_moves_struct)
                                origin_idx = selected_idx = None
                                legal_dests = []
                                history.clear()
                                turn_moves_text.clear()
                                turn_moves_struct.clear()
                                last_move = None
                                message = "Sin jugadas → turno rotado"
                            else:
                                message = "Aún hay jugadas; no se rota"

                    elif event.key == pygame.K_u:
                        if history:
                            snap = history.pop()
                            restore_game(game, board, snap)
                            if turn_moves_text:
                                turn_moves_text.pop()
                            if turn_moves_struct:
                                turn_moves_struct.pop()
                            origin_idx = selected_idx = None
                            legal_dests = []
                            message = "Deshacer: se restauró la última jugada"
                        else:
                            message = "No hay jugadas para deshacer"

                    elif event.key == pygame.K_c:
                        if turn_start_snap is not None:
                            restore_game(game, board, turn_start_snap)
                            history.clear()
                            turn_moves_text.clear()
                            turn_moves_struct.clear()
                            origin_idx = selected_idx = None
                            legal_dests = []
                            last_move = None
                            message = "Turno cancelado (estado tras tirada)"
                        else:
                            message = "No hay tirada activa para cancelar"

                    elif event.key == pygame.K_r:
                        game = BackgammonGame()
                        game.add_player("White", "white")
                        game.add_player("Black", "black")
                        game.setup_board()
                        board = game.board()
                        origin_idx = selected_idx = None
                        legal_dests = []
                        history.clear()
                        turn_moves_text.clear()
                        turn_moves_struct.clear()
                        last_move = None
                        last_completed_turn_struct = []
                        message = "Tablero reseteado (tirar con ESPACIO/F)"

                    elif event.key == pygame.K_s:
                        Path("screens").mkdir(parents=True, exist_ok=True)
                        fn = f"screens/snap-{time.strftime('%Y%m%d-%H%M%S')}.png"
                        pygame.image.save(screen, fn)
                        message = f"Captura guardada: {fn}"

                    # Guardar / Cargar
                    elif event.key == pygame.K_g:
                        fn = save_game()
                        message = f"Guardado: {fn}"

                    elif event.key == pygame.K_l:
                        new_g = load_game()
                        if new_g is None:
                            message = "No hay guardado para cargar"
                        else:
                            game = new_g
                            board = game.board()
                            origin_idx = selected_idx = None
                            legal_dests = []
                            history.clear()
                            turn_moves_text.clear()
                            turn_moves_struct.clear()
                            last_move = None
                            # Nota: no persistimos trails; se limpian al cargar
                            last_completed_turn_struct = []
                            message = "Partida cargada"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Click derecho: cancelar selección
                    if event.button == 3:
                        origin_idx = None
                        selected_idx = None
                        legal_dests = []
                        message = "Selección cancelada"
                        continue

                    # Click izquierdo: seleccionar / mover
                    if event.button == 1:
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
                            # Sólo destinos de la lista legal
                            legal_set = {d for (d, _) in legal_dests}
                            if not legal_dests or idx_hover not in legal_set:
                                message = f"No permitido: {origin_idx}->{idx_hover}"
                                continue

                            dest_idx = idx_hover
                            pip = next((p for (d, p) in legal_dests if d == dest_idx), None)
                            if pip is None:
                                message = "Error interno: pip no encontrado"
                                continue

                            # Snapshot para U
                            history.append(snapshot_game(game, board))
                            real_dest = game.apply_move(origin_idx, pip)
                            last_move = (origin_idx, real_dest, cur_color, pip)
                            turn_moves_text.append(f"{origin_idx}->{real_dest} (pip {pip})")
                            turn_moves_struct.append((origin_idx, real_dest, cur_color, pip))
                            message = f"Move: {origin_idx}->{real_dest} (pip {pip}) | Pips: {game.pips()}"

                            origin_idx = None
                            selected_idx = None
                            legal_dests = []

            # ---- Dibujo ----
            screen.fill(BG)
            col_w = BOARD_W / 12

            # Triángulos superiores
            for i in range(12):
                poly = tri_polygon_top(i, col_w)
                color = SELECT if i == origin_idx else (HILIGHT if i == idx_hover else TOP_CLR)
                border_w = 3 if i == origin_idx else (2 if i == idx_hover else 0)
                pygame.draw.polygon(screen, color, poly)
                if border_w:
                    pygame.draw.polygon(screen, OUTLINE, poly, width=border_w)

            # Triángulos inferiores
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
                t1 = font_small.render(str(i), True, TXT)
                screen.blit(t1, t1.get_rect(center=(cx, MARGIN + TRI_H + 10)))
                idxb = 12 + i
                t2 = font_small.render(str(idxb), True, TXT)
                screen.blit(t2, t2.get_rect(center=(cx, H - MARGIN - TRI_H - 12)))

            # Fichas
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

            # Último movimiento propio (línea)
            if last_move is not None:
                o, d, _, _ = last_move
                x0, y0 = tri_center(o, col_w)
                x1, y1 = tri_center(d, col_w)
                pygame.draw.line(screen, LAST_MOVE_CLR, (x0, y0), (x1, y1), width=4)

            # Jugadas del turno anterior (rival), si están habilitadas
            if show_rival_trail and last_completed_turn_struct:
                for (o, d, _color, _pip) in last_completed_turn_struct:
                    x0, y0 = tri_center(o, col_w)
                    x1, y1 = tri_center(d, col_w)
                    pygame.draw.line(screen, RIVAL_TURN_CLR, (x0, y0), (x1, y1), width=3)

            # Panel lateral (único)
            panel_x = W - MARGIN - PANEL_W
            pygame.draw.rect(screen, BG_PANEL, pygame.Rect(panel_x, MARGIN, PANEL_W, H - 2 * MARGIN), border_radius=8)
            pygame.draw.line(screen, SEP, (panel_x - 6, MARGIN), (panel_x - 6, H - MARGIN), 2)

            fps = clock.get_fps()
            screen.blit(font_small.render(f"{fps:.0f} FPS", True, TXT), (panel_x + PANEL_W - 40, MARGIN + 6))
            screen.blit(font.render("Ayuda", True, TXT), (panel_x + 10, MARGIN + 4))

            help_lines = [
                "- ESPACIO: tirar dados  | F: tirada fija (3,4)",
                "- Click: ORIGEN → DESTINO (usa pip)  |  Click der.: cancelar",
                "- U: deshacer  |  C: cancelar turno",
                "- E: fin de turno  |  A: auto-end si no hay jugadas",
                "- V: ver/ocultar turno rival",
                "- G: guardar  |  L: cargar",
                "- R: reset  |  S: captura  |  ESC/Q: menú",
            ]
            y = MARGIN + 32
            for line in help_lines:
                surf = font_small.render(line, True, TXT)
                screen.blit(surf, (panel_x + 10, y)); y += 18

            # Estado
            cur_lbl = owner_label(current_color_int(game))
            roll = game.last_roll()
            pips_txt = str(game.pips())
            state_y = H - MARGIN - 126
            screen.blit(font_small.render(f"Jugador: {cur_lbl}", True, TXT), (panel_x + 10, state_y)); state_y += 18
            screen.blit(font_small.render(f"Dados: {roll}",   True, TXT), (panel_x + 10, state_y));    state_y += 18
            screen.blit(font_small.render(f"Pips:  {pips_txt}",True, TXT), (panel_x + 10, state_y));   state_y += 18

            # Mensaje de estado (una sola línea)
            msg_txt = (message or "Listo")
            if len(msg_txt) > 42:
                msg_txt = msg_txt[:39] + "..."
            screen.blit(font_small.render(msg_txt, True, TXT), (panel_x + 10, state_y)); state_y += 12

            # Lista de movimientos del turno (máx. 6, más nuevo arriba)
            list_title_y = state_y + 16
            screen.blit(font_small.render("Turno (últimos 6):", True, TXT), (panel_x + 10, list_title_y))
            y_list = list_title_y + 16
            for mv in turn_moves_text[-6:][::-1]:
                if y_list > H - MARGIN - 6:
                    break
                screen.blit(font_small.render(f"• {mv}", True, TXT), (panel_x + 14, y_list))
                y_list += 16

            pygame.display.flip()
            clock.tick(60)

    # ---------- menú simple ----------
    pygame.init()
    try:
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Backgammon - Menú")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 32)
        font_small = pygame.font.SysFont(None, 20)
        font_badge = pygame.font.SysFont(None, 14)

        class Button:
            def __init__(self, text, rect):
                self.text = text
                self.rect = pygame.Rect(rect)
            def draw(self, surf, hover=False):
                c = (220, 226, 244) if hover else (206, 214, 236)
                pygame.draw.rect(surf, c, self.rect, border_radius=8)
                pygame.draw.rect(surf, (80, 90, 120), self.rect, width=2, border_radius=8)
                label = font.render(self.text, True, (30, 34, 46))
                surf.blit(label, label.get_rect(center=self.rect.center))
            def hit(self, pos):
                return self.rect.collidepoint(pos)

        title = "Backgammon — Menú"
        btn_play  = Button("Jugar partida nueva", (W//2 - 150, H//2 - 40, 300, 48))
        btn_load  = Button("Cargar última partida", (W//2 - 150, H//2 + 20, 300, 48))
        btn_exit  = Button("Salir", (W//2 - 150, H//2 + 80, 300, 48))
        info = "ESC para salir · ENTER para jugar"

        in_menu = True
        while in_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit(); return
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # jugar directo
                        run_game_loop(screen, clock, font, font_small, font_badge)
                        pygame.display.set_caption("Backgammon - Menú")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_play.hit(event.pos):
                        run_game_loop(screen, clock, font, font_small, font_badge)
                        pygame.display.set_caption("Backgammon - Menú")
                    elif btn_load.hit(event.pos):
                        # Intentar cargar y entrar al loop reutilizando teclas de carga (L) apenas inicia
                        # Aquí simplemente abrimos el loop; el propio juego permite L para cargar.
                        # (Mantenemos comportamiento existente sin duplicar lógica)
                        run_game_loop(screen, clock, font, font_small, font_badge)
                        pygame.display.set_caption("Backgammon - Menú")
                    elif btn_exit.hit(event.pos):
                        pygame.quit(); return

            # draw menú
            screen.fill((238, 240, 248))
            t = font.render(title, True, (28, 32, 40))
            screen.blit(t, t.get_rect(center=(W//2, H//2 - 100)))
            mx, my = pygame.mouse.get_pos()
            btn_play.draw(screen, btn_play.hit((mx, my)))
            btn_load.draw(screen, btn_load.hit((mx, my)))
            btn_exit.draw(screen, btn_exit.hit((mx, my)))
            screen.blit(font_small.render(info, True, (60, 64, 80)),
                        (W//2 - font_small.size(info)[0]//2, H - 60))

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
