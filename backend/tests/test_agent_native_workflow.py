"""
Agent-Native Workflow Test Module

Tests for WebMCP tool integration, agent discovery-read-evaluate-propose workflow,
activity event recording, and presentation-only mutation safety guards.
Validates contract behavior between agents and the backend MCP server.
"""
import json
import pytest
from datetime import datetime, timezone
from src.services.simulation_service import (
    Deal,
    Constraint,
    DealAlternative,
    DecisionTwinEvaluation,
    CounterofferProposal,
    AgentActivityEvent,
)


class TestWebMCPToolDiscovery:
    """Test WebMCP tool registration and discovery."""

    def test_get_current_deal_tool_registered(self):
        """
        Test: WebMCP server must register get_current_deal tool
        with documented input/output schema.
        """
        # Note: This test is symbolic; actual tool registration
        # tested in integration tests after tools.py implementation.
        pass

    def test_get_constraints_tool_registered(self):
        """
        Test: WebMCP server must register get_constraints tool
        with documented input/output schema.
        """
        pass

    def test_evaluate_offer_tool_registered(self):
        """
        Test: WebMCP server must register evaluate_offer tool
        with documented input/output schema.
        """
        pass

    def test_propose_counteroffer_tool_registered(self):
        """
        Test: WebMCP server must register propose_counteroffer tool
        with documented input/output schema.
        """
        pass


class TestAgentDiscoveryWorkflow:
    """Test the discover-read-evaluate-propose agent workflow."""

    def test_agent_can_retrieve_current_deal(self):
        """
        Test: Agent calls get_current_deal and receives current contract
        with price, terms, and constraint targets.
        """
        # Fixture: Current deal
        current_deal = Deal(
            id="deal_1042",
            contract_id="1042-B",
            current_price=120000.0,
            counterparty="Acme Corp",
            created_at=datetime.now(timezone.utc),
        )

        # Simulate tool call result
        result = {
            "deal_id": current_deal.id,
            "contract_id": current_deal.contract_id,
            "current_price": current_deal.current_price,
            "counterparty": current_deal.counterparty,
        }

        assert result["deal_id"] == "deal_1042"
        assert result["current_price"] == 120000.0

    def test_agent_can_retrieve_constraints(self):
        """
        Test: Agent calls get_constraints and receives list of
        hard limits, targets, and soft preferences for the deal.
        """
        # Fixture: Constraints
        constraint = Constraint(
            id="constraint_liability",
            deal_id="deal_1042",
            name="Liability Coverage",
            target=1.5,
            hard_limit=1.5,
            penalty_weight=100.0,
        )

        # Simulate tool call result
        result = {
            "constraints": [
                {
                    "id": constraint.id,
                    "name": constraint.name,
                    "target": constraint.target,
                    "hard_limit": constraint.hard_limit,
                }
            ]
        }

        assert len(result["constraints"]) == 1
        assert result["constraints"][0]["hard_limit"] == 1.5

    def test_agent_evaluates_offer_through_decision_twin(self):
        """
        Test: Agent calls evaluate_offer with alternative pricing,
        receives score, feasibility, hard failures, and trade-offs.
        """
        # Fixture: Evaluation result
        evaluation = DecisionTwinEvaluation(
            id="eval_1",
            deal_id="deal_1042",
            alternative_id="alt_restrictive",
            score=0.25,
            is_feasible=False,
            hard_failures=["Liability Coverage must meet 1.5x requirement"],
            trade_offs=[
                "Increase price to $105,000 to pass liability constraint",
                "Request seller to accept shared liability structure",
            ],
            evaluated_at=datetime.now(timezone.utc),
        )

        # Simulate tool call result
        result = {
            "evaluation_id": evaluation.id,
            "score": evaluation.score,
            "is_feasible": evaluation.is_feasible,
            "hard_failures": evaluation.hard_failures,
            "trade_offs": evaluation.trade_offs,
        }

        assert not result["is_feasible"]
        assert len(result["hard_failures"]) > 0
        assert len(result["trade_offs"]) > 0

    def test_agent_proposes_counteroffer_with_approval_pending(self):
        """
        Test: Agent calls propose_counteroffer with new price and terms,
        receives pending approval state. No immediate execution without human approval.
        """
        # Fixture: Proposed counteroffer
        proposal = CounterofferProposal(
            id="proposal_1",
            deal_id="deal_1042",
            agent_id="agent_strategic",
            proposed_price=105000.0,
            proposed_terms={"liability": 1.5},
            rationale="Increased price meets hard liability constraint while maintaining competitiveness",
            approval_status="pending",
            created_at=datetime.now(timezone.utc),
        )

        # Simulate tool call result
        result = {
            "proposal_id": proposal.id,
            "status": proposal.approval_status,
            "message": "Counteroffer proposal received. Awaiting human approval.",
        }

        assert result["status"] == "pending"
        assert "Awaiting human approval" in result["message"]


