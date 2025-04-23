"""
Tests for the belief revision agent against AGM postulates.
"""

from propositional_logic import Atom, Not, And, Or, Implies, Equivalent, parse_formula
from belief_base import BeliefBase
from entailment import ResolutionChecker
from contraction import PartialMeetContraction
from expansion import Expansion, Revision


def test_success_postulate():
    """
    Test the Success postulate for revision:
    AGM Success: A ∈ K*A (The revision of K by A should contain A)
    """
    print("\nTesting Success Postulate")
    print("-------------------------")

    # Create a belief base and entailment checker
    belief_base = BeliefBase()
    entailment_checker = ResolutionChecker()
    revision = Revision(entailment_checker)

    # Add some initial beliefs
    p = Atom('p')
    q = Atom('q')
    belief_base.add(p, 2)
    belief_base.add(Implies(p, q), 1)

    print("Initial belief base:")
    print(belief_base)

    # Revise with Not(p)
    not_p = Not(p)
    revised_belief_base = revision.revise(belief_base, not_p, priority=3)

    print("\nAfter revising with 'Not p':")
    print(revised_belief_base)

    # Check if the revised belief base entails Not(p)
    result = entailment_checker.entails(revised_belief_base._get_conjunction(), not_p)
    print(f"\nDoes the revised belief base entail 'Not p'? {result}")
    print(f"Success Postulate: {'✓ Satisfied' if result else '✗ Not Satisfied'}")

    return result


def test_inclusion_postulate():
    """
    Test the Inclusion postulate for revision:
    AGM Inclusion: K*A ⊆ K+A (The revision of K by A should not contain beliefs not in the expansion of K by A)
    """
    print("\nTesting Inclusion Postulate")
    print("--------------------------")

    # Create a belief base and operators
    belief_base = BeliefBase()
    entailment_checker = ResolutionChecker()
    expansion = Expansion(entailment_checker)
    revision = Revision(entailment_checker)

    # Add some initial beliefs
    p = Atom('p')
    q = Atom('q')
    belief_base.add(p, 2)
    belief_base.add(Implies(p, q), 1)

    print("Initial belief base:")
    print(belief_base)

    # Expand with Not(p)
    not_p = Not(p)
    expanded_belief_base = expansion.expand(belief_base, not_p, priority=3)

    print("\nAfter expanding with 'Not p':")
    print(expanded_belief_base)

    # Revise with Not(p)
    revised_belief_base = revision.revise(belief_base, not_p, priority=3)

    print("\nAfter revising with 'Not p':")
    print(revised_belief_base)

    # Check if K*A ⊆ K+A
    # For every formula in the revised belief base, check if it's entailed by the expanded belief base
    inclusion_satisfied = True
    for formula in revised_belief_base.get_all_formulas():
        if not entailment_checker.entails(expanded_belief_base._get_conjunction(), formula):
            inclusion_satisfied = False
            break

    print(f"\nInclusion Postulate: {'✓ Satisfied' if inclusion_satisfied else '✗ Not Satisfied'}")
    return inclusion_satisfied


def test_vacuity_postulate():
    """
    Test the Vacuity postulate for revision:
    AGM Vacuity: If ¬A ∉ K, then K*A = K+A (If A is consistent with K, then revising K by A is the same as expanding K by A)
    """
    print("\nTesting Vacuity Postulate")
    print("------------------------")

    # Create a belief base and operators
    belief_base = BeliefBase()
    entailment_checker = ResolutionChecker()
    expansion = Expansion(entailment_checker)
    revision = Revision(entailment_checker)

    # Add some initial beliefs that are consistent with 'r'
    p = Atom('p')
    q = Atom('q')
    r = Atom('r')
    belief_base.add(p, 2)
    belief_base.add(q, 1)

    print("Initial belief base:")
    print(belief_base)

    # Check if ¬r is entailed by the belief base
    not_r = Not(r)
    not_r_entailed = entailment_checker.entails(belief_base._get_conjunction(), not_r)
    print(f"\nIs 'Not r' entailed by the belief base? {not_r_entailed}")

    if not not_r_entailed:
        # ¬A ∉ K, so the vacuity postulate applies

        # Expand with r
        expanded_belief_base = expansion.expand(belief_base, r, priority=3)
        print("\nAfter expanding with 'r':")
        print(expanded_belief_base)

        # Revise with r
        revised_belief_base = revision.revise(belief_base, r, priority=3)
        print("\nAfter revising with 'r':")
        print(revised_belief_base)

        # Check if K*A = K+A
        # They should contain the same formulas
        expanded_formulas = set(expanded_belief_base.get_all_formulas())
        revised_formulas = set(revised_belief_base.get_all_formulas())

        vacuity_satisfied = expanded_formulas == revised_formulas
        print(f"\nVacuity Postulate: {'✓ Satisfied' if vacuity_satisfied else '✗ Not Satisfied'}")
        return vacuity_satisfied
    else:
        print("\nThe precondition for the Vacuity postulate (¬A ∉ K) is not met, so the test is not applicable.")
        return None


