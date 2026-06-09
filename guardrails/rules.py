"""Guardrails Rule Definitions."""
import re
from typing import List, Tuple
INJECTION_PATTERNS: List[str] = [
    r"ignore\s+(previous|all|above|prior)\s+instructions",
    r"you\s+are\s+now\s+(?!acting\s+as\s+a\s+financial)",
]
INJECTION_PATTERNS.extend([
    r"\bjailbreak\b",
    r"\bdan\s+mode\b",
    r"system\s*prompt\s*(reveal|leak|show|print|dump)",
])
