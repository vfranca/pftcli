"""
Controller do plugin tape.

Integra CLI (click), model e view.
"""

import logging
import click

from .config import load_tape_config
from .model import TapeModel
from .view import TapeView

logger = logging.getLogger("profitcli.tape")


@click.command()
@click.argument("ticker")
@click.option(
    "-n",
    "--limit",
    type=int,
    help="Quantidade máxima de trades exibidos (buffer)",
)
@click.pass_obj
def tape(app_ctx, ticker, limit):
    """
    Exibe o tape (times & trades) em tempo real.

    Um trade por linha, em ordem cronológica.
    """
    cfg = load_tape_config()

    effective_limit = limit or cfg["limit"]

    model = TapeModel(
        ticker=ticker,
        limit=effective_limit,
    )

    view = TapeView(
        show_side=cfg["show_side"]
    )

    def on_trade(evt):
        trade = model.on_trade(evt)
        if trade:
            click.echo(view.render_trade(trade))

    logger.info(
        "Tape iniciado | ticker=%s limit=%s",
        ticker,
        effective_limit,
    )

    app_ctx.subscribe_trades(on_trade)

    click.echo(
        f"Tape ativo | {ticker} | buffer={effective_limit}"
    )

    # mantém processo vivo
    click.get_current_context().exit_on_close = False
