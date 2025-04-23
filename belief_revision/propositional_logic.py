"""
Propositional logic representation for belief revision agent.
This module defines the classes and operations for propositional logic formulas.
"""

import sys

class Formula:
    """Base class for propositional logic formulas."""
    def __init__(self):
        pass

    def __eq__(self, other):
        return type(self) == type(other) and self._eq(other)

    def _eq(self, other):
        raise NotImplementedError("Subclasses must implement this")

    def __hash__(self):
        raise NotImplementedError("Subclasses must implement this")

    def evaluate(self, valuation):
        """Evaluate formula under a given valuation (dictionary of variables to boolean values)."""
        raise NotImplementedError("Subclasses must implement this")

    def to_cnf(self):
        """Convert formula to Conjunctive Normal Form."""
        raise NotImplementedError("Subclasses must implement this")

    def get_variables(self):
        """Get set of variables in the formula."""
        raise NotImplementedError("Subclasses must implement this")


class Atom(Formula):
    """Atomic proposition in propositional logic."""
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return self.name

    def _eq(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(("atom", self.name))

    def evaluate(self, valuation):
        return valuation.get(self.name, False)

    def to_cnf(self):
        return self

    def get_variables(self):
        return {self.name}


class Not(Formula):
    """Negation operator in propositional logic."""
    def __init__(self, formula):
        super().__init__()
        self.formula = formula

    def __repr__(self):
        if isinstance(self.formula, Atom):
            return f"¬{self.formula}"
        else:
            return f"¬({self.formula})"

    def _eq(self, other):
        return self.formula == other.formula

    def __hash__(self):
        return hash(("not", hash(self.formula)))

    def evaluate(self, valuation):
        return not self.formula.evaluate(valuation)

    def to_cnf(self):
        # Apply De Morgan's laws and other transformations
        if isinstance(self.formula, Not):
            # Double negation elimination: ¬¬p ≡ p
            return self.formula.formula.to_cnf()
        elif isinstance(self.formula, And):
            # De Morgan: ¬(p ∧ q) ≡ ¬p ∨ ¬q
            left_neg = Not(self.formula.left).to_cnf()
            right_neg = Not(self.formula.right).to_cnf()
            return Or(left_neg, right_neg)
        elif isinstance(self.formula, Or):
            # De Morgan: ¬(p ∨ q) ≡ ¬p ∧ ¬q
            left_neg = Not(self.formula.left).to_cnf()
            right_neg = Not(self.formula.right).to_cnf()
            return And(left_neg, right_neg)
        elif isinstance(self.formula, Implies):
            # ¬(p → q) ≡ p ∧ ¬q
            left_cnf = self.formula.left.to_cnf()
            right_neg = Not(self.formula.right).to_cnf()
            return And(left_cnf, right_neg)
        elif isinstance(self.formula, Equivalent):
            # ¬(p ↔ q) ≡ (p ∧ ¬q) ∨ (¬p ∧ q)
            left_cnf = self.formula.left.to_cnf()
            right_cnf = self.formula.right.to_cnf()
            left_neg = Not(self.formula.left).to_cnf()
            right_neg = Not(self.formula.right).to_cnf()
            left_impl = And(left_cnf, right_neg)
            right_impl = And(left_neg, right_cnf)
            return Or(left_impl, right_impl)
        else:
            return self

    def get_variables(self):
        return self.formula.get_variables()


class And(Formula):
    """Conjunction operator in propositional logic."""
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} ∧ {self.right})"

    def _eq(self, other):
        # Check direct equality
        direct_eq = self.left == other.left and self.right == other.right
        # Check commutative equality (p ∧ q) == (q ∧ p)
        commutative_eq = self.left == other.right and self.right == other.left
        return direct_eq or commutative_eq

    def __hash__(self):
        # Using a canonical form for hashing to ensure (p ∧ q) and (q ∧ p) have the same hash
        h1, h2 = hash(self.left), hash(self.right)
        return hash(("and", min(h1, h2), max(h1, h2)))

    def evaluate(self, valuation):
        return self.left.evaluate(valuation) and self.right.evaluate(valuation)

    def to_cnf(self):
        # Try to limit recursion depth
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(5000)

        try:
            left_cnf = self.left.to_cnf()
            right_cnf = self.right.to_cnf()

            # Simple case: both sides are simple formulas (not And/Or)
            if not (isinstance(left_cnf, And) or isinstance(left_cnf, Or) or
                    isinstance(right_cnf, And) or isinstance(right_cnf, Or)):
                return And(left_cnf, right_cnf)

            # If either side is an And, just combine them
            if isinstance(left_cnf, And) and isinstance(right_cnf, And):
                # Flatten nested Ands into a list
                formulas = []
                self._collect_and_formulas(left_cnf, formulas)
                self._collect_and_formulas(right_cnf, formulas)

                # Rebuild a balanced And tree
                return self._build_balanced_and(formulas)
            elif isinstance(left_cnf, And):
                formulas = []
                self._collect_and_formulas(left_cnf, formulas)
                formulas.append(right_cnf)
                return self._build_balanced_and(formulas)
            elif isinstance(right_cnf, And):
                formulas = []
                formulas.append(left_cnf)
                self._collect_and_formulas(right_cnf, formulas)
                return self._build_balanced_and(formulas)

            # Handle distributivity: p ∧ (q ∨ r) ≡ (p ∧ q) ∨ (p ∧ r)
            if isinstance(left_cnf, Or):
                # (a ∨ b) ∧ c -> (a ∧ c) ∨ (b ∧ c)
                result_left = And(left_cnf.left, right_cnf)
                result_right = And(left_cnf.right, right_cnf)
                return Or(result_left, result_right)
            elif isinstance(right_cnf, Or):
                # a ∧ (b ∨ c) -> (a ∧ b) ∨ (a ∧ c)
                result_left = And(left_cnf, right_cnf.left)
                result_right = And(left_cnf, right_cnf.right)
                return Or(result_left, result_right)
            else:
                return And(left_cnf, right_cnf)
        finally:
            sys.setrecursionlimit(old_limit)

    def _collect_and_formulas(self, formula, result_list):
        """Helper method to collect formulas from nested And expressions."""
        if isinstance(formula, And):
            self._collect_and_formulas(formula.left, result_list)
            self._collect_and_formulas(formula.right, result_list)
        else:
            result_list.append(formula)

    def _build_balanced_and(self, formulas):
        """Build a balanced tree of And expressions to minimize recursion depth."""
        if not formulas:
            return Atom("True")  # Empty conjunction is equivalent to True
        if len(formulas) == 1:
            return formulas[0]
        if len(formulas) == 2:
            return And(formulas[0], formulas[1])

        # Recursively build a balanced tree
        mid = len(formulas) // 2
        left = self._build_balanced_and(formulas[:mid])
        right = self._build_balanced_and(formulas[mid:])
        return And(left, right)

    def get_variables(self):
        return self.left.get_variables().union(self.right.get_variables())


