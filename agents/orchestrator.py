"""
Orchestrator: Autonomous Agent Routing & Pipeline Management.
Routes queries intelligently based on semantic and keyword scoring,
executes multi-agent sequential pipelines, and enables parallel agent processing.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Tuple
import structlog

from agents.compliance_agent import ComplianceAgent
from agents.financial_analysis_agent import FinancialAnalysisAgent
from agents.fraud_detection_agent import FraudDetectionAgent
from agents.portfolio_agent import PortfolioAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from core.config import settings
from guardrails.input_guardrails import InputGuardrails
from models.schemas import AgentResponse

log = structlog.get_logger("orchestrator")

INTENT_TAXONOMY: Dict[str, List[str]] = {
    "financial_analysis": [
        "analyze", "stock", "equity", "market", "revenue", "earnings",
        "pe ratio", "balance sheet", "ticker", "valuation", "quarterly", "nifty",
        "hdfc", "reliance", "tcs", "infy", "fundamentals", "profit",
    ],
    "risk_assessment": [
        "risk", "volatility", "exposure", "hedge", "downside", "beta",
        "credit risk", "liquidity risk", "counterparty", "default", "drawdown",
    ],
    "portfolio": [
        "portfolio", "allocate", "diversify", "rebalance", "invest", "capital",
        "asset allocation", "g-sec", "sgb", "gold", "mutual fund", "sip",
    ],
    "fraud_detection": [
        "fraud", "suspicious", "transaction", "flagged", "anomaly", "scam",
        "phishing", "mule", "smurfing", "unauthorized", "chargeback", "upi",
    ],
    "compliance": [
        "compliance", "regulation", "sebi", "rbi", "kyc", "aml", "pmla",
        "dpdp", "fema", "legal", "statutory", "audit", "license",
    ],
}


class Orchestrator:
    """Central intelligent router and pipeline orchestrator."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.model = model or settings.model
        client = None

        if not settings.is_simulation_mode and (api_key or settings.anthropic_api_key):
            try:
                import anthropic
                key = api_key or settings.anthropic_api_key
                client = anthropic.Anthropic(api_key=key)
            except Exception as e:
                log.warning("anthropic_client_error", error=str(e), fallback="simulation_mode")

        agent_kwargs = {"client": client, "model": self.model}

        self.agents = {
            "financial_analysis": FinancialAnalysisAgent(**agent_kwargs),
            "risk_assessment":    RiskAssessmentAgent(**agent_kwargs),
            "portfolio":          PortfolioAgent(**agent_kwargs),
            "fraud_detection":    FraudDetectionAgent(**agent_kwargs),
            "compliance":         ComplianceAgent(**agent_kwargs),
        }
        self.input_guard = InputGuardrails()

    # ── Public Routing Methods ──────────────────────────────────────────────────

    async def route(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Analyze intent and dispatch request to the most appropriate agent."""
        guard = self.input_guard.validate(query, agent_name="orchestrator")
        if not guard.passed:
            log.warning("query_blocked_by_guardrail", reason=guard.reason)
            return AgentResponse(
                agent="orchestrator",
                success=False,
                output=guard.reason or "Blocked by input guardrails.",
            )

        sanitized_query = guard.sanitized_text or query
        agent_name, confidence = self.classify_intent(sanitized_query)
        log.info("intent_routed", target_agent=agent_name, confidence=confidence, preview=sanitized_query[:60])

        agent = self.agents[agent_name]
        resp = await agent.run(sanitized_query, context)
        resp.metadata["routed_by"] = "orchestrator"
        resp.metadata["intent_confidence"] = f"{confidence:.1f}%"
        resp.guardrail_flags = guard.pii_types
        return resp

    async def run_pipeline(
        self,
        query: str,
        pipeline: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[AgentResponse]:
        """
        Execute an ordered sequential multi-agent pipeline.
        Each agent's output is automatically passed into the context of the subsequent agent.
        """
        guard = self.input_guard.validate(query, agent_name="orchestrator_pipeline")
        if not guard.passed:
            return [
                AgentResponse(
                    agent="orchestrator",
                    success=False,
                    output=guard.reason or "Blocked by input guardrails.",
                )
            ]

        results: List[AgentResponse] = []
        current_context = dict(context or {})
        current_input = guard.sanitized_text or query

        for agent_name in pipeline:
            agent = self.agents.get(agent_name)
            if not agent:
                log.warning("unrecognized_pipeline_agent", name=agent_name)
                continue

            log.info("executing_pipeline_stage", agent=agent_name)
            resp = await agent.run(current_input, current_context)
            results.append(resp)

            # Accumulate structured output into context for downstream agents
            current_context[f"{agent_name}_output"] = resp.output
            current_context[f"{agent_name}_metadata"] = resp.metadata

            # Feed text forward as narrative baseline
            current_input = resp.output

        return results

    async def run_parallel(
        self,
        query: str,
        agent_names: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[AgentResponse]:
        """Execute multiple agents concurrently on the same query."""
        guard = self.input_guard.validate(query, agent_name="orchestrator_parallel")
        if not guard.passed:
            return [
                AgentResponse(
                    agent="orchestrator",
                    success=False,
                    output=guard.reason or "Blocked by input guardrails.",
                )
            ]

        sanitized_query = guard.sanitized_text or query
        tasks = [
            self.agents[name].run(sanitized_query, context)
            for name in agent_names
            if name in self.agents
        ]
        results = await asyncio.gather(*tasks)
        return list(results)

    # ── Intent Classification Engine ───────────────────────────────────────────

    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Compute intent affinity scores using weighted keyword density.
        Returns: (agent_name, confidence_percentage)
        """
        text_lower = text.lower()
        scores: Dict[str, int] = {name: 0 for name in INTENT_TAXONOMY}

        for agent_name, keywords in INTENT_TAXONOMY.items():
            for kw in keywords:
                if kw in text_lower:
                    # Multi-word matches carry higher weight
                    weight = 2 if " " in kw else 1
                    scores[agent_name] += weight

        total_score = sum(scores.values())
        best_agent = max(scores, key=lambda k: scores[k])

        if total_score == 0:
            return "financial_analysis", 50.0  # Safe default baseline

        confidence = (scores[best_agent] / total_score) * 100.0
        return best_agent, round(confidence, 1)

    def get_agent(self, agent_name: str) -> Optional[Any]:
        return self.agents.get(agent_name)
