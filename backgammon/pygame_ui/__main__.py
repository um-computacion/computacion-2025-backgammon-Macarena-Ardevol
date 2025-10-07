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

            # Triángulos superiores (puntos 0..11)
            for i in range(12):
                x0 = MARGIN + i * col_w
                x1 = x0 + col_w
                pygame.draw.polygon(
                    screen, TOP_CLR,
                    [(x0, MARGIN), (x1, MARGIN), ((x0 + x1) / 2, MARGIN + TRI_H)]
                )

            # Triángulos inferiores (puntos 12..23)
            for i in range(12):
                x0 = MARGIN + i * col_w
                x1 = x0 + col_w
                pygame.draw.polygon(
                    screen, BOT_CLR,
                    [(x0, H - MARGIN), (x1, H - MARGIN), ((x0 + x1) / 2, H - MARGIN - TRI_H)]
                )

            # Totales de fichas
            white_total = board.count_total(Board.WHITE)
            black_total = board.count_total(Board.BLACK)
            info = font.render(f"White: {white_total} | Black: {black_total}", True, TXT)
            screen.blit(info, (MARGIN, MARGIN - 28))

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
