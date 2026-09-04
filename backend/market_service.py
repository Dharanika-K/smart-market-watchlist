import yfinance as yf
from datetime import datetime, timezone


def get_stock_data(symbol: str):
    symbol = symbol.upper().strip()

    ticker = yf.Ticker(symbol)

    history = ticker.history(period="5d")

    if history.empty:
        raise ValueError(f"No market data found for {symbol}")

    latest = history.iloc[-1]

    current_price = float(latest["Close"])
    current_volume = int(latest["Volume"])

    previous_history = history.iloc[:-1]

    if len(previous_history) > 0:
        average_volume = float(
            previous_history["Volume"].mean()
        )
    else:
        average_volume = current_volume

    if average_volume > 0:
        volume_ratio = current_volume / average_volume
    else:
        volume_ratio = 1

    return {
        "symbol": symbol,
        "price": current_price,
        "volume": current_volume,
        "average_volume": average_volume,
        "volume_ratio": volume_ratio,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }