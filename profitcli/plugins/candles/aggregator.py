from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(slots=True)
class Candle:
    start: datetime
    end: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class CandleAggregator:
    """
    Agregador de candles baseado em trades reais.
    """

    def __init__(self, timeframe_seconds: int):
        self.tf = timedelta(seconds=timeframe_seconds)
        self.current: Optional[Candle] = None

    def update(self, trade_time: datetime, price: float, qty: int) -> Optional[Candle]:
        """
        Atualiza o candle com um trade.
        Retorna candle fechado se houver.
        """

        if self.current is None:
            self.current = Candle(
                start=trade_time,
                end=trade_time + self.tf,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=qty,
            )
            return None

        if trade_time >= self.current.end:
            closed = self.current
            self.current = Candle(
                start=trade_time,
                end=trade_time + self.tf,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=qty,
            )
            return closed

        # update candle atual
        self.current.high = max(self.current.high, price)
        self.current.low = min(self.current.low, price)
        self.current.close = price
        self.current.volume += qty

        return None
