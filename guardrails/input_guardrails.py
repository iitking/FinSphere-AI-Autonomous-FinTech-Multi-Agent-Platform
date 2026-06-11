"""Input Guardrails."""
from dataclasses import dataclass, field
from core.config import settings
from models.schemas import GuardrailResult

@dataclass
class InputGuardrails:
    strict_mode: bool = field(default_factory=lambda: settings.strict_input_guardrail)
# Payload length checking
