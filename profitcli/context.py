"""
context.py

Application Context do profitcli.

Responsável por:
- Inicializar e finalizar serviços
- Expor API de alto nível para controllers/plugins
- Expor estado de conexão/login
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
        self.logged_in: bool = False

    # ---------------------------------------------
    # Lifecycle
    # ---------------------------------------------

    def start(self):
        if self._started:
            return

        log.info("Iniciando AppContext")

        # inicia DLL + login
        self._profit.start()

        # 🔑 healthcheck de login
        self.logged_in = self._profit.login_healthcheck()

        if self.logged_in:
            log.info("Login na corretora confirmado")
        else:
            log.warning("Login na corretora NÃO confirmado")

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

