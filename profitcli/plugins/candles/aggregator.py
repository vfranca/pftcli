from collections import deque
from datetime import datetime, timedelta


class Candle:
    __slots__ = ("open", "high", "low", "close", "volume", "start")

    def __init__(self, price, qty, start):
        self.open = price
        self.high = price
        self.low = price
        self.close = price
        self.volume = qty
        self.start = start

    def update(self, price, qty):
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price
        self.volume += qty


class CandleAggregator:
    def __init__(self, timeframe_sec: int, limit: int):
        self.tf = timedelta(seconds=timeframe_sec)
        self.limit = limit
        self.candles = deque(maxlen=limit)
        self.current = None

    def on_trade(self, evt):
        ts = evt.timestamp
        bucket = ts - timedelta(
            seconds=ts.second % self.tf.total_seconds(),
            microseconds=ts.microsecond,
        )

        if self.current is None or bucket != self.current.start:
            self.current = Candle(evt.price, evt.quantity, bucket)
            self.candles.append(self.current)
        else:
            self.current.update(evt.price, evt.quantity)

    def last(self):
        return list(self.candles)
