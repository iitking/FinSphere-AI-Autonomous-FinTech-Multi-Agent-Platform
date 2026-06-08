"""
Unit tests for configuration parameters and validation.
"""

from core.config import Settings


def test_default_settings():
    s = Settings()
    assert s.app_name == "FinSphere AI"
    assert s.base_currency == "INR"
    assert s.usd_to_inr_rate > 80.0
    assert s.stcg_tax_rate == 0.20
    assert s.ltcg_tax_rate == 0.125
    assert s.risk_free_rate == 0.07
    assert s.market_risk_weight + s.credit_risk_weight + s.liquidity_risk_weight + s.regulatory_risk_weight + s.operational_risk_weight == 1.0


def test_custom_parameters_override():
    s = Settings(
        app_name="Custom FinTech",
        base_currency="USD",
        usd_to_inr_rate=87.0,
        high_amount_threshold_inr=50000.0,
        strict_input_guardrail=True,
    )
    assert s.app_name == "Custom FinTech"
    assert s.base_currency == "USD"
    assert s.high_amount_threshold_inr == 50000.0
    assert s.strict_input_guardrail is True
