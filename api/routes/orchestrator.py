"""
Orchestrator Route: Auto-routing and Multi-Agent Pipeline endpoints.
"""

from __future__ import annotations

from typing import List, Union
from fastapi import APIRouter, Request
from models.schemas import AgentResponse, PipelineRequest, QueryRequest

router = APIRouter()


@router.post("/", response_model=Union[AgentResponse, List[AgentResponse]])
async def smart_query(req: QueryRequest, request: Request):
    """
    Intelligent routing endpoint.
    If 'pipeline' is specified, runs the agents sequentially.
    Otherwise, auto-classifies query intent and executes the optimal agent.
    """
    orch = request.app.state.orchestrator
    if req.pipeline and len(req.pipeline) > 0:
        return await orch.run_pipeline(req.query, req.pipeline)
    return await orch.route(req.query)


@router.post("/pipeline", response_model=List[AgentResponse])
async def execute_pipeline(req: PipelineRequest, request: Request):
    """
    Explicit sequential multi-agent execution.
    Passes output context down the chain.
    """
    orch = request.app.state.orchestrator
    return await orch.run_pipeline(req.query, req.agents)