class Or(Formula):
    """Disjunction operator in propositional logic."""
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} ∨ {self.right})"

    def _eq(self, other):
        # Check direct equality
        direct_eq = self.left == other.left and self.right == other.right
        # Check commutative equality (p ∨ q) == (q ∨ p)
        commutative_eq = self.left == other.right and self.right == other.left
        return direct_eq or commutative_eq

    def __hash__(self):
        # Using a canonical form for hashing to ensure (p ∨ q) and (q ∨ p) have the same hash
        h1, h2 = hash(self.left), hash(self.right)
        return hash(("or", min(h1, h2), max(h1, h2)))

    def evaluate(self, valuation):
        return self.left.evaluate(valuation) or self.right.evaluate(valuation)

    def to_cnf(self):
        # Try to limit recursion depth
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(5000)

        try:
            left_cnf = self.left.to_cnf()
            right_cnf = self.right.to_cnf()

            # Simple case: both sides are simple formulas (not And/Or)
            if not (isinstance(left_cnf, And) or isinstance(left_cnf, Or) or
                    isinstance(right_cnf, And) or isinstance(right_cnf, Or)):
                return Or(left_cnf, right_cnf)

            # If either side is an Or, combine them
            if isinstance(left_cnf, Or) and isinstance(right_cnf, Or):
                # Flatten nested Ors into a list
                formulas = []
                self._collect_or_formulas(left_cnf, formulas)
                self._collect_or_formulas(right_cnf, formulas)

                # Rebuild a balanced Or tree
                return self._build_balanced_or(formulas)
            elif isinstance(left_cnf, Or):
                formulas = []
                self._collect_or_formulas(left_cnf, formulas)
                formulas.append(right_cnf)
                return self._build_balanced_or(formulas)
            elif isinstance(right_cnf, Or):
                formulas = []
                formulas.append(left_cnf)
                self._collect_or_formulas(right_cnf, formulas)
                return self._build_balanced_or(formulas)

            # Handle distributivity: (p ∧ q) ∨ r ≡ (p ∨ r) ∧ (q ∨ r)
            if isinstance(left_cnf, And):
                # (a ∧ b) ∨ c -> (a ∨ c) ∧ (b ∨ c)
                result_left = Or(left_cnf.left, right_cnf)
                result_right = Or(left_cnf.right, right_cnf)
                return And(result_left, result_right)
            elif isinstance(right_cnf, And):
                # a ∨ (b ∧ c) -> (a ∨ b) ∧ (a ∨ c)
                result_left = Or(left_cnf, right_cnf.left)
                result_right = Or(left_cnf, right_cnf.right)
                return And(result_left, result_right)
            else:
                return Or(left_cnf, right_cnf)
        finally:
            sys.setrecursionlimit(old_limit)

    def _collect_or_formulas(self, formula, result_list):
        """Helper method to collect formulas from nested Or expressions."""
        if isinstance(formula, Or):
            self._collect_or_formulas(formula.left, result_list)
            self._collect_or_formulas(formula.right, result_list)
        else:
            result_list.append(formula)

    def _build_balanced_or(self, formulas):
        """Build a balanced tree of Or expressions to minimize recursion depth."""
        if not formulas:
            return Atom("False")  # Empty disjunction is equivalent to False
        if len(formulas) == 1:
            return formulas[0]
        if len(formulas) == 2:
            return Or(formulas[0], formulas[1])

        # Recursively build a balanced tree
        mid = len(formulas) // 2
        left = self._build_balanced_or(formulas[:mid])
        right = self._build_balanced_or(formulas[mid:])
        return Or(left, right)

    def get_variables(self):
        return self.left.get_variables().union(self.right.get_variables())


