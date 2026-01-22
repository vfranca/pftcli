"""
plugin_loader.py

Descobre e carrega plugins do profitcli.
"""

import importlib
import pkgutil

import profitcli.plugins


def load_plugins(cli_group):
    """
    Procura plugins e registra comandos click.
    """
    for _, name, _ in pkgutil.iter_modules(profitcli.plugins.__path__):
        module = importlib.import_module(f"profitcli.plugins.{name}")

        if hasattr(module, "register"):
            module.register(cli_group)
