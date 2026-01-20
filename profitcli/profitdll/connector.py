# profitcli/profitdll/connector.py
from typing import List
from datetime import datetime
from .models import Candle

class ProfitDLLConnector:
    def __init__(self):
        self.initialized = False

    def connect(self):
        # aqui entra DLLInitializeLogin(...)
        self.initialized = True

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        count: int
    ) -> List[Candle]:
        """
        Retorna candles em ordem cronológica (antigo -> recente)
        """
        # MOCK para exemplo
        now = datetime.now()
        candles = []

        for i in range(count):
            candles.append(
                Candle(
                    timestamp=now,
                    open=128.40 + i * 0.01,
                    high=128.50 + i * 0.01,
                    low=128.35 + i * 0.01,
                    close=128.45 + i * 0.01,
                    volume=1000 + i * 10
                )
            )
        return candles
