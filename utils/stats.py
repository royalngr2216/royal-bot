import json
import os

STATS_FILE = "data/player_stats.json"


def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({}, f)

    with open(STATS_FILE, "r") as f:
        return json.load(f)


def save_stats(data):
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def ensure_user(user_id):
    data = load_stats()

    if str(user_id) not in data:
        data[str(user_id)] = {
            "wins": 0,
            "losses": 0,
            "matches": 0,
            "total_won": 0,
            "total_lost": 0
        }
        save_stats(data)

    return data


def record_win(user_id, amount):
    data = ensure_user(user_id)

    data[str(user_id)]["wins"] += 1
    data[str(user_id)]["matches"] += 1
    data[str(user_id)]["total_won"] += amount

    save_stats(data)


def record_loss(user_id, amount):
    data = ensure_user(user_id)

    data[str(user_id)]["losses"] += 1
    data[str(user_id)]["matches"] += 1
    data[str(user_id)]["total_lost"] += amount

    save_stats(data)


def get_profile(user_id):
    data = load_stats()

    if str(user_id) not in data:
        return None

    stats = data[str(user_id)]

    wins = stats["wins"]
    losses = stats["losses"]
    matches = stats["matches"]

    winrate = 0
    if matches > 0:
        winrate = round((wins / matches) * 100, 2)

    return {
        "wins": wins,
        "losses": losses,
        "matches": matches,
        "winrate": winrate,
        "total_won": stats["total_won"],
        "total_lost": stats["total_lost"]
    }
    
def get_leaderboard():
    data = load_stats()

    leaderboard = []

    for user_id, stats in data.items():
        matches = stats["matches"]
        wins = stats["wins"]

        winrate = 0
        if matches > 0:
            winrate = round((wins / matches) * 100, 2)

        leaderboard.append(
            (user_id, matches, winrate)
        )

    # Sort by matches descending
    leaderboard.sort(key=lambda x: x[1], reverse=True)

    return leaderboard[:10]  # Top 10
