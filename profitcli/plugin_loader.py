# profitcli/plugin_loader.py
import importlib
import pkgutil
from profitcli import plugins


def load_plugins(cli_group):
    for module in pkgutil.iter_modules(plugins.__path__):
        plugin = importlib.import_module(
            f"profitcli.plugins.{module.name}.command"
        )
        if hasattr(plugin, "register"):
            plugin.register(cli_group)
