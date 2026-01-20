# plugins/candles/command.py
import click

def register(cli_group):

    @cli_group.command()
    @click.option("--symbol", required=True, help="Ativo (ex: WINJ26)")
    @click.option("--timeframe", default="1m", help="Timeframe (ex: 1m)")
    @click.option("--count", default=20, help="Quantidade de candles")
    @click.pass_obj
    def candles(app_ctx, symbol, timeframe, count):
        """
        Exibe candles OHLC em formato acessível
        """
        candles = app_ctx.dll.get_candles(symbol, timeframe, count)

        for c in candles:
            click.echo(
                f"{c.timestamp:%Y-%m-%d %H:%M} | "
                f"O: {c.open:.3f} | "
                f"H: {c.high:.3f} | "
                f"L: {c.low:.3f} | "
                f"C: {c.close:.3f} | "
                f"V: {c.volume}"
            )
