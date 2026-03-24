import os
import json

def _load_json(path, default):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_elo(data_file: str, winner_id: str, loser_id: str, k: int, is_draw: bool = False):
    """Calcule et sauvegarde l'ELO pour un jeu 1v1 (clés : elo/wins/losses/draws)."""
    data = _load_json(data_file, {"messages": {}, "players": {}})
    players = data["players"]
    for uid in [winner_id, loser_id]:
        if uid not in players:
            players[uid] = {"elo": 1000, "wins": 0, "losses": 0, "draws": 0}
    r1, r2 = players[winner_id]["elo"], players[loser_id]["elo"]
    e1 = 1 / (1 + 10 ** ((r2 - r1) / 400))
    e2 = 1 / (1 + 10 ** ((r1 - r2) / 400))
    if is_draw:
        nw, nl = round(r1 + k * (0.5 - e1)), round(r2 + k * (0.5 - e2))
        players[winner_id]["draws"] += 1
        players[loser_id]["draws"] += 1
    else:
        nw, nl = round(r1 + k * (1 - e1)), round(r2 + k * (0 - e2))
        players[winner_id]["wins"] += 1
        players[loser_id]["losses"] += 1
    diff = abs(nw - r1)
    players[winner_id]["elo"] = nw
    players[loser_id]["elo"] = nl
    _save_json(data_file, data)
    return nw, nl, diff
