def format_candle(c):
    return (
        f"{c.start:%Y-%m-%d %H:%M} | "
        f"O={c.open:.2f} "
        f"H={c.high:.2f} "
        f"L={c.low:.2f} "
        f"C={c.close:.2f} "
        f"V={c.volume}"
    )
