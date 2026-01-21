from .aggregator import Candle


def format_candle(candle: Candle) -> str:
    """
    Formato simples e acessível.
    Uma linha por candle.
    """
    ts = candle.start.strftime("%H:%M:%S")
    return (
        f"{ts} | "
        f"O {candle.open:.2f} "
        f"H {candle.high:.2f} "
        f"L {candle.low:.2f} "
        f"C {candle.close:.2f} "
        f"V {candle.volume}"
    )
