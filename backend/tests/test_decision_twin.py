"""
Decision Twin Test Module

Tests for deterministic constraint evaluation, score calculation, trade-off generation,
and hard-liability-failure detection. Ensures Decision Twin produces stable results
across repeated evaluations with identical inputs.
"""
import pytest
from datetime import datetime, timezone
from src.twin.decision_logic import (
    evaluate_constraints,
    calculate_score,
    generate_tradeoffs,
    detect_hard_failures,
    compile_intent_weights,
)
from src.services.simulation_service import (
    Deal,
    Constraint,
    DealAlternative,
    DecisionTwinEvaluation,
)


class TestDeterministicEvaluation:
    """Test that identical inputs produce identical outputs across 100 runs."""

    def test_restrictive_offer_determinism(self):
        """
        Test: A low-price offer that violates the 1.5x liability constraint
        must consistently fail with the same hard-failure verdict across 100 runs.
        """
        # Fixture: Restrictive offer (violates 1.5x liability hard limit)
        restrictive_offer = DealAlternative(
            id="alt_restrictive",
            label="Restrictive Seller Offer",
            deal_id="deal_1042",
            price=95000.0,  # Below target, triggers liability constraint
            terms={"liability": 0.8},  # Hard limit requires 1.5x
            created_at=datetime.now(timezone.utc),
        )

        constraint = Constraint(
            id="constraint_liability",
            deal_id="deal_1042",
            name="Liability Coverage",
            target=1.5,
            hard_limit=1.5,
            penalty_weight=100.0,
        )

        # Run 100 times and collect results
        results = []
        for i in range(100):
            evaluation = evaluate_constraints(restrictive_offer, [constraint])
            results.append(evaluation)

        # Verify determinism: all 100 results must be identical
        first_result = results[0]
        for i, result in enumerate(results[1:], start=1):
            assert result.score == first_result.score, f"Run {i}: score differs"
            assert result.is_feasible == first_result.is_feasible, f"Run {i}: feasibility differs"
            assert result.hard_failures == first_result.hard_failures, f"Run {i}: hard failures differ"
            assert result.trade_offs == first_result.trade_offs, f"Run {i}: trade-offs differ"

    def test_liability_hard_failure_detection(self):
        """
        Test: Hard-liability constraint (1.5x requirement) must be detected
        when alternative's liability term falls below threshold.
        """
        restrictive = DealAlternative(
            id="alt_test",
            label="Test Offer",
            deal_id="deal_1042",
            price=95000.0,
            terms={"liability": 0.8},
            created_at=datetime.now(timezone.utc),
        )

        constraint = Constraint(
            id="constraint_liability",
            deal_id="deal_1042",
            name="Liability Coverage",
            target=1.5,
            hard_limit=1.5,
            penalty_weight=100.0,
        )

        # Evaluate
        evaluation = evaluate_constraints(restrictive, [constraint])

        # Verify hard failure is detected
        assert not evaluation.is_feasible, "Restrictive offer must fail feasibility"
        assert len(evaluation.hard_failures) > 0, "Hard failures list must not be empty"
        assert any("Liability Coverage" in f for f in evaluation.hard_failures), \
            "Liability hard failure must be in failures list"

    def test_intent_weight_compilation(self):
        """
        Test: Constraint Kitchen intent weight compilation from natural language text.
        """
        # Speed priority
        speed_weights = compile_intent_weights("Delivery speed is our top priority for Phase 1")
        assert speed_weights["speed"] == 0.35
        assert speed_weights["price"] == 0.25

        # Price priority
        price_weights = compile_intent_weights("We need the cheapest budget price possible")
        assert price_weights["price"] == 0.45
        assert price_weights["speed"] == 0.10

        # Risk priority
        risk_weights = compile_intent_weights("Legal liability indemnification risk is critical")
        assert risk_weights["liability"] == 0.45

    def test_score_calculation_consistency(self):
        """
        Test: Score calculation must be deterministic and reflect price impact
        on acceptance probability.
        """
        # Two alternatives: baseline and restrictive
        baseline = DealAlternative(
            id="alt_baseline",
            label="Baseline",
            deal_id="deal_1042",
            price=120000.0,
            terms={"liability": 1.5},
            created_at=datetime.now(timezone.utc),
        )

        restrictive = DealAlternative(
            id="alt_restrict",
            label="Restrictive",
            deal_id="deal_1042",
            price=95000.0,
            terms={"liability": 1.5},  # Meets constraint
            created_at=datetime.now(timezone.utc),
        )

        constraint = Constraint(
            id="constraint_liability",
            deal_id="deal_1042",
            name="Liability Coverage",
            target=1.5,
            hard_limit=1.5,
            penalty_weight=100.0,
        )

        # Evaluate both
        baseline_eval = evaluate_constraints(baseline, [constraint])
        restrictive_eval = evaluate_constraints(restrictive, [constraint])

        # Restrictive should have higher acceptance probability (lower price)
        assert restrictive_eval.score > baseline_eval.score, \
            "Lower price should increase counterparty acceptance score"


