"""
Portfolio Optimization Route.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from models.schemas import AgentResponse, PortfolioRequest

router = APIRouter()


@router.post("/", response_model=AgentResponse)
async def optimize_portfolio(req: PortfolioRequest, request: Request):
    """
    Direct endpoint for Portfolio Asset Allocation and Modern Portfolio Theory optimization.
    """
    orch = request.app.state.orchestrator
    assets_str = ", ".join(req.assets)
    query = (
        f"Design an optimal diversified portfolio for capital of ₹{req.capital_inr:,.0f} "
        f"with '{req.risk_tolerance}' risk profile over {req.horizon_years} years. "
        f"Candidate asset universe: {assets_str}."
    )
    return await orch.agents["portfolio"].run(query)
