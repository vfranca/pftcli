# profitcli/profitdll/trade_subscription.py
from ctypes import WINFUNCTYPE, c_int
from .profitTypes import TNewTradeCallback
from profitcli.profitdll.parsers import parse_trade_callback

NewTradeCB = WINFUNCTYPE(None, TNewTradeCallback)

class TradeSubscriber:
    def __init__(self, dll):
        self.dll = dll
        self._callback_ref = None

    def subscribe(self, on_trade):
        """
        on_trade recebe Trade
        """

        def _internal(cb):
            trade = parse_trade_callback(cb)
            if trade:
                on_trade(trade)

        self._callback_ref = NewTradeCB(_internal)

        # Exemplo típico (nome pode variar conforme DLL)
        self.dll.SetNewTradeCallback(self._callback_ref)
