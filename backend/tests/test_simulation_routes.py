"""
Tests for simulation service and FastAPI simulation routes.
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from src.main import app
from src.services.simulation_service import (
    SimulationRequest,
    ProposedChange,
    resolve_proposed_price,
    build_recommendation,
    run_tradeoff_simulation,
)

client = TestClient(app)


def test_resolve_proposed_price_with_delta():
    change = ProposedChange(current_price=120000.0, price_delta=-20000.0)
    current, proposed = resolve_proposed_price(change)
    assert current == 120000.0
    assert proposed == 100000.0


def test_resolve_proposed_price_with_absolute_price():
    change = ProposedChange(current_price=120000.0, proposed_price=110000.0)
    current, proposed = resolve_proposed_price(change)
    assert current == 120000.0
    assert proposed == 110000.0


def test_resolve_proposed_price_negative_error():
    change = ProposedChange(current_price=5000.0, price_delta=-10000.0)
    with pytest.raises(ValueError, match="cannot be negative"):
        resolve_proposed_price(change)


def test_simulation_service_run_success():
    req = SimulationRequest(
        request_id="test-req-001",
        contract_id="1042-B",
        proposed_change=ProposedChange(current_price=120000.0, price_delta=-20000.0),
    )
    outcome = run_tradeoff_simulation(req)
    assert outcome.request_id == "test-req-001"
    assert outcome.contract_id == "1042-B"
    assert outcome.current_price == 120000.0
    assert outcome.proposed_price == 100000.0
    assert outcome.risk_score_delta == 0.5
    assert outcome.acceptance_probability == 0.8
    assert "Lowering the price" in outcome.recommendation
    assert outcome.affected_terms == ["Base Price"]
    assert outcome.completed_at is not None


def test_api_tradeoff_success():
    response = client.post(
        "/api/simulations/tradeoff",
        json={
            "request_id": "sim-test-200",
            "contract_id": "1042-B",
            "proposed_change": {
                "current_price": 120000.0,
                "price_delta": -20000.0,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "sim-test-200"
    assert data["contract_id"] == "1042-B"
    assert data["current_price"] == 120000.0
    assert data["proposed_price"] == 100000.0
    assert data["risk_score_delta"] == 0.5
    assert data["acceptance_probability"] == 0.8
    assert data["affected_terms"] == ["Base Price"]
    assert "completed_at" in data
    assert "recommendation" in data


def test_api_tradeoff_blank_contract_id_error():
    response = client.post(
        "/api/simulations/tradeoff",
        json={
            "request_id": "sim-test-blank",
            "contract_id": "   ",
            "proposed_change": {
                "current_price": 120000.0,
                "price_delta": -20000.0,
            },
        },
    )
    assert response.status_code == 422


def test_api_tradeoff_negative_price_error():
    response = client.post(
        "/api/simulations/tradeoff",
        json={
            "request_id": "sim-test-neg",
            "contract_id": "1042-B",
            "proposed_change": {
                "current_price": 10000.0,
                "price_delta": -50000.0,
            },
        },
    )
    assert response.status_code == 422
    assert "cannot be negative" in response.text


def test_api_tradeoff_server_failure():
    with patch(
        "src.api.simulation_routes.run_tradeoff_simulation",
        side_effect=Exception("Database or twin connection broke"),
    ):
        response = client.post(
            "/api/simulations/tradeoff",
            json={
                "request_id": "sim-test-500",
                "contract_id": "1042-B",
                "proposed_change": {
                    "current_price": 120000.0,
                    "price_delta": -20000.0,
                },
            },
        )
        assert response.status_code == 500
        data = response.json()
        assert data["request_id"] == "sim-test-500"
        assert "The tradeoff simulation could not be completed. Try again." in data["detail"]
