"""
Global Configuration Management.
Centralizes all system parameters, risk thresholds, guardrail settings,
and financial economics using Pydantic Settings.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Application Info ─────────────────────────────────────────────────────────
    app_name: str = Field(default="FinSphere AI", description="Application branding name")
    app_version: str = Field(default="2.0.0", description="System version")
    app_env: str = Field(default="development", description="development | staging | production")
    debug: bool = Field(default=False, description="Enable debug diagnostics")
    host: str = Field(default="0.0.0.0", description="API bind host")
    port: int = Field(default=8000, description="API port")
    log_level: str = Field(default="INFO", description="DEBUG, INFO, WARNING, ERROR")

    # ── LLM & Execution Parameters ──────────────────────────────────────────────
    anthropic_api_key: str = Field(default="", description="Anthropic API Key")
    model: str = Field(
        default="claude-3-7-sonnet-20250219",
        description="LLM Model (e.g. claude-3-7-sonnet-20250219, claude-3-5-sonnet-20241022, claude-3-haiku-20240307)",
    )
    max_tokens: int = Field(default=4096, description="Max token limit per LLM response")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="LLM sampling temperature")
    timeout_seconds: float = Field(default=30.0, description="Network timeout for AI calls")
    max_retries: int = Field(default=3, description="Retry attempts for transient AI errors")
    mock_mode: bool = Field(
        default=False,
        description="Run in offline simulation mode without needing an active paid API key",
    )

    # ── Currency & Economic Parameters ─────────────────────────────────────────
    base_currency: str = Field(default="INR", description="Default accounting currency")
    usd_to_inr_rate: float = Field(default=86.50, description="Current USD to INR conversion rate")
    stcg_tax_rate: float = Field(default=0.20, description="Indian Short-Term Capital Gains Tax Rate (20%)")
    ltcg_tax_rate: float = Field(default=0.125, description="Indian Long-Term Capital Gains Tax Rate (12.5%)")
    risk_free_rate: float = Field(default=0.07, description="India 10-Yr Benchmark G-Sec yield proxy (7%)")

    # ── Guardrail Parameters ───────────────────────────────────────────────────
    max_input_length: int = Field(default=8000, description="Maximum characters allowed in query")
    min_output_length: int = Field(default=10, description="Minimum characters for valid response")
    max_output_length: int = Field(default=16000, description="Maximum characters in agent output")
    strict_input_guardrail: bool = Field(default=False, description="Reject instead of sanitizing PII")
    enable_pii_redaction: bool = Field(default=True, description="Enable automatic PII redaction")
    enable_indian_pii: bool = Field(default=True, description="Enable Indian PAN, Aadhaar, Phone & UPI masking")
    enable_injection_detection: bool = Field(default=True, description="Block prompt injection attacks")
    enable_topic_blocking: bool = Field(default=True, description="Block illegal financial topics")
    enable_toxicity_blocking: bool = Field(default=True, description="Block unprofessional or toxic outputs")

    # ── Fraud Detection Rules Parameters ───────────────────────────────────────
    high_amount_threshold_inr: float = Field(
        default=100_000.0,
        description="Threshold (INR) triggering immediate high-value fraud review",
    )
    velocity_window_minutes: int = Field(
        default=5,
        description="Sliding window in minutes to evaluate transaction velocity abuse",
    )
    max_transactions_in_velocity_window: int = Field(
        default=3,
        description="Max transactions allowed per user within velocity window before alert",
    )
    max_speed_kmh_threshold: float = Field(
        default=800.0,
        description="Impossible geographic velocity speed limit in km/h between successive transactions",
    )
    night_hours_start: int = Field(default=0, description="Midnight hour (0-23) for night-time alert flagging")
    night_hours_end: int = Field(default=5, description="Morning hour (0-23) end for night-time alert flagging")

    # ── Risk Assessment Parameters ─────────────────────────────────────────────
    market_risk_weight: float = Field(default=0.30, description="Weight of Market Risk in Overall Score")
    credit_risk_weight: float = Field(default=0.25, description="Weight of Credit Risk in Overall Score")
    liquidity_risk_weight: float = Field(default=0.20, description="Weight of Liquidity Risk in Overall Score")
    regulatory_risk_weight: float = Field(default=0.15, description="Weight of Regulatory Risk in Overall Score")
    operational_risk_weight: float = Field(default=0.10, description="Weight of Operational Risk in Overall Score")
    risk_low_cutoff: float = Field(default=30.0, description="Upper bound for Low Risk category")
    risk_medium_cutoff: float = Field(default=60.0, description="Upper bound for Medium Risk category")
    risk_high_cutoff: float = Field(default=80.0, description="Upper bound for High Risk category (above is Critical)")

    # ── Portfolio Optimization Parameters ──────────────────────────────────────
    conservative_equity_cap: float = Field(default=0.30, description="Max equity fraction for conservative")
    moderate_equity_cap: float = Field(default=0.60, description="Max equity fraction for moderate")
    aggressive_equity_cap: float = Field(default=0.85, description="Max equity fraction for aggressive")
    gold_cap: float = Field(default=0.15, description="Recommended upper bound for Gold/SGB allocation")
    international_cap: float = Field(default=0.20, description="Recommended upper bound for overseas equity")
    min_asset_diversification_count: int = Field(default=4, description="Minimum recommended distinct asset classes")

    # ── Compliance Regulatory Parameters ───────────────────────────────────────
    active_regulations: List[str] = Field(
        default_factory=lambda: [
            "RBI Master Directions (KYC / Digital Lending)",
            "SEBI LODR & Insider Trading Regulations",
            "PMLA 2002 (STR / CTR Monitoring)",
            "DPDP Act 2023 (Digital Data Protection)",
            "FEMA 1999 (Cross-Border Capital Flows)",
        ],
        description="Active compliance frameworks evaluated by the Compliance Agent",
    )
    mandatory_disclaimer: str = Field(
        default=(
            "⚠️ **Regulatory Disclaimer:** This automated intelligence report is generated "
            "for informational and analytic purposes only and does NOT constitute licensed financial, "
            "tax, or investment advisory. Users must consult a SEBI/RBI registered professional."
        ),
        description="Mandatory disclaimer appended to advisory responses",
    )

    @property
    def is_simulation_mode(self) -> bool:
        """Determines if the system runs in offline simulation / mock mode."""
        return self.mock_mode or not bool(self.anthropic_api_key.strip())


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
