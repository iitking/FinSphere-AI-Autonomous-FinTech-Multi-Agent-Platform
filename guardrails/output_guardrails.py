"""Output Guardrails."""
from dataclasses import dataclass
from core.config import settings
from models.schemas import GuardrailResult

@dataclass
class OutputGuardrails:
    pass
# Length bounds
# Disclaimer append
# Hallucination guard
