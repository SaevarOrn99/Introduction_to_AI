# Belief Revision Agent

This project implements a belief revision agent based on the AGM (Alchourrón, Gärdenfors, and Makinson) theory of belief change. It supports belief expansion, contraction, and revision, and provides both a command-line demonstration and a graphical user interface (GUI).

## Features

- **Propositional Logic Engine:** Supports parsing, representing, and manipulating propositional logic formulas.
- **Belief Base:** Stores formulas with priorities, allowing for prioritized belief change.
- **Entailment Checking:** Uses resolution-based methods to check logical entailment.
- **AGM Belief Change:** Implements expansion, contraction (partial meet), and revision (Levi identity) operations.
- **GUI:** User-friendly interface for interacting with the belief base and performing belief change operations.
- **Tests:** Includes tests for AGM postulates (success, inclusion, vacuity, consistency, extensionality).

---

## File Overview

- `main.py` — Command-line demonstration of the belief revision agent.
- `belief_revision_gui.py` — Graphical user interface for the agent (Tkinter).
- `belief_base.py` — Belief base implementation with priorities.
- `propositional_logic.py` — Propositional logic formula classes and parser.
- `entailment.py` — Resolution-based entailment checker.
- `contraction.py` — Partial meet contraction operator.
- `expansion.py` — Expansion and revision operators (AGM).
- `test.py` — Tests for AGM postulates and belief revision logic.

---

## Requirements

- Python 3.7+
- Tkinter (usually included with Python)
- No external dependencies required

---

## How It Works

### Core Concepts

- **Belief Base:** A set of propositional formulas, each with a priority.
- **Expansion:** Adds a new belief without checking for consistency.
- **Contraction:** Removes a belief while preserving as much information as possible.
- **Revision:** Incorporates a new belief, possibly removing some existing beliefs to maintain consistency (using the Levi identity: contract by the negation, then expand).

### Main Components

- **Formulas:** Represented as objects (`Atom`, `Not`, `And`, `Or`, `Implies`, `Equivalent`).
- **Entailment:** Checks if a set of beliefs logically entails a formula.
- **Belief Change:** Follows AGM postulates for rational belief change.

---

## Usage

### 1. Command-Line Demonstration

To run the command-line demo:

```bash
python main.py
```

This will:

- Create a belief base with example beliefs.
- Demonstrate entailment, contraction, expansion, and revision.
- Show how the Levi identity is used for revision.

### 2. Graphical User Interface

To launch the GUI:

```bash
python belief_revision_gui.py
```

**Features:**

- Add formulas to the belief base (with priorities).
- Perform contraction, expansion, and revision.
- Check entailment of formulas.
- View and clear the current belief base.
- See results and explanations for each operation.
- Built-in help and example loader.

**Formula Syntax:**

- Atoms: `p`, `q`, `r`
- Negation: `~p` or `¬p`
- And: `p & q`
- Or: `p | q`
- Implies: `p -> q`
- Equivalent: `p <-> q`

### 3. Running Tests

To run all AGM postulate tests and verify correctness:

```bash
python test.py
```

This will print a summary of which AGM postulates are satisfied by the implementation.

---

## Example

**Adding beliefs:**

- "If it rains, the ground is wet" (`p -> q`, priority 3)
- "It is raining" (`p`, priority 2)
- "If the ground is wet, the floor is slippery" (`q -> r`, priority 2)

**Operations:**

- Check if the belief base entails "The floor is slippery" (`r`).
- Contract the belief base to remove "It is raining" (`p`).
- Expand with "The ground is wet" (`q`).
- Revise with "It is not raining" (`~p`).

---

## Extending

- You can add new logical operators or change the selection function for contraction.
- The code is modular: logic, belief base, and GUI are separated for easy extension.

---

## License

This project is provided for educational and research purposes.
