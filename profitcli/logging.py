"""
logging.py

Configuração centralizada de logging do profitcli.
"""

import logging
import os
from pathlib import Path


def _get_appdata_dir() -> Path:
    """
    Retorna o diretório base de dados da aplicação.

    Windows:
      %APPDATA%\\profitcli

    Fallback (caso raro):
      ~/.profitcli
    """
    appdata = os.getenv("APPDATA")

    if appdata:
        return Path(appdata) / "profitcli"

    # Fallback seguro (Linux / ambiente estranho)
    return Path.home() / ".profitcli"


APP_DIR = _get_appdata_dir()
LOG_DIR = APP_DIR / "logs"
LOG_FILE = LOG_DIR / "profitcli.log"


def setup_logging(level=logging.INFO):
    """
    Configura logging SOMENTE em arquivo.

    - Nenhum log no console
    - Arquivo único em %APPDATA%\\profitcli\\logs
    """

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove handlers existentes (console, click, etc.)
    root_logger.handlers.clear()

    # Apenas arquivo
    root_logger.addHandler(file_handler)

    # Evita propagação duplicada
    root_logger.propagate = False