class Implies(Formula):
    """Implication operator in propositional logic."""
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} → {self.right})"

    def _eq(self, other):
        return self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("implies", hash(self.left), hash(self.right)))

    def evaluate(self, valuation):
        return (not self.left.evaluate(valuation)) or self.right.evaluate(valuation)

    def to_cnf(self):
        # p → q ≡ ¬p ∨ q
        return Or(Not(self.left), self.right).to_cnf()

    def get_variables(self):
        return self.left.get_variables().union(self.right.get_variables())


class Equivalent(Formula):
    """Bi-implication (equivalence) operator in propositional logic."""
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} ↔ {self.right})"

    def _eq(self, other):
        # Check direct equality
        direct_eq = self.left == other.left and self.right == other.right
        # Check commutative equality (p ↔ q) == (q ↔ p)
        commutative_eq = self.left == other.right and self.right == other.left
        return direct_eq or commutative_eq

    def __hash__(self):
        # Using a canonical form for hashing to ensure (p ↔ q) and (q ↔ p) have the same hash
        h1, h2 = hash(self.left), hash(self.right)
        return hash(("equivalent", min(h1, h2), max(h1, h2)))

    def evaluate(self, valuation):
        return self.left.evaluate(valuation) == self.right.evaluate(valuation)

    def to_cnf(self):
        # p ↔ q ≡ (p → q) ∧ (q → p) ≡ (¬p ∨ q) ∧ (¬q ∨ p)
        left_to_right = Or(Not(self.left), self.right)
        right_to_left = Or(Not(self.right), self.left)
        return And(left_to_right, right_to_left).to_cnf()

    def get_variables(self):
        return self.left.get_variables().union(self.right.get_variables())


