from game import OthelloGame
from player import HumanPlayer, MCTSPlayer, RandomPlayer
import time


def main():
    # 创建新游戏实例
    game = OthelloGame()

    # 创建玩家
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

    # 根据选择创建玩家
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

    # AI对战时检查，但不显示优势信息
    if black_choice == 2 and white_choice == 2:
        black_sims = black_player.simulation_count
        white_sims = white_player.simulation_count
        print(f"AI vs AI battle: Black ({black_sims} simulations) vs White ({white_sims} simulations)")

    print(f"\nGame starting: Black ({black_name}) vs White ({white_name})")
    print("Board representation: ○ = Black, ● = White")

    # 为先进策略添加游戏记录追踪
    move_history = []

    # 主游戏循环
    move_count = 0  # 跟踪移动次数
    turn_count = 1  # 跟踪回合数
    no_moves_count = 0  # 跟踪连续无移动次数

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

        # AI移动之间的轻微延迟
        if ((black_choice != 1 and game.current_player == OthelloGame.BLACK) or
                (white_choice != 1 and game.current_player == OthelloGame.WHITE)):
            time.sleep(0.5)

        move = current_player.get_move(game)
        if move:
            # 记录这个移动
            if isinstance(current_player, MCTSPlayer):
                move_history.append((player_name, move))

            success = game.make_move(*move)
            if success:
                move_count += 1
                if game.current_player == OthelloGame.BLACK:
                    turn_count += 1  # 每次轮到黑棋时增加回合数
                no_moves_count = 0
            else:
                print(f"ERROR: Failed to make move at {move}")
                no_moves_count += 1
        else:
            # 无有效移动
            print(f"{player_name} has no valid moves. Passing to next player.")
            no_moves_count += 1

            # 手动切换玩家
            if game.current_player is not None:
                game.current_player = OthelloGame.WHITE if game.current_player == OthelloGame.BLACK else OthelloGame.BLACK
                if game.current_player == OthelloGame.BLACK:
                    turn_count += 1  # 每次轮到黑棋时增加回合数

                # 如果另一个玩家也没有有效移动，游戏结束
                if not game.get_valid_moves():
                    game.current_player = None

        # 安全检查
        if no_moves_count >= 4:
            print("WARNING: Multiple consecutive no-move turns detected. Ending game.")
            break

        if move_count > 70:
            print("WARNING: Unusually high number of moves. Ending game.")
            break

    # 显示最终状态和胜者
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

    # 打印最终得分
    print(f"Final score - Black: {black_count}, White: {white_count}")


if __name__ == "__main__":
    main()