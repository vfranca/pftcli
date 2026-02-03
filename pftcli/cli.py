"""
cli.py

CLI principal do pftcli.
"""

import click

from pftcli.logging import setup_logging
from pftcli.context import AppContext
from pftcli.plugin_loader import load_plugins
from pftcli.commands.status import status_cmd
from pftcli.commands.stop import stop_cmd


# inicializa logging global
setup_logging()


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(package_name="pftcli")
@click.pass_context
def cli(ctx: click.Context):
    """
    pftcli

    CLI extensível baseada na Profit DLL.
    """
    if ctx.obj is None:
        app_ctx = AppContext()
        app_ctx.start()
        ctx.obj = app_ctx


# plugins carregados no topo (registram comandos)
load_plugins(cli)


cli.add_command(status_cmd, name="status")
cli.add_command(stop_cmd, name="stop")


def main():
    cli()


if __name__ == "__main__":
    main()
