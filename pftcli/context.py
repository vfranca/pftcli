# -*- coding: utf-8 -*-
"""
context.py

Application Context do pftcli.
"""

import time
import logging
from typing import Callable

from pftcli.models.trade import TradeEvent
from pftcli.services.profit_service import ProfitService

log = logging.getLogger("pftcli.context")


class AppContext:
    def __init__(self):
        self._service = ProfitService()
        self._started = False

    # -------------------------------
    # Lifecycle
    # -------------------------------

    def start(self):
        if self._started:
            return

        log.info("Iniciando AppContext")
        self._service.start()
        self._started = True

    def stop(self):
        if not self._started:
            return

        log.info("Finalizando AppContext")
        self._service.shutdown()
        self._started = False

    # -------------------------------
    # API oficial
    # -------------------------------

    @property
    def service(self) -> ProfitService:
        return self._service

    # -------------------------------
    # Compatibilidade legada
    # -------------------------------

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        self._service.subscribe_trades(fn)

    def request_historical_trades(
        self,
        ticker: str,
        start_ts_ms: int,
        end_ts_ms: int,
    ):
        self._service.request_historical_trades(
            ticker,
            start_ts_ms,
            end_ts_ms,
        )

    def is_market_ready(self) -> bool:
        return self._service.is_market_ready()

    def is_logged_in(self) -> bool:
        return self._service.is_logged_in()

    def has_accounts(self) -> bool:
        return self._service.has_accounts()

    def wait_until_connected(
        self,
        timeout_sec: float = 15.0,
        poll_interval: float = 0.2,
    ) -> bool:
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            if self.is_logged_in() and self.is_market_ready():
                return True
            time.sleep(poll_interval)

        log.error("Timeout aguardando conexão")
        return False
