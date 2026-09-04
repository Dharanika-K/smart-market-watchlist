from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import (
    watchlists_collection,
    snapshots_collection
)
from models import WatchlistCreate, AddStock
from market_service import get_stock_data
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
def add_stock(
    watchlist_id: str,
    data: AddStock
):

    symbol = data.symbol.upper().strip()

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

    if symbol not in watchlist.get(
        "symbols",
        []
    ):

        watchlists_collection.update_one(
            {"_id": ObjectId(watchlist_id)},
            {
                "$push": {
                    "symbols": symbol
                }
            }
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

            change = calculate_change(
                current_price=current["price"],
                previous_price=previous_price,
                current_volume=current["volume"],
                average_volume=current["average_volume"]
            )

            results.append({
                "symbol": symbol,
                "current_price": current["price"],
                "previous_price": previous_price,
                "current_volume": current["volume"],
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