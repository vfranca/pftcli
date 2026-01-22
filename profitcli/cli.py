"""
cli.py

CLI principal do profitcli.
- cria AppContext
- carrega plugins
- NÃO acessa DLL diretamente
"""

import click

from profitcli.context import AppContext
from profitcli.plugin_loader import load_plugins


# ============================================================
# CLI principal
# ============================================================

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.pass_context
def cli(ctx: click.Context):
    """
    profitcli

    CLI extensível baseada na Profit DLL.
    """
    if ctx.obj is None:
        # ❗ NÃO chama start aqui
        ctx.obj = AppContext()


# 🔑 Plugins precisam ser carregados na definição do grupo
load_plugins(cli)


# ============================================================
# Core commands
# ============================================================

@cli.command()
@click.pass_obj
def status(app_ctx: AppContext):
    """Mostra status básico da conexão."""
    click.echo("profitcli ativo.")


@cli.command()
@click.pass_obj
def stop(app_ctx: AppContext):
    """Finaliza a DLL."""
    app_ctx.stop()
    click.echo("Profit DLL finalizada.")


# ============================================================
# Entry point
# ============================================================

def main():
    cli()


if __name__ == "__main__":
    main()
