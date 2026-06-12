"""
Enterprise Output Guardrails.
Inspects and amends model outputs before delivery to users.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.config import settings
from core.logging import get_logger
from guardrails.rules import HALLUCINATION_PATTERNS, TOXIC_PATTERNS
from models.schemas import GuardrailResult

log = get_logger("output_guardrail")

ADVISORY_AGENTS = {"financial_analysis", "risk_assessment", "portfolio"}
DISCLAIMER_KEYWORD = "disclaimer"


@dataclass
class OutputGuardrails:

    def validate(self, output: str, input_text: str = "", agent_name: str = "agent") -> GuardrailResult:
        """Validate agent output text and enforce safety constraints."""
        if not output:
            return GuardrailResult(passed=False, reason="Empty output received from agent.")

        # 1. Output Length Bounds
        if len(output.strip()) < settings.min_output_length:
            return GuardrailResult(passed=False, reason="Response too short: agent failed to generate sufficient analysis.")

        if len(output) > settings.max_output_length:
            log.warning("output_truncated", agent=agent_name, original_len=len(output), max=settings.max_output_length)
            output = output[: settings.max_output_length] + "\n\n[Note: Output safely truncated at maximum length limit]"

        # 2. Hard Toxicity Filter
        if settings.enable_toxicity_blocking:
            for pattern in TOXIC_PATTERNS:
                if re.search(pattern, output, re.IGNORECASE):
                    log.error("toxic_output_intercepted", agent=agent_name, pattern=pattern)
                    return GuardrailResult(
                        passed=False,
                        reason="Output blocked: unprofessional or toxic content detected.",
                    )

        # 3. Regulatory Disclaimer Enforcement
        final_output = output
        if agent_name in ADVISORY_AGENTS:
            if DISCLAIMER_KEYWORD not in final_output.lower():
                log.info("disclaimer_appended", agent=agent_name)
                final_output = final_output.rstrip() + f"\n\n---\n{settings.mandatory_disclaimer}"

        # 4. Hallucination and False Certainty Guard
        for pattern in HALLUCINATION_PATTERNS:
            if re.search(pattern, final_output, re.IGNORECASE):
                log.warning("hallucination_or_guarantee_detected", agent=agent_name, pattern=pattern)
                final_output += (
                    "\n\n⚠️ **Caution Regarding Projections:** Language implying guaranteed yield or certainty "
                    "was identified. In financial markets, all forecasts carry risk and past trends do not guarantee future returns."
                )
                break

        return GuardrailResult(passed=True, sanitized_text=final_output)