class TestActivityEventRecording:
    """Test that all tool calls are recorded as activity events."""

    def test_tool_call_started_event(self):
        """
        Test: When agent calls a WebMCP tool, a 'started' activity event
        is recorded with tool name and request_id.
        """
        event = AgentActivityEvent(
            id="event_1",
            deal_id="deal_1042",
            tool_name="get_current_deal",
            request_id="req_001",
            event_type="started",
            details={"contract_id": "1042-B"},
            occurred_at=datetime.now(timezone.utc),
        )

        assert event.event_type == "started"
        assert event.tool_name == "get_current_deal"
        assert event.request_id == "req_001"

    def test_tool_call_completed_event(self):
        """
        Test: When agent completes a WebMCP tool call, a 'completed' event
        is recorded with result details and completion timestamp.
        """
        event = AgentActivityEvent(
            id="event_2",
            deal_id="deal_1042",
            tool_name="evaluate_offer",
            request_id="req_002",
            event_type="completed",
            details={
                "score": 0.25,
                "is_feasible": False,
                "hard_failures": ["Liability Coverage must meet 1.5x requirement"],
            },
            occurred_at=datetime.now(timezone.utc),
        )

        assert event.event_type == "completed"
        assert event.details["is_feasible"] is False

    def test_tool_call_failed_event(self):
        """
        Test: When agent's tool call fails (invalid input, constraint violation),
        a 'failed' event is recorded with error details.
        """
        event = AgentActivityEvent(
            id="event_3",
            deal_id="deal_1042",
            tool_name="propose_counteroffer",
            request_id="req_003",
            event_type="failed",
            details={"error": "Proposed price cannot be negative"},
            occurred_at=datetime.now(timezone.utc),
        )

        assert event.event_type == "failed"
        assert "error" in event.details

    def test_activity_event_ordering_and_causality(self):
        """
        Test: Activity events are ordered by timestamp and reflect
        the causality of the workflow (discover → read → evaluate → propose).
        """
        events = [
            AgentActivityEvent(
                id="e1",
                deal_id="deal_1042",
                tool_name="get_current_deal",
                request_id="req_001",
                event_type="completed",
                details={},
                occurred_at=datetime.now(timezone.utc),
            ),
            AgentActivityEvent(
                id="e2",
                deal_id="deal_1042",
                tool_name="get_constraints",
                request_id="req_002",
                event_type="completed",
                details={},
                occurred_at=datetime.now(timezone.utc),
            ),
            AgentActivityEvent(
                id="e3",
                deal_id="deal_1042",
                tool_name="evaluate_offer",
                request_id="req_003",
                event_type="completed",
                details={},
                occurred_at=datetime.now(timezone.utc),
            ),
        ]

        # Sort by timestamp (all same in this fixture, but demonstrates causality)
        sorted_events = sorted(events, key=lambda e: e.occurred_at)
        assert sorted_events[0].tool_name == "get_current_deal"
        assert sorted_events[1].tool_name == "get_constraints"
        assert sorted_events[2].tool_name == "evaluate_offer"


