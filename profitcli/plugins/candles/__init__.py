from .command import candles


def register(cli_group):
    cli_group.add_command(candles)