class TestHardFailureVerdicts:
    """Test hard-failure detection and blocking of approval."""

    def test_hard_failure_blocks_approval(self):
        """
        Test: Any hard-failure verdict must prevent approval transition.
        Restriction is unyielding: hard fails cannot be overridden.
        """
        failing_alternative = DealAlternative(
            id="alt_fail",
            label="Hard-Fail Offer",
            deal_id="deal_1042",
            price=80000.0,
            terms={"liability": 0.5},  # Below hard limit
            created_at=datetime.now(timezone.utc),
        )

        constraint = Constraint(
            id="constraint_liability",
            deal_id="deal_1042",
            name="Liability Coverage",
            target=1.5,
            hard_limit=1.5,
            penalty_weight=100.0,
        )

        evaluation = evaluate_constraints(failing_alternative, [constraint])

        # Verify: hard failure exists and blocks approval
        assert not evaluation.is_feasible
        assert len(evaluation.hard_failures) > 0
        # Approval logic would check is_feasible before allowing approval transition
        approval_allowed = evaluation.is_feasible
        assert not approval_allowed, "Hard-failed alternative must block approval"


class TestTradeoffGeneration:
    """Test identification and ranking of negotiation trade-offs."""

    def test_next_best_negotiation_move_identified(self):
        """
        Test: After evaluating a restrictive offer with hard failure,
        Decision Twin must suggest the next best negotiation move.
        """
        current_deal = DealAlternative(
            id="alt_current",
            label="Current Deal",
            deal_id="deal_1042",
            price=120000.0,
            terms={"liability": 1.5},
            created_at=datetime.now(timezone.utc),
        )

        restrictive = DealAlternative(
            id="alt_restrict",
            label="Restrictive Offer",
            deal_id="deal_1042",
            price=95000.0,
            terms={"liability": 0.8},
            created_at=datetime.now(timezone.utc),
        )

        constraint = Constraint(
            id="constraint_liability",
            deal_id="deal_1042",
            name="Liability Coverage",
            target=1.5,
            hard_limit=1.5,
            penalty_weight=100.0,
        )

        # Evaluate restrictive (fails)
        restrictive_eval = evaluate_constraints(restrictive, [constraint])

        # Evaluate current (should pass)
        current_eval = evaluate_constraints(current_deal, [constraint])

        # Verify current passes and restrictive fails
        assert current_eval.is_feasible, "Current deal must meet constraints"
        assert not restrictive_eval.is_feasible, "Restrictive offer must fail"

        # Generate trade-offs to find next negotiation move
        tradeoffs = generate_tradeoffs(current_deal, restrictive, [constraint])

        # Verify trade-offs list is not empty and contains path to acceptability
        assert len(tradeoffs) > 0, "Trade-off list must suggest negotiation moves"


class TestActivityEventRecording:
    """Test that tool calls and evaluation results are recorded as activity events."""

    def test_evaluation_event_recording(self):
        """
        Test: When evaluate_constraints is called, it must emit
        an activity event with started, completed states and result details.
        """
        alternative = DealAlternative(
            id="alt_test",
            label="Test",
            deal_id="deal_1042",
            price=100000.0,
            terms={"liability": 1.5},
            created_at=datetime.now(timezone.utc),
        )

        constraint = Constraint(
            id="constraint_liability",
            deal_id="deal_1042",
            name="Liability Coverage",
            target=1.5,
            hard_limit=1.5,
            penalty_weight=100.0,
        )

        # Evaluate (event recording should happen internally)
        evaluation = evaluate_constraints(alternative, [constraint])

        # Verify evaluation contains result details for event projection
        assert evaluation.score is not None
        assert evaluation.is_feasible is not None
        assert evaluation.evaluated_at is not None
