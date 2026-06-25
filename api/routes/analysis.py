"""
Financial Analysis Route.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from models.schemas import AgentResponse, AnalysisRequest

router = APIRouter()


@router.post("/", response_model=AgentResponse)
async def analyze_stock(req: AnalysisRequest, request: Request):
    """
    Direct endpoint for Equity Research and Fundamental Financial Analysis.
    """
    orch = request.app.state.orchestrator
    query = (
        f"Perform in-depth financial analysis for ticker '{req.ticker}' over a {req.timeframe} investment horizon. "
        f"{'Include market sentiment and institutional flows.' if req.include_sentiment else ''}"
    )
    return await orch.agents["financial_analysis"].run(query)
