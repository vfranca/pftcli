# profitcli/utils/candle_aggregator.py
from datetime import datetime, timedelta
from profitcli.profitdll.models import Candle, Trade

class CandleAggregator:
    def __init__(self, timeframe_seconds: int):
        self.tf = timedelta(seconds=timeframe_seconds)
        self.current: Candle | None = None

    def _bucket_start(self, ts: datetime) -> datetime:
        epoch = int(ts.timestamp())
        bucket = epoch - (epoch % int(self.tf.total_seconds()))
        return datetime.fromtimestamp(bucket)

    def process_trade(self, trade: Trade) -> Candle | None:
        """
        Processa um trade.
        Retorna um candle FECHADO se houver mudança de período.
        """
        bucket = self._bucket_start(trade.timestamp)

        # primeiro trade
        if self.current is None:
            self.current = Candle(
                start=bucket,
                open=trade.price,
                high=trade.price,
                low=trade.price,
                close=trade.price,
                volume=trade.volume,
            )
            return None

        # mesmo candle
        if bucket == self.current.start:
            self.current.high = max(self.current.high, trade.price)
            self.current.low = min(self.current.low, trade.price)
            self.current.close = trade.price
            self.current.volume += trade.volume
            return None

        # novo período → fecha candle anterior
        closed = self.current

        self.current = Candle(
            start=bucket,
            open=trade.price,
            high=trade.price,
            low=trade.price,
            close=trade.price,
            volume=trade.volume,
        )

        return closed
