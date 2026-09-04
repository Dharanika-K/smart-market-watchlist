from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

print("Mongo URL loaded:", bool(MONGO_URL))

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=10000
)

db = client["smart_market_watchlist"]

users_collection = db["users"]
watchlists_collection = db["watchlists"]
snapshots_collection = db["snapshots"]
market_cache_collection = db["market_cache"]


# Test connection
try:
    client.admin.command("ping")
    print("MongoDB Atlas connected successfully!")

except Exception as e:
    print("MongoDB connection failed:")
    print(e)