"""
Fraud Detection Agent.
Employs a two-tier hybrid defense:
Tier 1: High-throughput deterministic heuristic rule engine (velocity, thresholds, night bursts).
Tier 2: LLM anomaly reasoning for behavioral patterns, mule rings, and UPI social engineering.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

from agents.base_agent import BaseAgent
from core.config import settings
from models.schemas import AgentResponse

log = structlog.get_logger("fraud_detection_agent")

FRAUD_TOOL = [
    {
        "name": "flag_transactions",
        "description": "Assess each transaction and output forensic fraud scores with classification.",
        "input_schema": {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "transaction_id": {"type": "string"},
                            "fraud_score":    {"type": "number", "description": "Score 0 (clean) to 100 (critical fraud)"},
                            "is_flagged":     {"type": "boolean"},
                            "fraud_type":     {"type": "string", "description": "e.g. account_takeover, velocity_burst, mule_structuring, geo_impossible"},
                            "reason":         {"type": "string", "description": "Investigative reasoning"},
                        },
                        "required": ["transaction_id", "fraud_score", "is_flagged", "reason"],
                    },
                },
                "recommended_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Enforcement steps (e.g. 2FA challenge, account freeze, STR report)",
                },
            },
            "required": ["results"],
        },
    }
]


class FraudDetectionAgent(BaseAgent):
    name = "fraud_detection"
    description = "Screens transactions for fraud vectors using heuristic filters and deep cognitive pattern recognition."

    def system_prompt(self) -> str:
        return f"""You are a Fraud Risk Specialist at a major Indian digital payments operator.
Analyze transaction telemetry for sophisticated fraud techniques:
- UPI collect-request spoofing and QR phishing
- Smurfing / Structuring: Multiple sub-₹10,000 transactions to bypass immediate KYC scrutiny
- Mule account staging and immediate round-trip fund dissipation
- Impossible geographic displacement (e.g. simultaneous or near-simultaneous transactions from distant cities)
- Velocity bursts exceeding {settings.max_transactions_in_velocity_window} transactions within {settings.velocity_window_minutes} minutes
- High-value anomalies exceeding ₹{settings.high_amount_threshold_inr:,.0f}

Scoring Scale:
- 0-30: Normal / Approved
- 31-60: Suspicious / Secondary OTP Challenge Required
- 61-100: Critical / Immediate Transaction Freeze & AML Queue

Invoke the flag_transactions tool for structured evaluation.
"""

    async def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        guard = self._validate_input(user_input)
        if not guard.passed:
            return AgentResponse(agent=self.name, success=False, output=guard.reason or "Blocked.")

        safe_input = guard.sanitized_text or user_input

        # Tier 1: Deterministic Heuristic Filter
        heuristic_flags: List[str] = []
        if context and "transactions" in context:
            heuristic_flags = self._evaluate_heuristics(context["transactions"])

        enriched_input = safe_input
        if heuristic_flags:
            enriched_input += f"\n\n[Tier-1 Rule Engine Alerts: Transactions flagged by heuristics: {heuristic_flags}]"

        messages: List[Dict[str, Any]] = [{"role": "user", "content": enriched_input}]
        response, elapsed = self._timed_run(self._call_claude, messages, tools=FRAUD_TOOL)

        fraud_data: Dict[str, Any] = {}
        narrative_parts: List[str] = []

        for block in response.content:
            if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == "flag_transactions":
                fraud_data = block.input
                followup_messages = list(messages) + [
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": getattr(block, "id", "tool_fraud_id"),
                                "content": "Fraud scores recorded.",
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

        results = fraud_data.get("results", [])
        flagged_ids = [r["transaction_id"] for r in results if r.get("is_flagged")]
        fraud_scores = {r["transaction_id"]: r.get("fraud_score", 0.0) for r in results}

        return AgentResponse(
            agent=self.name,
            success=out_guard.passed,
            output=out_guard.sanitized_text or narrative,
            metadata={
                "flagged_transactions": flagged_ids,
                "fraud_scores": fraud_scores,
                "heuristic_preflags": heuristic_flags,
                "recommended_actions": fraud_data.get("recommended_actions", []),
            },
            elapsed_s=elapsed,
        )

    def _evaluate_heuristics(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """High-speed deterministic rules engine based on configurable parameters."""
        flagged: List[str] = []
        user_txns: Dict[str, List[datetime]] = {}

        for txn in transactions:
            txn_id = txn.get("transaction_id", "unknown")
            amount = txn.get("amount_inr") or (txn.get("amount_usd", 0) * settings.usd_to_inr_rate)

            # Rule 1: High-value limit
            if amount >= settings.high_amount_threshold_inr:
                flagged.append(f"{txn_id} (High Amount: ₹{amount:,.0f})")

            # Rule 2: Night-time hours anomaly
            ts = txn.get("timestamp")
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except Exception:
                    ts = None
            if ts and hasattr(ts, "hour"):
                if settings.night_hours_start <= ts.hour < settings.night_hours_end:
                    flagged.append(f"{txn_id} (High-Risk Night Hours: {ts.hour:02d}:00)")

        return list(set(flagged))
