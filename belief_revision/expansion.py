"""
Belief expansion and revision for belief revision agent.
This module implements expansion and revision of belief base following AGM postulates.
"""

from propositional_logic import And, Not
from contraction import PartialMeetContraction


class Expansion:
    """
    Implementation of belief expansion according to AGM theory.

    Expansion simply adds a new formula to the belief base without
    checking for consistency.
    """

    def __init__(self, entailment_checker=None):
        """
        Initialize the expansion operator with an entailment checker.

        Args:
            entailment_checker: An instance of an entailment checker (optional)
        """
        if entailment_checker:
            self.entailment_checker = entailment_checker
        else:
            from entailment import ResolutionChecker
            self.entailment_checker = ResolutionChecker()

    def expand(self, belief_base, formula, priority=1):
        """
        Expand a belief base by adding a formula without checking for consistency.

        This follows the AGM expansion definition: K+A = Cn(K ∪ {A})

        Args:
            belief_base: The belief base to expand
            formula: The formula to add
            priority: The priority of the formula (default: 1)

        Returns:
            BeliefBase: A new belief base after expansion
        """
        # Create a copy of the belief base
        result = belief_base.copy()

        # Simply add the formula to the belief base
        result.add(formula, priority)

        return result

    def safe_expand(self, belief_base, formula, priority=1):
        """
        Safely expand a belief base by adding a formula only if it doesn't lead to inconsistency.

        Args:
            belief_base: The belief base to expand
            formula: The formula to add
            priority: The priority of the formula (default: 1)

        Returns:
            BeliefBase: A new belief base after expansion
        """
        # Create a copy of the belief base
        result = belief_base.copy()

        # Add the formula to the belief base
        result.add(formula, priority)

        # Check if the result is consistent
        if result.is_consistent(self.entailment_checker):
            return result
        else:
            # If adding the formula leads to inconsistency, return the original belief base
            return belief_base.copy()


class Revision:
    """
    Implementation of belief revision using Levi identity following AGM theory:

    Revision(B, A) = Expansion(Contraction(B, ¬A), A)

    This approach ensures that the AGM postulates for revision are satisfied.
    """

    def __init__(self, entailment_checker=None):
        """
        Initialize the revision operator with an entailment checker.

        Args:
            entailment_checker: An instance of an entailment checker (optional)
        """
        if entailment_checker:
            self.entailment_checker = entailment_checker
        else:
            from entailment import ResolutionChecker
            self.entailment_checker = ResolutionChecker()

        self.contraction = PartialMeetContraction(self.entailment_checker)
        self.expansion = Expansion(self.entailment_checker)

    def revise(self, belief_base, formula, priority=1):
        """
        Revise a belief base by incorporating a new formula using the Levi identity.

        The Levi identity defines revision as:
        K*A = (K-¬A)+A

        First contract by the negation of the formula to make room for it,
        then expand with the formula.

        Args:
            belief_base: The belief base to revise
            formula: The formula to incorporate
            priority: The priority of the formula (default: 1)

        Returns:
            BeliefBase: A new belief base after revision
        """
        # First, contract the belief base by the negation of the formula
        negated_formula = Not(formula)
        contracted = self.contraction.contract(belief_base, negated_formula)

        # Then, expand the contracted belief base with the formula
        revised = self.expansion.expand(contracted, formula, priority)

        # Ensure the result is consistent (Consistency postulate)
        if not revised.is_consistent(self.entailment_checker):
            # If inconsistent, try a more conservative approach: retain only the new formula
            from belief_base import BeliefBase
            result = BeliefBase()
            result.add(formula, priority)
            return result

        return revised

    def iterative_revision(self, belief_base, formulas, priorities=None):
        """
        Revise a belief base iteratively with a sequence of formulas.

        Args:
            belief_base: The belief base to revise
            formulas: List of formulas to incorporate
            priorities: List of priorities for the formulas (default: all 1)

        Returns:
            BeliefBase: A new belief base after revision
        """
        if priorities is None:
            priorities = [1] * len(formulas)

        result = belief_base.copy()

        for formula, priority in zip(formulas, priorities):
            result = self.revise(result, formula, priority)

        return result