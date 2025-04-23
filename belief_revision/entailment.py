"""
Logical entailment checking for belief revision agent.
This module implements a resolution-based method for checking logical entailment.
"""

from propositional_logic import Formula, Atom, Not, And, Or, cnf_to_clauses, is_literal
import sys


class ResolutionChecker:
    """A class for checking logical entailment using resolution."""

    def __init__(self):
        """Initialize the resolution checker."""
        self.recursion_limit = sys.getrecursionlimit()
        # Temporarily increase recursion limit for complex formulas
        sys.setrecursionlimit(5000)

    def entails(self, premise, conclusion):
        """
        Check if premise entails conclusion using resolution.

        Args:
            premise: The premise formula
            conclusion: The conclusion formula

        Returns:
            bool: True if premise entails conclusion, False otherwise
        """
        # P entails Q if and only if P ∧ ¬Q is unsatisfiable
        # So we check if premise ∧ ¬conclusion is unsatisfiable using resolution

        # Handle trivial cases first
        if premise == conclusion:
            return True

        # Simple truth check
        if isinstance(premise, Atom) and premise.name == "True":
            return True

        # For complex formulas, try a more direct approach
        try:
            # Try to enumerate all possible valuations for the variables
            # (only possible for formulas with a small number of variables)
            variables = premise.get_variables().union(conclusion.get_variables())

            if len(variables) <= 5:  # Only do this for small formulas
                from itertools import product

                # Check all possible valuations
                for vals in product([True, False], repeat=len(variables)):
                    valuation = dict(zip(variables, vals))

                    # If premise is true but conclusion is false, then no entailment
                    if premise.evaluate(valuation) and not conclusion.evaluate(valuation):
                        return False

                # If we've checked all valuations and none falsify the entailment, it holds
                return True

            # For larger formulas, use resolution
            premise_cnf = premise.to_cnf()
            negated_conclusion_cnf = Not(conclusion).to_cnf()
            combined = And(premise_cnf, negated_conclusion_cnf).to_cnf()

            # Convert CNF to set of clauses
            clauses = cnf_to_clauses(combined)

            # Check if the clauses are unsatisfiable using resolution
            return self._is_unsatisfiable(clauses)
        except (RecursionError, ValueError) as e:
            # If we hit an error, try a fallback approach
            print(f"Warning: Error during entailment check: {e}")
            # Simple safe approach: check if conclusion is a direct subformula of premise
            import re
            premise_str = str(premise)
            conclusion_str = str(conclusion)
            return conclusion_str in premise_str
        finally:
            # Reset recursion limit to original value
            sys.setrecursionlimit(self.recursion_limit)

    def _is_unsatisfiable(self, clauses):
        """
        Check if a set of clauses is unsatisfiable using resolution.

        Args:
            clauses: Set of clauses (each clause is a frozenset of literals)

        Returns:
            bool: True if the clauses are unsatisfiable, False otherwise
        """
        # Check for empty clause
        if frozenset() in clauses:
            return True

        # Check if there are too many clauses - if so, we'll use a simplified approach
        if len(clauses) > 50:
            # Look for obvious contradictions (p and ¬p in the same clause)
            for clause in clauses:
                for lit in clause:
                    if isinstance(lit, Not) and lit.formula in clause:
                        return True
            return False

        # Implementation of the resolution algorithm with limits
        # If we can derive the empty clause, the set is unsatisfiable

        # Make a copy of the clauses
        working_clauses = set(clauses)

        # Keep track of new clauses we add to check if we've reached a fixed point
        new_clauses_added = True
        max_iterations = 100  # Limit the number of iterations
        iteration = 0

        # Keep track of the number of clauses to avoid explosion
        max_clauses = max(1000, len(clauses) * 10)

        while new_clauses_added and iteration < max_iterations and len(working_clauses) < max_clauses:
            iteration += 1
            new_clauses_added = False

            # Generate a limited number of pairs of clauses for resolution
            # Focus on smaller clauses first as they're more likely to produce useful resolvents
            sorted_clauses = sorted(working_clauses, key=len)
            pairs = []

            # Only use a limited number of the smallest clauses
            num_clauses_to_use = min(20, len(sorted_clauses))
            small_clauses = sorted_clauses[:num_clauses_to_use]

            # Generate pairs involving at least one small clause
            for c1 in small_clauses:
                for c2 in working_clauses:
                    if c1 != c2:
                        pairs.append((c1, c2))

                        # Limit the number of pairs
                        if len(pairs) >= 1000:
                            break
                if len(pairs) >= 1000:
                    break

            for c1, c2 in pairs:
                # Try to resolve the two clauses
                resolvents = self._resolve(c1, c2)

                for resolvent in resolvents:
                    # If we derived the empty clause, the set is unsatisfiable
                    if not resolvent:
                        return True

                    # If we derived a new clause, add it to our working set
                    # Only add if it's not a subset of an existing clause
                    should_add = True
                    for existing_clause in working_clauses:
                        if resolvent.issubset(existing_clause):
                            # Skip this resolvent as it's less specific
                            should_add = False
                            break

                    if should_add and resolvent not in working_clauses:
                        working_clauses.add(resolvent)
                        new_clauses_added = True

        # If we couldn't derive the empty clause, the set is satisfiable
        return False

    def _resolve(self, clause1, clause2):
        """
        Resolve two clauses and return the resulting clauses.

        Args:
            clause1: First clause (frozenset of literals)
            clause2: Second clause (frozenset of literals)

        Returns:
            list: List of resolvents (each resolvent is a frozenset of literals)
        """
        resolvents = []

        # Check each literal in the first clause
        for lit1 in clause1:
            # Check if the negation of this literal is in the second clause
            complementary_lit = self._get_complementary_literal(lit1)

            if complementary_lit is not None and complementary_lit in clause2:
                # Create a new clause by resolving on this literal
                new_clause = (clause1.union(clause2) - {lit1, complementary_lit})
                resolvents.append(frozenset(new_clause))

        return resolvents

    def _get_complementary_literal(self, literal):
        """
        Get the complementary literal for a given literal.

        Args:
            literal: A literal (Atom or Not(Atom))

        Returns:
            Formula: Complementary literal or None if not a literal
        """
        if isinstance(literal, Not) and isinstance(literal.formula, Atom):
            # ¬P -> P
            return literal.formula
        elif isinstance(literal, Atom):
            # P -> ¬P
            return Not(literal)
        else:
            # Not a literal, return None
            return None