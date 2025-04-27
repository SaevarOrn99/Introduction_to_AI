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

    # Demonstrate belief revision using the Levi identity
    print("\nDemonstrating belief revision using the Levi identity:")
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

    # Demonstrate that the revision follows the Levi identity
    print("\nDemonstrating that revision follows the Levi identity:")
    print("Step 1: Contract by the negation of the formula (¬¬p = p)")
    contracted_by_not_not_p = contraction.contract(belief_base, p)
    print("After contracting by p:")
    print(contracted_by_not_not_p)

    print("\nStep 2: Expand with the formula (¬p)")
    expanded_with_not_p = expansion.expand(contracted_by_not_not_p, Not(p), priority=3)
    print("After expanding with ¬p:")
    print(expanded_with_not_p)

    print("\nCompare with direct revision:")
    print(revised_belief_base)

    # Check if they are equivalent (might differ in representation but should entail the same beliefs)
    direct_conjunction = revised_belief_base._get_conjunction()
    levi_conjunction = expanded_with_not_p._get_conjunction()

    direct_entails_levi = entailment_checker.entails(direct_conjunction, levi_conjunction)
    levi_entails_direct = entailment_checker.entails(levi_conjunction, direct_conjunction)

    print(f"\nDoes direct revision entail Levi-based revision? {direct_entails_levi}")
    print(f"Does Levi-based revision entail direct revision? {levi_entails_direct}")

    if direct_entails_levi and levi_entails_direct:
        print("\nConfirmed: The revision operator correctly implements the Levi identity.")
    else:
        print("\nWarning: The revision operator might not correctly implement the Levi identity.")

    print("\nDemonstration complete.")


if __name__ == "__main__":
    main()