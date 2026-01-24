"""
services.profit_service

Camada de serviço responsável por:
- Inicializar a Profit DLL
- Realizar login
- Registrar callbacks nativos
- Converter eventos da DLL em eventos de domínio
"""

import time
import logging
from ctypes import WINFUNCTYPE, c_int, c_uint, c_size_t, byref
from typing import Callable, List

from profitcli.config import load_credentials, load_dll_path
from profitcli.models.trade import TradeEvent
from profitcli.profitdll.profit_dll import initializeDll
from profitcli.profitdll.profitTypes import (
    TConnectorTrade,
    TConnectorAssetIdentifier,
)

log = logging.getLogger("profitcli.service")


class ProfitService:
    """
    Serviço de integração com a Profit DLL.
    """

    def __init__(self):
        self._dll = None
        self._trade_listeners: List[Callable[[TradeEvent], None]] = []

        # manter referências de callbacks
        self._cb_state = None
        self._cb_trade = None

        self._started = False

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
        log.info("ProfitService iniciado")

    def stop(self):
        if not self._started:
            return

        log.info("Finalizando Profit DLL")
        self._dll.DLLFinalize()
        self._started = False

    # -------------------------------------------------
    # Public API (usada pelo Context)
    # -------------------------------------------------

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        self._trade_listeners.append(fn)

    # -------------------------------------------------
    # Callbacks
    # -------------------------------------------------

    def _register_callbacks(self):
        log.info("Registrando callbacks")

        @WINFUNCTYPE(None, c_int, c_int)
        def state_callback(nType, nResult):
            log.info("Estado DLL | type=%s result=%s", nType, nResult)

        @WINFUNCTYPE(None, TConnectorAssetIdentifier, c_size_t, c_uint)
        def trade_callback(asset_id, p_trade, flags):
            trade = TConnectorTrade(Version=0)
            is_edit = bool(flags & 1)

            if self._dll.TranslateTrade(p_trade, byref(trade)):
                evt = TradeEvent(
                    ticker=asset_id.Ticker,
                    price=trade.Price,
                    quantity=trade.Quantity,
                    timestamp_ns=time.time_ns(),
                    is_edit=is_edit,
                )

                log.debug(
                    "Trade recebido %s %s %s",
                    evt.ticker, evt.price, evt.quantity
                )

                for listener in self._trade_listeners:
                    listener(evt)

        self._cb_state = state_callback
        self._cb_trade = trade_callback

        self._dll.SetTradeCallbackV2(self._cb_trade)

    # -------------------------------------------------
    # Login
    # -------------------------------------------------

    def _login(self):
        key, user, password = load_credentials()

        if not all([key, user, password]):
            raise RuntimeError(
                "Credenciais não encontradas "
                "(ENV ou profitcli.ini)"
            )

        log.info("Realizando login na Profit DLL")

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
