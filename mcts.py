import math
import random
import time


class Node:
    def __init__(self, state, parent=None, action=None):
        self.state = state  # Game state
        self.parent = parent  # Parent node
        self.action = action  # Action that led to this state
        self.children = []  # Child nodes
        self.visits = 0  # Number of visits
        self.wins = 0  # Number of wins from this node's perspective
        self.untried_actions = state.get_valid_moves()  # Moves not yet explored
        self.player = state.current_player  # Player who would make the move from this state

    def ucb1(self, exploration_weight):
        """Calculate UCB1 value for this node."""
        if self.visits == 0:
            return float('inf')

        # UCB1 formula: (wins/visits) + exploration_weight * sqrt(ln(parent_visits) / visits)
        exploitation = self.wins / self.visits
        exploration = exploration_weight * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def select_child(self, exploration_weight):
        """Select the child with the highest UCB1 value."""
        return max(self.children, key=lambda child: child.ucb1(exploration_weight))

    def add_child(self, state, action):
        """Add a child node with the given state and action."""
        child = Node(state, self, action)
        self.untried_actions.remove(action)
        self.children.append(child)
        return child

    def update(self, result):
        """Update node statistics."""
        self.visits += 1
        self.wins += result


class MCTS:
    def __init__(self, exploration_weight=1.0, simulation_count=1000, time_limit=None):
        self.exploration_weight = exploration_weight
        self.simulation_count = simulation_count
        self.time_limit = time_limit

    def get_move(self, game):
        """Get the best move according to MCTS."""
        # If there's only one valid move, return it immediately
        valid_moves = game.get_valid_moves()
        if len(valid_moves) <= 1:
            return valid_moves[0] if valid_moves else None

        # Create the root node
        root = Node(game.clone())

        # Run MCTS
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

        # Find the best move (usually the one with most visits)
        if not root.children:
            return None

        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.action

    def _simulate(self, node):
        """Run one MCTS simulation."""
        # 1. Selection: Find the most promising node to expand
        current = node
        while current.untried_actions == [] and current.children != []:
            current = current.select_child(self.exploration_weight)

        # 2. Expansion: If the selected node is not fully expanded, expand it
        if current.untried_actions:
            action = random.choice(current.untried_actions)
            state = current.state.clone()
            state.make_move(*action)
            current = current.add_child(state, action)

        # 3. Simulation: Play the game randomly until a terminal state
        state = current.state.clone()
        current_player = current.player  # Remember who made the move that got us here

        while not state.is_terminal():
            valid_moves = state.get_valid_moves()
            if not valid_moves:
                # No valid moves, switch player
                original_player = state.current_player
                state.current_player = 3 - original_player  # Switch between 1 and 2

                if not state.get_valid_moves():
                    # No valid moves for either player, game over
                    state.current_player = None
                    break
            else:
                action = random.choice(valid_moves)
                state.make_move(*action)

        # 4. Backpropagation: Update the statistics of all nodes in the path
        winner = state.get_winner()

        # Traverse back up the tree
        while current:
            # Determine the result from this node's perspective
            result = 0
            if winner == current.player:
                result = 1  # Win
            elif winner != 0 and winner != current.player:
                result = -1  # Loss
            # Draw (result = 0) already set

            current.update(result)
            current = current.parent