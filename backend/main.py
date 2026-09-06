from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import (
    watchlists_collection,
    snapshots_collection
)
from models import WatchlistCreate, AddStock
from market_service import get_stock_data, get_market_events
from change_engine import calculate_change
from datetime import datetime, timezone
from bson import ObjectId

app = FastAPI(title="Smart Market Watchlist API")


# ---------------------------------------
# CORS
# ---------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------
# HOME
# ---------------------------------------

@app.get("/")
def home():

    return {
        "message": "Smart Market Watchlist API",
        "status": "running"
    }


# ---------------------------------------
# CREATE WATCHLIST
# ---------------------------------------

@app.post("/watchlists")
def create_watchlist(data: WatchlistCreate):

    watchlist = {
        "name": data.name,
        "symbols": [],
        "created_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    result = watchlists_collection.insert_one(
        watchlist
    )

    return {
        "id": str(result.inserted_id),
        "name": data.name,
        "symbols": []
    }


# ---------------------------------------
# GET WATCHLISTS
# ---------------------------------------

@app.get("/watchlists")
def get_watchlists():

    watchlists = []

    for item in watchlists_collection.find():

        watchlists.append({
            "id": str(item["_id"]),
            "name": item["name"],
            "symbols": item.get(
                "symbols",
                []
            )
        })

    return watchlists


# ---------------------------------------
# ADD STOCK
# ---------------------------------------

@app.post("/watchlists/{watchlist_id}/stocks")
@app.post("/watchlists/{watchlist_id}/stocks")
def add_stock(watchlist_id: str, data: AddStock):
    symbol = data.symbol.upper().strip()

    if not symbol:
        raise HTTPException(
            status_code=400,
            detail="Stock symbol cannot be empty"
        )

    try:
        watchlist = watchlists_collection.find_one(
            {"_id": ObjectId(watchlist_id)}
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid watchlist ID"
        )

    if not watchlist:
        raise HTTPException(
            status_code=404,
            detail="Watchlist not found"
        )

    # Check whether the stock already exists
    if symbol in watchlist.get("symbols", []):
        raise HTTPException(
            status_code=400,
            detail=f"{symbol} is already in this watchlist"
        )

    # Validate the symbol using market data
    try:
        get_stock_data(symbol)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"{symbol} is not a valid or supported stock symbol"
        )

    # Add only after successful validation
    watchlists_collection.update_one(
        {"_id": ObjectId(watchlist_id)},
        {"$push": {"symbols": symbol}}
    )

    return {
        "message": f"{symbol} added",
        "symbol": symbol
    }

# ---------------------------------------
# REMOVE STOCK
# ---------------------------------------

@app.delete(
    "/watchlists/{watchlist_id}/stocks/{symbol}"
)
def remove_stock(
    watchlist_id: str,
    symbol: str
):

    watchlists_collection.update_one(
        {"_id": ObjectId(watchlist_id)},
        {
            "$pull": {
                "symbols": symbol.upper()
            }
        }
    )

    return {
        "message": f"{symbol.upper()} removed"
    }


# ---------------------------------------
# GET CURRENT STOCK
# ---------------------------------------
@app.get("/stocks/search")
def search_stocks(q: str):
    stocks = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "AMZN", "name": "Amazon.com Inc."},
        {"symbol": "GOOGL", "name": "Alphabet Inc."},
        {"symbol": "META", "name": "Meta Platforms Inc."},
        {"symbol": "AMD", "name": "Advanced Micro Devices Inc."},
        {"symbol": "NFLX", "name": "Netflix Inc."},
        {"symbol": "INTC", "name": "Intel Corporation"},
        {"symbol": "ORCL", "name": "Oracle Corporation"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
        {"symbol": "V", "name": "Visa Inc."},
        {"symbol": "WMT", "name": "Walmart Inc."},
        {"symbol": "DIS", "name": "The Walt Disney Company"},
    ]

    query = q.strip().lower()

    if not query:
        return []

    results = [
        stock
        for stock in stocks
        if query in stock["symbol"].lower()
        or query in stock["name"].lower()
    ]

    return results[:8]
@app.get("/stocks/{symbol}/history")
def get_stock_history(symbol: str):
    try:
        import yfinance as yf

        symbol = symbol.upper().strip()

        ticker = yf.Ticker(symbol)
        history = ticker.history(period="5d", interval="1h")

        if history.empty:
            raise ValueError(f"No market history found for {symbol}")

        result = []

        for index, row in history.iterrows():
            result.append({
                "time": index.strftime("%Y-%m-%d %H:%M"),
                "price": round(float(row["Close"]), 2)
            })

        return {
            "symbol": symbol,
            "history": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@app.get("/stocks/{symbol}/events")
def get_stock_events(symbol: str):
    try:
        return {
            "symbol": symbol.upper(),
            "events": get_market_events(symbol)
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.get("/stocks/{symbol}")
def get_stock(symbol: str):

    try:

        return get_stock_data(
            symbol.upper()
        )

    except Exception as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ---------------------------------------
# GET CHANGES
# ---------------------------------------

@app.get(
    "/watchlists/{watchlist_id}/changes"
)
def get_changes(
    watchlist_id: str
):

    try:

        watchlist = watchlists_collection.find_one(
            {"_id": ObjectId(watchlist_id)}
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid watchlist ID"
        )

    if not watchlist:

        raise HTTPException(
            status_code=404,
            detail="Watchlist not found"
        )

    results = []

    for symbol in watchlist.get(
        "symbols",
        []
    ):

        try:

            current = get_stock_data(symbol)

            previous = snapshots_collection.find_one(
                {
                    "watchlist_id": watchlist_id,
                    "symbol": symbol
                },
                sort=[
                    ("checked_at", -1)
                ]
            )

            previous_price = (
                previous["price"]
                if previous
                else None
            )
            last_checked = previous["checked_at"] if previous else None

            events = get_market_events(symbol)

            change = calculate_change(
                current_price=current["price"],
                previous_price=previous_price,
                current_volume=current["volume"],
                average_volume=current["average_volume"],
                events=events
            )

            results.append({
                "symbol": symbol,
                "current_price": current["price"],
                "previous_price": previous_price,
                "current_volume": current["volume"],
                "last_checked": last_checked,
                "data_status": current.get("data_status", "UNKNOWN"),
                "data_timestamp": current.get("timestamp"),
                **change
            })

        except Exception as e:

            results.append({
                "symbol": symbol,
                "error": str(e)
            })

    return results


# ---------------------------------------
# MARK STOCK AS CHECKED
# ---------------------------------------

@app.post(
    "/watchlists/{watchlist_id}/stocks/{symbol}/check"
)
def mark_checked(
    watchlist_id: str,
    symbol: str
):

    symbol = symbol.upper()

    current = get_stock_data(symbol)

    snapshot = {
        "watchlist_id": watchlist_id,
        "symbol": symbol,
        "price": current["price"],
        "volume": current["volume"],
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    snapshots_collection.insert_one(
        snapshot
    )

    return {
        "message": "Stock marked as checked",
        "symbol": symbol,
        "price": current["price"]
    }