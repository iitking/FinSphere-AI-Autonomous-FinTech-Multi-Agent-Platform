"""
Financial Analysis Agent.
Evaluates public equities, fundamentals, valuation multiples, and industry trends
with a focus on Indian (NSE/BSE) and global capital markets.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

from agents.base_agent import BaseAgent
from models.schemas import AgentResponse

log = structlog.get_logger("financial_analysis_agent")

FINANCIAL_TOOLS = [
    {
        "name": "extract_financial_metrics",
        "description": "Extract structured fundamental financial indicators, valuation multiples, and sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pe_ratio":       {"type": "number", "description": "Trailing or forward Price-to-Earnings multiple"},
                "pb_ratio":       {"type": "number", "description": "Price-to-Book multiple"},
                "roe_pct":        {"type": "number", "description": "Return on Equity %"},
                "revenue_growth": {"type": "number", "description": "YoY revenue growth %"},
                "profit_margin":  {"type": "number", "description": "Net profit margin %"},
                "debt_to_equity": {"type": "number", "description": "Total debt to equity ratio"},
                "analyst_rating": {
                    "type": "string",
                    "enum": ["strong_buy", "buy", "hold", "sell", "strong_sell"],
                    "description": "Synthesized consensus recommendation",
                },
                "key_risks":      {"type": "array", "items": {"type": "string"}, "description": "Key macro or micro headwinds"},
                "key_catalysts":  {"type": "array", "items": {"type": "string"}, "description": "Growth drivers and upside triggers"},
            },
            "required": ["analyst_rating", "key_risks", "key_catalysts"],
        },
    }
]


class FinancialAnalysisAgent(BaseAgent):
    name = "financial_analysis"
    description = "Analyzes company balance sheets, revenue growth, multiples, and Indian market macroeconomic catalysts."

    def system_prompt(self) -> str:
        return """You are a senior equity research analyst at a top-tier institutional investment firm covering Indian and global markets.
Your mission is to perform rigorous fundamental analysis of listed companies (NSE/BSE and international equities).

Analytical Standards:
1. Examine valuation multiples (P/E, P/B, EV/EBITDA, Debt/Equity) relative to 5-year historical medians and sector peers.
2. Contextualize with Indian macroeconomic dynamics: RBI monetary policy, repo rate cycle, FII/DII liquidity, and capex themes.
3. Present both the bull case (catalysts, moat, expanding margins) and bear case (competition, regulatory scrutiny, raw material costs).
4. Utilize the extract_financial_metrics tool to return structured metrics alongside your analysis.
5. Strictly adhere to compliance: Never promise guaranteed profits or absolute certainty.
"""

    async def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        guard = self._validate_input(user_input)
        if not guard.passed:
            return AgentResponse(agent=self.name, success=False, output=guard.reason or "Input blocked.")

        safe_input = guard.sanitized_text or user_input
        messages: List[Dict[str, Any]] = [{"role": "user", "content": safe_input}]

        # Invoke model with metric extraction tool
        response, elapsed = self._timed_run(self._call_claude, messages, tools=FINANCIAL_TOOLS)

        metrics: Dict[str, Any] = {}
        narrative_parts: List[str] = []

        for block in response.content:
            if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == "extract_financial_metrics":
                metrics = block.input
                # Return tool result to continue generation
                followup_messages = list(messages) + [
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": getattr(block, "id", "tool_metrics_id"),
                                "content": "Metrics recorded.",
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

        return AgentResponse(
            agent=self.name,
            success=out_guard.passed,
            output=out_guard.sanitized_text or narrative,
            metadata={
                "metrics": metrics,
                "pii_redacted": guard.pii_types,
                "ticker_analyzed": safe_input[:30],
            },
            elapsed_s=elapsed,
        )
