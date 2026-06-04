"""Market Simulation Utility."""
from core.config import settings

def convert_currency(amount: float, from_curr: str = "USD", to_curr: str = "INR") -> float:
    if from_curr == "USD" and to_curr == "INR": return amount * settings.usd_to_inr_rate
    return amount
