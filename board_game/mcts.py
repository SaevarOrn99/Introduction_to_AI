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

        # Board position weights
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

        # Key position sets
        self.corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        self.x_squares = [(1, 1), (1, 6), (6, 1), (6, 6)]
        self.c_squares = [(0, 1), (1, 0), (0, 6), (6, 0), (1, 7), (7, 1), (6, 7), (7, 6)]

    def get_move(self, game):
        """Get the best move according to MCTS"""
        # Get valid moves
        valid_moves = game.get_valid_moves()
        if len(valid_moves) <= 1:
            return valid_moves[0] if valid_moves else None

        # If a corner is available, take it immediately
        for corner in self.corners:
            if corner in valid_moves:
                return corner

        # Avoid dangerous positions when having simulation advantage
        if self.has_simulation_advantage():
            safe_moves = [move for move in valid_moves if move not in self.x_squares]
            if safe_moves and len(safe_moves) < len(valid_moves):
                valid_moves = safe_moves

            # Avoid giving opponent access to corners
            no_corner_setup = []
            for move in valid_moves:
                sim_game = game.clone()
                sim_game.make_move(*move)
                opponent_moves = sim_game.get_valid_moves()
                if not any(corner in opponent_moves for corner in self.corners):
                    no_corner_setup.append(move)

            if no_corner_setup and len(no_corner_setup) < len(valid_moves):
                valid_moves = no_corner_setup

        # Create root node
        root = Node(game.clone())
        root.visits = 1

        # Run MCTS
        if self.time_limit:
            end_time = time.time() + self.time_limit
            simulations = 0
            while time.time() < end_time:
                self._simulate(root)
                simulations += 1
        else:
            for _ in range(self.simulation_count):
                self._simulate(root)

        # Print move statistics
        print("Move statistics:")
        for child in sorted(root.children, key=lambda c: c.visits, reverse=True):
            win_rate = child.wins / child.visits if child.visits > 0 else 0
            move_row, move_col = child.action
            human_readable = (move_row + 1, chr(97 + move_col))
            print(f"Move {human_readable}: {child.wins}/{child.visits} = {win_rate:.2f}")

        # Determine best move
        if self.has_simulation_advantage():
            best_move = self._select_strategic_move(valid_moves, root)
        else:
            best_child = max(root.children, key=lambda c: c.visits)
            best_move = best_child.action

        # Safety check - avoid moves that give opponent corner access
        if self.has_simulation_advantage():
            sim_game = game.clone()
            sim_game.make_move(*best_move)
            opponent_valid_moves = sim_game.get_valid_moves()

            if any(corner in opponent_valid_moves for corner in self.corners):
                safer_moves = []
                for move in valid_moves:
                    test_game = game.clone()
                    test_game.make_move(*move)
                    test_opponent_moves = test_game.get_valid_moves()
                    if not any(corner in test_opponent_moves for corner in self.corners):
                        safer_moves.append(move)

                if safer_moves:
                    best_move = self._get_best_positional_move(safer_moves)

        return best_move

    def has_simulation_advantage(self):
        """Check if we have simulation count advantage"""
        if self.opponent_sim_count is None:
            return True
        return self.simulation_count > self.opponent_sim_count

    def _get_best_positional_move(self, moves):
        """Select the best move based on position value"""
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
        """Select the best move based on strategic considerations"""
        # Create move scoring dictionary
        move_scores = {}
        for child in root.children:
            action = child.action
            if action in valid_moves:
                position_score = self.position_weights[action[0]][action[1]]
                visit_score = child.visits
                win_rate = child.wins / child.visits if child.visits > 0 else 0

                # Total score = position * 0.5 + visits * 0.3 + win_rate * 0.2
                total_score = position_score * 0.5 + visit_score * 0.3 + win_rate * 100 * 0.2
                move_scores[action] = total_score

        # Assign default scores for unexplored valid moves
        for move in valid_moves:
            if move not in move_scores:
                move_scores[move] = self.position_weights[move[0]][move[1]] * 0.5

        # Return highest scoring move
        return max(move_scores.items(), key=lambda x: x[1])[0]

    def _simulate(self, node):
        """Run one MCTS simulation"""
        path = [node]
        current = node

        # 1. Selection
        while current.untried_actions == [] and current.children:
            current = current.select_child(self.exploration_weight)
            path.append(current)

        # 2. Expansion
        if current.untried_actions:
            action = random.choice(current.untried_actions)
            state = current.state.clone()
            state.make_move(*action)
            current = current.add_child(state, action)
            path.append(current)

        # 3. Simulation
        state = current.state.clone()

        simulation_limit = 200  # Prevent infinite loops
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
                # Use heuristic rollout policy
                action = self._smart_rollout_policy(state, valid_moves)
                state.make_move(*action)

        # 4. Get simulation result
        winner = state.get_winner()

        # 5. Backpropagation
        for node in path:
            if node.player is None:
                continue

            if winner == 0:  # Draw
                result = 0.5
            elif winner == node.player:  # Win
                result = 1.0
            else:  # Loss
                result = 0.0

            node.update(result)

    def _smart_rollout_policy(self, state, valid_moves):
        """Use position-weighted random selection for rollout"""
        # Prioritize corner positions
        corner_moves = [move for move in valid_moves if move in self.corners]
        if corner_moves:
            return random.choice(corner_moves)

        # Avoid harmful positions
        if self.has_simulation_advantage():
            avoid_moves = [move for move in valid_moves if move in self.x_squares]
            safe_moves = [move for move in valid_moves if move not in avoid_moves]
            if safe_moves:
                valid_moves = safe_moves

        # Use position weights for selection
        weights = []
        for move in valid_moves:
            row, col = move
            # Convert negative weights to positive
            weight = self.position_weights[row][col] + 50
            weights.append(weight)

        # Weighted random choice
        return random.choices(valid_moves, weights=weights, k=1)[0]