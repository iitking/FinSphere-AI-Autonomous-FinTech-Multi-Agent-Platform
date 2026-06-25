"""
Regulatory Compliance Route.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from models.schemas import AgentResponse, ComplianceRequest

router = APIRouter()


@router.post("/", response_model=AgentResponse)
async def check_compliance(req: ComplianceRequest, request: Request):
    """
    Direct endpoint for Indian Regulatory Compliance Audit.
    """
    orch = request.app.state.orchestrator
    query = (
        f"Perform an institutional compliance audit against regulations ({req.regulation_context}) "
        f"in jurisdiction '{req.jurisdiction}' for the following document or operational policy:\n\n"
        f"{req.document_text}"
    )
    return await orch.agents["compliance"].run(query)
