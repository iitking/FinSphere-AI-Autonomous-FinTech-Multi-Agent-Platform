"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "simulation_mode" in data


def test_config_endpoints():
    res = client.get("/api/v1/config/")
    assert res.status_code == 200
    data = res.json()
    assert data["base_currency"] == "INR"

    res_params = client.get("/api/v1/config/parameters")
    assert res_params.status_code == 200
    params = res_params.json()
    assert "economics" in params
    assert "risk_model_weights" in params


def test_smart_query_endpoint():
    res = client.post("/api/v1/query/", json={"query": "Analyze HDFC Bank stock fundamentals"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["agent"] == "financial_analysis"


def test_analysis_endpoint():
    res = client.post("/api/v1/analysis/", json={"ticker": "TATAMOTORS", "timeframe": "1Y"})
    assert res.status_code == 200
    data = res.json()
    assert data["agent"] == "financial_analysis"


def test_risk_endpoint():
    res = client.post("/api/v1/risk/", json={"asset_description": "High yield NBFC bond", "investor_profile": "moderate"})
    assert res.status_code == 200
    data = res.json()
    assert data["agent"] == "risk_assessment"


def test_portfolio_endpoint():
    res = client.post("/api/v1/portfolio/", json={"capital_inr": 2000000, "risk_tolerance": "moderate", "horizon_years": 5, "assets": ["Nifty 50", "G-Sec 10Y"]})
    assert res.status_code == 200
    data = res.json()
    assert data["agent"] == "portfolio"


def test_fraud_endpoint():
    payload = {
        "transactions": [
            {
                "transaction_id": "TXN_TEST_1",
                "amount_inr": 150000,
                "merchant": "Luxury Watch Co",
                "location": "Mumbai",
                "user_id": "U123",
                "channel": "UPI"
            }
        ]
    }
    res = client.post("/api/v1/fraud/", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["agent"] == "fraud_detection"


def test_compliance_endpoint():
    res = client.post("/api/v1/compliance/", json={"document_text": "Sample loan agreement without explicit DPDP user consent clause."})
    assert res.status_code == 200
    data = res.json()
    assert data["agent"] == "compliance"
