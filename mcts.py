import math
import random
import time


class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_actions = state.get_valid_moves().copy() if state.current_player is not None else []
        self.player = state.current_player

    def ucb1(self, exploration_weight):
        if self.visits == 0:
            return float('inf')
        exploitation = self.wins / self.visits
        exploration = exploration_weight * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def select_child(self, exploration_weight):
        return max(self.children, key=lambda child: child.ucb1(exploration_weight))

    def add_child(self, state, action):
        child = Node(state, self, action)
        if action in self.untried_actions:
            self.untried_actions.remove(action)
        self.children.append(child)
        return child

    def update(self, result):
        self.visits += 1
        self.wins += result


class MCTS:
    def __init__(self, exploration_weight=0.5, simulation_count=1000, time_limit=None, opponent_sim_count=None):
        self.exploration_weight = exploration_weight
        self.simulation_count = simulation_count
        self.time_limit = time_limit
        self.opponent_sim_count = opponent_sim_count

        # 棋盘位置权重
        self.position_weights = [
            [120, -20, 20, 5, 5, 20, -20, 120],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [5, -5, 3, 3, 3, 3, -5, 5],
            [20, -5, 15, 3, 3, 15, -5, 20],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [120, -20, 20, 5, 5, 20, -20, 120]
        ]

        # 关键位置集合
        self.corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        self.x_squares = [(1, 1), (1, 6), (6, 1), (6, 6)]
        self.c_squares = [(0, 1), (1, 0), (0, 6), (6, 0), (1, 7), (7, 1), (6, 7), (7, 6)]

    def get_move(self, game):
        """获取MCTS认为最佳的移动"""
        # 获取有效移动
        valid_moves = game.get_valid_moves()
        if len(valid_moves) <= 1:
            return valid_moves[0] if valid_moves else None

        # 关键策略：如果能直接占领角落，立即执行
        for corner in self.corners:
            if corner in valid_moves:
                return corner

        # 关键策略：避免X位置（角落旁的对角线位置）
        if self.has_simulation_advantage():
            safe_moves = [move for move in valid_moves if move not in self.x_squares]
            if safe_moves and len(safe_moves) < len(valid_moves):
                valid_moves = safe_moves

            # 避免给对手提供角落的机会
            no_corner_setup = []
            for move in valid_moves:
                # 模拟这个移动
                sim_game = game.clone()
                sim_game.make_move(*move)
                # 检查下一步对手是否能占领角落
                opponent_moves = sim_game.get_valid_moves()
                if not any(corner in opponent_moves for corner in self.corners):
                    no_corner_setup.append(move)

            if no_corner_setup and len(no_corner_setup) < len(valid_moves):
                valid_moves = no_corner_setup

        # 创建根节点
        root = Node(game.clone())
        root.visits = 1

        # 运行MCTS
        if self.time_limit:
            end_time = time.time() + self.time_limit
            simulations = 0
            while time.time() < end_time:
                self._simulate(root)
                simulations += 1
            print(f"Performed {simulations} simulations")
        else:
            for _ in range(self.simulation_count):
                self._simulate(root)

        # 输出移动统计
        print("Move statistics:")
        for child in sorted(root.children, key=lambda c: c.visits, reverse=True):
            win_rate = child.wins / child.visits if child.visits > 0 else 0
            position_score = self.position_weights[child.action[0]][child.action[1]]
            move_row, move_col = child.action
            human_readable = (move_row + 1, chr(97 + move_col))
            print(
                f"Move {human_readable}: {child.wins}/{child.visits} = {win_rate:.2f}, Position Score: {position_score}")

        # 决定最佳移动
        if self.has_simulation_advantage():
            # 有模拟优势时采用更稳健的战略
            best_move = self._select_strategic_move(valid_moves, root)
        else:
            # 模拟次数不占优时，尽可能挑选最好的移动
            best_child = max(root.children, key=lambda c: c.visits)
            best_move = best_child.action

        # 最终安全检查 - 如果选择的移动会导致对手下一步能占角，而有其他选择，则重新选择
        if self.has_simulation_advantage():
            sim_game = game.clone()
            sim_game.make_move(*best_move)
            opponent_valid_moves = sim_game.get_valid_moves()

            if any(corner in opponent_valid_moves for corner in self.corners):
                # 找出不会让对手占角的移动
                safer_moves = []
                for move in valid_moves:
                    test_game = game.clone()
                    test_game.make_move(*move)
                    test_opponent_moves = test_game.get_valid_moves()
                    if not any(corner in test_opponent_moves for corner in self.corners):
                        safer_moves.append(move)

                if safer_moves:
                    best_move = self._get_best_positional_move(safer_moves)

        # 显示最终选择
        row, col = best_move
        print(f"Selected best move: ({row + 1}, {chr(97 + col)})")
        return best_move

    def has_simulation_advantage(self):
        """判断是否有模拟次数优势"""
        if self.opponent_sim_count is None:
            return True
        return self.simulation_count > self.opponent_sim_count

    def _get_best_positional_move(self, moves):
        """根据位置价值选择最佳移动"""
        best_score = float('-inf')
        best_move = None

        for move in moves:
            row, col = move
            score = self.position_weights[row][col]

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _select_strategic_move(self, valid_moves, root):
        """根据战略考量选择最佳移动"""
        # 创建移动评分字典
        move_scores = {}
        for child in root.children:
            action = child.action
            if action in valid_moves:
                # 基础分 = 访问次数
                position_score = self.position_weights[action[0]][action[1]]
                visit_score = child.visits
                win_rate = child.wins / child.visits if child.visits > 0 else 0

                # 总分 = 位置分 * 0.5 + 访问分 * 0.3 + 胜率 * 0.2
                total_score = position_score * 0.5 + visit_score * 0.3 + win_rate * 100 * 0.2
                move_scores[action] = total_score

        # 如果有些有效移动没有在树中探索，为其分配默认分数
        for move in valid_moves:
            if move not in move_scores:
                move_scores[move] = self.position_weights[move[0]][move[1]] * 0.5

        # 返回得分最高的移动
        return max(move_scores.items(), key=lambda x: x[1])[0]

    def _simulate(self, node):
        """运行一次MCTS模拟"""
        path = [node]
        current = node

        # 1. 选择
        while current.untried_actions == [] and current.children:
            current = current.select_child(self.exploration_weight)
            path.append(current)

        # 2. 扩展
        if current.untried_actions:
            action = random.choice(current.untried_actions)
            state = current.state.clone()
            state.make_move(*action)
            current = current.add_child(state, action)
            path.append(current)

        # 3. 模拟
        state = current.state.clone()

        simulation_limit = 200  # 防止无限循环
        simulation_count = 0

        while not state.is_terminal() and simulation_count < simulation_limit:
            simulation_count += 1
            valid_moves = state.get_valid_moves()
            if not valid_moves:
                if state.current_player is not None:
                    state.current_player = 3 - state.current_player
                    if not state.get_valid_moves():
                        state.current_player = None
                else:
                    break
            else:
                # 使用启发式随机策略
                action = self._smart_rollout_policy(state, valid_moves)
                state.make_move(*action)

        # 4. 获取模拟结果
        winner = state.get_winner()

        # 5. 反向传播
        for node in path:
            if node.player is None:
                continue

            if winner == 0:  # 平局
                result = 0.5
            elif winner == node.player:  # 获胜
                result = 1.0
            else:  # 失败
                result = 0.0

            node.update(result)

    def _smart_rollout_policy(self, state, valid_moves):
        """使用基于位置价值的启发式策略随机走子"""
        # 关键角落位置优先
        corner_moves = [move for move in valid_moves if move in self.corners]
        if corner_moves:
            return random.choice(corner_moves)

        # 避免有害的位置
        if self.has_simulation_advantage():
            avoid_moves = [move for move in valid_moves if move in self.x_squares]
            safe_moves = [move for move in valid_moves if move not in avoid_moves]
            if safe_moves:
                valid_moves = safe_moves

        # 使用位置权重选择
        weights = []
        for move in valid_moves:
            row, col = move
            # 将负权重转为正数，保证所有权重为正
            weight = self.position_weights[row][col] + 50
            weights.append(weight)

        # 按权重随机选择
        return random.choices(valid_moves, weights=weights, k=1)[0]