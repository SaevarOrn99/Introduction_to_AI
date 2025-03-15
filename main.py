from game import OthelloGame
from player import HumanPlayer, MCTSPlayer, RandomPlayer
import time


def main():
    # Create a new game instance
    game = OthelloGame()

    # Create players
    print("=== OTHELLO GAME ===")
    print("Select player type for Black:")
    print("1. Human")
    print("2. AI (MCTS)")
    print("3. Random")

    while True:
        try:
            black_choice = int(input("Enter your choice (1-3): "))
            if 1 <= black_choice <= 3:
                break
            print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")

    print("\nSelect player type for White:")
    print("1. Human")
    print("2. AI (MCTS)")
    print("3. Random")

    while True:
        try:
            white_choice = int(input("Enter your choice (1-3): "))
            if 1 <= white_choice <= 3:
                break
            print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")

    # Create players based on choices
    if black_choice == 1:
        black_player = HumanPlayer(OthelloGame.BLACK)
        black_name = "Human"
    elif black_choice == 2:
        sim_count = int(input("Enter number of simulations for Black AI (e.g., 1000): "))
        black_player = MCTSPlayer(OthelloGame.BLACK, simulation_count=sim_count)
        black_name = f"MCTS AI ({sim_count} sims)"
    else:
        black_player = RandomPlayer(OthelloGame.BLACK)
        black_name = "Random AI"

    if white_choice == 1:
        white_player = HumanPlayer(OthelloGame.WHITE)
        white_name = "Human"
    elif white_choice == 2:
        sim_count = int(input("Enter number of simulations for White AI (e.g., 1000): "))
        white_player = MCTSPlayer(OthelloGame.WHITE, simulation_count=sim_count)
        white_name = f"MCTS AI ({sim_count} sims)"
    else:
        white_player = RandomPlayer(OthelloGame.WHITE)
        white_name = "Random AI"

    print(f"\nGame starting: Black ({black_name}) vs White ({white_name})")
    print("Board representation: ● = Black, ○ = White")

    # Main game loop
    while not game.is_terminal():
        game.display()

        current_player = black_player if game.current_player == OthelloGame.BLACK else white_player
        player_name = "Black" if game.current_player == OthelloGame.BLACK else "White"
        print(f"\n{player_name}'s turn ({black_name if player_name == 'Black' else white_name})")

        # Slight delay between AI moves to make the game more readable
        if (black_choice != 1 and game.current_player == OthelloGame.BLACK) or \
                (white_choice != 1 and game.current_player == OthelloGame.WHITE):
            time.sleep(0.5)

        move = current_player.get_move(game)
        if move:
            game.make_move(*move)
        else:
            # No valid moves, game handles switching player internally
            print(f"{player_name} has no valid moves. Passing to next player.")

    # Display the final state and the winner
    print("\n=== GAME OVER ===")
    game.display()

    winner = game.get_winner()
    if winner == OthelloGame.BLACK:
        print(f"Black ({black_name}) wins!")
    elif winner == OthelloGame.WHITE:
        print(f"White ({white_name}) wins!")
    else:
        print("It's a draw!")

    # Print final score
    black_count, white_count = game.get_score()
    print(f"Final score - Black: {black_count}, White: {white_count}")


if __name__ == "__main__":
    main()