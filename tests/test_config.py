"""Tests for configuration."""
from core.config import Settings

def test_default_settings():
    s = Settings()
    assert s.app_name == "FinSphere AI"
    assert s.base_currency == "INR"
