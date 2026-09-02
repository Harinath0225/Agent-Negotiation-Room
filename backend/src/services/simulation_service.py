"""
Simulation service providing typed simulation boundaries, validation,
and Decision Twin orchestration.
"""
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

from ..twin.decision_logic import evaluate_tradeoff, evaluate_constraints, detect_hard_failures, generate_tradeoffs

logger = logging.getLogger("simulation_service")


# ============================================================================
# Core Deal and Constraint Models (Phase 2 Foundational)
# ============================================================================

class Constraint(BaseModel):
    """Hard and advisory constraints governing deal acceptability."""
    id: str = Field(..., min_length=1, description="Unique constraint ID")
    deal_id: str = Field(..., min_length=1, description="Associated deal ID")
    name: str = Field(..., min_length=1, description="Constraint name (e.g., 'Liability Coverage')")
    term: Optional[str] = Field(default=None, description="Material term being constrained")
    operator: Literal[">=", "<=", ">", "<", "==", "!="] = Field(
        default=">=", description="Comparison operator for constraint evaluation"
    )
    target: float = Field(..., description="Target value for the constraint")
    hard_limit: Optional[float] = Field(
        default=None, description="Hard limit; violation blocks approval. None means advisory only."
    )
    penalty_weight: float = Field(default=1.0, ge=0, description="Weight for soft-failure penalty")
    severity: Literal["hard", "advisory"] = Field(
        default="advisory", description="Constraint severity level"
    )
    message: Optional[str] = Field(
        default=None, description="User-facing message when constraint fails"
    )


