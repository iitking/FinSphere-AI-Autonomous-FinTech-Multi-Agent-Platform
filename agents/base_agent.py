"""
Base agent class for all FinTech agents.
Provides Anthropic client lifecycle, offline Mock fallback,
retry resilience, structured logging, and guardrail integration.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from core.config import settings
from core.mock_engine import MockClaudeResponse, MockEngine
from guardrails.input_guardrails import InputGuardrails
from guardrails.output_guardrails import OutputGuardrails
from models.schemas import AgentResponse, GuardrailResult

log = structlog.get_logger("agent")


class BaseAgent(ABC):
    """Abstract base class for all FinTech autonomous intelligence agents."""

    name: str = "base"
    description: str = ""

    def __init__(
        self,
        client: Optional[Any] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        self.model = model or settings.model
        self.max_tokens = max_tokens or settings.max_tokens
        self.input_guard = InputGuardrails()
        self.output_guard = OutputGuardrails()
        self._call_count = 0

        # Initialize Anthropic client if key is configured and not simulated
        self.client = client
        if self.client is None and not settings.is_simulation_mode:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            except Exception as e:
                log.warning("anthropic_client_init_failed", error=str(e), fallback="simulation_mode")
                self.client = None

    @abstractmethod
    def system_prompt(self) -> str:
        """Return the persona and prompt contract for this agent."""

    @abstractmethod
    async def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Execute the agent's core task."""

    def _call_claude(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
        """Call Claude with retry logic or invoke offline MockEngine if in simulation mode."""
        self._call_count += 1
        log.info("agent_executing", agent=self.name, invocation=self._call_count, simulation=settings.is_simulation_mode)

        if settings.is_simulation_mode or self.client is None:
            return MockEngine.generate_response(self.name, messages, tools)

        return self._invoke_anthropic_api(messages, tools)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6))
    def _invoke_anthropic_api(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": self.system_prompt(),
            "messages": messages,
            "temperature": settings.temperature,
        }
        if tools:
            kwargs["tools"] = tools
        return self.client.messages.create(**kwargs)

    def _validate_input(self, user_input: str) -> GuardrailResult:
        return self.input_guard.validate(user_input, agent_name=self.name)

    def _validate_output(self, output: str, input_text: str = "") -> GuardrailResult:
        return self.output_guard.validate(output, input_text=input_text, agent_name=self.name)

    def _extract_text(self, message: Any) -> str:
        if hasattr(message, "content"):
            return "".join(
                block.text
                for block in message.content
                if hasattr(block, "text") and block.text
            )
        return str(message)

    def _timed_run(self, fn, *args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = round(time.perf_counter() - start, 3)
        log.info("agent_call_finished", agent=self.name, elapsed_seconds=elapsed)
        return result, elapsed
