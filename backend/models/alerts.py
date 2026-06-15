from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class AlertCondition(str, Enum):
    """Direction the price must cross to trigger the alert."""

    ABOVE = "above"
    BELOW = "below"


class PriceAlert(BaseModel):
    id: str
    coin_id: str
    symbol: str
    condition: AlertCondition
    target_price: float
    current_price: float
    created_at: datetime


class AlertsResponse(BaseModel):
    data: List[PriceAlert]
