import os
from pymongo import MongoClient

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["royal_bot"]
stats_collection = db["player_stats"]


def ensure_user(user_id):
    user_id = str(user_id)

    user = stats_collection.find_one({"user_id": user_id})

    if not user:
        user = {
            "user_id": user_id,
            "wins": 0,
            "losses": 0,
            "matches": 0,
            "total_won": 0,
            "total_lost": 0
        }
        stats_collection.insert_one(user)

    return user


def record_win(user_id, amount):
    ensure_user(user_id)

    stats_collection.update_one(
        {"user_id": str(user_id)},
        {
            "$inc": {
                "wins": 1,
                "matches": 1,
                "total_won": amount
            }
        }
    )


def record_loss(user_id, amount):
    ensure_user(user_id)

    stats_collection.update_one(
        {"user_id": str(user_id)},
        {
            "$inc": {
                "losses": 1,
                "matches": 1,
                "total_lost": amount
            }
        }
    )


def get_profile(user_id):
    user = stats_collection.find_one({"user_id": str(user_id)})

    if not user:
        return None

    wins = user["wins"]
    losses = user["losses"]
    matches = user["matches"]

    winrate = 0
    if matches > 0:
        winrate = round((wins / matches) * 100, 2)

    return {
        "wins": wins,
        "losses": losses,
        "matches": matches,
        "winrate": winrate,
        "total_won": user["total_won"],
        "total_lost": user["total_lost"]
    }


def get_leaderboard():
    users = stats_collection.find()

    leaderboard = []

    for user in users:
        matches = user["matches"]
        wins = user["wins"]

        winrate = 0
        if matches > 0:
            winrate = round((wins / matches) * 100, 2)

        leaderboard.append(
            (user["user_id"], matches, winrate)
        )

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    return leaderboard[:10]
