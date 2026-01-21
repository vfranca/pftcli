# profitcli/profitdll/parsers.py
from datetime import datetime
from profitcli.profitdll.models import Trade

def parse_trade_callback(cb) -> Trade | None:
    """
    Converte TNewTradeCallback em Trade.
    Ignora edições de trade.
    """
    if cb.bIsEdit:
        return None

    ts = datetime.strptime(cb.date, "%Y-%m-%d %H:%M:%S")

    return Trade(
        timestamp=ts,
        price=cb.price,
        volume=cb.qtd,
    )
