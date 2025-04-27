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

    The implementation follows the AGM framework:
    1. Compute the remainder set (all maximal subsets that don't entail the formula)
    2. Use a selection function to choose the "best" remainder sets
    3. Take the intersection of the selected remainder sets
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

        # Combine the selected remainder sets by taking their intersection
        return self._intersect_remainder_sets(selected_remainder_sets)

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

        # Generate all possible subsets of the belief base
        all_subsets = []
        for i in range(len(all_formulas) + 1):
            all_subsets.extend(combinations(all_formulas, i))

        # Create belief bases from these subsets and check entailment
        candidate_sets = []
        for subset in all_subsets:
            subset_base = BeliefBase()
            for f in subset:
                subset_base.add(f, belief_base.get_priority(f))

            # Check if this subset entails the formula
            subset_conjunction = subset_base._get_conjunction()
            if not self.entailment_checker.entails(subset_conjunction, formula):
                candidate_sets.append(subset_base)

        # Filter to retain only maximal sets
        remainder_sets = []
        for candidate in candidate_sets:
            candidate_formulas = set(candidate.get_all_formulas())
            is_maximal = True

            # Check if this candidate is a subset of any other candidate
            for other in candidate_sets:
                if candidate == other:
                    continue

                other_formulas = set(other.get_all_formulas())
                if candidate_formulas.issubset(other_formulas) and not candidate_formulas == other_formulas:
                    is_maximal = False
                    break

            if is_maximal:
                remainder_sets.append(candidate)

        return remainder_sets

    def _select_remainder_sets(self, remainder_sets, original_belief_base):
        """
        Select the "best" remainder sets based on priority.

        This is the selection function in AGM terminology.

        Args:
            remainder_sets: List of remainder sets
            original_belief_base: The original belief base (for priorities)

        Returns:
            list: List of selected remainder sets
        """
        if not remainder_sets:
            return []

        # Calculate a score for each remainder set based on the priorities of formulas
        scored_sets = []

        for remainder in remainder_sets:
            # Calculate a score for this remainder set
            score = 0
            for formula in remainder.get_all_formulas():
                score += original_belief_base.get_priority(formula)

            # The more high-priority formulas are kept, the better
            scored_sets.append((remainder, score))

        # Sort by score (highest first)
        scored_sets.sort(key=lambda x: x[1], reverse=True)

        # Get the highest score
        highest_score = scored_sets[0][1]

        # Select all sets with the highest score (might be more than one)
        selected = [set_info[0] for set_info in scored_sets if set_info[1] == highest_score]

        return selected

    def _intersect_remainder_sets(self, remainder_sets):
        """
        Compute the intersection of the selected remainder sets.

        This follows the AGM definition of partial meet contraction.

        Args:
            remainder_sets: List of selected remainder sets

        Returns:
            BeliefBase: The contracted belief base
        """
        if not remainder_sets:
            from belief_base import BeliefBase
            return BeliefBase()

        # If there's only one remainder set, return it
        if len(remainder_sets) == 1:
            return remainder_sets[0]

        # Get the set of formulas in the first remainder set
        from belief_base import BeliefBase
        result = BeliefBase()

        # Find formulas that are in all remainder sets (the intersection)
        common_formulas = set(remainder_sets[0].get_all_formulas())
        for remainder in remainder_sets[1:]:
            common_formulas.intersection_update(set(remainder.get_all_formulas()))

        # Add the common formulas to the result with their original priorities
        for formula in common_formulas:
            # Use the maximum priority from all remainder sets
            max_priority = max(
                remainder.get_priority(formula)
                for remainder in remainder_sets
                if formula in remainder.get_all_formulas()
            )
            result.add(formula, max_priority)

        return result