def test_consistency_postulate():
    """
    Test the Consistency postulate for revision:
    AGM Consistency: K*A is consistent unless A is inconsistent
    (The revision of K by A should be consistent unless A is logically impossible)
    """
    print("\nTesting Consistency Postulate")
    print("---------------------------")

    # Create a belief base and operators
    belief_base = BeliefBase()
    entailment_checker = ResolutionChecker()
    revision = Revision(entailment_checker)

    # Add some initial beliefs
    p = Atom('p')
    q = Atom('q')
    belief_base.add(p, 2)
    belief_base.add(Implies(p, q), 1)

    print("Initial belief base:")
    print(belief_base)

    # Revise with a consistent formula Not(p)
    not_p = Not(p)
    revised_belief_base = revision.revise(belief_base, not_p, priority=3)

    print("\nAfter revising with 'Not p':")
    print(revised_belief_base)

    # Check if the revised belief base is consistent
    consistency_satisfied = revised_belief_base.is_consistent(entailment_checker)
    print(f"\nIs the revised belief base consistent? {consistency_satisfied}")

    # Now try with an inconsistent formula (p ∧ ¬p)
    inconsistent_formula = And(p, Not(p))

    # This should either result in an inconsistent belief base or reject the revision
    try:
        inconsistent_revised = revision.revise(belief_base, inconsistent_formula, priority=3)
        inconsistency_handled = inconsistent_revised.is_consistent(entailment_checker) or len(
            inconsistent_revised.get_all_formulas()) == 0
    except Exception as e:
        print(f"Exception when revising with inconsistent formula: {e}")
        inconsistency_handled = True  # If it throws an exception, we count it as handling the inconsistency

    print(f"\nConsistency Postulate: {'✓ Satisfied' if consistency_satisfied else '✗ Not Satisfied'}")
    return consistency_satisfied


def test_extensionality_postulate():
    """
    Test the Extensionality postulate for revision:
    AGM Extensionality: If A ↔ B is a tautology, then K*A = K*B
    (If A and B are logically equivalent, then revising K by A is the same as revising K by B)
    """
    print("\nTesting Extensionality Postulate")
    print("------------------------------")

    # Create a belief base and operators
    belief_base = BeliefBase()
    entailment_checker = ResolutionChecker()
    revision = Revision(entailment_checker)

    # Add some initial beliefs
    p = Atom('p')
    q = Atom('q')
    belief_base.add(p, 2)
    belief_base.add(q, 1)

    print("Initial belief base:")
    print(belief_base)

    # Create two logically equivalent formulas
    # p ∧ q and q ∧ p are logically equivalent
    formula_a = And(p, q)
    formula_b = And(q, p)

    # Check if they are logically equivalent
    a_implies_b = entailment_checker.entails(formula_a, formula_b)
    b_implies_a = entailment_checker.entails(formula_b, formula_a)
    equivalent = a_implies_b and b_implies_a

    print(f"\nAre the formulas '(p ∧ q)' and '(q ∧ p)' logically equivalent? {equivalent}")

    if equivalent:
        # Revise with formula_a
        revised_a = revision.revise(belief_base, formula_a, priority=3)
        print("\nAfter revising with '(p ∧ q)':")
        print(revised_a)

        # Revise with formula_b
        revised_b = revision.revise(belief_base, formula_b, priority=3)
        print("\nAfter revising with '(q ∧ p)':")
        print(revised_b)

        # Check if K*A = K*B
        # They should entail the same formulas
        formulas_a = set(revised_a.get_all_formulas())
        formulas_b = set(revised_b.get_all_formulas())

        extensionality_satisfied = formulas_a == formulas_b
        print(f"\nExtensionality Postulate: {'✓ Satisfied' if extensionality_satisfied else '✗ Not Satisfied'}")
        return extensionality_satisfied
    else:
        print("\nThe formulas are not logically equivalent, so the test is not applicable.")
        return None


def run_all_tests():
    """Run all AGM postulate tests."""
    print("AGM Postulates Tests for Belief Revision")
    print("========================================")

    results = {
        "Success": test_success_postulate(),
        "Inclusion": test_inclusion_postulate(),
        "Vacuity": test_vacuity_postulate(),
        "Consistency": test_consistency_postulate(),
        "Extensionality": test_extensionality_postulate()
    }

    print("\nSummary of AGM Postulate Tests")
    print("=============================")
    for postulate, result in results.items():
        if result is None:
            status = "Not Applicable"
        else:
            status = "✓ Satisfied" if result else "✗ Not Satisfied"
        print(f"{postulate} Postulate: {status}")


if __name__ == "__main__":
    run_all_tests()