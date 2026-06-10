"""
Rule definitions and regex patterns for input and output guardrails.
Includes comprehensive coverage for Indian PII (PAN, Aadhaar, UPI, Phone, IFSC),
Global PII, Prompt Injection, and Disallowed Financial Topics.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# ── Prompt Injection Defense ──────────────────────────────────────────────────
INJECTION_PATTERNS: List[str] = [
    r"ignore\s+(previous|all|above|prior)\s+instructions",
    r"you\s+are\s+now\s+(?!acting\s+as\s+a\s+financial)",
    r"disregard\s+(your|all)\s+(system|training|guidelines|rules)",
    r"act\s+as\s+(a|an)\s+(?!financial|risk|compliance|fraud|portfolio|quant)",
    r"\bjailbreak\b",
    r"\bdan\s+mode\b",
    r"<\|.*?\|>",
    r"\[INST\]",
    r"system\s*prompt\s*(reveal|leak|show|print|dump)",
    r"override\s+(all\s+)?restrictions",
    r"pretend\s+you\s+have\s+no\s+(rules|limits|guidelines)",
]

# ── Prohibited Financial Activities ───────────────────────────────────────────
DISALLOWED_TOPICS: List[str] = [
    r"\bmanipulate\s+(stock|market|price|securities)\b",
    r"\binsider\s+trad(e|ing)\b",
    r"\bwash\s+trad(e|ing)\b",
    r"\bpump\s+and\s+dump\b",
    r"\bmoney\s+launder(ing)?\b",
    r"\bevade\s+(tax|taxes|regulation|kyc|aml|pmla)\b",
    r"\bponzi\s+scheme\b",
    r"\bhawala\s+transaction(s)?\b",
    r"\bunlicensed\s+(investment\s+advising|chit\s+fund)\b",
]

# ── Indian PII Patterns ────────────────────────────────────────────────────────
INDIAN_PII_PATTERNS: List[Tuple[str, str]] = [
    # Permanent Account Number (PAN): 5 letters + 4 digits + 1 letter (e.g., ABCDE1234F)
    (r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "pan_card"),
    # Aadhaar Number: 12 digits (starting with 2-9) optionally separated by space/hyphen
    (r"\b[2-9]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}\b", "aadhaar_number"),
    # Indian Mobile Numbers (starts with 6-9, optional +91 or 0 prefix)
    (r"(?:\+91[\-\s]?|91[\-\s]?|0)?[6-9]\d{9}\b", "indian_phone"),
    # Bank IFSC Code: 4 alphabetic chars + '0' + 6 alphanumeric chars
    (r"\b[A-Z]{4}0[A-Z0-9]{6}\b", "ifsc_code"),
    # UPI Virtual Payment Address (e.g. user@okhdfcbank, user@paytm, user@upi)
    (r"\b[a-zA-Z0-9.\-_]{2,64}@(okhdfcbank|okaxis|okicici|oksbi|paytm|upi|ybl|axl|ibl)\b", "upi_vpa"),
]

# ── Global PII Patterns ────────────────────────────────────────────────────────
GLOBAL_PII_PATTERNS: List[Tuple[str, str]] = [
    # US Social Security Number
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn"),
    # Major Credit / Debit Cards (Visa, Mastercard, Amex, Discover, RuPay 16 digits)
    (r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6[0-9]{15})\b", "credit_card"),
    # Email Address
    (r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", "email"),
]

# ── Output Safety & Hallucination Defense ─────────────────────────────────────
HALLUCINATION_PATTERNS: List[str] = [
    r"\b\d{2,3}\.\d{3,}%",                       # Over-precise precision hallucination
    r"guaranteed\s+(return|profit|yield|gain)",   # Guaranteed returns (illegal under SEBI)
    r"100%\s+(safe|risk.free|certain|guaranteed)",
    r"will\s+(definitely|certainly|always)\s+(rise|fall|double|triple)",
    r"zero\s+risk\s+investment",
]

TOXIC_PATTERNS: List[str] = [
    r"\b(idiot|stupid|dumb|fool|moron|retard|scam artist)\b",
    r"you\s+should\s+(kill|harm|hurt)",
]
