# profitcli/plugins/candles/command.py
import click
from profitcli.utils.candle_aggregator import CandleAggregator

TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
}

def normalize_timeframe(tf: str) -> str:
    return tf.strip().lower()

def format_candle(c):
    return (
        f"{c.start:%H:%M} | "
        f"Abertura {c.open:.2f} | "
        f"Máxima {c.high:.2f} | "
        f"Mínima {c.low:.2f} | "
        f"Fechamento {c.close:.2f} | "
        f"Volume {c.volume}"
    )

def register(cli):

    @cli.command(name="bars")
    @click.option("--symbol", "-s", required=True)
    @click.option("--timeframe", "-t", default="1m", help="Ex: 1m, 5m, 15m")
    @click.pass_obj
    def candles(app_ctx, symbol, timeframe):
        """
        Candles agregados a partir dos trades da Profit DLL
        """

        tf_key = timeframe.strip().lower()

        if tf_key not in TIMEFRAMES:
            raise click.BadParameter(
                f"timeframe inválido: {timeframe}. "
                f"Use: {', '.join(TIMEFRAMES.keys())}"
            )

        tf_sec = TIMEFRAMES[tf_key]

        aggregator = CandleAggregator(tf_sec)

        click.echo(
            f"Agregando candles de {symbol} ({timeframe})"
        )

        def on_trade(trade):
            closed = aggregator.process_trade(trade)
            if closed:
                click.echo(format_candle(closed))

        app_ctx.trade_subscriber.subscribe(on_trade)

        try:
            while True:
                pass
        except KeyboardInterrupt:
            click.echo("Encerrado.")
