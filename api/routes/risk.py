"""
Risk Assessment Route.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from models.schemas import AgentResponse, RiskRequest

router = APIRouter()


@router.post("/", response_model=AgentResponse)
async def assess_risk(req: RiskRequest, request: Request):
    """
    Direct endpoint for Quantitative & Regulatory Risk Assessment.
    """
    orch = request.app.state.orchestrator
    scale_text = f" Portfolio scale: ₹{req.portfolio_size_inr:,.0f}." if req.portfolio_size_inr else ""
    query = (
        f"Conduct 5-dimension risk evaluation for asset '{req.asset_description}'. "
        f"Investor risk tolerance profile is '{req.investor_profile}'.{scale_text}"
    )
    return await orch.agents["risk_assessment"].run(query)
