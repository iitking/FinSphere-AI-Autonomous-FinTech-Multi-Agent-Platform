"""
Configuration and Parameters Route.
Provides dynamic parameter inspection and tuning status.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter
from core.config import settings
from models.schemas import SystemConfigResponse

router = APIRouter()


@router.get("/", response_model=SystemConfigResponse)
async def get_system_config():
    """
    Retrieve active runtime parameters, economic indicators, and guardrail settings.
    """
    return SystemConfigResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.app_env,
        model=settings.model,
        simulation_mode=settings.is_simulation_mode,
        base_currency=settings.base_currency,
        usd_to_inr_rate=settings.usd_to_inr_rate,
        active_regulations=settings.active_regulations,
        guardrails_enabled={
            "pii_redaction": settings.enable_pii_redaction,
            "indian_pii": settings.enable_indian_pii,
            "injection_defense": settings.enable_injection_detection,
            "topic_blocking": settings.enable_topic_blocking,
            "toxicity_blocking": settings.enable_toxicity_blocking,
            "strict_mode": settings.strict_input_guardrail,
        },
    )


@router.get("/parameters", response_model=Dict[str, Any])
async def get_all_parameters():
    """
    Retrieve detailed parameter configuration for all agents and risk models.
    """
    return {
        "economics": {
            "base_currency": settings.base_currency,
            "usd_to_inr_rate": settings.usd_to_inr_rate,
            "stcg_tax_rate_pct": settings.stcg_tax_rate * 100,
            "ltcg_tax_rate_pct": settings.ltcg_tax_rate * 100,
            "risk_free_rate_pct": settings.risk_free_rate * 100,
        },
        "risk_model_weights": {
            "market_risk": settings.market_risk_weight,
            "credit_risk": settings.credit_risk_weight,
            "liquidity_risk": settings.liquidity_risk_weight,
            "regulatory_risk": settings.regulatory_risk_weight,
            "operational_risk": settings.operational_risk_weight,
            "cutoffs": {
                "low": settings.risk_low_cutoff,
                "medium": settings.risk_medium_cutoff,
                "high": settings.risk_high_cutoff,
            },
        },
        "portfolio_caps": {
            "conservative_equity": settings.conservative_equity_cap,
            "moderate_equity": settings.moderate_equity_cap,
            "aggressive_equity": settings.aggressive_equity_cap,
            "gold_cap": settings.gold_cap,
            "international_cap": settings.international_cap,
            "min_asset_count": settings.min_asset_diversification_count,
        },
        "fraud_rules": {
            "high_amount_inr": settings.high_amount_threshold_inr,
            "velocity_window_minutes": settings.velocity_window_minutes,
            "max_txns_in_window": settings.max_transactions_in_velocity_window,
            "night_hours": f"{settings.night_hours_start:02d}:00 - {settings.night_hours_end:02d}:00",
        },
    }
