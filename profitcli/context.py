"""
context.py

Application Context do profitcli.
"""

import logging
from typing import Callable

from profitcli.models.trade import TradeEvent
from profitcli.services.profit_service import ProfitService

log = logging.getLogger("profitcli.context")


class AppContext:
    def __init__(self):
        self._profit = ProfitService()
        self._started = False

    def start(self):
        if self._started:
            return

        log.info("Iniciando AppContext")
        self._profit.start()
        self._started = True

    def stop(self):
        if not self._started:
            return

        log.info("Finalizando AppContext")
        self._profit.stop()
        self._started = False

    # -------------------------------
    # API exposta ao CLI / plugins
    # -------------------------------

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        self._profit.subscribe_trades(fn)

    def is_connected(self) -> bool:
        return self._profit.login_healthcheck()
