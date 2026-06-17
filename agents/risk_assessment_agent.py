"""
Risk Assessment Agent.
Evaluates multi-dimensional financial risk across Market, Credit, Liquidity,
Regulatory, and Operational exposures with configurable factor weights.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

from agents.base_agent import BaseAgent
from core.config import settings
from models.schemas import AgentResponse, RiskLevel

log = structlog.get_logger("risk_assessment_agent")

RISK_TOOL = [
    {
        "name": "score_risk",
        "description": "Quantify risk exposures across 5 dimensions and return structured scores.",
        "input_schema": {
            "type": "object",
            "properties": {
                "overall_score":    {"type": "number", "description": "Aggregated risk score between 0 (safe) and 100 (critical danger)"},
                "risk_level":       {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                "market_risk":      {"type": "number", "description": "Beta, volatility, sector drawdown exposure (0-100)"},
                "credit_risk":      {"type": "number", "description": "Counterparty quality, rating downgrade probability (0-100)"},
                "liquidity_risk":   {"type": "number", "description": "Slippage, daily turnover, ease of exit (0-100)"},
                "regulatory_risk":  {"type": "number", "description": "SEBI/RBI policy shifts, statutory adherence (0-100)"},
                "operational_risk": {"type": "number", "description": "Governance, cyber, execution risks (0-100)"},
                "top_risk_factors": {"type": "array", "items": {"type": "string"}, "description": "Primary risk vulnerabilities"},
                "mitigants":        {"type": "array", "items": {"type": "string"}, "description": "Actionable hedging or mitigation steps"},
            },
            "required": ["overall_score", "risk_level", "top_risk_factors"],
        },
    }
]


class RiskAssessmentAgent(BaseAgent):
    name = "risk_assessment"
    description = "Evaluates investment risk across market, credit, liquidity, regulatory, and operational axes."

    def system_prompt(self) -> str:
        return f"""You are the Chief Risk Officer (CRO) at an Indian financial institution.
Your job is to provide unflinching, data-backed risk assessments.

Weight your analysis according to system risk parameters:
- Market Risk (Weight: {settings.market_risk_weight * 100:.0f}%)
- Credit Risk (Weight: {settings.credit_risk_weight * 100:.0f}%)
- Liquidity Risk (Weight: {settings.liquidity_risk_weight * 100:.0f}%)
- Regulatory Risk (Weight: {settings.regulatory_risk_weight * 100:.0f}%)
- Operational Risk (Weight: {settings.operational_risk_weight * 100:.0f}%)

Risk Classifications:
- 0 to {settings.risk_low_cutoff:.0f}: Low Risk
- {settings.risk_low_cutoff:.0f} to {settings.risk_medium_cutoff:.0f}: Medium Risk
- {settings.risk_medium_cutoff:.0f} to {settings.risk_high_cutoff:.0f}: High Risk
- Above {settings.risk_high_cutoff:.0f}: Critical Risk

Invoke the score_risk tool to output structured risk telemetry. Be conservative and prioritize capital preservation.
"""

    async def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        guard = self._validate_input(user_input)
        if not guard.passed:
            return AgentResponse(agent=self.name, success=False, output=guard.reason or "Blocked.")

        safe_input = guard.sanitized_text or user_input
        enriched_input = safe_input

        # Forward previous agent context if available in pipeline
        if context and "financial_analysis_output" in context:
            enriched_input = (
                f"Context from Financial Research Analysis:\n{context['financial_analysis_output']}\n\n"
                f"Evaluate the risk for this request:\n{safe_input}"
            )

        messages: List[Dict[str, Any]] = [{"role": "user", "content": enriched_input}]
        response, elapsed = self._timed_run(self._call_claude, messages, tools=RISK_TOOL)

        risk_data: Dict[str, Any] = {}
        narrative_parts: List[str] = []

        for block in response.content:
            if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == "score_risk":
                risk_data = block.input
                followup_messages = list(messages) + [
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": getattr(block, "id", "tool_risk_id"),
                                "content": "Risk scores registered.",
                            }
                        ],
                    },
                ]
                followup, elapsed_followup = self._timed_run(self._call_claude, followup_messages)
                elapsed += elapsed_followup
                narrative_parts.append(self._extract_text(followup))
            elif hasattr(block, "text") and block.text:
                narrative_parts.append(block.text)

        narrative = "\n\n".join(narrative_parts).strip()
        out_guard = self._validate_output(narrative, safe_input)

        # Fallback score computation if tool wasn't invoked
        overall_score = risk_data.get("overall_score", 45.0)
        level_str = risk_data.get("risk_level", "medium").lower()

        return AgentResponse(
            agent=self.name,
            success=out_guard.passed,
            output=out_guard.sanitized_text or narrative,
            metadata={
                "risk_score": overall_score,
                "risk_level": level_str,
                "breakdown": {
                    "market": risk_data.get("market_risk", 40.0),
                    "credit": risk_data.get("credit_risk", 30.0),
                    "liquidity": risk_data.get("liquidity_risk", 35.0),
                    "regulatory": risk_data.get("regulatory_risk", 45.0),
                    "operational": risk_data.get("operational_risk", 25.0),
                },
                "top_factors": risk_data.get("top_risk_factors", []),
                "mitigants": risk_data.get("mitigants", []),
            },
            elapsed_s=elapsed,
        )
