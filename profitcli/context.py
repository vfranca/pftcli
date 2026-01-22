"""
context.py

Core do profitcli.

Responsável por:
- carregar configuração (ENV / INI)
- inicializar/finalizar a Profit DLL
- registrar callbacks reais
- expor eventos Python-friendly para plugins
"""

from ctypes import (
    WINFUNCTYPE,
    c_int,
    c_uint,
    c_size_t,
    byref,
)
from dataclasses import dataclass
from typing import Callable, List

from profitcli.config import load_credentials, load_dll_path
from profitcli.profitdll.profit_dll import initializeDll
from profitcli.profitdll.profitTypes import (
    TConnectorTrade,
    TConnectorAssetIdentifier,
)

# ============================================================
# Eventos Python-friendly
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

    - mantém a DLL viva
    - registra callbacks reais
    - redistribui eventos para plugins
    """

    def __init__(self):
        # ----------------------------------------------------
        # Configuração
        # ----------------------------------------------------
        self._dll_path = load_dll_path()
        self._key, self._user, self._password = load_credentials()

        if not all([self._key, self._user, self._password]):
            raise RuntimeError(
                "Credenciais da Profit não encontradas.\n"
                "Defina via variáveis de ambiente ou profitcli.ini."
            )

        # ----------------------------------------------------
        # DLL
        # ----------------------------------------------------
        self.dll = initializeDll(self._dll_path)

        # ----------------------------------------------------
        # Listeners (plugins)
        # ----------------------------------------------------
        self._trade_listeners: List[Callable[[TradeEvent], None]] = []

        # ----------------------------------------------------
        # Callbacks (referências obrigatórias)
        # ----------------------------------------------------
        self._cb_state = None
        self._cb_trade = None

        self._started = False

    # ========================================================
    # Lifecycle
    # ========================================================

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

    # ========================================================
    # API para plugins
    # ========================================================

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        """
        Plugins usam isso para receber trades em tempo real.
        """
        self._trade_listeners.append(fn)

    # ========================================================
    # Callbacks reais da Profit DLL
    # ========================================================

    def _register_callbacks(self):
        """
        Registra callbacks reais na DLL.
        """

        # ----------------------------
        # Estado / Login
        # ----------------------------
        @WINFUNCTYPE(None, c_int, c_int)
        def state_callback(n_type, n_result):
            if n_type == 0:
                print(f"Login: status={n_result}")
            elif n_type == 1:
                print(f"Broker: status={n_result}")
            elif n_type == 2:
                print(f"Market: status={n_result}")
            elif n_type == 3:
                print(f"Ativação: status={n_result}")

        # ----------------------------
        # Trades (SetTradeCallbackV2)
        # ----------------------------
        @WINFUNCTYPE(None, TConnectorAssetIdentifier, c_size_t, c_uint)
        def trade_callback(asset_id, p_trade, flags):
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

        # manter referências vivas
        self._cb_state = state_callback
        self._cb_trade = trade_callback

        # registrar callbacks na DLL
        self.dll.SetTradeCallbackV2(self._cb_trade)

    # ========================================================
    # Login
    # ========================================================

    def _initialize_login(self):
        """
        Login NÃO interativo.
        """

        ret = self.dll.DLLInitializeLogin(
            self._key,
            self._user,
            self._password,
            self._cb_state,
            None,  # broker callback
            None,  # market callback
            None,  # account callback
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

        print(f"DLLInitializeLogin: {ret}")
