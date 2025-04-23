"""
Belief base implementation for belief revision agent.
This module defines the BeliefBase class that stores formulas with priorities.
"""

class BeliefBase:
    """
    A belief base is a set of propositional logic formulas with priorities.
    Higher priority values indicate more important beliefs.
    """

    def __init__(self):
        """Initialize an empty belief base."""
        # Dictionary mapping formulas to their priorities
        self.beliefs = {}

    def __repr__(self):
        """String representation of the belief base."""
        if not self.beliefs:
            return "Empty belief base"

        # Sort beliefs by priority (highest first)
        sorted_beliefs = sorted(self.beliefs.items(), key=lambda x: x[1], reverse=True)

        result = "Belief base:\n"
        for formula, priority in sorted_beliefs:
            result += f"  {formula} (priority: {priority})\n"

        return result

    def add(self, formula, priority=1):
        """
        Add a formula to the belief base with the given priority.
        If the formula already exists, update its priority.

        Args:
            formula: The formula to add
            priority: The priority of the formula (default: 1)
        """
        self.beliefs[formula] = priority

    def remove(self, formula):
        """
        Remove a formula from the belief base.

        Args:
            formula: The formula to remove

        Returns:
            bool: True if the formula was removed, False if it wasn't in the belief base
        """
        if formula in self.beliefs:
            del self.beliefs[formula]
            return True
        return False

    def contains(self, formula):
        """
        Check if the belief base contains a specific formula.

        Args:
            formula: The formula to check

        Returns:
            bool: True if the formula is in the belief base, False otherwise
        """
        return formula in self.beliefs

    def get_priority(self, formula):
        """
        Get the priority of a formula in the belief base.

        Args:
            formula: The formula to check

        Returns:
            int: The priority of the formula, or None if the formula is not in the belief base
        """
        return self.beliefs.get(formula, None)

    def get_all_formulas(self):
        """
        Get all formulas in the belief base.

        Returns:
            list: List of all formulas in the belief base
        """
        return list(self.beliefs.keys())

    def get_formulas_by_priority(self, min_priority=None, max_priority=None):
        """
        Get formulas with priorities in the specified range.

        Args:
            min_priority: Minimum priority (inclusive)
            max_priority: Maximum priority (inclusive)

        Returns:
            list: List of formulas with priorities in the specified range
        """
        result = []

        for formula, priority in self.beliefs.items():
            if (min_priority is None or priority >= min_priority) and \
               (max_priority is None or priority <= max_priority):
                result.append(formula)

        return result

    def is_consistent(self, entailment_checker):
        """
        Check if the belief base is consistent.
        A belief base is consistent if it does not entail a contradiction.

        Args:
            entailment_checker: An instance of an entailment checker

        Returns:
            bool: True if the belief base is consistent, False otherwise
        """
        # A belief base is inconsistent if it entails a contradiction (P ∧ ¬P)
        # For efficiency, we can check if the belief base entails False

        if not self.beliefs:
            # An empty belief base is always consistent
            return True

        # Check if we can derive a contradiction
        # Create a formula that is the conjunction of all formulas in the belief base
        belief_conjunction = self._get_conjunction()

        # Create a contradiction (P ∧ ¬P)
        # We can use any atom for this, let's use 'p'
        from propositional_logic import Atom, And, Not
        p = Atom('p')
        contradiction = And(p, Not(p))

        # Check if the belief base entails the contradiction
        return not entailment_checker.entails(belief_conjunction, contradiction)

    def _get_conjunction(self):
        """
        Get the conjunction of all formulas in the belief base.

        Returns:
            Formula: The conjunction of all formulas in the belief base
        """
        from propositional_logic import Atom, And

        formulas = self.get_all_formulas()

        if not formulas:
            # By convention, an empty conjunction is equivalent to True
            # We'll represent True as an atom 'True'
            return Atom('True')

        if len(formulas) == 1:
            return formulas[0]

        # Build the conjunction in a balanced way to reduce recursion depth
        def build_conjunction(formulas_list):
            if len(formulas_list) == 1:
                return formulas_list[0]
            elif len(formulas_list) == 2:
                return And(formulas_list[0], formulas_list[1])
            else:
                # Split the list in half and build each half separately
                mid = len(formulas_list) // 2
                left = build_conjunction(formulas_list[:mid])
                right = build_conjunction(formulas_list[mid:])
                return And(left, right)

        return build_conjunction(formulas)

    def copy(self):
        """
        Create a deep copy of the belief base.

        Returns:
            BeliefBase: A new belief base with the same formulas and priorities
        """
        new_belief_base = BeliefBase()

        for formula, priority in self.beliefs.items():
            new_belief_base.add(formula, priority)

        return new_belief_base