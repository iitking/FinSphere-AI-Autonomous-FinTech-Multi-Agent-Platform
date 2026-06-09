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
DISALLOWED_TOPICS: List[str] = [
    r"\bmanipulate\s+(stock|market|price|securities)\b",
    r"\binsider\s+trad(e|ing)\b",
    r"\bwash\s+trad(e|ing)\b",
    r"\bpump\s+and\s+dump\b",
]
DISALLOWED_TOPICS.extend([
    r"\bmoney\s+launder(ing)?\b",
    r"\bevade\s+(tax|taxes|regulation|kyc|aml|pmla)\b",
    r"\bhawala\s+transaction(s)?\b",
])
