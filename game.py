class OthelloGame:
    # Board constants
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

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
        # 检查坐标是否在棋盘范围内
        if not (0 <= row < 8 and 0 <= col < 8):
            return False

        # 检查位置是否为空
        if self.board[row][col] != self.EMPTY:
            return False

        opponent = self.WHITE if self.current_player == self.BLACK else self.BLACK

        # 检查每个方向是否有夹击的可能性
        for dr, dc in self.DIRECTIONS:
            r, c = row + dr, col + dc
            # 相邻的第一个棋子必须是对手的
            if not (0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent):
                continue

            # 继续在这个方向上移动
            r, c = r + dr, c + dc
            found_own = False
            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] == self.EMPTY:
                    # 空位置，这个方向上没有夹击
                    break
                if self.board[r][c] == self.current_player:
                    # 找到了自己的棋子，可以在这个方向上夹击
                    found_own = True
                    break
                # 继续寻找自己的棋子
                r, c = r + dr, c + dc

            if found_own:
                return True

        # 没有找到任何方向上的夹击
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

        # 放置棋子
        self.board[row][col] = self.current_player

        # 更新分数
        if self.current_player == self.BLACK:
            self.black_count += 1
        else:
            self.white_count += 1

        # 识别并翻转被夹击的棋子
        opponent = self.WHITE if self.current_player == self.BLACK else self.BLACK
        flipped_count = 0

        for dr, dc in self.DIRECTIONS:
            pieces_to_flip = []
            r, c = row + dr, col + dc

            # 找到可以翻转的对手棋子
            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                pieces_to_flip.append((r, c))
                r, c = r + dr, c + dc

            # 检查是否找到了以自己的棋子结尾的有效线
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == self.current_player:
                # 翻转中间的所有棋子
                for flip_r, flip_c in pieces_to_flip:
                    self.board[flip_r][flip_c] = self.current_player
                    flipped_count += 1

        # 更新翻转棋子的分数
        if self.current_player == self.BLACK:
            self.black_count += flipped_count
            self.white_count -= flipped_count
        else:
            self.white_count += flipped_count
            self.black_count -= flipped_count

        # 切换到下一个玩家
        next_player = self.BLACK if self.current_player == self.WHITE else self.WHITE
        self.current_player = next_player

        # 检查下一个玩家是否有合法移动
        if not self.get_valid_moves():
            # 如果下一个玩家没有合法移动，切换回原始玩家
            self.current_player = self.BLACK if self.current_player == self.WHITE else self.WHITE

            # 如果原始玩家也没有合法移动，游戏结束
            if not self.get_valid_moves():
                self.current_player = None  # 没有更多可能的移动

        return True

    def is_terminal(self):
        """Check if the game is over."""
        # 如果current_player为None(双方都无法移动)则游戏结束
        if self.current_player is None:
            return True

        # 检查是否有任何一方没有棋子
        if self.black_count == 0 or self.white_count == 0:
            return True

        # 检查是否还有空位
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == self.EMPTY:
                    # 还有空位，游戏未结束
                    return False

        # 没有空位，游戏结束
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
            return 0  # 平局

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

        # 打印当前分数
        print(f"Black (○): {self.black_count}, White (●): {self.white_count}")