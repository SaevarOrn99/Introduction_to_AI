import random
from mcts import MCTS


class Player:
    def __init__(self, color):
        self.color = color

    def get_move(self, game):
        """Get the player's move."""
        raise NotImplementedError("Subclasses must implement this method")


class HumanPlayer(Player):
    COLUMNS = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

    def get_move(self, game):
        """Get the human player's move from input."""
        valid_moves = game.get_valid_moves()

        if not valid_moves:
            print("No valid moves available.")
            return None

        # 用人类可读格式显示有效移动
        human_readable_moves = [(row + 1, chr(97 + col)) for row, col in valid_moves]
        print("Valid moves:", human_readable_moves)

        while True:
            try:
                row_input = int(input("Enter row (1-8): "))
                col_input = input("Enter column (a-h): ").lower()

                if col_input in self.COLUMNS:
                    row = row_input - 1  # 转换为0索引
                    col = self.COLUMNS[col_input]

                    if 0 <= row < 8 and 0 <= col < 8 and (row, col) in valid_moves:
                        return (row, col)
                    else:
                        print("Invalid move. Please try again.")
                else:
                    print("Valid columns are: a, b, c, d, e, f, g, and h.")
            except ValueError:
                print("Please enter a valid row number (1-8).")


class MCTSPlayer(Player):
    # 存储所有MCTS玩家的模拟次数，让他们互相知道对方的能力
    AI_SIMULATION_COUNTS = {}

    def __init__(self, color, exploration_weight=0.5, simulation_count=1000, time_limit=None):
        super().__init__(color)
        self.name = "MCTS AI"
        self.exploration_weight = exploration_weight
        self.simulation_count = simulation_count
        self.time_limit = time_limit

        # 记录这个AI的模拟次数
        MCTSPlayer.AI_SIMULATION_COUNTS[color] = simulation_count

        # 找出对手的模拟次数
        opponent_color = 2 if color == 1 else 1  # 1=BLACK, 2=WHITE
        opponent_sim_count = MCTSPlayer.AI_SIMULATION_COUNTS.get(opponent_color)

        # 创建MCTS实例，告诉它对手的模拟次数
        self.mcts = MCTS(exploration_weight, simulation_count, time_limit, opponent_sim_count)

    def get_move(self, game):
        """Get the MCTS player's move."""
        valid_moves = game.get_valid_moves()

        if not valid_moves:
            print("No valid moves available for AI.")
            return None

        # 确保MCTS知道对手的最新模拟次数
        opponent_color = 2 if self.color == 1 else 1
        self.mcts.opponent_sim_count = MCTSPlayer.AI_SIMULATION_COUNTS.get(opponent_color)

        # 只显示简单信息
        print(f"AI is thinking... (running {self.simulation_count} simulations)")

        move = self.mcts.get_move(game)

        # 转换为人类可读格式
        if move:
            row, col = move
            human_readable_move = (row + 1, chr(97 + col))
            print(f"AI places at {human_readable_move}")

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

        # 转换为人类可读格式
        row, col = move
        human_readable_move = (row + 1, chr(97 + col))
        print(f"Random AI places at {human_readable_move}")

        return move