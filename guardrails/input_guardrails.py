"""
Enterprise Input Guardrails.
Sanitizes and secures incoming prompts before they reach any agent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from core.config import settings
from core.logging import get_logger
from guardrails.rules import (
    DISALLOWED_TOPICS,
    GLOBAL_PII_PATTERNS,
    INDIAN_PII_PATTERNS,
    INJECTION_PATTERNS,
)
from models.schemas import GuardrailResult

log = get_logger("input_guardrail")


@dataclass
class InputGuardrails:
    strict_mode: bool = field(default_factory=lambda: settings.strict_input_guardrail)
    _blocked_count: int = field(default=0, repr=False)

    def validate(self, text: str, agent_name: str = "orchestrator") -> GuardrailResult:
        """Run multi-layer input validation and redaction pipeline."""
        if not text or not text.strip():
            return GuardrailResult(passed=False, reason="Query input is empty.")

        # 1. Payload length validation
        if len(text) > settings.max_input_length:
            self._blocked_count += 1
            log.warning("input_length_exceeded", agent=agent_name, len=len(text), max=settings.max_input_length)
            return GuardrailResult(
                passed=False,
                reason=f"Input payload exceeds maximum character threshold ({len(text)} > {settings.max_input_length}).",
            )

        # 2. Prompt Injection Defense
        if settings.enable_injection_detection:
            for pattern in INJECTION_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    self._blocked_count += 1
                    log.warning("prompt_injection_blocked", agent=agent_name, pattern=pattern)
                    return GuardrailResult(
                        passed=False,
                        reason="Input blocked: malicious prompt injection or instruction override signature detected.",
                    )

        # 3. Disallowed Financial Topics
        if settings.enable_topic_blocking:
            for pattern in DISALLOWED_TOPICS:
                if re.search(pattern, text, re.IGNORECASE):
                    self._blocked_count += 1
                    log.warning("disallowed_financial_topic_blocked", agent=agent_name, pattern=pattern)
                    return GuardrailResult(
                        passed=False,
                        reason="Input blocked: query involves prohibited financial activity (market manipulation, insider trading, or money laundering).",
                    )

        # 4. PII Redaction Pipeline
        sanitized = text
        pii_detected: List[str] = []

        if settings.enable_pii_redaction:
            active_pii_patterns = list(GLOBAL_PII_PATTERNS)
            if settings.enable_indian_pii:
                active_pii_patterns.extend(INDIAN_PII_PATTERNS)

            for pattern, label in active_pii_patterns:
                matches = re.findall(pattern, sanitized, re.IGNORECASE)
                if matches:
                    pii_detected.append(label)
                    tag = f"[REDACTED_{label.upper()}]"
                    sanitized = re.sub(pattern, tag, sanitized, flags=re.IGNORECASE)

            if pii_detected:
                log.info("pii_sanitized", agent=agent_name, types=list(set(pii_detected)))
                if self.strict_mode:
                    self._blocked_count += 1
                    return GuardrailResult(
                        passed=False,
                        reason=f"PII detected under strict mode: {list(set(pii_detected))}. Submission rejected.",
                    )

        return GuardrailResult(
            passed=True,
            sanitized_text=sanitized,
            pii_types=list(set(pii_detected)),
        )

    @property
    def blocked_count(self) -> int:
        return self._blocked_count
