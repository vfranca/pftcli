import click

from .formatter import format_trade


@click.command()
@click.argument("ticker")
@click.option(
    "-n",
    "--limit",
    default=50,
    type=int,
    help="Quantidade máxima de trades exibidos (buffer)",
)
@click.pass_obj
def tape(app_ctx, ticker, limit):
    """
    Exibe o tape (times & trades) em tempo real.
    Um trade por linha, em ordem cronológica.
    """

    buffer = []

    def on_trade(evt):
        if evt.ticker != ticker:
            return

        buffer.append(evt)

        # mantém buffer limitado
        if len(buffer) > limit:
            buffer.pop(0)

        click.echo(format_trade(evt))

    app_ctx.subscribe_trades(on_trade)

    click.echo(f"Tape ativo | {ticker} | buffer={limit}")

    # mantém processo vivo
    click.get_current_context().exit_on_close = False
