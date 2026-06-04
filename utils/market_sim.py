"""
Market Data & Simulation Utility.
Provides price lookup simulation, currency conversion,
and Sharpe ratio estimation for Indian and global equities.
"""

from __future__ import annotations

import math
from typing import Dict, Any
from core.config import settings


def convert_currency(amount: float, from_curr: str = "USD", to_curr: str = "INR") -> float:
    """Convert currency using configured USD/INR exchange rate."""
    if from_curr.upper() == to_curr.upper():
        return amount
    if from_curr.upper() == "USD" and to_curr.upper() == "INR":
        return amount * settings.usd_to_inr_rate
    if from_curr.upper() == "INR" and to_curr.upper() == "USD":
        return amount / settings.usd_to_inr_rate
    return amount


def calculate_sharpe(expected_return: float, volatility: float, risk_free_rate: float | None = None) -> float:
    """
    Compute annualized Sharpe ratio.
    Default benchmark risk-free rate is sourced from settings (e.g. 7.0% for Indian 10Y G-Sec).
    """
    rf = (risk_free_rate if risk_free_rate is not None else settings.risk_free_rate) * 100
    if volatility <= 0:
        return 0.0
    return round((expected_return - rf) / volatility, 2)
