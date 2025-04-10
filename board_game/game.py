class OthelloGame:
    # Board constants
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]

    def __init__(self):
        # Initialize an 8x8 board with the starting position
        self.board = [[self.EMPTY for _ in range(8)] for _ in range(8)]
        # Standard Othello starting position
        self.board[3][3] = self.WHITE
        self.board[3][4] = self.BLACK
        self.board[4][3] = self.BLACK
        self.board[4][4] = self.WHITE
        # Black goes first
        self.current_player = self.BLACK
        # Keep track of the score
        self.black_count = 2
        self.white_count = 2

    def clone(self):
        """Create a deep copy of the game state."""
        new_game = OthelloGame()
        new_game.board = [row[:] for row in self.board]
        new_game.current_player = self.current_player
        new_game.black_count = self.black_count
        new_game.white_count = self.white_count
        return new_game

    def is_valid_move(self, row, col):
        """Check if a move is valid for the current player."""
        # Check if the coordinates are within the board range
        if not (0 <= row < 8 and 0 <= col < 8):
            return False

        # Check if the position is empty
        if self.board[row][col] != self.EMPTY:
            return False

        opponent = self.WHITE if self.current_player == self.BLACK else self.BLACK

        # Check each direction to see if there's a possible capture
        for dr, dc in self.DIRECTIONS:
            r, c = row + dr, col + dc
            # The first adjacent piece must be the opponent's
            if not (0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent):
                continue

            # Continue moving in this direction
            r, c = r + dr, c + dc
            found_own = False
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == self.EMPTY:
                    # If it's an empty space, no capture in this direction
                    break
                if self.board[r][c] == self.current_player:
                    # Found our own piece, capturing is possible in this direction
                    found_own = True
                    break
                # Continue searching for our own piece
                r, c = r + dr, c + dc

            if found_own:
                return True

        # Did not find a capture in any direction
        return False

    def get_valid_moves(self):
        """Return a list of all valid moves for the current player."""
        if self.current_player is None:
            return []

        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(row, col):
                    valid_moves.append((row, col))
        return valid_moves

    def make_move(self, row, col):
        """Execute a move and flip captured pieces."""
        if not self.is_valid_move(row, col):
            return False

        # Place the piece
        self.board[row][col] = self.current_player

        # Update the score
        if self.current_player == self.BLACK:
            self.black_count += 1
        else:
            self.white_count += 1

        # Identify and flip captured pieces
        opponent = self.WHITE if self.current_player == self.BLACK else self.BLACK
        flipped_count = 0

        for dr, dc in self.DIRECTIONS:
            pieces_to_flip = []
            r, c = row + dr, col + dc

            # Find the opponent's pieces that can be flipped
            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                pieces_to_flip.append((r, c))
                r, c = r + dr, c + dc

            # Check if we ended with our own piece, forming a valid line
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == self.current_player:
                # Flip all pieces in between
                for flip_r, flip_c in pieces_to_flip:
                    self.board[flip_r][flip_c] = self.current_player
                    flipped_count += 1

        # Update the score based on flipped pieces
        if self.current_player == self.BLACK:
            self.black_count += flipped_count
            self.white_count -= flipped_count
        else:
            self.white_count += flipped_count
            self.black_count -= flipped_count

        # Switch to the next player
        next_player = self.BLACK if self.current_player == self.WHITE else self.WHITE
        self.current_player = next_player

        # Check if the next player has any valid move
        if not self.get_valid_moves():
            # If the next player has no valid moves, switch back to the original player
            self.current_player = self.BLACK if self.current_player == self.WHITE else self.WHITE

            # If the original player also has no valid moves, the game ends
            if not self.get_valid_moves():
                self.current_player = None

        return True

    def is_terminal(self):
        """Check if the game is over."""
        # If current_player is None (both players cannot move), the game is over
        if self.current_player is None:
            return True

        # Check if either side has no pieces left
        if self.black_count == 0 or self.white_count == 0:
            return True

        # Check if there are any empty spaces left
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == self.EMPTY:
                    # There is still an empty space, so the game is not over
                    return False

        # No empty spaces, game over
        return True

    def get_winner(self):
        """Determine the winner."""
        if not self.is_terminal():
            return None

        if self.black_count > self.white_count:
            return self.BLACK
        elif self.white_count > self.black_count:
            return self.WHITE
        else:
            return 0  # It's a tie

    def get_score(self):
        """Return the current score."""
        return self.black_count, self.white_count

    def display(self):
        """Print the current board state."""
        print("  a b c d e f g h")
        for i in range(8):
            print(f"{i + 1} ", end="")
            for j in range(8):
                if self.board[i][j] == self.EMPTY:
                    print(". ", end="")
                elif self.board[i][j] == self.BLACK:
                    print("○ ", end="")
                else:
                    print("● ", end="")
            print(f" {i + 1}")
        print("  a b c d e f g h")

        # Print the current score
        print(f"Black (○): {self.black_count}, White (●): {self.white_count}")
