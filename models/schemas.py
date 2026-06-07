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
class RiskRequest(BaseModel):
    asset_description: str
    portfolio_size_inr: Optional[float] = None
    investor_profile: str = "moderate"

class RiskResponse(AgentResponse):
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_score: float = 0.0
class PortfolioRequest(BaseModel):
    assets: List[str] = Field(default_factory=list)
    capital_inr: float
    risk_tolerance: str = "moderate"
    horizon_years: int = 5

class PortfolioResponse(AgentResponse):
    allocation: Dict[str, float] = Field(default_factory=dict)
class Transaction(BaseModel):
    transaction_id: str
    amount_inr: float
    merchant: str
    location: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    channel: str = "UPI"
