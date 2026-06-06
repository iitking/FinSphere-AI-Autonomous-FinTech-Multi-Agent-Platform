"""Pydantic Schemas."""
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, List, Optional

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
class GuardrailResult(BaseModel):
    passed: bool
    reason: Optional[str] = None
    sanitized_text: Optional[str] = None
    pii_types: List[str] = Field(default_factory=list)
