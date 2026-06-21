"""Tests for agents."""
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
