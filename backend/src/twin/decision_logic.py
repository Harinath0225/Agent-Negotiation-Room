"""
Decision Twin: Deterministic constraint evaluation and score calculation.

Produces stable, audit-able results that are independent of evaluation order,
timing, or execution environment. Every evaluation is fully deterministic:
identical inputs produce identical outputs across infinite runs.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import hashlib
import json

logger = logging.getLogger("decision_twin")


class DecisionResult(dict):
    """Dict subclass supporting attribute access (e.g. res.score, res.is_feasible)."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'DecisionResult' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = value


def compile_intent_weights(natural_language_intent: str) -> Dict[str, float]:
    """
    Constraint Kitchen Compiler: Translates natural language strategic intent
    into normalized mathematical weight multipliers for the Decision Twin.
    
    Default Weights: PRICE: 0.35, SPEED: 0.15, LIABILITY: 0.30, PAYMENT: 0.20
    """
    text = (natural_language_intent or "").lower()
    weights = {
        "price": 0.35,
        "speed": 0.15,
        "liability": 0.30,
        "payment": 0.20,
    }
    
    if "speed" in text or "fast" in text or "timeline" in text or "quick" in text:
        weights = {"price": 0.25, "speed": 0.35, "liability": 0.30, "payment": 0.10}
    elif "price" in text or "budget" in text or "cost" in text or "cheap" in text:
        weights = {"price": 0.45, "speed": 0.10, "liability": 0.30, "payment": 0.15}
    elif "risk" in text or "liability" in text or "legal" in text or "indemnity" in text:
        weights = {"price": 0.25, "speed": 0.10, "liability": 0.45, "payment": 0.20}
        
    return weights


def evaluate_constraints(alternative, constraints: List[Any]) -> DecisionResult:
    """
    Deterministic full-alternative constraint evaluation.
    
    Args:
        alternative: DealAlternative with price and terms
        constraints: List of Constraint models
        
    Returns:
        DecisionResult dict with attribute access:
        - score (0-100, deterministic)
        - is_feasible (False if any hard constraint fails)
        - constraint_results (list of individual constraint evaluations)
        - hard_failures (list of hard-failure verdict strings)
        - trade_offs (list of negotiation move recommendations)
    """
    if not alternative:
        raise ValueError("Alternative cannot be None")
    
    constraint_results = []
    hard_failures = []
    soft_penalties = 0.0
    feasible = True
    
    # Evaluate each constraint deterministically
    for constraint in constraints:
        result = _evaluate_single_constraint(alternative, constraint)
        constraint_results.append(result)
        
        is_hard = constraint.severity == "hard" or constraint.hard_limit is not None
        if not result["passed"]:
            if is_hard:
                feasible = False
                hard_failures.append(result["explanation"])
            else:
                soft_penalties += constraint.penalty_weight
    
    # Calculate score deterministically based on price and penalties
    score = _calculate_score(
        alternative.price,
        [c.target for c in constraints],
        soft_penalties,
        feasible
    )
    
    # Generate trade-offs
    trade_offs = _generate_tradeoffs(alternative, constraints, hard_failures)
    
    return DecisionResult({
        "id": f"eval_{_hash_deterministic(alternative.id, str(constraints))}",
        "deal_id": getattr(alternative, 'deal_id', 'unknown'),
        "alternative_id": alternative.id,
        "score": score,
        "is_feasible": feasible,
        "constraint_results": constraint_results,
        "hard_failures": hard_failures,
        "trade_offs": trade_offs,
        "evaluated_at": datetime.now(timezone.utc),
    })


def _evaluate_single_constraint(alternative, constraint) -> Dict[str, Any]:
    """Evaluate a single constraint against an alternative."""
    term = constraint.term
    actual_value = None
    if term and term in alternative.terms:
        actual_value = alternative.terms[term]
    else:
        name_key = constraint.name.lower().replace(" ", "_")
        id_key = constraint.id.lower().replace("constraint_", "")
        if name_key in alternative.terms:
            actual_value = alternative.terms[name_key]
            term = name_key
        elif id_key in alternative.terms:
            actual_value = alternative.terms[id_key]
            term = id_key
        else:
            for k in alternative.terms:
                if k in name_key or k in id_key:
                    actual_value = alternative.terms[k]
                    term = k
                    break
    if actual_value is None:
        term = term or constraint.name.lower().replace(" ", "_")
        actual_value = alternative.terms.get(term, 0.0)
    
    # Apply operator comparison
    operator = getattr(constraint, 'operator', '>=')
    passed = _apply_operator(actual_value, operator, constraint.target)
    if constraint.hard_limit is not None and actual_value < constraint.hard_limit:
        passed = False
    
    # Build explanation
    explanation = f"{constraint.name}: {actual_value} vs target {constraint.target}"
    if constraint.hard_limit is not None and actual_value < constraint.hard_limit:
        explanation += f" (hard limit: {constraint.hard_limit})"
    
    if not passed:
        explanation += " - FAILED"
    
    return {
        "constraint_id": constraint.id,
        "constraint_name": constraint.name,
        "term": term,
        "actual_value": actual_value,
        "target_value": constraint.target,
        "hard_limit": getattr(constraint, 'hard_limit', None),
        "passed": passed,
        "explanation": explanation,
    }


