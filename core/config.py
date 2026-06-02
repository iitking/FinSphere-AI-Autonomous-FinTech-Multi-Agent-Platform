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