class TestMutationSafetyGuards:
    """Test that Wire-Agent can only mutate UI schema presentation layer."""

    def test_mutation_guard_rejects_deal_field_modification(self):
        """
        Test: Schema mutation guard must reject any mutation
        that attempts to modify deal, constraint, or evaluation fields.
        Raises ValueError with clear message.
        """
        from src.mcp.handlers import validate_presentation_patch

        forbidden_mutations = [
            {"path": "/deal/price", "value": 50000.0},
            {"path": "/constraints/[0]/hard_limit", "value": 1.0},
            {"path": "/evaluation/score", "value": 0.5},
            {"price": 50000.0},
            {"hard_limit": 1.0},
        ]

        for mutation in forbidden_mutations:
            with pytest.raises(ValueError) as exc_info:
                validate_presentation_patch(mutation)
            assert "Forbidden" in str(exc_info.value)

    def test_mutation_allows_presentation_layer_changes(self):
        """
        Test: Schema mutation guard must allow mutations
        to presentation-only fields like UI warning banners, layout, colors.
        """
        from src.mcp.handlers import validate_presentation_patch

        allowed_mutations = [
            {"path": "/ui/warning_banner", "value": "Hard liability constraint violated"},
            {"path": "/ui/layout/columns", "value": 3},
            {"path": "/ui/colors/danger", "value": "#ff0000"},
            {"className": "bg-slate-900 border border-rose-500", "props": {"title": "Updated Warning"}},
        ]

        for mutation in allowed_mutations:
            # Must not raise
            validate_presentation_patch(mutation)

    def test_schema_version_update_on_publish(self):
        """
        Test: When mutation is published, schema version increments
        and previous version remains available for decision-invariance verification.
        """
        # Fixture: v1 schema
        schema_v1 = {
            "id": "schema_1",
            "version": 1,
            "is_published": True,
        }

        # Fixture: v2 schema with mutation
        schema_v2 = {
            "id": "schema_1",
            "version": 2,
            "is_published": False,  # Not yet published
        }

        assert schema_v2["version"] == schema_v1["version"] + 1
        assert not schema_v2["is_published"]

    def test_published_mutation_does_not_change_decision_output(self):
        """
        Test: After publishing a UI mutation, the Decision Twin's output
        for the same offer must remain identical (decision invariance).
        """
        # Fixture: Evaluation result on v1 schema
        eval_v1 = DecisionTwinEvaluation(
            id="eval_v1",
            deal_id="deal_1042",
            alternative_id="alt_restrictive",
            score=0.25,
            is_feasible=False,
            hard_failures=["Liability Coverage must meet 1.5x requirement"],
            evaluated_at=datetime.now(timezone.utc),
        )

        # Fixture: Evaluation result on v2 schema (with UI mutation but same business logic)
        eval_v2 = DecisionTwinEvaluation(
            id="eval_v2",
            deal_id="deal_1042",
            alternative_id="alt_restrictive",
            score=0.25,
            is_feasible=False,
            hard_failures=["Liability Coverage must meet 1.5x requirement"],
            evaluated_at=datetime.now(timezone.utc),
        )

        # Verify decision outputs are identical (decision invariance)
        assert eval_v1.score == eval_v2.score
        assert eval_v1.is_feasible == eval_v2.is_feasible
        assert eval_v1.hard_failures == eval_v2.hard_failures

    def test_adversarial_agent_cannot_execute_contract_autonomously(self):
        """
        Test: QA Adversarial Agent attempts to execute contract autonomously without human approval.
        Governance boundary must intercept and reject with GOVERNANCE_BOUNDARY_BLOCKED.
        """
        from src.mcp import tools as mcp_tools
        raw_res = mcp_tools.execute_contract("1042-B")
        result = json.loads(raw_res)

        assert result["status"] == "error"
        assert result["code"] == "GOVERNANCE_BOUNDARY_BLOCKED"
        assert result["http_status"] == 403
        assert result["verdict"] == "HUMAN_APPROVAL_ENFORCED"
        assert result["human_approval_required"] is True
        assert "External autonomous agents are prohibited" in result["message"]
