"""
Belief contraction for belief revision agent.
This module implements contraction of belief base using a priority order.
"""

from itertools import combinations
from propositional_logic import And
from entailment import ResolutionChecker


class PartialMeetContraction:
    """
    Implementation of partial meet contraction for belief revision.

    Partial meet contraction removes a formula from the belief base
    while preserving as much information as possible, using a priority
    ordering to determine which formulas to keep.
    """

    def __init__(self, entailment_checker=None):
        """
        Initialize the contraction operator with an entailment checker.

        Args:
            entailment_checker: An instance of an entailment checker (optional)
        """
        self.entailment_checker = entailment_checker or ResolutionChecker()

    def contract(self, belief_base, formula):
        """
        Contract a belief base by removing a formula.

        Args:
            belief_base: The belief base to contract
            formula: The formula to remove

        Returns:
            BeliefBase: A new belief base after contraction
        """
        # If the formula is not entailed by the belief base,
        # then there's nothing to contract (Vacuity postulate)
        belief_conjunction = belief_base._get_conjunction()
        if not self.entailment_checker.entails(belief_conjunction, formula):
            return belief_base.copy()

        # Compute all the maximal subsets that do not entail the formula
        remainder_sets = self._compute_remainder_sets(belief_base, formula)

        # If there are no remainder sets, return the empty belief base
        if not remainder_sets:
            from belief_base import BeliefBase
            return BeliefBase()

        # Select the "best" remainder sets based on priority
        selected_remainder_sets = self._select_remainder_sets(remainder_sets, belief_base)

        # Combine the selected remainder sets
        return self._combine_remainder_sets(selected_remainder_sets)

    def _compute_remainder_sets(self, belief_base, formula):
        """
        Compute all maximal subsets of the belief base that do not entail the formula.

        Args:
            belief_base: The belief base
            formula: The formula to remove

        Returns:
            list: List of remainder sets (each is a BeliefBase)
        """
        from belief_base import BeliefBase
        all_formulas = belief_base.get_all_formulas()

        # If the set is empty, return an empty belief base
        if not all_formulas:
            return [BeliefBase()]

        # For small belief bases, use the incremental approach
        remainder_sets = []

        # Start with the empty set and add formulas one by one if they don't cause entailment
        empty_base = BeliefBase()

        # For each formula in the belief base
        for f in all_formulas:
            # Try adding it to each current remainder set
            new_remainder_sets = []

            # If this is the first formula, start with the empty set
            if not remainder_sets:
                test_base = empty_base.copy()
                test_base.add(f, belief_base.get_priority(f))

                # Check if this causes entailment
                if not self.entailment_checker.entails(test_base._get_conjunction(), formula):
                    new_remainder_sets.append(test_base)

                remainder_sets = new_remainder_sets
                continue

            # For each existing remainder set
            for r in remainder_sets:
                # Make a copy without the formula
                r_without_f = r.copy()

                # Make a copy with the formula
                r_with_f = r.copy()
                r_with_f.add(f, belief_base.get_priority(f))

                # Check if adding the formula causes entailment
                if not self.entailment_checker.entails(r_with_f._get_conjunction(), formula):
                    new_remainder_sets.append(r_with_f)
                else:
                    new_remainder_sets.append(r_without_f)

            remainder_sets = new_remainder_sets

        # Check maximality
        final_remainders = []
        for r in remainder_sets:
            is_maximal = True
            r_formulas = set(r.get_all_formulas())

            for other in remainder_sets:
                if r == other:
                    continue

                other_formulas = set(other.get_all_formulas())
                if r_formulas.issubset(other_formulas) and r_formulas != other_formulas:
                    is_maximal = False
                    break

            if is_maximal:
                final_remainders.append(r)

        return final_remainders

    def _select_remainder_sets(self, remainder_sets, original_belief_base):
        """
        Select the "best" remainder sets based on priority.

        Args:
            remainder_sets: List of remainder sets
            original_belief_base: The original belief base (for priorities)

        Returns:
            list: List of selected remainder sets
        """
        # Compute the "average priority" of each remainder set
        # We'll select the one with the highest average priority
        scores = []

        for remainder in remainder_sets:
            total_priority = sum(original_belief_base.get_priority(f)
                                for f in remainder.get_all_formulas())
            avg_priority = total_priority / len(remainder.get_all_formulas()) if remainder.get_all_formulas() else 0
            scores.append((remainder, avg_priority))

        # Sort by average priority (highest first)
        scores.sort(key=lambda x: x[1], reverse=True)

        # If there's a tie for highest priority, select all tied sets
        if not scores:
            return []

        highest_priority = scores[0][1]
        selected = [s[0] for s in scores if s[1] == highest_priority]

        return selected

    def _combine_remainder_sets(self, remainder_sets):
        """
        Combine the selected remainder sets to form the contracted belief base.

        Args:
            remainder_sets: List of selected remainder sets

        Returns:
            BeliefBase: The contracted belief base
        """
        if not remainder_sets:
            from belief_base import BeliefBase
            return BeliefBase()

        # The intersection of all remainder sets
        from belief_base import BeliefBase
        result = BeliefBase()

        # Get all formulas that appear in all remainder sets
        all_formulas = set()
        common_formulas = None

        for remainder in remainder_sets:
            remainder_formulas = set(remainder.get_all_formulas())
            all_formulas.update(remainder_formulas)

            if common_formulas is None:
                common_formulas = remainder_formulas
            else:
                common_formulas.intersection_update(remainder_formulas)

        # Add the common formulas to the result with their original priorities
        for formula in common_formulas:
            # Use the maximum priority from all remainder sets
            priority = max(remainder.get_priority(formula) for remainder in remainder_sets)
            result.add(formula, priority)

        return result