"""
context.py

Core do profitcli.
Responsável por:
- inicializar/finalizar a Profit DLL (lazy)
- registrar callbacks reais
- expor eventos em Python puro para plugins
"""

from ctypes import (
    WINFUNCTYPE,
    c_int,
    c_uint,
    c_size_t,
    byref,
)
from dataclasses import dataclass
from typing import Callable, List, Optional

from .profitdll.profit_dll import initializeDll
from .profitdll.profitTypes import (
    TConnectorTrade,
    TConnectorAssetIdentifier,
)

# ============================================================
# Configuração
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
    Inicializa a DLL SOMENTE sob demanda.
    """

    def __init__(self, dll_path: str = PROFIT_DLL_PATH):
        self._dll_path = dll_path
        self.dll = None  # lazy

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

        self.dll = initializeDll(self._dll_path)
        self._register_callbacks()
        self._initialize_login()

        self._started = True

    def stop(self):
        if not self._started:
            return

        self.dll.DLLFinalize()
        self.dll = None
        self._started = False

    # --------------------------------------------------------
    # Subscriptions (usadas por plugins)
    # --------------------------------------------------------

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        """
        Plugins chamam isso para receber trades.
        Inicializa a DLL automaticamente se necessário.
        """
        if not self._started:
            self.start()

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
            Callback REAL conforme Profit DLL:
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
