# Introduction to AI - Othello Game

This is a repository for the DTU course Introduction to A.I, featuring an implementation of the Othello (Reversi) game with AI capabilities using Monte Carlo Tree Search (MCTS).

## Project Overview

This project implements the classic Othello game with three types of players:

- Human Player
- AI Player using Monte Carlo Tree Search (MCTS)
- Random Player

The MCTS implementation includes configurable parameters for:

- Number of simulations
- Exploration weight (for balancing exploration vs exploitation)

## Prerequisites

- Python 3.x installed on your system
- No additional dependencies required (uses only Python standard library)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/Introduction_to_AI.git
cd Introduction_to_AI
```

2. No additional installation steps are required as the project uses only Python's standard library.

## How to Run

1. Navigate to the project directory:

```bash
cd Introduction_to_AI
```

2. Run the main game:

```bash
python main.py
```

3. Follow the on-screen prompts to:
   - Select player type for Black (Human, AI, or Random)
   - Select player type for White (Human, AI, or Random)
   - If choosing AI players:
     - Specify the number of simulations (e.g., 1000)
     - Set the exploration weight (recommended: 0.5)
   - Play the game!

## Game Controls

- For Human players:
  - Enter moves in the format "row column" (e.g., "3 4")
  - Rows and columns are numbered from 0 to 7
  - The top-left corner is (0,0)

## Project Structure

- `main.py`: Main game loop and user interface
- `game.py`: Othello game logic and board representation
- `player.py`: Player implementations (Human, MCTS, Random)
- `mcts.py`: Monte Carlo Tree Search implementation with configurable parameters

## Game Features

- Turn counter and move tracking
- Safety checks to prevent infinite loops
- Configurable AI parameters
- Detailed game statistics
- Support for AI vs AI battles
- Automatic game termination when no valid moves are available

## Game Rules

1. The game is played on an 8x8 board
2. Players take turns placing their pieces (Black and White)
3. A move is valid if it:
   - Is placed on an empty square
   - Flanks at least one opponent's piece
4. All flanked pieces are captured and turned to the current player's color
5. The game ends when:
   - No more valid moves are possible
   - Both players pass consecutively
   - Maximum number of moves is reached
6. The player with the most pieces wins

## License

This project is licensed under the terms specified in the LICENSE file.