# Utility functions for parsing and manipulating formulas
def parse_formula(formula_str):
    """Parse a string representation of a formula.
    This is a simple parser for demonstration purposes.

    Examples:
        parse_formula("p")  # Atom
        parse_formula("~p")  # Not
        parse_formula("p & q")  # And
        parse_formula("p | q")  # Or
        parse_formula("p -> q")  # Implies
        parse_formula("p <-> q")  # Equivalent
    """
    # This is a simplified parser for demonstration
    formula_str = formula_str.strip()

    # Simple case: it's an atom
    if len(formula_str) == 1 and formula_str.isalpha():
        return Atom(formula_str)

    # Handle parenthesized expressions
    if formula_str.startswith("(") and formula_str.endswith(")"):
        # Check if the outer parentheses match
        count = 0
        for i, char in enumerate(formula_str):
            if char == "(":
                count += 1
            elif char == ")":
                count -= 1
            if count == 0 and i < len(formula_str) - 1:
                # Found a closing parenthesis before the end, so the outer parentheses
                # are not a matching pair
                break
        else:
            # The outer parentheses match, remove them
            formula_str = formula_str[1:-1].strip()

    # Check for negation (it has highest precedence)
    if formula_str.startswith("~") or formula_str.startswith("¬"):
        return Not(parse_formula(formula_str[1:].strip()))

    # Find the main operator (lowest precedence operator not in parentheses)
    operators = {
        "<->": Equivalent,  # Lowest precedence
        "->": Implies,
        "|": Or,
        "&": And           # Highest precedence
    }

    # Scan the formula to find the main operator
    main_op_pos = -1
    main_op = None
    paren_count = 0

    for i in range(len(formula_str)):
        if formula_str[i] == "(":
            paren_count += 1
        elif formula_str[i] == ")":
            paren_count -= 1

        # Only consider operators that are not inside parentheses
        if paren_count == 0:
            for op in operators:
                if i + len(op) <= len(formula_str) and formula_str[i:i+len(op)] == op:
                    # If we haven't found an operator yet, or this one has lower precedence
                    if main_op is None or list(operators.keys()).index(op) < list(operators.keys()).index(main_op):
                        main_op = op
                        main_op_pos = i

    # If we found a main operator, split on it
    if main_op_pos >= 0:
        left = formula_str[:main_op_pos].strip()
        right = formula_str[main_op_pos + len(main_op):].strip()
        left_formula = parse_formula(left)
        right_formula = parse_formula(right)

        # Create the appropriate formula based on the operator
        if main_op == "<->":
            return Equivalent(left_formula, right_formula)
        elif main_op == "->":
            return Implies(left_formula, right_formula)
        elif main_op == "|":
            return Or(left_formula, right_formula)
        elif main_op == "&":
            return And(left_formula, right_formula)

    # If no operators found, it's an atom
    return Atom(formula_str)


def cnf_to_clauses(formula):
    """Convert a CNF formula to a set of clauses.
    Each clause is a set of literals, and a literal is either an Atom or a Not(Atom).
    """
    # Base case: single literal (atom or negated atom)
    if is_literal(formula):
        return {frozenset({formula})}

    # Handle conjunction (p ∧ q): combine clauses from both sides
    if isinstance(formula, And):
        try:
            left_clauses = cnf_to_clauses(formula.left)
            right_clauses = cnf_to_clauses(formula.right)
            return left_clauses.union(right_clauses)
        except RecursionError:
            # Fallback if recursion limit is reached
            return {frozenset({formula})}

    # Handle disjunction (p ∨ q): make a single clause of all literals
    elif isinstance(formula, Or):
        # For a disjunction, we create a single clause containing all disjuncts
        literals = set()

        # Use iteration instead of recursion to collect literals
        to_process = [formula]
        while to_process:
            f = to_process.pop()
            if isinstance(f, Or):
                to_process.append(f.left)
                to_process.append(f.right)
            elif is_literal(f):
                literals.add(f)
            else:
                # Non-literal encountered in disjunction
                # This can happen if CNF conversion was incomplete
                literals.add(f)

        return {frozenset(literals)}
    else:
        # Any other formula is treated as a single clause
        return {frozenset({formula})}


def is_literal(formula):
    """Check if a formula is a literal (atom or negated atom)."""
    return isinstance(formula, Atom) or (isinstance(formula, Not) and isinstance(formula.formula, Atom))