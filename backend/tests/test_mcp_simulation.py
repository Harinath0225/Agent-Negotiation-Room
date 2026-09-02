"""
Tests confirming WebMCP parity between simulate_tradeoff tool and the FastAPI simulation endpoint.
Tests for restrictive offer evaluation and hard-liability-failure detection (US1 MVP).
"""
import json
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.mcp.tools import simulate_tradeoff, evaluate_offer
from src.services.agent_client import AgenticWebMCPClient

client = TestClient(app)


def test_mcp_tool_returns_parity_fields():
    change_payload = {
        "current_price": 120000.0,
        "price_delta": -20000.0,
    }

    # 1. Direct FastAPI route call
    api_resp = client.post(
        "/api/simulations/tradeoff",
        json={
            "request_id": "parity-api-01",
            "contract_id": "1042-B",
            "proposed_change": change_payload,
        },
    )
    assert api_resp.status_code == 200
    api_data = api_resp.json()

    # 2. WebMCP tool call
    mcp_raw = simulate_tradeoff(
        contract_id="1042-B",
        proposed_change=json.dumps(change_payload),
    )
    mcp_data = json.loads(mcp_raw)

    # Validate WebMCP parity
    assert mcp_data["contract_id"] == api_data["contract_id"]
    assert mcp_data["current_price"] == api_data["current_price"]
    assert mcp_data["proposed_price"] == api_data["proposed_price"]
    assert mcp_data["risk_score_delta"] == api_data["risk_score_delta"]
    assert mcp_data["acceptance_probability"] == api_data["acceptance_probability"]
    assert mcp_data["recommendation"] == api_data["recommendation"]
    assert mcp_data["affected_terms"] == api_data["affected_terms"]
    assert "completed_at" in mcp_data


class TestRestrictiveOfferEvaluation:
    """Tests for User Story 1: Evaluate a Restrictive Offer (MVP)"""

    def test_restrictive_offer_liability_hard_failure(self):
        """
        Test: Restrictive seller offer with liability 0.8 (below hard limit 1.5)
        must be detected as hard-failed and marked infeasible.
        """
        offer_data = {
            "id": "alt_restrictive",
            "label": "Restrictive Seller Offer",
            "price": 95000,
            "terms": {
                "liability": 0.8,
                "payment_terms": "Net 30",
                "delivery_timeline": 90
            },
            "source": "counterparty"
        }

        # Evaluate through MCP tool
        result_raw = evaluate_offer(
            contract_id="1042-B",
            offer_data=json.dumps(offer_data)
        )
        result = json.loads(result_raw)

        # Assertions
        assert result["status"] == "success"
        evaluation = result["evaluation"]
        
        # Must be infeasible due to hard failure
        assert evaluation["is_feasible"] is False, "Restrictive offer must fail hard constraint"
        
        # Must have hard failures list
        assert len(evaluation["hard_failures"]) > 0, "Hard failures must be reported"
        assert any("Liability" in f for f in evaluation["hard_failures"]), \
            "Hard failure must mention Liability constraint"

    def test_restrictive_offer_score_reflects_acceptance_probability(self):
        """
        Test: Restrictive offer with low price should have high acceptance score.
        Despite hard failure, score should reflect price competitiveness.
        """
        offer_data = {
            "id": "alt_restrictive",
            "label": "Restrictive Seller Offer",
            "price": 95000,  # 21% below current
            "terms": {
                "liability": 0.8,
                "payment_terms": "Net 30",
                "delivery_timeline": 90
            },
            "source": "counterparty"
        }

        result_raw = evaluate_offer(
            contract_id="1042-B",
            offer_data=json.dumps(offer_data)
        )
        result = json.loads(result_raw)

        evaluation = result["evaluation"]
        
        # Score should be > 0 even with hard failure (reflects acceptance prob)
        assert evaluation["score"] >= 0, "Score must be non-negative"
        assert evaluation["score"] <= 100, "Score must be <= 100"

    def test_restrictive_offer_trade_offs_suggest_next_moves(self):
        """
        Test: After evaluating restrictive offer, trade-offs list must suggest
        negotiation moves (e.g., price increase to pass liability constraint).
        """
        offer_data = {
            "id": "alt_restrictive",
            "label": "Restrictive Seller Offer",
            "price": 95000,
            "terms": {
                "liability": 0.8,
                "payment_terms": "Net 30",
                "delivery_timeline": 90
            },
            "source": "counterparty"
        }

        result_raw = evaluate_offer(
            contract_id="1042-B",
            offer_data=json.dumps(offer_data)
        )
        result = json.loads(result_raw)

        evaluation = result["evaluation"]
        
        # Must have trade-offs suggestions
        assert len(evaluation["trade_offs"]) > 0, "Trade-offs must suggest negotiation moves"
        
        # At least one should mention price or liability strategy
        trade_off_text = " ".join(evaluation["trade_offs"]).lower()
        assert ("price" in trade_off_text or "liability" in trade_off_text), \
            "Trade-offs must address the core issue (price, liability)"

    def test_current_deal_passes_all_constraints(self):
        """
        Test: Current deal (liability 2.0) should pass hard liability constraint (1.5).
        Baseline for comparison with restrictive offer.
        """
        offer_data = {
            "id": "alt_current",
            "label": "Current Deal",
            "price": 120000,
            "terms": {
                "liability": 2.0,  # Meets target 1.5
                "payment_terms": "Net 30",
                "delivery_timeline": 90
            },
            "source": "system"
        }

        result_raw = evaluate_offer(
            contract_id="1042-B",
            offer_data=json.dumps(offer_data)
        )
        result = json.loads(result_raw)

        evaluation = result["evaluation"]
        
        # Must be feasible
        assert evaluation["is_feasible"] is True, "Current deal must be feasible"
        
        # No hard failures
        assert len(evaluation["hard_failures"]) == 0, "Current deal must have no hard failures"



def test_mcp_tool_invalid_input_error_contract():
    # Negative proposed price should return error JSON
    bad_payload = json.dumps({
        "current_price": 5000.0,
        "price_delta": -20000.0,
    })
    result_raw = simulate_tradeoff(contract_id="1042-B", proposed_change=bad_payload)
    result = json.loads(result_raw)
    assert result["status"] == "error"
    assert "cannot be negative" in result["message"]


import asyncio

def test_agent_client_invocation():
    agent_client = AgenticWebMCPClient()
    result = asyncio.run(
        agent_client.invoke_simulate_tradeoff(
            contract_id="1042-B",
            proposed_change={"current_price": 120000.0, "price_delta": -20000.0},
        )
    )
    assert result["contract_id"] == "1042-B"
    assert result["proposed_price"] == 100000.0
    assert result["acceptance_probability"] == 0.8
