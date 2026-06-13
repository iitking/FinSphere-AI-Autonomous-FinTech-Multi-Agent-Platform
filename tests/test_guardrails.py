"""Guardrail Tests."""
import pytest
from guardrails.input_guardrails import InputGuardrails
from guardrails.output_guardrails import OutputGuardrails

@pytest.fixture
def input_guard(): return InputGuardrails()

@pytest.fixture
def output_guard(): return OutputGuardrails()
