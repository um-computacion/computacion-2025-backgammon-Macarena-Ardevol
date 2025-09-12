from backgammon.core.game import BackgammonGame

def main():
    game = BackgammonGame()
    game.add_player("White", "white")
    game.add_player("Black", "black")
    roll = game.start_turn()  # tirada automática
    print(f"Dados: {roll}")
    print(f"Pips disponibles: {game.pips()}")

if __name__ == "__main__":
    main()
