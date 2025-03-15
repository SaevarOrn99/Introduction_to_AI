import random
from mcts import MCTS


class Player:
    def __init__(self, color):
        self.color = color

    def get_move(self, game):
        """Get the player's move."""
        raise NotImplementedError("Subclasses must implement this method")


class HumanPlayer(Player):
    def get_move(self, game):
        """Get the human player's move from input."""
        valid_moves = game.get_valid_moves()

        if not valid_moves:
            print("No valid moves available.")
            return None

        # Show valid moves to the player
        print("Valid moves:", valid_moves)

        while True:
            try:
                x = int(input("Enter row (0-7): "))
                y = int(input("Enter column (0-7): "))

                if 0 <= x < 8 and 0 <= y < 8 and (x, y) in valid_moves:
                    return (x, y)
                else:
                    print("Invalid move. Please try again.")
            except ValueError:
                print("Please enter valid numbers.")


class MCTSPlayer(Player):
    def __init__(self, color, exploration_weight=1.0, simulation_count=1000, time_limit=None):
        super().__init__(color)
        self.mcts = MCTS(exploration_weight, simulation_count, time_limit)
        self.name = "MCTS AI"
        self.exploration_weight = exploration_weight
        self.simulation_count = simulation_count
        self.time_limit = time_limit

    def get_move(self, game):
        """Get the MCTS player's move."""
        valid_moves = game.get_valid_moves()

        if not valid_moves:
            print("No valid moves available for AI.")
            return None

        print(f"AI is thinking... (running {self.simulation_count} simulations)")
        move = self.mcts.get_move(game)
        print(f"AI places at {move}")
        return move


class RandomPlayer(Player):
    def __init__(self, color):
        super().__init__(color)
        self.name = "Random AI"

    def get_move(self, game):
        """Get a random valid move."""
        valid_moves = game.get_valid_moves()

        if not valid_moves:
            print("No valid moves available for Random AI.")
            return None

        move = random.choice(valid_moves)
        print(f"Random AI places at {move}")
        return move