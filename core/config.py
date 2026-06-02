"""Global Configuration."""
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "FinSphere AI"
    app_version: str = "2.0.0"
    app_env: str = "development"
