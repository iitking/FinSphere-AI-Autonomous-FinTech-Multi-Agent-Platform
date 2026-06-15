"""Base Agent Framework."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from core.config import settings
from guardrails.input_guardrails import InputGuardrails
from guardrails.output_guardrails import OutputGuardrails

class BaseAgent(ABC):
    name: str = "base"
    description: str = ""
# Client init
# Simulation fallback
