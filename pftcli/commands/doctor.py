"""
pft doctor

Diagnóstico do estado do serviço Profit.
Não executa login nem ações ativas.
"""

import logging
import click

from pftcli.context import AppContext
from pftcli.helpers.service_resolver import resolve_service

log = logging.getLogger("pftcli.commands.doctor")


@click.command("doctor")
@click.pass_obj
def doctor_cmd(app_ctx: AppContext):
    service = resolve_service(app_ctx)
    st = service.get_status()

    click.echo("PFT DOCTOR")
    click.echo("-" * 40)

    click.echo(f"Login       : {st.login.name}")
    click.echo(f"Market      : {st.market.name}")
    click.echo(f"Activation  : {st.activation.name}")

    click.echo("-" * 40)

    # Diagnóstico derivado EXPLICITAMENTE
    if st.login.name != "OK":
        click.echo("Diagnóstico : OFF (login não confirmado)")
    elif st.market.name != "OK":
        click.echo("Diagnóstico : DEGRADED (market não pronto)")
    elif st.activation.name != "OK":
        click.echo("Diagnóstico : DEGRADED (activation pendente)")
    else:
        click.echo("Diagnóstico : OK (serviço operacional)")

    log.info("Doctor summary: %s", st.summary())
