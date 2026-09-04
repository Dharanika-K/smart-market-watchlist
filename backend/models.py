from pydantic import BaseModel
from typing import List, Optional


class WatchlistCreate(BaseModel):
    name: str


class AddStock(BaseModel):
    symbol: str


class WatchlistResponse(BaseModel):
    id: str
    name: str
    symbols: List[str]


class Snapshot(BaseModel):
    symbol: str
    price: float
    volume: int
    checked_at: str


class ChangeResult(BaseModel):
    symbol: str
    current_price: float
    previous_price: Optional[float]
    price_change_percent: float
    current_volume: int
    volume_ratio: float
    change_score: int
    severity: str
    reasons: List[str]