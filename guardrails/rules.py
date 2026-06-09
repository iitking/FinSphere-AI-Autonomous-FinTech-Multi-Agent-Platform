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
GLOBAL_PII_PATTERNS: List[Tuple[str, str]] = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn"),
    (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6[0-9]{15})\b", "credit_card"),
    (r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", "email"),
]
