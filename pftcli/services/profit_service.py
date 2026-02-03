# -*- coding: utf-8 -*-
"""
services.profit_service

Integração com a Profit DLL (Clear / B3).
"""

import time
import logging
from enum import Enum, auto
from ctypes import (
    WINFUNCTYPE,
    c_int,
    c_uint,
    c_size_t,
    c_longlong,
    byref,
    memset,
    sizeof,
)
from typing import Callable, List, Optional

from pftcli.config import load_credentials, load_dll_path
from pftcli.models.trade import TradeEvent
from pftcli.profitdll.profit_dll import initializeDll
from pftcli.profitdll.profitTypes import (
    TConnectorTrade,
    TConnectorAssetIdentifier,
)

log = logging.getLogger("pftcli.service")


# -------------------------------------------------
# Status explícito
# -------------------------------------------------

class LoginStatus(Enum):
    OFF = auto()
    OK = auto()
    FAIL = auto()


class MarketStatus(Enum):
    UNKNOWN = auto()
    READY = auto()
    OFF = auto()


class ActivationStatus(Enum):
    OFF = auto()
    OK = auto()
    FAIL = auto()


class ServiceStatus:
    def __init__(self):
        self.login = LoginStatus.OFF
        self.market = MarketStatus.UNKNOWN
        self.activation = ActivationStatus.OFF

    def summary(self) -> str:
        return (
            f"STATUS | LOGIN={self.login.name} "
            f"| MARKET={self.market.name} "
            f"| ACTIVATION={self.activation.name}"
        )


# -------------------------------------------------
# Serviço principal
# -------------------------------------------------

class ProfitService:
    def __init__(self):
        self._dll = None
        self._started = False

        self._trade_listeners: List[Callable[[TradeEvent], None]] = []
        self._cb_state = None
        self._cb_trade_rt = None
        self._cb_trade_hist = None

        self._status = ServiceStatus()

    # -------------------------------
    # Lifecycle
    # -------------------------------

    def start(self):
        if self._started:
            return

        dll_path = load_dll_path()
        log.info("Inicializando Profit DLL: %s", dll_path)

        self._dll = initializeDll(dll_path)
        self._register_callbacks()
        self._login()

        self._started = True

    def shutdown(self):
        if not self._started:
            return

        log.info("Finalizando Profit DLL")
        try:
            self._dll.DLLFinalize()
        except Exception:
            log.exception("Erro ao finalizar DLL")

        self._started = False

    # -------------------------------
    # Status
    # -------------------------------

    def get_status(self) -> ServiceStatus:
        return self._status

    def is_logged_in(self) -> bool:
        return self._status.login == LoginStatus.OK

    def is_market_ready(self) -> bool:
        return self._status.market == MarketStatus.READY

    def has_accounts(self) -> bool:
        # Profit pode não enumerar contas; mantemos compatibilidade
        return self.is_logged_in()

    # -------------------------------
    # API pública
    # -------------------------------

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        self._trade_listeners.append(fn)

    def request_historical_trades(
        self,
        ticker: str,
        start_ts_ms: int,
        end_ts_ms: int,
    ):
        if not self.is_market_ready():
            raise RuntimeError("Mercado ainda não está pronto")

        asset = TConnectorAssetIdentifier()
        memset(byref(asset), 0, sizeof(asset))
        asset.Ticker = ticker

        self._dll.GetHistoryTrades(
            byref(asset),
            c_longlong(start_ts_ms),
            c_longlong(end_ts_ms),
        )

    # -------------------------------
    # Callbacks
    # -------------------------------

    def _register_callbacks(self):
        @WINFUNCTYPE(None, c_int, c_int)
        def state_callback(nType, nResult):
            # LOGIN
            if nType == 0:
                self._status.login = (
                    LoginStatus.OK if nResult == 0 else LoginStatus.FAIL
                )
                log.info("Login state=%s", nResult)

            # MARKET
            elif nType == 2:
                self._status.market = (
                    MarketStatus.READY if nResult == 4 else MarketStatus.OFF
                )
                log.info("Market state=%s", nResult)

            # ACTIVATION
            elif nType == 3:
                self._status.activation = (
                    ActivationStatus.OK if nResult == 0 else ActivationStatus.FAIL
                )
                log.info("Activation state=%s", nResult)

        @WINFUNCTYPE(None, TConnectorAssetIdentifier, c_size_t, c_uint)
        def trade_callback_rt(asset_id, p_trade, flags):
            trade = TConnectorTrade(Version=0)
            if self._dll.TranslateTrade(p_trade, byref(trade)):
                evt = TradeEvent(
                    ticker=asset_id.Ticker.rstrip(b"\x00").decode("ascii"),
                    price=trade.Price,
                    quantity=trade.Quantity,
                    timestamp_ns=time.time_ns(),
                    is_edit=bool(flags & 1),
                    is_historical=False,
                )
                for fn in self._trade_listeners:
                    fn(evt)

        @WINFUNCTYPE(None, TConnectorAssetIdentifier, c_size_t, c_uint)
        def trade_callback_hist(asset_id, p_trade, flags):
            trade = TConnectorTrade(Version=0)
            if self._dll.TranslateTrade(p_trade, byref(trade)):
                evt = TradeEvent(
                    ticker=asset_id.Ticker.rstrip(b"\x00").decode("ascii"),
                    price=trade.Price,
                    quantity=trade.Quantity,
                    timestamp_ns=trade.Timestamp * 1_000_000,
                    is_edit=False,
                    is_historical=True,
                )
                for fn in self._trade_listeners:
                    fn(evt)

        self._cb_state = state_callback
        self._cb_trade_rt = trade_callback_rt
        self._cb_trade_hist = trade_callback_hist

        self._dll.SetTradeCallbackV2(self._cb_trade_rt)
        self._dll.SetHistoryTradeCallback(self._cb_trade_hist)

    # -------------------------------
    # Login
    # -------------------------------

    def _login(self):
        key, user, password = load_credentials()
        rc = self._dll.DLLInitializeLogin(
            key,
            user,
            password,
            self._cb_state,
            None, None, None, None,
            None, None, None, None,
            None, None,
        )
        log.info("DLLInitializeLogin rc=%s", rc)