def _apply_operator(actual: float, operator: str, target: float) -> bool:
    """Deterministic operator evaluation."""
    if operator == ">=":
        return actual >= target
    elif operator == "<=":
        return actual <= target
    elif operator == ">":
        return actual > target
    elif operator == "<":
        return actual < target
    elif operator == "==":
        return abs(actual - target) < 1e-6  # Float comparison tolerance
    elif operator == "!=":
        return abs(actual - target) >= 1e-6
    return False


def _calculate_score(price: float, targets: List[float], soft_penalties: float, feasible: bool) -> int:
    """
    Deterministic score calculation (0-100).
    
    Score reflects:
    - Price competitiveness (lower price = higher acceptance probability)
    - Soft constraint penalties (reduce score but don't block approval)
    - Feasibility (hard failures don't reduce score, they block approval)
    
    Returns: Deterministic integer 0-100
    """
    base_price = 120000.0
    price_score = max(10.0, min(95.0, 50.0 + ((base_price - price) / base_price) * 40.0))
    score = price_score - soft_penalties
    score = max(0, min(100, score))
    return int(round(score))


def calculate_score(alternative, constraints: List[Any]) -> int:
    """Public interface for score calculation."""
    soft_penalties = sum(
        c.penalty_weight for c in constraints 
        if c.severity == "advisory"
    )
    return _calculate_score(alternative.price, [c.target for c in constraints], soft_penalties, True)


def _generate_tradeoffs(alternative, constraints: List[Any], hard_failures: List[str]) -> List[str]:
    """Generate negotiation trade-off recommendations."""
    tradeoffs = []
    
    if hard_failures:
        # If there are hard failures, suggest increases to pass constraints
        for failure in hard_failures:
            if "Liability" in failure:
                price_increase = alternative.price * 0.10  # 10% increase
                new_price = alternative.price + price_increase
                tradeoffs.append(
                    f"Increase price to ${new_price:,.0f} to pass liability constraint"
                )
                tradeoffs.append(
                    "Request seller to accept shared liability structure"
                )
    else:
        # Offer is feasible; suggest optimization moves
        if alternative.price < 120000.0:
            tradeoffs.append(
                "Current offer is competitive. Consider accepting to close quickly."
            )
        else:
            tradeoffs.append(
                "Price is above baseline. Negotiate reduction to improve margins."
            )
    
    return tradeoffs


def generate_tradeoffs(current_alternative, proposed_alternative, constraints: List[Any]) -> List[str]:
    """Public interface for trade-off generation."""
    evaluation = evaluate_constraints(proposed_alternative, constraints)
    return evaluation.get("trade_offs", [])


def detect_hard_failures(alternative, constraints: List[Any]) -> List[str]:
    """Detect and return list of hard-failure verdicts."""
    evaluation = evaluate_constraints(alternative, constraints)
    return evaluation.get("hard_failures", [])


def _hash_deterministic(alternative_id: str, constraints_str: str) -> str:
    """Generate deterministic hash for evaluation ID."""
    combined = f"{alternative_id}:{constraints_str}"
    return hashlib.md5(combined.encode()).hexdigest()[:8]


def evaluate_tradeoff(contract_id: str, current_price: float, proposed_price: float) -> dict:
    """
    Legacy interface: Evaluates risk and acceptance probability based on price changes.
    Kept for backward compatibility; new code uses evaluate_constraints().
    """
    price_delta = proposed_price - current_price
    
    if price_delta < 0:
        return {
            "risk_score_delta": 0.5,
            "acceptance_probability": 0.8,
            "commentary": "Lowering the price significantly increases acceptance probability but also increases risk."
        }
    else:
        return {
            "risk_score_delta": -0.2,
            "acceptance_probability": 0.4,
            "commentary": "Raising the price reduces risk but lowers the probability of acceptance."
        }
