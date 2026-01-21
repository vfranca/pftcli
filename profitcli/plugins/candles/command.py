import click
from datetime import datetime

from profitcli.context import AppContext, TradeEvent
from .aggregator import CandleAggregator
from .formatter import format_candle

TIMEFRAMES = {
    "1s": 1,
    "5s": 5,
    "10s": 10,
    "30s": 30,
    "1m": 60,
    "5m": 300,
}


@click.command("candles")
@click.option(
    "--timeframe",
    "-t",
    default="1m",
    type=click.Choice(TIMEFRAMES.keys(), case_sensitive=False),
    help="Timeframe do candle",
)
@click.option(
    "--max",
    "max_candles",
    default=50,
    type=int,
    help="Número máximo de candles exibidos",
)
@click.pass_obj
def candles(app_ctx: AppContext, timeframe: str, max_candles: int):
    """
    Exibe candles agregados por trades reais.
    """
    tf_sec = TIMEFRAMES[timeframe.lower()]
    aggregator = CandleAggregator(tf_sec)
    buffer = []

    def on_trade(evt: TradeEvent):
        now = datetime.now()
        closed = aggregator.update(now, evt.price, evt.quantity)

        if closed:
            buffer.append(closed)
            if len(buffer) > max_candles:
                buffer.pop(0)

            print("\n")
            for c in buffer:
                print(format_candle(c))

    app_ctx.subscribe_trades(on_trade)

    click.echo(
        f"Candles ativos | TF={timeframe} | Ctrl+C para sair"
    )

    try:
        while True:
            pass
    except KeyboardInterrupt:
        click.echo("Encerrando candles.")


# 🔑 FUNÇÃO EXIGIDA PELO plugin_loader
def register(cli_group):
    cli_group.add_command(candles)
