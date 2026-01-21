"""
context.py

Core do profitcli.
Responsável por:
- inicializar/finalizar a Profit DLL
- registrar callbacks reais
- expor eventos em Python puro para plugins
"""

from ctypes import (
    WINFUNCTYPE,
    POINTER,
    c_int,
    c_uint,
    c_size_t,
    byref,
)
from dataclasses import dataclass
from typing import Callable, List

from .profitdll.profit_dll import initializeDll
from .profitdll.profitTypes import (
    TConnectorTrade,
    TConnectorAssetIdentifier,
)

# ============================================================
# Inicialização da DLL
# ============================================================

PROFIT_DLL_PATH = "./ProfitDLL.dll"


# ============================================================
# Estruturas Python-friendly
# ============================================================

@dataclass(slots=True)
class TradeEvent:
    ticker: str
    price: float
    quantity: int
    is_edit: bool


# ============================================================
# AppContext
# ============================================================

class AppContext:
    """
    Contexto global do profitcli.
    Mantém DLL viva, callbacks e listeners.
    """

    def __init__(self, dll_path: str = PROFIT_DLL_PATH):
        self.dll = initializeDll(dll_path)

        # listeners Python
        self._trade_listeners: List[Callable[[TradeEvent], None]] = []

        # referências de callbacks (NÃO remover!)
        self._cb_state = None
        self._cb_trade = None

        self._started = False

    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------

    def start(self):
        if self._started:
            return

        self._register_callbacks()
        self._initialize_login()

        self._started = True

    def stop(self):
        if not self._started:
            return

        self.dll.DLLFinalize()
        self._started = False

    # --------------------------------------------------------
    # Subscriptions (usadas por plugins)
    # --------------------------------------------------------

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        """Plugins chamam isso para receber trades."""
        self._trade_listeners.append(fn)

    # --------------------------------------------------------
    # Callbacks reais da Profit DLL
    # --------------------------------------------------------

    def _register_callbacks(self):
        """
        Registra TODOS os callbacks necessários.
        """

        @WINFUNCTYPE(None, c_int, c_int)
        def state_callback(nType, nResult):
            # Saída simples e linear (screen reader friendly)
            if nType == 0:
                print(f"Login: status={nResult}")
            elif nType == 1:
                print(f"Broker: status={nResult}")
            elif nType == 2:
                print(f"Market: status={nResult}")
            elif nType == 3:
                print(f"Ativação: status={nResult}")

        @WINFUNCTYPE(None, TConnectorAssetIdentifier, c_size_t, c_uint)
        def trade_callback(asset_id, p_trade, flags):
            """
            Callback REAL conforme main.py:
            SetTradeCallbackV2
            """
            is_edit = bool(flags & 1)

            trade = TConnectorTrade(Version=0)

            if self.dll.TranslateTrade(p_trade, byref(trade)):
                evt = TradeEvent(
                    ticker=asset_id.Ticker,
                    price=trade.Price,
                    quantity=trade.Quantity,
                    is_edit=is_edit,
                )

                for listener in self._trade_listeners:
                    listener(evt)

        # manter referências!
        self._cb_state = state_callback
        self._cb_trade = trade_callback

        # registrar na DLL
        self.dll.SetTradeCallbackV2(self._cb_trade)

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    def _initialize_login(self):
        """
        Inicializa a DLL (login completo).
        """
        key = input("Chave de acesso: ")
        user = input("Usuário: ")
        password = input("Senha: ")

        ret = self.dll.DLLInitializeLogin(
            key,
            user,
            password,
            self._cb_state,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

        print(f"DLLInitializeLogin: {ret}")
