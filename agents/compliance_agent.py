"""
Regulatory Compliance Agent.
Audits financial agreements, onboarding documents, and operational workflows against
Indian statutory mandates: RBI, SEBI, PMLA, FEMA, and the DPDP Act 2023.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import structlog

from agents.base_agent import BaseAgent
from core.config import settings
from models.schemas import AgentResponse

log = structlog.get_logger("compliance_agent")

COMPLIANCE_TOOL = [
    {
        "name": "compliance_check",
        "description": "Perform legal & statutory compliance review and output violations and recommendations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "overall_compliant": {"type": "boolean", "description": "True if no critical or major statutory violations exist"},
                "violations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "regulation":  {"type": "string", "description": "Statute name & section (e.g. RBI Digital Lending Circular 2022 Clause 4.1)"},
                            "description": {"type": "string", "description": "Explanation of non-compliant practice"},
                            "severity":    {"type": "string", "enum": ["minor", "major", "critical"]},
                        },
                        "required": ["regulation", "description", "severity"],
                    },
                },
                "recommendations": {"type": "array", "items": {"type": "string"}, "description": "Remediation action items"},
                "kyc_aml_status":   {"type": "string", "enum": ["clear", "review_required", "blocked"]},
            },
            "required": ["overall_compliant", "violations", "recommendations"],
        },
    }
]


class ComplianceAgent(BaseAgent):
    name = "compliance"
    description = "Screens business processes and agreements against RBI, SEBI, PMLA, FEMA, and DPDP Act regulations."

    def system_prompt(self) -> str:
        regs_list = "\n".join(f"- {r}" for r in settings.active_regulations)
        return f"""You are a Principal Regulatory Counsel and Compliance Officer for an Indian FinTech enterprise.
Conduct exhaustive legal and compliance audits across Indian statutes:

Active Statutory Frameworks:
{regs_list}

Compliance Rigor Guidelines:
1. RBI Digital Lending: Verify that all loan disbursals and repayments occur strictly between borrower bank account and Regulated Entity (RE) bank account without passing through any third-party pool account.
2. PMLA 2002: Ensure strict customer due diligence (CDD), beneficial owner verification (>10% stake), and Suspicious Transaction Reporting (STR) readiness.
3. DPDP Act 2023: Enforce purpose limitation, verifiable parental consent for minors, explicit consent notices in bilingual formats, and data erasure mechanisms.
4. SEBI Regulations: Guard against unlicensed investment advisory (IA), front-running, and research analyst (RA) disclosure failures.

Invoke the compliance_check tool for structured output.
"""

    async def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        guard = self._validate_input(user_input)
        if not guard.passed:
            return AgentResponse(agent=self.name, success=False, output=guard.reason or "Blocked.")

        safe_input = guard.sanitized_text or user_input
        messages: List[Dict[str, Any]] = [{"role": "user", "content": safe_input}]

        response, elapsed = self._timed_run(self._call_claude, messages, tools=COMPLIANCE_TOOL)

        compliance_data: Dict[str, Any] = {}
        narrative_parts: List[str] = []

        for block in response.content:
            if getattr(block, "type", "") == "tool_use" and getattr(block, "name", "") == "compliance_check":
                compliance_data = block.input
                followup_messages = list(messages) + [
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": getattr(block, "id", "tool_compliance_id"),
                                "content": "Compliance check registered.",
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

        violations = compliance_data.get("violations", [])
        has_critical = any(v.get("severity") == "critical" for v in violations)

        return AgentResponse(
            agent=self.name,
            success=out_guard.passed,
            output=out_guard.sanitized_text or narrative,
            metadata={
                "compliant": compliance_data.get("overall_compliant", not has_critical),
                "violations": violations,
                "recommendations": compliance_data.get("recommendations", []),
                "kyc_aml_status": compliance_data.get("kyc_aml_status", "clear"),
                "has_critical_violations": has_critical,
            },
            elapsed_s=elapsed,
        )
