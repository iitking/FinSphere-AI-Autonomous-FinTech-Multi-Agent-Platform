"""Global Configuration."""
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "FinSphere AI"
    app_version: str = "2.0.0"
    app_env: str = "development"
    anthropic_api_key: str = ""
    model: str = "claude-3-7-sonnet-20250219"
    max_tokens: int = 4096
    temperature: float = 0.2
    mock_mode: bool = False
    base_currency: str = "INR"
    usd_to_inr_rate: float = 86.50
    stcg_tax_rate: float = 0.20
    ltcg_tax_rate: float = 0.125
    risk_free_rate: float = 0.07
    max_input_length: int = 8000
    min_output_length: int = 10
    max_output_length: int = 16000
    strict_input_guardrail: bool = False
    enable_pii_redaction: bool = True
    enable_indian_pii: bool = True
