# -*- coding: utf-8 -*-
"""
pft status
"""

import logging
import click
from pftcli.context import AppContext

log = logging.getLogger("pftcli.commands.status")


@click.command("status")
@click.pass_obj
def status_cmd(app_ctx: AppContext):
    st = app_ctx.service.get_status()

    click.echo("STATUS")
    click.echo(f"Login       : {st.login.name}")
    click.echo(f"Market      : {st.market.name}")
    click.echo(f"Activation  : {st.activation.name}")

    log.info(st.summary())
