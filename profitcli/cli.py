# profitcli/cli.py
import click
from profitcli.context import AppContext
from profitcli.plugin_loader import load_plugins

@click.group()
@click.pass_context
def cli(ctx):
    """
    profitcli - CLI acessível para Profit DLL
    """
    app_ctx = AppContext()
    app_ctx.initialize()
    ctx.obj = app_ctx

load_plugins(cli)

if __name__ == "__main__":
    cli()
