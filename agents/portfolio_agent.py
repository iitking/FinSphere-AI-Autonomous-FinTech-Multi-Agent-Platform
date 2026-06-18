"""
Portfolio Optimization Agent.
Allocates capital across Indian equities, G-Secs, corporate bonds, Sovereign Gold,
and international index funds using Modern Portfolio Theory and Indian tax optimization.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

from agents.base_agent import BaseAgent
from core.config import settings
from models.schemas import AgentResponse

log = structlog.get_logger("portfolio_agent")

PORTFOLIO_TOOL = [
    {
        "name": "suggest_allocation",
        "description": "Output targeted asset allocation breakdown, expected return, and Sharpe ratio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "allocations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "asset":           {"type": "string", "description": "Asset name or ETF/index"},
                            "weight_pct":      {"type": "number", "description": "Portfolio weight percentage (0-100)"},
                            "rationale":       {"type": "string", "description": "Strategic reason for allocation"},
                            "expected_return": {"type": "number", "description": "Expected annualized CAGR %"},
                        },
                        "required": ["asset", "weight_pct", "rationale"],
                    },
                },
                "expected_portfolio_return": {"type": "number", "description": "Weighted average annualized portfolio return %"},
                "estimated_sharpe":          {"type": "number", "description": "Projected Sharpe ratio relative to risk-free rate"},
                "rebalance_frequency":       {"type": "string", "enum": ["monthly", "quarterly", "semi-annually", "annually"]},
                "tax_notes":                 {"type": "string", "description": "Tax considerations under STCG (20%) and LTCG (12.5%)"},
            },
            "required": ["allocations", "rebalance_frequency"],
        },
    }
]


class PortfolioAgent(BaseAgent):
    name = "portfolio"
    description = "Engineers asset allocations across Indian equity, fixed income, gold, and international assets."

    def system_prompt(self) -> str:
        return f"""You are a senior quantitative portfolio strategist specializing in wealth management for Indian investors.
Structure robust portfolios balancing capital preservation, inflation hedging, and compounding.

Regulatory & Parameter Constraints:
- Conservative Risk: Max {settings.conservative_equity_cap * 100:.0f}% equity exposure
- Moderate Risk: Max {settings.moderate_equity_cap * 100:.0f}% equity exposure
- Aggressive Risk: Max {settings.aggressive_equity_cap * 100:.0f}% equity exposure
- Gold / SGB Cap: Recommended max {settings.gold_cap * 100:.0f}%
- Overseas Equity (via LRS / FoF): Recommended max {settings.international_cap * 100:.0f}%
- Minimum distinct asset classes for diversification: {settings.min_asset_diversification_count}
- Indian Tax Rules: Short-Term Capital Gains (STCG) at {settings.stcg_tax_rate * 100:.1f}%, Long-Term Capital Gains (LTCG) at {settings.ltcg_tax_rate * 100:.1f}%, Risk-Free Rate benchmark at {settings.risk_free_rate * 100:.1f}%.

Asset Universe:
- Indian Large Cap (Nifty 50, Sensex)
- Mid & Small Cap (Nifty Midcap 150)
- Indian Sovereign Debt (10-Year G-Secs, SDLs)
- Gold (Sovereign Gold Bonds - SGB, Gold ETFs)
- International Diversification (US S&P 500 / Nasdaq 100 FoF)
- Real Estate & Infrastructure (Indian REITs / InvITs)

Call the suggest_allocation tool to return the mathematically structured allocation weights.
"""

    async def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        guard = self._validate_input(user_input)
        if not guard.passed:
            return AgentResponse(agent=self.name, success=False, output=guard.reason or "Blocked.")

        safe_input = guard.sanitized_text or user_input
        enriched = safe_input

        # Forward previous risk assessment context if present
        if context and "risk_assessment_output" in context:
            enriched = (
                f"Risk Profile from Prior Agent:\n{context['risk_assessment_output']}\n\n"
                f"Portfolio Mandate:\n{safe_input}"
            )

        messages: List[Dict[str, Any]] = [{"role": "user", "content": enriched}]
        response, elapsed = self._timed_run(self._call_claude, messages, tools=PORTFOLIO_TOOL)

        alloc_data: Dict[str, Any] = {}
        narrative_parts: List[str] = []

        for block in response.content:
            if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == "suggest_allocation":
                alloc_data = block.input
                followup_messages = list(messages) + [
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": getattr(block, "id", "tool_portfolio_id"),
                                "content": "Allocation validated.",
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

        allocations_list = alloc_data.get("allocations", [])
        alloc_dict = {item["asset"]: item["weight_pct"] for item in allocations_list if "asset" in item and "weight_pct" in item}

        return AgentResponse(
            agent=self.name,
            success=out_guard.passed,
            output=out_guard.sanitized_text or narrative,
            metadata={
                "allocation": alloc_dict,
                "expected_return_pct": alloc_data.get("expected_portfolio_return", 12.0),
                "sharpe_estimate": alloc_data.get("estimated_sharpe", 1.4),
                "rebalance_frequency": alloc_data.get("rebalance_frequency", "quarterly"),
                "tax_notes": alloc_data.get("tax_notes", f"STCG {settings.stcg_tax_rate*100}%, LTCG {settings.ltcg_tax_rate*100}%"),
            },
            elapsed_s=elapsed,
        )
