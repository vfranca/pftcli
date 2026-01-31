"""
Configurações do plugin tape.

Ordem de precedência:
1) Variáveis de ambiente
2) profitcli.ini
3) Defaults
"""

import os
from profitcli.config import load_config

ENV_PREFIX = "PROFITCLI_TAPE_"


def load_tape_config():
    cfg = load_config()

    def env(key, default=None):
        return os.getenv(f"{ENV_PREFIX}{key}", default)

    limit = int(
        env(
            "LIMIT",
            cfg.get("tape", "default_limit", fallback=50)
        )
    )

    show_side = str(
        env(
            "SHOW_SIDE",
            cfg.get("tape", "show_side", fallback="true")
        )
    ).lower() in ("1", "true", "yes", "on")

    return {
        "limit": limit,
        "show_side": show_side,
    }
