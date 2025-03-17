import numpy as np


class OthelloGame:
    # Game constants
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    DIRECTIONS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    def __init__(self):
        # Initialize the 8x8 board
        self.board = np.zeros((8, 8), dtype=int)
        # Set up the initial configuration
        self.board[3][3] = self.WHITE
        self.board[3][4] = self.BLACK
        self.board[4][3] = self.BLACK
        self.board[4][4] = self.WHITE

        # Black moves first
        self.current_player = self.BLACK

        # Keep track of the game history
        self.history = []

    def get_valid_moves(self):
        """Returns all valid moves for the current player."""
        valid_moves = []
        for i in range(8):
            for j in range(8):
                if self.is_valid_move(i, j):
                    valid_moves.append((i, j))
        return valid_moves

    def is_valid_move(self, x, y):
        """Check if a move at position (x, y) is valid for the current player."""
        # Check if the position is empty
        if self.board[x][y] != self.EMPTY:
            return False

        opponent = self.WHITE if self.current_player == self.BLACK else self.BLACK

        # Check in all directions
        for dx, dy in self.DIRECTIONS:
            nx, ny = x + dx, y + dy

            # Make sure we're not out of bounds and we're looking at an opponent's piece
            if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent:
                # Continue in this direction
                nx, ny = nx + dx, ny + dy
                while 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent:
                    nx, ny = nx + dx, ny + dy

                # If we found one of our own pieces, this is a valid move
                if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == self.current_player:
                    return True

        return False

    def make_move(self, x, y):
        """Make a move at position (x, y) for the current player."""
        if not self.is_valid_move(x, y):
            return False

        # Save current state for history
        self.history.append((np.copy(self.board), self.current_player))

        # Place the piece
        self.board[x][y] = self.current_player
        opponent = self.WHITE if self.current_player == self.BLACK else self.BLACK

        # Flip pieces in all directions
        for dx, dy in self.DIRECTIONS:
            # Pieces to flip in this direction
            to_flip = []
            nx, ny = x + dx, y + dy

            # Collect pieces to flip
            while 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent:
                to_flip.append((nx, ny))
                nx, ny = nx + dx, ny + dy

            # If we found one of our own pieces, flip all the pieces in between
            if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == self.current_player:
                for fx, fy in to_flip:
                    self.board[fx][fy] = self.current_player

        # Switch to the other player
        self.current_player = opponent

        # If the opponent has no valid moves, switch back to the current player
        if not self.get_valid_moves():
            self.current_player = self.BLACK if self.current_player == self.WHITE else self.WHITE

            # If the current player also has no valid moves, the game is over
            if not self.get_valid_moves():
                self.current_player = None  # Game over

        return True

    def is_terminal(self):
        """Check if the game is over."""
        return self.current_player is None

    def get_winner(self):
        """Return the winner of the game or None if it's a draw."""
        if not self.is_terminal():
            return None

        black_count = np.count_nonzero(self.board == self.BLACK)
        white_count = np.count_nonzero(self.board == self.WHITE)

        if black_count > white_count:
            return self.BLACK
        elif white_count > black_count:
            return self.WHITE
        else:
            return self.EMPTY  # Draw

    def get_score(self):
        """Return the current score (black_count, white_count)."""
        black_count = np.count_nonzero(self.board == self.BLACK)
        white_count = np.count_nonzero(self.board == self.WHITE)
        return black_count, white_count

    def display(self):
        """Display the current state of the board with a full grid and proper alignment."""
        # Print column headers
        print("    ", end="")
        for j in range(8):
            print(f" {j} ", end=" ")
        print()

        # Print the top border
        print("   +" + "+".join(["---" for _ in range(8)]) + "+")

        # Print each row with grid lines
        for i in range(8):
            print(f" {i} |", end="")
            for j in range(8):
                if self.board[i][j] == self.EMPTY:
                    cell = " "
                elif self.board[i][j] == self.BLACK:
                    cell = "●"
                else:
                    cell = "○"
                print(f" {cell} |", end="")
            print()

            # Print row separator
            print("   +" + "+".join(["---" for _ in range(8)]) + "+")

        # Display the current score
        black_count, white_count = self.get_score()
        print(f"Black: {black_count}, White: {white_count}")

    def clone(self):
        """Create a deep copy of the game state."""
        new_game = OthelloGame.__new__(OthelloGame)
        new_game.board = np.copy(self.board)
        new_game.current_player = self.current_player
        new_game.history = [(np.copy(b), p) for b, p in self.history]
        return new_game