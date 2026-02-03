"""
pft stop

Finaliza o serviço e encerra a Profit DLL de forma limpa.
"""

import logging
import click

from pftcli.context import AppContext
from pftcli.helpers.service_resolver import resolve_service

log = logging.getLogger("pftcli.commands.stop")


@click.command("stop")
@click.pass_obj
def stop_cmd(app_ctx: AppContext):
    service = resolve_service(app_ctx)

    log.info("Encerrando serviço Profit")
    service.shutdown()

    click.echo("Profit DLL finalizada.")
