"""
Model do Tape (Times & Trades).

Responsável por:
- Filtrar ticker
- Manter buffer
- Expor callback para eventos de trade
"""

import logging

logger = logging.getLogger("profitcli.tape.model")


class TapeModel:
    """
    Modelo de estado do tape.

    :param ticker: Ativo monitorado
    :param limit: Tamanho máximo do buffer
    """

    def __init__(self, ticker: str, limit: int):
        self.ticker = ticker
        self.limit = limit
        self.buffer = []

        logger.debug(
            "TapeModel inicializado | ticker=%s limit=%s",
            ticker,
            limit,
        )

    def on_trade(self, evt):
        """
        Callback chamado a cada TradeEvent.
        """
        if evt.ticker != self.ticker:
            return None

        self.buffer.append(evt)

        if len(self.buffer) > self.limit:
            self.buffer.pop(0)

        return evt
