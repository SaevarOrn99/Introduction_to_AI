from game import OthelloGame
from player import HumanPlayer, MCTSPlayer, RandomPlayer
import time


def main():
    # Create new game instance
    game = OthelloGame()

    # Player selection
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
        exploration = float(input("Enter exploration weight for Black AI (recommended: 0.5): ") or "0.5")
        black_player = MCTSPlayer(OthelloGame.BLACK, exploration_weight=exploration, simulation_count=sim_count)
        black_name = f"MCTS AI ({sim_count} simulations)"
    else:
        black_player = RandomPlayer(OthelloGame.BLACK)
        black_name = "Random AI"

    if white_choice == 1:
        white_player = HumanPlayer(OthelloGame.WHITE)
        white_name = "Human"
    elif white_choice == 2:
        sim_count = int(input("Enter number of simulations for White AI (e.g., 1000): "))
        exploration = float(input("Enter exploration weight for White AI (recommended: 0.5): ") or "0.5")
        white_player = MCTSPlayer(OthelloGame.WHITE, exploration_weight=exploration, simulation_count=sim_count)
        white_name = f"MCTS AI ({sim_count} simulations)"
    else:
        white_player = RandomPlayer(OthelloGame.WHITE)
        white_name = "Random AI"

    # AI battle info
    if black_choice == 2 and white_choice == 2:
        black_sims = black_player.simulation_count
        white_sims = white_player.simulation_count
        print(f"AI vs AI battle: Black ({black_sims} simulations) vs White ({white_sims} simulations)")

    print(f"\nGame starting: Black ({black_name}) vs White ({white_name})")
    print("Board representation: ○ = Black, ● = White")

    # Game loop
    move_count = 0
    turn_count = 1
    no_moves_count = 0

    while not game.is_terminal():
        game.display()

        if game.current_player == OthelloGame.BLACK:
            current_player = black_player
            player_name = "Black"
            player_display_name = black_name
        else:
            current_player = white_player
            player_name = "White"
            player_display_name = white_name

        print(f"\nTurn {turn_count}: {player_name}'s turn ({player_display_name})")

        # Add slight delay between AI moves
        if ((black_choice != 1 and game.current_player == OthelloGame.BLACK) or
                (white_choice != 1 and game.current_player == OthelloGame.WHITE)):
            time.sleep(0.5)

        move = current_player.get_move(game)
        if move:
            success = game.make_move(*move)
            if success:
                move_count += 1
                if game.current_player == OthelloGame.BLACK:
                    turn_count += 1  # Increment turn counter when it's Black's turn again
                no_moves_count = 0
            else:
                print(f"ERROR: Failed to make move at {move}")
                no_moves_count += 1
        else:
            # No valid moves
            print(f"{player_name} has no valid moves. Passing to next player.")
            no_moves_count += 1

            # Switch player manually
            if game.current_player is not None:
                game.current_player = OthelloGame.WHITE if game.current_player == OthelloGame.BLACK else OthelloGame.BLACK
                if game.current_player == OthelloGame.BLACK:
                    turn_count += 1

                # End game if other player also has no moves
                if not game.get_valid_moves():
                    game.current_player = None

        # Safety checks
        if no_moves_count >= 4:
            print("WARNING: Multiple consecutive no-move turns detected. Ending game.")
            break

        if move_count > 70:
            print("WARNING: Unusually high number of moves. Ending game.")
            break

    # Show final state and winner
    print("\n=== GAME OVER ===")
    print(f"Total turns: {turn_count}")
    game.display()

    winner = game.get_winner()
    black_count, white_count = game.get_score()

    if winner == OthelloGame.BLACK:
        print(f"Black ({black_name}) wins!")
    elif winner == OthelloGame.WHITE:
        print(f"White ({white_name}) wins!")
    else:
        print("It's a draw!")

    print(f"Final score - Black: {black_count}, White: {white_count}")


if __name__ == "__main__":
    main()