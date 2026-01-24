"""
context.py

Application Context do profitcli.

Responsável por:
- Inicializar e finalizar serviços
- Expor API de alto nível para controllers/plugins
"""

import logging
from typing import Callable

from profitcli.models.trade import TradeEvent
from profitcli.services.profit_service import ProfitService

log = logging.getLogger("profitcli.context")


class AppContext:
    """
    Contexto global da aplicação.

    Atua como fachada entre:
    - CLI / plugins
    - Serviços internos
    """

    def __init__(self):
        self._profit = ProfitService()
        self._started = False

    # ---------------------------------------------
    # Lifecycle
    # ---------------------------------------------

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

    # ---------------------------------------------
    # API para plugins
    # ---------------------------------------------

    def subscribe_trades(self, fn: Callable[[TradeEvent], None]):
        """
        Permite que plugins recebam eventos de trade.
        """
        self._profit.subscribe_trades(fn)
