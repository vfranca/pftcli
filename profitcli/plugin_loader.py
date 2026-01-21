import importlib
import pkgutil
from profitcli import plugins


def load_plugins(cli_group):
    for module in pkgutil.iter_modules(plugins.__path__):
        try:
            plugin = importlib.import_module(
                f"profitcli.plugins.{module.name}.command"
            )
        except ModuleNotFoundError:
            # plugin sem command.py → ignora
            continue

        register = getattr(plugin, "register", None)
        if callable(register):
            register(cli_group)
