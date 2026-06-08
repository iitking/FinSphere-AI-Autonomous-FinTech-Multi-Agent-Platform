"""Tests for configuration."""
from core.config import Settings

def test_default_settings():
    s = Settings()
    assert s.app_name == "FinSphere AI"
    assert s.base_currency == "INR"
    assert s.usd_to_inr_rate > 80.0
    assert s.stcg_tax_rate == 0.20
    assert s.ltcg_tax_rate == 0.125
