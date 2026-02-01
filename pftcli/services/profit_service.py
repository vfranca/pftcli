"""
services.profit_service

Integração com a Profit DLL.
"""

import time
import logging
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
from typing import Callable, List

from pftcli.config import load_credentials, load_dll_path
from pftcli.models.trade import TradeEvent
from pftcli.profitdll.profit_dll import initializeDll
from pftcli.profitdll.profitTypes import (
    TConnectorTrade,
    TConnectorAssetIdentifier,
    TConnectorTradingAccountOut,
)

log = logging.getLogger("pftcli.service")


class ProfitService:
    def __init__(self):
        self._dll = None
        self._trade_listeners: List[Callable[[TradeEvent], None]] = []

        self._cb_state = None
        self._cb_trade_rt = None
        self._cb_trade_hist = None

        self._accounts: list[TConnectorTradingAccountOut] = []
        self._logged_in = False
        self._market_ready = False
        self._started = False

        # ---- diagnóstico em tempo real
        self._last_state_type = None
        self._last_state_result = None
        self._last_account_count = 0

    # -------------------------------------------------
    # Lifecycle
    # -------------------------------------------------

    def start(self):
        if self._started:
            return

        dll_path = load_dll_path()
        log.info("Inicializando Profit DLL: %s", dll_path)

        self._dll = initializeDll(dll_path)
        self._register_callbacks()
        self._login()

        self._started = True

    def stop(self):
        if not self._started:
            return

        self._dll.DLLFinalize()
        self._started = False

    # -------------------------------------------------
    # API pública
    # -------------------------------------------------

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        self._trade_listeners.append(fn)

    def request_historical_trades(
        self,
        ticker: str,
        start_ts_ms: int,
        end_ts_ms: int,
    ):
        if not self._market_ready:
            raise RuntimeError("Mercado ainda não está pronto")

        asset = TConnectorAssetIdentifier()
        memset(byref(asset), 0, sizeof(asset))
        asset.Ticker = ticker  # char[N] → string, NÃO bytes

        ret = self._dll.GetHistoryTrades(
            byref(asset),
            c_longlong(start_ts_ms),
            c_longlong(end_ts_ms),
        )

        log.info(
            "Requisição de histórico enviada | ticker=%s ret=%s",
            ticker,
            ret,
        )

    def login_healthcheck(self, timeout_sec: float = 5.0) -> bool:
        deadline = time.time() + timeout_sec
        self._accounts.clear()

        while time.time() < deadline:
            if not self._market_ready:
                log.debug(
                    "Aguardando market_state=4 | último estado: type=%s result=%s",
                    self._last_state_type,
                    self._last_state_result,
                )
                time.sleep(0.2)
                continue

            try:
                count = self._dll.GetAccountCount()
                self._last_account_count = count
            except Exception as exc:
                log.error("Erro ao consultar contas: %s", exc)
                break

            if count > 0:
                accounts = (TConnectorTradingAccountOut * count)()
                filled = self._dll.GetAccounts(accounts, count)

                for i in range(filled):
                    acc = accounts[i]
                    self._accounts.append(acc)
                    log.info(
                        "Conta ativa | Broker=%s Conta=%s SubConta=%s",
                        acc.AccountID.BrokerID,
                        acc.AccountID.AccountID,
                        acc.AccountID.SubAccountID,
                    )

                self._logged_in = True
                return True

            log.debug(
                "Mercado OK, aguardando contas | GetAccountCount=%s",
                count,
            )

            time.sleep(0.3)

        log.warning(
            "Login não confirmado | market_ready=%s accounts=%s",
            self._market_ready,
            self._last_account_count,
        )

        self._logged_in = False
        return False

    # -------------------------------------------------
    # Callbacks
    # -------------------------------------------------

    def _register_callbacks(self):
        @WINFUNCTYPE(None, c_int, c_int)
        def state_callback(nType, nResult):
            self._last_state_type = nType
            self._last_state_result = nResult

            log.info("Estado DLL | type=%s result=%s", nType, nResult)

            if nType == 2 and nResult == 4:
                log.info("Mercado pronto (market_state=4)")
                self._market_ready = True

        @WINFUNCTYPE(None, TConnectorAssetIdentifier, c_size_t, c_uint)
        def trade_callback_rt(asset_id, p_trade, flags):
            trade = TConnectorTrade(Version=0)
            is_edit = bool(flags & 1)

            if self._dll.TranslateTrade(p_trade, byref(trade)):
                evt = TradeEvent(
                    ticker=asset_id.Ticker.rstrip(b"\x00").decode("ascii"),
                    price=trade.Price,
                    quantity=trade.Quantity,
                    timestamp_ns=time.time_ns(),
                    is_edit=is_edit,
                    is_historical=False,
                )
                for listener in self._trade_listeners:
                    listener(evt)

        @WINFUNCTYPE(None, TConnectorAssetIdentifier, c_size_t, c_uint)
        def trade_callback_history(asset_id, p_trade, flags):
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
                for listener in self._trade_listeners:
                    listener(evt)

        self._cb_state = state_callback
        self._cb_trade_rt = trade_callback_rt
        self._cb_trade_hist = trade_callback_history

        self._dll.SetTradeCallbackV2(self._cb_trade_rt)
        self._dll.SetHistoryTradeCallback(self._cb_trade_hist)

    # -------------------------------------------------
    # Login
    # -------------------------------------------------

    def _login(self):
        key, user, password = load_credentials()

        if not all([key, user, password]):
            raise RuntimeError("Credenciais não encontradas")

        ret = self._dll.DLLInitializeLogin(
            key,
            user,
            password,
            self._cb_state,
            None, None, None, None,
            None, None, None, None,
            None, None,
        )

        log.info("DLLInitializeLogin retornou: %s", ret)
