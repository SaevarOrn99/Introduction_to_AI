"""
Main script for demonstrating the belief revision agent.
"""

from propositional_logic import Atom, Not, And, Or, Implies, Equivalent, parse_formula
from belief_base import BeliefBase
from entailment import ResolutionChecker
from contraction import PartialMeetContraction
from expansion import Expansion, Revision


def main():
    """Main function to demonstrate the belief revision agent."""
    print("Belief Revision Agent Demonstration")
    print("-----------------------------------")

    # Create a belief base with some initial beliefs
    belief_base = BeliefBase()

    # Add some formulas to the belief base with different priorities
    p = Atom('p')
    q = Atom('q')
    r = Atom('r')

    # "If it rains, the ground is wet" (priority 3)
    belief_base.add(Implies(p, q), 3)

    # "It is raining" (priority 2)
    belief_base.add(p, 2)

    # "If the ground is wet, the floor is slippery" (priority 2)
    belief_base.add(Implies(q, r), 2)

    print("\nInitial belief base:")
    print(belief_base)

    # Create an entailment checker
    entailment_checker = ResolutionChecker()

    # Check if the belief base entails "The floor is slippery"
    print("\nChecking entailment:")
    print(f"Does the belief base entail 'The floor is slippery'? {entailment_checker.entails(belief_base._get_conjunction(), r)}")

    # Contract the belief base to remove "It is raining"
    print("\nContracting the belief base to remove 'It is raining'...")
    contraction = PartialMeetContraction(entailment_checker)
    contracted_belief_base = contraction.contract(belief_base, p)

    print("\nBelief base after contraction:")
    print(contracted_belief_base)

    # Check entailment after contraction
    print("\nChecking entailment after contraction:")
    print(f"Does the contracted belief base entail 'The floor is slippery'? {entailment_checker.entails(contracted_belief_base._get_conjunction(), r)}")

    # Expand the contracted belief base with "The ground is wet"
    print("\nExpanding the contracted belief base with 'The ground is wet'...")
    expansion = Expansion(entailment_checker)
    expanded_belief_base = expansion.expand(contracted_belief_base, q, priority=1)

    print("\nBelief base after expansion:")
    print(expanded_belief_base)

    # Check entailment after expansion
    print("\nChecking entailment after expansion:")
    print(f"Does the expanded belief base entail 'The floor is slippery'? {entailment_checker.entails(expanded_belief_base._get_conjunction(), r)}")

    # Demonstrate belief revision
    print("\nDemonstrating belief revision:")
    print("Revising the original belief base with 'It is not raining'...")

    revision = Revision(entailment_checker)
    revised_belief_base = revision.revise(belief_base, Not(p), priority=3)

    print("\nBelief base after revision:")
    print(revised_belief_base)

    # Check consistency of the revised belief base
    print("\nChecking consistency of the revised belief base:")
    print(f"Is the revised belief base consistent? {revised_belief_base.is_consistent(entailment_checker)}")

    # Check if the belief base entails "It is not raining" (Success postulate)
    print("\nChecking the Success postulate:")
    print(f"Does the revised belief base entail 'It is not raining'? {entailment_checker.entails(revised_belief_base._get_conjunction(), Not(p))}")

    print("\nDemonstration complete.")


if __name__ == "__main__":
    main()