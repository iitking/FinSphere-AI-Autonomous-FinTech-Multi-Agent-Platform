"""Pydantic Schemas."""
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, List, Optional

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
