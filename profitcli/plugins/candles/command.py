import click

from .aggregator import CandleAggregator
from .formatter import format_candle


TIMEFRAMES = {
    "1M": 60,
    "5M": 300,
    "15M": 900,
}


@click.command()
@click.argument("ticker")
@click.option(
    "-t",
    "--timeframe",
    default="5M",
    help="Timeframe do candle (1M, 5M, 15M)",
)
@click.option(
    "-n",
    "--limit",
    default=20,
    type=int,
    help="Quantidade máxima de candles no buffer",
)
@click.pass_obj
def candles(app_ctx, ticker, timeframe, limit):
    """
    Exibe candles agregados via trades (tempo real).
    Cada candle fechado é exibido em uma única linha.
    """

    tf_sec = TIMEFRAMES.get(timeframe.upper())
    if not tf_sec:
        raise click.BadParameter("Timeframe inválido")

    aggregator = CandleAggregator(
        timeframe_sec=tf_sec,
        limit=limit,
    )

    def on_trade(evt):
        # filtro por ativo (SEM DLL)
        if evt.ticker != ticker:
            return

        candle = aggregator.on_trade(evt)

        # só imprime quando um candle FECHA
        if candle:
            click.echo(format_candle(candle))

    # subscrição global de trades
    app_ctx.subscribe_trades(on_trade)

    click.echo(
        f"Candles {ticker} | TF={timeframe.upper()} | buffer={limit}"
    )

    # mantém o processo vivo
    click.get_current_context().exit_on_close = False
