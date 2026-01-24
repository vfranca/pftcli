from configparser import ConfigParser
from pathlib import Path
import os

APP_NAME = "profitcli"

APPDATA_DIR = Path(os.getenv("APPDATA")) / APP_NAME
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = APPDATA_DIR / "profitcli.ini"


def load_config():
    parser = ConfigParser()

    if CONFIG_FILE.exists():
        parser.read(CONFIG_FILE, encoding="utf-8")

    return parser


def load_credentials():
    """
    Ordem:
    1) Variáveis de ambiente
    2) profitcli.ini em %APPDATA%
    """
    key = os.getenv("PROFIT_KEY")
    user = os.getenv("PROFIT_USER")
    password = os.getenv("PROFIT_PASSWORD")

    if key and user and password:
        return key, user, password

    cfg = load_config()

    if cfg.has_section("profit"):
        key = cfg.get("profit", "key", fallback=None)
        user = cfg.get("profit", "user", fallback=None)
        password = cfg.get("profit", "password", fallback=None)

        if key and user and password:
            return key, user, password

    return None, None, None


def load_dll_path(default=None):
    """
    Retorna o caminho absoluto da ProfitDLL.
    """
    cfg = load_config()

    if cfg.has_section("dll"):
        path = cfg.get("dll", "path", fallback=None)
        if path:
            return path

    if default:
        return default

    raise FileNotFoundError(
        "Caminho da ProfitDLL não configurado. "
        "Defina em %APPDATA%/profitcli/profitcli.ini"
    )
