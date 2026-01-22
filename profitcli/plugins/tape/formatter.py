from datetime import datetime


def format_trade(evt):
    """
    Formata TradeEvent para saída linear e acessível.
    """
    ts = datetime.fromtimestamp(evt.timestamp).strftime("%H:%M:%S.%f")[:-3]

    side = "BUY" if evt.quantity > 0 else "SELL"
    qty = abs(evt.quantity)

    return (
        f"{ts} "
        f"{evt.ticker} "
        f"{side} "
        f"{qty} @ {evt.price}"
    )
