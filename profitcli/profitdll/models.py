# profitcli/profitdll/models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Trade:
    timestamp: datetime
    price: float
    volume: int


@dataclass
class Candle:
    start: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