class DealAlternative(BaseModel):
    """A deal alternative with complete terms (Current, Counter A, Counter B)."""
    id: str = Field(..., min_length=1, description="Unique alternative ID")
    label: str = Field(..., min_length=1, description="Label (Current Deal, Counter A, Counter B)")
    deal_id: str = Field(..., min_length=1, description="Associated deal ID")
    price: float = Field(..., ge=0, description="Proposed or current price")
    terms: Dict[str, Any] = Field(default_factory=dict, description="Complete material terms dict")
    source: Optional[str] = Field(
        default=None, description="Source of alternative (user, agent_id, system)"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Deal(BaseModel):
    """A deal with current terms and approval state."""
    id: str = Field(..., min_length=1, description="Unique deal ID")
    contract_id: str = Field(..., min_length=1, description="Business contract ID (e.g., '1042-B')")
    current_price: float = Field(..., ge=0, description="Current negotiated price")
    current_terms: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Current material terms"
    )
    targets: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Target terms (constraint targets)"
    )
    counterparty: str = Field(default="", description="Counterparty name")
    approval_state: Literal["draft", "pending", "approved", "rejected"] = Field(
        default="draft", description="Deal approval state"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConstraintResult(BaseModel):
    """Result of evaluating a single constraint against an alternative."""
    constraint_id: str
    constraint_name: str
    term: Optional[str] = None
    actual_value: Optional[float] = None
    target_value: float
    hard_limit: Optional[float] = None
    passed: bool
    explanation: str


class DecisionTwinEvaluation(BaseModel):
    """Complete evaluation result from Decision Twin for an alternative."""
    id: str = Field(..., min_length=1, description="Unique evaluation ID")
    deal_id: str = Field(..., min_length=1, description="Associated deal ID")
    alternative_id: str = Field(..., min_length=1, description="Evaluated alternative ID")
    score: float = Field(..., ge=0, le=100, description="Deterministic score 0-100")
    is_feasible: bool = Field(..., description="False when any hard constraint fails")
    constraint_results: List[ConstraintResult] = Field(
        default_factory=list, description="Outcome for every evaluated constraint"
    )
    hard_failures: List[str] = Field(
        default_factory=list, description="Hard-failure verdicts (term + limit + explanation)"
    )
    trade_offs: List[str] = Field(
        default_factory=list, description="Negotiation moves and trade-off recommendations"
    )
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CounterofferProposal(BaseModel):
    """Pending approval proposal from agent or human."""
    id: str = Field(..., min_length=1, description="Unique proposal ID")
    deal_id: str = Field(..., min_length=1, description="Associated deal ID")
    alternative_id: Optional[str] = Field(default="alt_proposed", description="Associated alternative ID")
    agent_id: Optional[str] = Field(default=None, description="Agent ID if agent-proposed")
    proposed_price: float = Field(..., ge=0, description="Proposed price in alternative")
    proposed_terms: Dict[str, Any] = Field(default_factory=dict, description="Proposed terms")
    rationale: str = Field(..., min_length=1, description="Proposal rationale")
    evaluation: Optional[DecisionTwinEvaluation] = Field(
        default=None, description="Decision Twin evaluation backing proposal"
    )
    approval_status: Literal["pending", "approved", "rejected", "invalid"] = Field(
        default="pending", description="Approval status"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentActivityEvent(BaseModel):
    """Activity event recording tool calls, evaluations, and approvals."""
    id: str = Field(..., min_length=1, description="Unique event ID")
    deal_id: str = Field(..., min_length=1, description="Associated deal ID")
    request_id: str = Field(..., min_length=1, description="Client-generated request ID")
    tool_name: str = Field(..., min_length=1, description="WebMCP tool name (or system stage)")
    stage: Optional[str] = Field(default=None, description="Workflow stage (discover, read, evaluate, propose, approve)")
    event_type: Literal["started", "completed", "failed"] = Field(..., description="Event status")
    details: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific result details")
    error: Optional[str] = Field(default=None, description="Error message if event_type == 'failed'")
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InterfaceMutation(BaseModel):
    """Schema mutation for presentation-layer changes only."""
    id: str = Field(..., min_length=1, description="Unique mutation ID")
    deal_id: str = Field(..., min_length=1, description="Associated deal ID")
    base_schema_version: int = Field(..., ge=1, description="Base schema version before mutation")
    patch: Dict[str, Any] = Field(..., description="Patch (presentation-layer fields only)")
    preview_layout: Optional[Dict[str, Any]] = Field(
        default=None, description="Rendered preview before publishing"
    )
    status: Literal["proposed", "previewed", "published", "rejected"] = Field(
        default="proposed", description="Mutation status"
    )
    published_version: Optional[int] = Field(default=None, description="Published schema version")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProposedChange(BaseModel):
    current_price: Optional[float] = Field(default=120000.0, ge=0)
    price_delta: Optional[float] = None
    proposed_price: Optional[float] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)


class SimulationRequest(BaseModel):
    request_id: str = Field(..., min_length=1, description="Unique client-generated identifier")
    contract_id: str = Field(..., min_length=1, description="Required, non-empty contract ID")
    proposed_change: ProposedChange = Field(..., description="Proposed change specification")

    @field_validator("contract_id")
    @classmethod
    def validate_contract_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("contract_id cannot be blank")
        return v.strip()


class SimulationOutcome(BaseModel):
    request_id: str
    contract_id: str
    current_price: float = Field(..., ge=0)
    proposed_price: float = Field(..., ge=0)
    risk_score_delta: float
    acceptance_probability: float = Field(..., ge=0.0, le=1.0)
    recommendation: str = Field(..., min_length=1)
    affected_terms: List[str] = Field(default_factory=lambda: ["Base Price"])
    completed_at: datetime


class SimulationErrorResponse(BaseModel):
    request_id: str
    detail: str


def resolve_proposed_price(change: ProposedChange) -> tuple[float, float]:
    """
    Resolves current_price and proposed_price from proposed_change payload.
    Raises ValueError on negative proposed price or missing pricing data.
    """
    current_price = change.current_price if change.current_price is not None else 120000.0

    if change.proposed_price is not None:
        proposed_price = float(change.proposed_price)
    elif change.price_delta is not None:
        proposed_price = current_price + float(change.price_delta)
    elif change.price is not None:
        # If price is small (< 1000 and not equal to zero), consider it delta, else absolute price
        if -1000 < change.price < 1000 and change.price != 0:
            proposed_price = current_price + float(change.price)
        else:
            proposed_price = float(change.price)
    else:
        raise ValueError("proposed_change must specify either price_delta or proposed_price")

    if proposed_price < 0:
        raise ValueError(f"Proposed price (${proposed_price:,.2f}) cannot be negative")

    return current_price, proposed_price


def build_recommendation(twin_result: Dict[str, Any], current_price: float, proposed_price: float) -> str:
    """
    Builds a concise, user-facing analytical recommendation from Decision Twin results.
    """
    commentary = twin_result.get("commentary")
    if commentary:
        return commentary

    price_diff = proposed_price - current_price
    if price_diff < 0:
        return f"Lowering price by ${abs(price_diff):,.2f} increases counterparty acceptance but elevates contract risk."
    elif price_diff > 0:
        return f"Raising price by ${price_diff:,.2f} improves margins and reduces risk, but lowers counterparty acceptance."
    return "Maintaining current price keeps baseline terms stable."


def run_tradeoff_simulation(request: SimulationRequest) -> SimulationOutcome:
    """
    Runs the Decision Twin tradeoff simulation and returns a validated SimulationOutcome.
    Handles error boundaries cleanly without leaking internal exceptions.
    """
    # Integration boundary: parse and resolve prices
    current_price, proposed_price = resolve_proposed_price(request.proposed_change)

    # Decision Twin analytical evaluation boundary
    try:
        twin_result = evaluate_tradeoff(
            contract_id=request.contract_id,
            current_price=current_price,
            proposed_price=proposed_price,
        )
    except Exception as exc:
        logger.error(
            f"[Decision Twin Error] request_id={request.request_id} contract_id={request.contract_id}: {exc}"
        )
        raise RuntimeError("Decision Twin calculation failed") from exc

    recommendation = build_recommendation(twin_result, current_price, proposed_price)

    outcome = SimulationOutcome(
        request_id=request.request_id,
        contract_id=request.contract_id,
        current_price=current_price,
        proposed_price=proposed_price,
        risk_score_delta=twin_result.get("risk_score_delta", 0.0),
        acceptance_probability=twin_result.get("acceptance_probability", 0.5),
        recommendation=recommendation,
        affected_terms=["Base Price"],
        completed_at=datetime.now(timezone.utc),
    )

    logger.info(
        f"[Simulation Succeeded] request_id={request.request_id} contract_id={request.contract_id} "
        f"proposed_price={proposed_price} acceptance_probability={outcome.acceptance_probability}"
    )

    return outcome


# ============================================================================
# Shared Evaluation Service (Phase 2 Foundational)
# ============================================================================

class EvaluationService:
    """
    Shared typed evaluation service that produces stable Decision Twin evaluations.
    All evaluators must route through this service to ensure consistent behavior.
    """

    @staticmethod
    def evaluate_alternative(
        alternative: DealAlternative,
        constraints: List[Constraint],
    ) -> DecisionTwinEvaluation:
        """
        Evaluate a single alternative against constraints.
        Returns a fully typed DecisionTwinEvaluation.
        """
        # Call Decision Twin
        twin_result = evaluate_constraints(alternative, constraints)
        
        # Convert to typed DecisionTwinEvaluation
        constraint_results = [
            ConstraintResult(**result) for result in twin_result.get("constraint_results", [])
        ]
        
        evaluation = DecisionTwinEvaluation(
            id=twin_result["id"],
            deal_id=twin_result["deal_id"],
            alternative_id=twin_result["alternative_id"],
            score=twin_result["score"],
            is_feasible=twin_result["is_feasible"],
            constraint_results=constraint_results,
            hard_failures=twin_result.get("hard_failures", []),
            trade_offs=twin_result.get("trade_offs", []),
            evaluated_at=twin_result["evaluated_at"],
        )
        
        logger.info(
            f"[Evaluation Complete] alternative={alternative.id} score={evaluation.score} "
            f"feasible={evaluation.is_feasible} hard_failures={len(evaluation.hard_failures)}"
        )
        
        return evaluation

    @staticmethod
    def compare_alternatives(
        alternatives: List[DealAlternative],
        constraints: List[Constraint],
    ) -> List[DecisionTwinEvaluation]:
        """
        Evaluate multiple alternatives for comparison.
        Returns list of evaluations in same order as input.
        """
        evaluations = []
        for alt in alternatives:
            evaluation = EvaluationService.evaluate_alternative(alt, constraints)
            evaluations.append(evaluation)
        
        logger.info(
            f"[Comparison Complete] alternatives={len(alternatives)} "
            f"feasible={sum(1 for e in evaluations if e.is_feasible)}"
        )
        
        return evaluations

    @staticmethod
    def validate_proposal(
        proposal: CounterofferProposal,
        constraints: List[Constraint],
    ) -> CounterofferProposal:
        """
        Validate a counteroffer proposal and attach evaluation.
        Sets approval_status to 'invalid' if proposal fails hard constraints.
        """
        # Create temporary alternative from proposal
        alternative = DealAlternative(
            id=proposal.alternative_id,
            label=f"Proposal {proposal.id}",
            deal_id=proposal.deal_id,
            price=proposal.proposed_price,
            terms=proposal.proposed_terms,
            source=proposal.agent_id,
        )
        
        # Evaluate
        evaluation = EvaluationService.evaluate_alternative(alternative, constraints)
        proposal.evaluation = evaluation
        
        # Set approval status based on feasibility
        if not evaluation.is_feasible:
            proposal.approval_status = "invalid"
            logger.warn(
                f"[Proposal Invalid] proposal={proposal.id} hard_failures={evaluation.hard_failures}"
            )
        else:
            logger.info(f"[Proposal Valid] proposal={proposal.id} score={evaluation.score}")
        
        return proposal
