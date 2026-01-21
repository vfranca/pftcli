import click

from profitcli.context import AppContext
from profitcli.plugin_loader import load_plugins


@click.group()
@click.version_option(package_name="profitcli")
@click.pass_context
def cli(ctx):
    """
    profit - CLI acessível para integração com a Profit DLL
    """
    # Cria e inicializa o contexto global da aplicação
    app_ctx = AppContext()
    app_ctx.initialize()

    # Armazena no contexto do Click
    ctx.obj = app_ctx


# Carrega plugins (candles, tape, etc.)
load_plugins(cli)


if __name__ == "__main__":
    cli()
