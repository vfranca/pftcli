# -*- coding: utf-8 -*-
"""
pft stop
"""

import logging
import click
from pftcli.context import AppContext

log = logging.getLogger("pftcli.commands.stop")


@click.command("stop")
@click.pass_obj
def stop_cmd(app_ctx: AppContext):
    log.info("Encerrando serviço Profit")
    app_ctx.stop()
    click.echo("Profit DLL finalizada.")
