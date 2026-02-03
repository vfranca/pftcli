"""
pft status

Exibe o status atual do serviço:
- LOGIN
- MARKET
- ACTIVATION
"""

import logging
import click

from pftcli.context import AppContext
from pftcli.helpers.service_resolver import resolve_service

log = logging.getLogger("pftcli.commands.status")


@click.command("status")
@click.pass_obj
def status_cmd(app_ctx: AppContext):
    service = resolve_service(app_ctx)
    st = service.get_status()

    click.echo("STATUS")
    click.echo(f"Login       : {st.login.name}")
    click.echo(f"Market      : {st.market.name}")
    click.echo(f"Activation  : {st.activation.name}")

    log.info(st.summary())
