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
class AgentResponse(BaseModel):
    agent: str
    success: bool
    output: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    elapsed_s: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    guardrail_flags: List[str] = Field(default_factory=list)
class AnalysisRequest(BaseModel):
    ticker: str
    timeframe: str = "1Y"
    include_sentiment: bool = True

class AnalysisResponse(AgentResponse):
    ticker: str = ""
