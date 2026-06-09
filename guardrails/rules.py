"""Guardrails Rule Definitions."""
import re
from typing import List, Tuple
INJECTION_PATTERNS: List[str] = [
    r"ignore\s+(previous|all|above|prior)\s+instructions",
    r"you\s+are\s+now\s+(?!acting\s+as\s+a\s+financial)",
]
