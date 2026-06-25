"""
Fraud Detection Route.
"""

from __future__ import annotations

import json
from fastapi import APIRouter, Request
from models.schemas import AgentResponse, FraudRequest

router = APIRouter()


@router.post("/", response_model=AgentResponse)
async def detect_fraud(req: FraudRequest, request: Request):
    """
    Direct endpoint for Transaction Anomaly and Payment Fraud Detection.
    """
    orch = request.app.state.orchestrator
    raw_txns = [t.model_dump(mode="json") for t in req.transactions]
    txn_json = json.dumps(raw_txns, indent=2, default=str)

    query = f"Investigate these {len(req.transactions)} financial transactions for fraud vectors and anomalies:\n{txn_json}"
    context = {"transactions": raw_txns}

    return await orch.agents["fraud_detection"].run(query, context)
