"""
Unit tests for individual agents in simulation mode.
"""

import pytest
from agents.financial_analysis_agent import FinancialAnalysisAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from agents.portfolio_agent import PortfolioAgent
from agents.fraud_detection_agent import FraudDetectionAgent
from agents.compliance_agent import ComplianceAgent


@pytest.mark.asyncio
async def test_financial_analysis_agent():
    agent = FinancialAnalysisAgent()
    resp = await agent.run("Analyze HDFCBANK fundamentals over 1Y")
    assert resp.success
    assert resp.agent == "financial_analysis"
    assert "metrics" in resp.metadata
    assert resp.metadata["metrics"].get("pe_ratio") is not None


@pytest.mark.asyncio
async def test_risk_assessment_agent():
    agent = RiskAssessmentAgent()
    resp = await agent.run("Assess risk for unsecured retail loan book")
    assert resp.success
    assert resp.agent == "risk_assessment"
    assert "risk_score" in resp.metadata
    assert "breakdown" in resp.metadata


@pytest.mark.asyncio
async def test_portfolio_agent():
    agent = PortfolioAgent()
    resp = await agent.run("Allocate ₹50,00,000 for moderate risk appetite")
    assert resp.success
    assert resp.agent == "portfolio"
    assert "allocation" in resp.metadata
    assert len(resp.metadata["allocation"]) > 0


@pytest.mark.asyncio
async def test_fraud_detection_agent_heuristics():
    agent = FraudDetectionAgent()
    sample_txns = [
        {"transaction_id": "TXN_1", "amount_inr": 250000, "merchant": "Jewels", "location": "Delhi"},
    ]
    resp = await agent.run("Scan transactions", context={"transactions": sample_txns})
    assert resp.success
    assert resp.agent == "fraud_detection"
    assert "flagged_transactions" in resp.metadata
    assert len(resp.metadata["heuristic_preflags"]) > 0


@pytest.mark.asyncio
async def test_compliance_agent():
    agent = ComplianceAgent()
    resp = await agent.run("Digital lending app escrow payment mechanism")
    assert resp.success
    assert resp.agent == "compliance"
    assert "compliant" in resp.metadata
    assert "recommendations" in resp.metadata
