"""Simulation Mock Engine."""
from core.config import settings
class MockMessageBlock:
    def __init__(self, block_type: str, text: str = "", tool_name: str = "", tool_input: dict = None, tool_id: str = "mock_001"):
        self.type = block_type
        self.text = text
        self.name = tool_name
        self.input = tool_input or {}
        self.id = tool_id

class MockClaudeResponse:
    def __init__(self, content):
        self.content = content
class MockEngine:
    @staticmethod
    def generate_response(agent_name: str, messages: list, tools: list = None):
        return MockClaudeResponse([MockMessageBlock("text", "Synthesizing analysis...")])
