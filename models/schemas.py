"""
Shared Pydantic v2 schemas for agents, guardrails, and API requests.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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
    agent: str = Field(..., description="Name of the agent generating the output")
    success: bool = Field(..., description="Whether the run completed successfully")
    output: str = Field(..., description="Primary narrative or recommendation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Structured tool outputs and scores")
    elapsed_s: float = Field(default=0.0, description="Execution duration in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC completion timestamp")
    guardrail_flags: List[str] = Field(default_factory=list, description="Guardrail sanitizations applied")


# ── Financial Analysis ────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker (e.g. HDFCBANK, RELIANCE, TCS) or company name", examples=["HDFCBANK"])
    timeframe: str = Field(default="1Y", description="Analysis horizon (e.g. 1M, 6M, 1Y, 3Y)", examples=["1Y"])
    include_sentiment: bool = Field(default=True, description="Analyze market sentiment and news catalysts")


class AnalysisResponse(AgentResponse):
    ticker: str = ""
    analyst_rating: Optional[str] = None
    pe_ratio: Optional[float] = None
    revenue_growth: Optional[float] = None


# ── Risk Assessment ───────────────────────────────────────────────────────────

class RiskRequest(BaseModel):
    asset_description: str = Field(..., description="Asset description, ticker, or portfolio summary", examples=["High-yield NBFC corporate debt offering 11.5% coupon"])
    portfolio_size_inr: Optional[float] = Field(default=None, description="Portfolio scale in INR", examples=[5000000])
    investor_profile: str = Field(default="moderate", description="conservative | moderate | aggressive", examples=["moderate"])


class RiskResponse(AgentResponse):
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_score: float = 0.0
    top_factors: List[str] = Field(default_factory=list)


# ── Portfolio Optimization ────────────────────────────────────────────────────

class PortfolioRequest(BaseModel):
    assets: List[str] = Field(
        default=["Nifty 50 Index", "Midcap 150", "G-Sec 10Y", "Gold SGB", "Nasdaq 100 FoF"],
        description="Candidate assets or themes",
    )
    capital_inr: float = Field(..., gt=0, description="Available capital to invest in INR", examples=[1000000])
    risk_tolerance: str = Field(default="moderate", pattern="^(conservative|moderate|aggressive)$", examples=["moderate"])
    horizon_years: int = Field(default=5, ge=1, le=35, description="Investment horizon in years", examples=[5])


class PortfolioResponse(AgentResponse):
    allocation: Dict[str, float] = Field(default_factory=dict, description="Asset to percentage weight")
    expected_return_pct: Optional[float] = None
    sharpe_estimate: Optional[float] = None


# ── Fraud Detection ───────────────────────────────────────────────────────────

class Transaction(BaseModel):
    transaction_id: str = Field(..., examples=["TXN_2026_001"])
    amount_inr: float = Field(..., gt=0, examples=[85000.0])
    merchant: str = Field(..., examples=["Digital Electronics Mumbai"])
    location: str = Field(..., examples=["Mumbai, India"])
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(..., examples=["USR_9921"])
    channel: str = Field(default="UPI", description="UPI | IMPS | NEFT | CARD | NETBANKING", examples=["UPI"])


class FraudRequest(BaseModel):
    transactions: List[Transaction]


class FraudResponse(AgentResponse):
    flagged: List[str] = Field(default_factory=list, description="IDs of flagged suspicious transactions")
    fraud_scores: Dict[str, float] = Field(default_factory=dict)
    recommended_actions: List[str] = Field(default_factory=list)


# ── Regulatory Compliance ──────────────────────────────────────────────────────

class ComplianceRequest(BaseModel):
    document_text: str = Field(..., description="Contract, agreement, or operational workflow text to inspect")
    regulation_context: str = Field(
        default="RBI Digital Lending, SEBI LODR, PMLA 2002, DPDP Act 2023",
        description="Regulatory frameworks to verify against",
    )
    jurisdiction: str = Field(default="India")


class ComplianceResponse(AgentResponse):
    compliant: bool = True
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ── Orchestrator Routing Requests ─────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language financial query", examples=["Analyze HDFC Bank fundamentals and assess credit risk"])
    pipeline: Optional[List[str]] = Field(
        default=None,
        description="Optional ordered pipeline of agents (e.g. ['financial_analysis', 'risk_assessment', 'portfolio'])",
        examples=[["financial_analysis", "risk_assessment"]],
    )


class PipelineRequest(BaseModel):
    query: str
    agents: List[str] = Field(..., description="Ordered list of agent names to execute sequentially")


class SystemConfigResponse(BaseModel):
    app_name: str
    app_version: str
    environment: str
    model: str
    simulation_mode: bool
    base_currency: str
    usd_to_inr_rate: float
    active_regulations: List[str]
    guardrails_enabled: Dict[str, bool]
