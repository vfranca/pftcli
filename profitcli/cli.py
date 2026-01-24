"""
cli.py

CLI principal do profitcli.
"""

import click

from profitcli.logging import setup_logging
from profitcli.context import AppContext
from profitcli.plugin_loader import load_plugins


setup_logging()


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(package_name="profitcli")
@click.pass_context
def cli(ctx: click.Context):
    """
    profitcli

    CLI extensível baseada na Profit DLL.
    """
    if ctx.obj is None:
        app_ctx = AppContext()
        app_ctx.start()
        ctx.obj = app_ctx


# 🔑 plugins são carregados NO TOPO, não dentro do callback
load_plugins(cli)


@cli.command()
@click.pass_obj
def status(app_ctx: AppContext):
    """Mostra status básico da conexão."""
    click.echo("profitcli ativo e conectado.")


@cli.command()
@click.pass_obj
def stop(app_ctx: AppContext):
    """Finaliza a DLL."""
    app_ctx.stop()
    click.echo("Profit DLL finalizada.")


def main():
    cli()


if __name__ == "__main__":
    main()
