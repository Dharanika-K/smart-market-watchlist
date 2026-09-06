import yfinance as yf
from datetime import datetime, timezone


def get_data_status(timestamp):
    try:
        data_time = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        age_seconds = (
            datetime.now(timezone.utc) - data_time
        ).total_seconds()

        if age_seconds <= 60:
            return "FRESH"

        elif age_seconds <= 300:
            return "STALE"

        else:
            return "DELAYED"

    except Exception:
        return "UNKNOWN"
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

    retrieved_at = datetime.now(timezone.utc)

    return {
        "symbol": symbol,
        "price": current_price,
        "volume": current_volume,
        "average_volume": average_volume,
        "volume_ratio": volume_ratio,
        "timestamp": retrieved_at.isoformat(),
        "data_status": get_data_status(
            retrieved_at.isoformat()
        )
    }
def get_market_events(symbol: str):
    symbol = symbol.upper().strip()

    events = {
        "AAPL": [
            {
                "type": "Earnings",
                "title": "Apple earnings update",
                "impact": "HIGH"
            }
        ],
        "NVDA": [
            {
                "type": "AI / Tech",
                "title": "AI semiconductor market activity",
                "impact": "HIGH"
            }
        ],
        "TSLA": [
            {
                "type": "Automotive",
                "title": "Tesla automotive market activity",
                "impact": "MEDIUM"
            }
        ],
        "MSFT": [
            {
                "type": "Technology",
                "title": "Microsoft technology market activity",
                "impact": "MEDIUM"
            }
        ],
        "AMZN": [
            {
                "type": "Retail / Cloud",
                "title": "Amazon business activity",
                "impact": "MEDIUM"
            }
        ]
    }

    return events.get(symbol, [])
