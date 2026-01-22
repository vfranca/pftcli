from configparser import ConfigParser
from pathlib import Path
import os

CONFIG_DIR = Path.cwd()
CONFIG_FILE = CONFIG_DIR / "profitcli.ini"


def load_config():
    parser = ConfigParser()

    if CONFIG_FILE.exists():
        parser.read(CONFIG_FILE, encoding="utf-8")

    return parser


def load_credentials():
    """
    Ordem:
    1) ENV
    2) profitcli.ini
    """
    # ENV primeiro
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


def load_dll_path(default="./ProfitDLL.dll"):
    cfg = load_config()

    if cfg.has_section("dll"):
        return cfg.get("dll", "path", fallback=default)

    return default
