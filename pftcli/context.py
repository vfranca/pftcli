"""
context.py

Application Context do pftcli.
Responsável apenas por bootstrap e lifecycle do serviço.
"""

import logging

from pftcli.services.profit_service import ProfitService

log = logging.getLogger("pftcli.context")


class AppContext:
    """
    Contexto raiz da aplicação.

    NÃO contém regras de negócio.
    NÃO expõe estado derivado (login, market, etc).
    """

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
        self._service.stop()
        self._started = False

    # -------------------------------
    # API oficial
    # -------------------------------

    @property
    def service(self) -> ProfitService:
        """
        Retorna o serviço principal da aplicação.
        """
        return self._service
