import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import time
import asyncio
import random
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════
WELCOME_CHANNEL_ID       = 1475325945001807952
ROULETTE_CHANNEL_ID      = 1480224572275032135
BLACKJACK_CHANNEL_ID     = 1480224707575021769
POKER_CHANNEL_ID         = 1480224841830236331
LEADERBOARD_MESSAGE_ID   = 1480299300356362270   # message fixe du classement
CASINO_FILE              = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "casino.json")

ROULETTE_RED   = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
ROULETTE_BLACK = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
ROULETTE_COLORS = {0: "🟢", **{n: "🔴" for n in ROULETTE_RED}, **{n: "⚫" for n in ROULETTE_BLACK}}

PANEL_CHANNEL_MAP = {
    "welcome":     WELCOME_CHANNEL_ID,
    "leaderboard": WELCOME_CHANNEL_ID,
    "guide":       WELCOME_CHANNEL_ID,
    "roulette":    ROULETTE_CHANNEL_ID,
    "blackjack":   BLACKJACK_CHANNEL_ID,
}

# ── GANG RANKS DEFINITIONS ────────────────────────────────
# 7 regular categories × 10 tiers — FB bonuses double each tier: 250, 500 … 128000
# + 1 special synergy category (auto-unlocks when all 7 are at same tier)
_TIER_BONUSES     = [250, 500, 1_000, 2_000, 4_000, 8_000, 16_000, 32_000, 64_000, 128_000]
_JETON_THRESHOLDS = [1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000, 100_000_000]
_GAMES_THRESHOLDS = [10, 50, 200, 500, 1_000, 5_000, 10_000, 25_000, 50_000, 100_000]

GANG_RANKS = {
    # ── Wagered (jetons/freebets) ──────────────────────────
    "roulette": {
        _JETON_THRESHOLDS[0]:  {"label": "Mule",              "emoji": "🐴", "bonus": _TIER_BONUSES[0]},
        _JETON_THRESHOLDS[1]:  {"label": "Passeur",           "emoji": "🚶", "bonus": _TIER_BONUSES[1]},
        _JETON_THRESHOLDS[2]:  {"label": "Dealer",            "emoji": "📦", "bonus": _TIER_BONUSES[2]},
        _JETON_THRESHOLDS[3]:  {"label": "Revendeur",         "emoji": "💊", "bonus": _TIER_BONUSES[3]},
        _JETON_THRESHOLDS[4]:  {"label": "Distributor",       "emoji": "🚛", "bonus": _TIER_BONUSES[4]},
        _JETON_THRESHOLDS[5]:  {"label": "Fournisseur",       "emoji": "🏭", "bonus": _TIER_BONUSES[5]},
        _JETON_THRESHOLDS[6]:  {"label": "Lieutenant",        "emoji": "⚓", "bonus": _TIER_BONUSES[6]},
        _JETON_THRESHOLDS[7]:  {"label": "Commandant",        "emoji": "🎯", "bonus": _TIER_BONUSES[7]},
        _JETON_THRESHOLDS[8]:  {"label": "El Jefe",           "emoji": "🔥", "bonus": _TIER_BONUSES[8]},
        _JETON_THRESHOLDS[9]:  {"label": "El Patron",         "emoji": "👑", "bonus": _TIER_BONUSES[9]},
    },
    "blackjack": {
        _JETON_THRESHOLDS[0]:  {"label": "Nobody",            "emoji": "👤", "bonus": _TIER_BONUSES[0]},
        _JETON_THRESHOLDS[1]:  {"label": "Apprenti",          "emoji": "🃏", "bonus": _TIER_BONUSES[1]},
        _JETON_THRESHOLDS[2]:  {"label": "Associate",         "emoji": "🤝", "bonus": _TIER_BONUSES[2]},
        _JETON_THRESHOLDS[3]:  {"label": "Soldato",           "emoji": "🔫", "bonus": _TIER_BONUSES[3]},
        _JETON_THRESHOLDS[4]:  {"label": "Capodecina",        "emoji": "🎩", "bonus": _TIER_BONUSES[4]},
        _JETON_THRESHOLDS[5]:  {"label": "Capo",              "emoji": "👔", "bonus": _TIER_BONUSES[5]},
        _JETON_THRESHOLDS[6]:  {"label": "Underboss",         "emoji": "💼", "bonus": _TIER_BONUSES[6]},
        _JETON_THRESHOLDS[7]:  {"label": "Consigliere",       "emoji": "⚖️", "bonus": _TIER_BONUSES[7]},
        _JETON_THRESHOLDS[8]:  {"label": "Boss dei Bossi",    "emoji": "🎭", "bonus": _TIER_BONUSES[8]},
        _JETON_THRESHOLDS[9]:  {"label": "Don",               "emoji": "🍷", "bonus": _TIER_BONUSES[9]},
    },
    "slots": {
        _JETON_THRESHOLDS[0]:  {"label": "Flambeur",            "emoji": "💸", "bonus": _TIER_BONUSES[0]},
        _JETON_THRESHOLDS[1]:  {"label": "Miseur",              "emoji": "🎰", "bonus": _TIER_BONUSES[1]},
        _JETON_THRESHOLDS[2]:  {"label": "Addict des Slots",    "emoji": "🃏", "bonus": _TIER_BONUSES[2]},
        _JETON_THRESHOLDS[3]:  {"label": "Grand Joueur",        "emoji": "⭐", "bonus": _TIER_BONUSES[3]},
        _JETON_THRESHOLDS[4]:  {"label": "Haut Rouleur",        "emoji": "💎", "bonus": _TIER_BONUSES[4]},
        _JETON_THRESHOLDS[5]:  {"label": "Briseur de Banque",   "emoji": "🏛️", "bonus": _TIER_BONUSES[5]},
        _JETON_THRESHOLDS[6]:  {"label": "Nabab",               "emoji": "🏅", "bonus": _TIER_BONUSES[6]},
        _JETON_THRESHOLDS[7]:  {"label": "Magnat des Machines", "emoji": "🏆", "bonus": _TIER_BONUSES[7]},
        _JETON_THRESHOLDS[8]:  {"label": "Sultan des Slots",    "emoji": "👑", "bonus": _TIER_BONUSES[8]},
        _JETON_THRESHOLDS[9]:  {"label": "Légende des Jackpots","emoji": "🌈", "bonus": _TIER_BONUSES[9]},
    },
    "total_bet": {
        _JETON_THRESHOLDS[0]:  {"label": "Pickpocket",        "emoji": "🕵️", "bonus": _TIER_BONUSES[0]},
        _JETON_THRESHOLDS[1]:  {"label": "Escroc",            "emoji": "🎭", "bonus": _TIER_BONUSES[1]},
        _JETON_THRESHOLDS[2]:  {"label": "Arnaqueur",         "emoji": "🎪", "bonus": _TIER_BONUSES[2]},
        _JETON_THRESHOLDS[3]:  {"label": "Scammeur",          "emoji": "💻", "bonus": _TIER_BONUSES[3]},
        _JETON_THRESHOLDS[4]:  {"label": "Manipulateur",      "emoji": "🧲", "bonus": _TIER_BONUSES[4]},
        _JETON_THRESHOLDS[5]:  {"label": "Cerveau",           "emoji": "🧠", "bonus": _TIER_BONUSES[5]},
        _JETON_THRESHOLDS[6]:  {"label": "Stratège",          "emoji": "♟️", "bonus": _TIER_BONUSES[6]},
        _JETON_THRESHOLDS[7]:  {"label": "Chef",              "emoji": "👨‍🍳", "bonus": _TIER_BONUSES[7]},
        _JETON_THRESHOLDS[8]:  {"label": "Parrain",           "emoji": "🎩", "bonus": _TIER_BONUSES[8]},
        _JETON_THRESHOLDS[9]:  {"label": "Caïd",              "emoji": "⛓️", "bonus": _TIER_BONUSES[9]},
    },
    # ── Fortune ───────────────────────────────────────────
    "holdings": {
        _JETON_THRESHOLDS[0]:  {"label": "Sans-le-sou",       "emoji": "📖", "bonus": _TIER_BONUSES[0]},
        _JETON_THRESHOLDS[1]:  {"label": "Livreur",           "emoji": "🎒", "bonus": _TIER_BONUSES[1]},
        _JETON_THRESHOLDS[2]:  {"label": "Contrebandier",     "emoji": "🧥", "bonus": _TIER_BONUSES[2]},
        _JETON_THRESHOLDS[3]:  {"label": "Trafiquant",        "emoji": "💰", "bonus": _TIER_BONUSES[3]},
        _JETON_THRESHOLDS[4]:  {"label": "Marchand Noir",     "emoji": "🏴", "bonus": _TIER_BONUSES[4]},
        _JETON_THRESHOLDS[5]:  {"label": "Marchand d'armes",  "emoji": "🚀", "bonus": _TIER_BONUSES[5]},
        _JETON_THRESHOLDS[6]:  {"label": "Oligarque",         "emoji": "🏰", "bonus": _TIER_BONUSES[6]},
        _JETON_THRESHOLDS[7]:  {"label": "Maître de l'arsenal","emoji": "🛡️","bonus": _TIER_BONUSES[7]},
        _JETON_THRESHOLDS[8]:  {"label": "Magnat",            "emoji": "💎", "bonus": _TIER_BONUSES[8]},
        _JETON_THRESHOLDS[9]:  {"label": "Seigneur de guerre","emoji": "⚔️", "bonus": _TIER_BONUSES[9]},
    },
    # ── Games played (roulette + blackjack only, no poker) ─
    "games_roulette": {
        _GAMES_THRESHOLDS[0]:  {"label": "Touriste",          "emoji": "🌱", "bonus": _TIER_BONUSES[0]},
        _GAMES_THRESHOLDS[1]:  {"label": "Pariant",           "emoji": "🎡", "bonus": _TIER_BONUSES[1]},
        _GAMES_THRESHOLDS[2]:  {"label": "Chanceux",          "emoji": "🍀", "bonus": _TIER_BONUSES[2]},
        _GAMES_THRESHOLDS[3]:  {"label": "Roulettiste",       "emoji": "🎲", "bonus": _TIER_BONUSES[3]},
        _GAMES_THRESHOLDS[4]:  {"label": "Croupier",          "emoji": "🎰", "bonus": _TIER_BONUSES[4]},
        _GAMES_THRESHOLDS[5]:  {"label": "Pro de la Roue",    "emoji": "⭐", "bonus": _TIER_BONUSES[5]},
        _GAMES_THRESHOLDS[6]:  {"label": "Maître du Zéro",    "emoji": "🎯", "bonus": _TIER_BONUSES[6]},
        _GAMES_THRESHOLDS[7]:  {"label": "Roi de la Table",   "emoji": "👁️", "bonus": _TIER_BONUSES[7]},
        _GAMES_THRESHOLDS[8]:  {"label": "Légende du Tapis",  "emoji": "🔱", "bonus": _TIER_BONUSES[8]},
        _GAMES_THRESHOLDS[9]:  {"label": "Dieu de la Roue",   "emoji": "🌈", "bonus": _TIER_BONUSES[9]},
    },
    "games_blackjack": {
        _GAMES_THRESHOLDS[0]:  {"label": "Novice",            "emoji": "🌱", "bonus": _TIER_BONUSES[0]},
        _GAMES_THRESHOLDS[1]:  {"label": "Compteur débutant", "emoji": "🃏", "bonus": _TIER_BONUSES[1]},
        _GAMES_THRESHOLDS[2]:  {"label": "Stratège junior",   "emoji": "🎮", "bonus": _TIER_BONUSES[2]},
        _GAMES_THRESHOLDS[3]:  {"label": "Card Counter",      "emoji": "🏅", "bonus": _TIER_BONUSES[3]},
        _GAMES_THRESHOLDS[4]:  {"label": "21 Addict",         "emoji": "♠️", "bonus": _TIER_BONUSES[4]},
        _GAMES_THRESHOLDS[5]:  {"label": "Shark",             "emoji": "🦈", "bonus": _TIER_BONUSES[5]},
        _GAMES_THRESHOLDS[6]:  {"label": "Maître du 21",      "emoji": "🏆", "bonus": _TIER_BONUSES[6]},
        _GAMES_THRESHOLDS[7]:  {"label": "Imbattable",        "emoji": "🌟", "bonus": _TIER_BONUSES[7]},
        _GAMES_THRESHOLDS[8]:  {"label": "Légende du Blackjack","emoji": "🔱","bonus": _TIER_BONUSES[8]},
        _GAMES_THRESHOLDS[9]:  {"label": "Rain Man",          "emoji": "🌈", "bonus": _TIER_BONUSES[9]},
    },
    "games_slots": {
        _GAMES_THRESHOLDS[0]:  {"label": "Badaud",               "emoji": "🌱", "bonus": _TIER_BONUSES[0]},
        _GAMES_THRESHOLDS[1]:  {"label": "Tourneur",             "emoji": "🎰", "bonus": _TIER_BONUSES[1]},
        _GAMES_THRESHOLDS[2]:  {"label": "Spinner",              "emoji": "🎲", "bonus": _TIER_BONUSES[2]},
        _GAMES_THRESHOLDS[3]:  {"label": "Addict",               "emoji": "🃏", "bonus": _TIER_BONUSES[3]},
        _GAMES_THRESHOLDS[4]:  {"label": "Roi des Rouleaux",     "emoji": "⚡", "bonus": _TIER_BONUSES[4]},
        _GAMES_THRESHOLDS[5]:  {"label": "Virtuose du Spin",     "emoji": "⭐", "bonus": _TIER_BONUSES[5]},
        _GAMES_THRESHOLDS[6]:  {"label": "Maître des Machines",  "emoji": "🏆", "bonus": _TIER_BONUSES[6]},
        _GAMES_THRESHOLDS[7]:  {"label": "Seigneur des Slots",   "emoji": "🌟", "bonus": _TIER_BONUSES[7]},
        _GAMES_THRESHOLDS[8]:  {"label": "Architecte du Jackpot","emoji": "🔱", "bonus": _TIER_BONUSES[8]},
        _GAMES_THRESHOLDS[9]:  {"label": "Dieu des Machines",    "emoji": "🌈", "bonus": _TIER_BONUSES[9]},
    },
    "total_games": {
        _GAMES_THRESHOLDS[0]:  {"label": "Curieux",           "emoji": "🌱", "bonus": _TIER_BONUSES[0]},
        _GAMES_THRESHOLDS[1]:  {"label": "Habitué",           "emoji": "🎲", "bonus": _TIER_BONUSES[1]},
        _GAMES_THRESHOLDS[2]:  {"label": "Joueur",            "emoji": "🎮", "bonus": _TIER_BONUSES[2]},
        _GAMES_THRESHOLDS[3]:  {"label": "Vétéran",           "emoji": "🏅", "bonus": _TIER_BONUSES[3]},
        _GAMES_THRESHOLDS[4]:  {"label": "Pro",               "emoji": "⭐", "bonus": _TIER_BONUSES[4]},
        _GAMES_THRESHOLDS[5]:  {"label": "Expert",            "emoji": "🌟", "bonus": _TIER_BONUSES[5]},
        _GAMES_THRESHOLDS[6]:  {"label": "Maître",            "emoji": "🏆", "bonus": _TIER_BONUSES[6]},
        _GAMES_THRESHOLDS[7]:  {"label": "Grand Maître",      "emoji": "👁️", "bonus": _TIER_BONUSES[7]},
        _GAMES_THRESHOLDS[8]:  {"label": "Légende",           "emoji": "🔱", "bonus": _TIER_BONUSES[8]},
        _GAMES_THRESHOLDS[9]:  {"label": "Immortel",          "emoji": "🌈", "bonus": _TIER_BONUSES[9]},
    },
}

# Labels for the auto-unlocking synergy category (tier N unlocks when all 7 categories have tier N)
_SYNERGY_LABELS = [
    ("Alliance I",    "🤝"), ("Alliance II",   "🤝"), ("Pacte III",    "🔗"),
    ("Pacte IV",      "🔗"), ("Cartel V",      "💼"), ("Cartel VI",    "💼"),
    ("Syndicat VII",  "⚜️"), ("Syndicat VIII", "⚜️"), ("Empire IX",   "🌐"),
    ("Empire X",      "🌐"),
]

MAFIA_NPCS = [
    {"name": "Pablo Escobar", "balance": 100000000, "rank": "El Patron", "emoji": "👑"},
    {"name": "El Chapo",      "balance": 10000000,  "rank": "El Jefe",   "emoji": "🔥"},
    {"name": "Al Capone",     "balance": 5000000,   "rank": "Don",       "emoji": "🍷"},
    {"name": "Frank Lucas",   "balance": 1000000,   "rank": "Cerveau",   "emoji": "🧠"},
    {"name": "John Gotti",    "balance": 500000,    "rank": "Capo",      "emoji": "👔"},
]

# ═══════════════════════════════════════════════════════════
#  PERSISTENCE HELPERS
# ═══════════════════════════════════════════════════════════
def load_casino() -> dict:
    if not os.path.exists(CASINO_FILE):
        os.makedirs(os.path.dirname(CASINO_FILE), exist_ok=True)
        return {"players": {}, "messages": {}, "roulette_history": []}
    
    try:
        with open(CASINO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {"players": {}, "messages": {}, "roulette_history": []}
        save_casino(data)
        
    if "players" not in data: data["players"] = {}
    if "messages" not in data: data["messages"] = {}
    if "roulette_history" not in data: data["roulette_history"] = []
    if "seated" not in data: data["seated"] = {}
    if "roulette_seats" not in data: data["roulette_seats"] = []
    # Seed le message ID du classement si absent (message fixe Discord)
    data["messages"].setdefault("leaderboard", LEADERBOARD_MESSAGE_ID)
    
    for uid in data["players"]:
        p = data["players"][uid]
        if "total_wagered_roulette" not in p:   p["total_wagered_roulette"] = 0
        if "total_wagered_blackjack" not in p:  p["total_wagered_blackjack"] = 0
        if "total_wagered_slots" not in p:      p["total_wagered_slots"] = 0
        if "total_games_roulette" not in p:     p["total_games_roulette"] = 0
        if "total_games_blackjack" not in p:    p["total_games_blackjack"] = 0
        if "total_games_slots" not in p:        p["total_games_slots"] = 0
        if "cash_streak" not in p:              p["cash_streak"] = 0
        if "freebets" not in p:                 p["freebets"] = 0
        if "selected_title" not in p:           p["selected_title"] = "Petit Joueur"
        if "currency" not in p:                 p["currency"] = "Freebets"
        if "max_balance" not in p:              p["max_balance"] = p.get("balance", 0)
    return data

def get_seated_game(uid: str, data: dict) -> str | None:
    """Returns the game the player is currently seated at, or None."""
    return data.get("seated", {}).get(str(uid))

def set_seated_game(uid: str, game: str | None, data: dict):
    """Set or clear the seated game for a player (must call save_casino after)."""
    seated = data.setdefault("seated", {})
    if game is None:
        seated.pop(str(uid), None)
    else:
        seated[str(uid)] = game

def save_casino(data: dict):
    os.makedirs(os.path.dirname(CASINO_FILE), exist_ok=True)
    with open(CASINO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_balance(user_id) -> int:
    data = load_casino()
    return data["players"].get(str(user_id), {}).get("balance", 0)

def add_balance(user_id, amount: int, username: str = None):
    data = load_casino()
    uid  = str(user_id)
    _ensure_player(data, uid)
    if username:
        data["players"][uid]["username"] = username
    data["players"][uid]["balance"] += amount
    if data["players"][uid]["balance"] > data["players"][uid].get("max_balance", 0):
        data["players"][uid]["max_balance"] = data["players"][uid]["balance"]
    save_casino(data)

def _ensure_player(data: dict, uid: str):
    if uid not in data["players"]:
        data["players"][uid] = {
            "balance": 0, "freebets": 0,
            "total_wagered_roulette": 0, "total_wagered_blackjack": 0, "total_wagered_slots": 0,
            "total_games_roulette": 0, "total_games_blackjack": 0, "total_games_slots": 0,
            "cash_streak": 0,
        }

def add_wager(user_id, amount: int, game_type: str, username: str = None):
    data = load_casino()
    uid  = str(user_id)
    _ensure_player(data, uid)
    if username:
        data["players"][uid]["username"] = username
    if game_type == "roulette":
        data["players"][uid]["total_wagered_roulette"] += amount
    elif game_type == "blackjack":
        data["players"][uid]["total_wagered_blackjack"] += amount
    elif game_type == "slots":
        data["players"][uid]["total_wagered_slots"] = data["players"][uid].get("total_wagered_slots", 0) + amount
    save_casino(data)

def add_game_count(user_id, game_type: str, username: str = None):
    """Call once per completed game/round to increment total_games counters."""
    data = load_casino()
    uid  = str(user_id)
    _ensure_player(data, uid)
    if username:
        data["players"][uid]["username"] = username
    key = f"total_games_{game_type}"
    data["players"][uid][key] = data["players"][uid].get(key, 0) + 1
    save_casino(data)

def get_player_stats(user_id, data: dict) -> dict:
    uid = str(user_id)
    p = data.get("players", {}).get(uid, {})
    wag_r     = p.get("total_wagered_roulette", 0)
    wag_b     = p.get("total_wagered_blackjack", 0)
    wag_s     = p.get("total_wagered_slots", 0)
    total_wag = wag_r + wag_b + wag_s
    balance   = p.get("balance", 0)
    games_r     = p.get("total_games_roulette", 0)
    games_b     = p.get("total_games_blackjack", 0)
    games_s     = p.get("total_games_slots", 0)
    total_games = games_r + games_b + games_s

    def _cat_val(cat):
        if cat == "roulette":       return wag_r
        if cat == "blackjack":      return wag_b
        if cat == "slots":          return wag_s
        if cat == "total_bet":      return total_wag        # roulette + blackjack + slots
        if cat == "holdings":       return p.get("max_balance", balance)
        if cat == "games_roulette": return games_r
        if cat == "games_blackjack":return games_b
        if cat == "games_slots":    return games_s
        if cat == "total_games":    return total_games
        return 0

    unlocked_titles = []
    category_progress = {}
    tiers_per_cat = {}   # cat -> number of tiers completed
    titles_fb = 0        # sum of HIGHEST unlocked tier bonus per category (not cumulative)

    for cat, ranks in GANG_RANKS.items():
        val = _cat_val(cat)
        sorted_thresh = sorted(ranks.keys())
        cat_prog = []
        cat_tiers_done = 0
        highest_bonus = 0
        for i, thresh in enumerate(sorted_thresh):
            info = ranks[thresh]
            is_unlocked = val >= thresh
            if is_unlocked:
                unlocked_titles.append(info["label"])
                highest_bonus = info["bonus"]   # keep updating — last one wins (highest tier)
                cat_tiers_done += 1
            cat_prog.append({
                "label": info["label"], "emoji": info["emoji"],
                "threshold": thresh, "is_unlocked": is_unlocked, "bonus": info["bonus"],
                "tier_index": i,
            })
        titles_fb += highest_bonus  # only the highest tier bonus contributes
        category_progress[cat] = {"current": val, "max": sorted_thresh[-1], "ranks": cat_prog}
        tiers_per_cat[cat] = cat_tiers_done

    # Synergy category: tier N unlocks when ALL 7 regular categories have tier N
    completed_global_tiers = min(tiers_per_cat.values()) if tiers_per_cat else 0
    synergy_ranks = []
    for i, (label, emoji) in enumerate(_SYNERGY_LABELS):
        is_unlocked = completed_global_tiers > i
        synergy_ranks.append({"label": label, "emoji": emoji, "tier_index": i, "is_unlocked": is_unlocked})
    # Linear multiplier: ×1.1 at tier 1, ×1.2 at tier 2 … ×2.0 at tier 10
    global_mult = 1.0 + 0.1 * completed_global_tiers
    tier_cd_min = completed_global_tiers * 5

    # Leaderboard rank
    combined = [{"id": _uid, "balance": _p.get("balance", 0), "freebets": _p.get("freebets", 0)}
                for _uid, _p in data.get("players", {}).items()]
    for npc in MAFIA_NPCS:
        combined.append({"id": "npc", "balance": npc["balance"], "freebets": 0})
    combined.sort(key=lambda x: (x["balance"], x["freebets"]), reverse=True)
    rank = next((i + 1 for i, item in enumerate(combined) if item["id"] == uid), 999)

    # Special rank titles give a fraction of total FB as real jetons (no FB bonus, no CD reduction)
    # Bras Droit (top 3) = 1/4 of total_fb in jetons
    # Boss (top 1)       = 3/4 of total_fb in jetons
    # Cumulative: rank 1 gets both → 1.0× total_fb in jetons
    rank_title = None
    jeton_frac = 0.0
    if rank == 1:
        rank_title  = "Boss"
        jeton_frac  = 1.0   # Boss (3/4) + Bras Droit (1/4)
    elif rank <= 3:
        rank_title  = "Bras Droit"
        jeton_frac  = 0.25  # Bras Droit only

    # Cooldown: only synergy reduces it (no rank CD reduction)
    cooldown = max(600, 3600 - (tier_cd_min * 60))

    # streak (read-only here — updated in cash_btn)
    # Linear multiplier: ×1.1 at streak 1 … ×2.0 at streak 10
    cash_streak = p.get("cash_streak", 0)
    streak_mult = 1.0 + 0.1 * cash_streak

    # base_total = 1000 (base) + titles_fb (highest tier per category)
    # No rank FB bonus — rank gives jetons instead
    base_total = 1000 + titles_fb
    total_fb_after_global = base_total * global_mult
    total_fb_after_streak = total_fb_after_global * streak_mult

    return {
        "unlocked_titles": unlocked_titles,
        "completed_global_tiers": completed_global_tiers,
        "global_mult": global_mult,
        "rank": rank, "rank_title": rank_title,
        "titles_fb": titles_fb,
        "tier_cd_min": tier_cd_min,
        "jeton_frac": jeton_frac,
        "cooldown": cooldown,
        "base_total": base_total,
        "total_fb_after_global": total_fb_after_global,
        "total_fb_after_streak": total_fb_after_streak,
        "cash_streak": cash_streak,
        "streak_mult": streak_mult,
        "category_progress": category_progress,
        "tiers_per_cat": tiers_per_cat,
        "synergy_ranks": synergy_ranks,
    }

# ── GANG VIEWS ──────────────────────────────────
# ── GANG CATEGORY LIST ────────────────────────────────────
_CATEGORIES = [
    ("roulette",        "🎡", "Roulette Misé",        "Total misé à la roulette"),
    ("blackjack",       "🃏", "Blackjack Misé",        "Total misé au blackjack"),
    ("slots",           "🎰", "Slots Misé",            "Total misé aux machines à sous"),
    ("total_bet",       "💰", "Total Misé",            "Roulette + Blackjack + Slots"),
    ("holdings",        "🏦", "Fortune",               "Record de jetons 🪙 détenus"),
    ("games_roulette",  "🎡", "Parties Roulette",      "Parties jouées à la roulette"),
    ("games_blackjack", "🃏", "Parties Blackjack",     "Parties jouées au blackjack"),
    ("games_slots",     "🎰", "Parties Slots",         "Parties jouées aux machines à sous"),
    ("total_games",     "🎮", "Total Parties",         "Roulette + Blackjack + Slots"),
]

def _fmt_val(n: int) -> str:
    return f"{n:,}".replace(",", " ")

def _build_gang_overview_embed(stats: dict, user) -> discord.Embed:
    embed = discord.Embed(
        title="🏢  CENTRAL DU GANG",
        description=(
            "**9 catégories × 10 paliers** — chaque palier débloqué ajoute des Freebets 🎟️.\n"
            "**✨ Synergie** : même palier dans les 9 catégories → ×1.1 FB & −5 min ⏳ par niveau.\n"
        ),
        color=discord.Color.from_rgb(180, 140, 80),
    )
    for cat_key, cat_emoji, cat_name, _cat_desc in _CATEGORIES:
        tiers = stats["tiers_per_cat"][cat_key]
        current = stats["category_progress"][cat_key]["current"]
        next_thresh = None
        for tier_info in stats["category_progress"][cat_key]["ranks"]:
            if not tier_info["is_unlocked"]:
                next_thresh = tier_info["threshold"]
                break
        bar = "▓" * tiers + "░" * (10 - tiers)
        if next_thresh:
            pct = int(min(current / next_thresh, 1.0) * 100)
            progress = f" → {_fmt_val(current)}/{_fmt_val(next_thresh)} ({pct}%)"
        else:
            progress = " ✅ COMPLÉTÉ"
        embed.add_field(
            name=f"{cat_emoji} {cat_name}",
            value=f"`{bar}` {tiers}/10{progress}",
            inline=False,
        )
    syn_n = stats["completed_global_tiers"]
    syn_bar = "▓" * syn_n + "░" * (10 - syn_n)
    embed.add_field(
        name="✨ Synergie Globale",
        value=f"`{syn_bar}` {syn_n}/10 — ×{stats['global_mult']:.1f} FB, −{stats['tier_cd_min']} min ⏳",
        inline=False,
    )
    bd = "✅" if stats["rank"] <= 3 else "❌"
    boss = "✅" if stats["rank"] == 1 else "❌"
    embed.add_field(
        name="👑 Titres Spéciaux",
        value=f"{bd} Bras Droit (Top 3)  |  {boss} Boss (Top 1)\nRang actuel : **#{stats['rank']}**",
        inline=False,
    )
    embed.set_footer(text=f"{user.display_name} — Clique sur une catégorie pour voir les paliers")
    return embed

def _build_gang_category_embed(stats: dict, cat_idx: int, equipped_title: str) -> discord.Embed:
    cat_key, cat_emoji, cat_name, cat_desc = _CATEGORIES[cat_idx]
    cat_info = stats["category_progress"][cat_key]
    current = cat_info["current"]
    tiers_done = stats["tiers_per_cat"][cat_key]
    embed = discord.Embed(
        title=f"{cat_emoji}  {cat_name}  ({tiers_done}/10)",
        description=f"*{cat_desc}* — Valeur actuelle : **{_fmt_val(current)}**\n\n",
        color=discord.Color.from_rgb(100, 160, 220),
    )
    lines = []
    for tier_info in cat_info["ranks"]:
        is_unlocked = tier_info["is_unlocked"]
        label = tier_info["label"]
        thresh = tier_info["threshold"]
        bonus = tier_info["bonus"]
        emoji_t = tier_info["emoji"]
        if is_unlocked:
            eq = " ← **ÉQUIPÉ**" if equipped_title == label else ""
            lines.append(f"✅ {emoji_t} **{label}**{eq} — +{_fmt_val(bonus)} 🎟️")
        else:
            pct = int(min(current / thresh, 1.0) * 100)
            lines.append(f"❌ {emoji_t} {label} — {_fmt_val(current)}/{_fmt_val(thresh)} ({pct}%) — +{_fmt_val(bonus)} 🎟️")
    embed.description += "\n".join(lines)
    prev_name = _CATEGORIES[(cat_idx - 1) % len(_CATEGORIES)][2]
    next_name = _CATEGORIES[(cat_idx + 1) % len(_CATEGORIES)][2]
    embed.set_footer(text=f"Catégorie {cat_idx + 1}/{len(_CATEGORIES)} • ◀ {prev_name}  •  ▶ {next_name}")
    return embed

def _build_gang_synergy_embed(stats: dict) -> discord.Embed:
    syn_n = stats["completed_global_tiers"]
    embed = discord.Embed(
        title=f"✨  SYNERGIE GLOBALE  ({syn_n}/10)",
        description=(
            "*Se débloque automatiquement quand les 9 catégories atteignent le même palier.*\n"
            f"Palier actuel : **{syn_n}** → ×{stats['global_mult']:.1f} FB, −{stats['tier_cd_min']} min ⏳\n\n"
        ),
        color=discord.Color.from_rgb(120, 80, 200),
    )
    lines = []
    for t in stats["synergy_ranks"]:
        i = t["tier_index"]
        mult = 1.0 + 0.1 * (i + 1)
        cd = (i + 1) * 5
        status = "✅" if t["is_unlocked"] else "❌"
        lines.append(f"{status} {t['emoji']} **{t['label']}** — ×{mult:.1f} FB, −{cd} min ⏳")
    embed.description += "\n".join(lines)
    return embed

def _build_gang_special_embed(stats: dict, equipped_title: str) -> discord.Embed:
    rank = stats["rank"]
    embed = discord.Embed(
        title="👑  TITRES SPÉCIAUX",
        description="*Obtenus en étant Top 3 ou Top 1 au classement global.*\n\n",
        color=discord.Color.from_rgb(220, 180, 50),
    )
    bd_unlocked = rank <= 3
    boss_unlocked = rank == 1
    bd_eq = " ← **ÉQUIPÉ**" if equipped_title == "Bras Droit" else ""
    boss_eq = " ← **ÉQUIPÉ**" if equipped_title == "Boss" else ""
    embed.add_field(
        name=f"🥈 Bras Droit{bd_eq}",
        value=(
            f"**Condition** : Top 3 au classement\n"
            f"**Statut** : {'✅ Débloqué' if bd_unlocked else f'❌ Rang actuel : #{rank}'}\n"
            f"**Récompense** : +**1/4** du total FB en Jetons 🪙"
        ),
        inline=False,
    )
    embed.add_field(
        name=f"👑 Boss{boss_eq}",
        value=(
            f"**Condition** : Top 1 au classement\n"
            f"**Statut** : {'✅ Débloqué' if boss_unlocked else f'❌ Rang actuel : #{rank}'}\n"
            f"**Récompense** : +**3/4** du total FB en Jetons 🪙\n"
            f"*Cumulable avec Bras Droit → totalité des FB aussi en Jetons 🪙*"
        ),
        inline=False,
    )
    return embed

# ── GANG VIEWS ─────────────────────────────────────────────
class GangOverviewView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        cat_defs = [
            ("🎡 Roulette Misé",     discord.ButtonStyle.primary,   0, 0),
            ("🃏 Blackjack Misé",    discord.ButtonStyle.primary,   1, 0),
            ("🎰 Slots Misé",        discord.ButtonStyle.primary,   2, 0),
            ("💰 Total Misé",        discord.ButtonStyle.primary,   3, 0),
            ("🏦 Fortune",           discord.ButtonStyle.primary,   4, 0),
            ("🎡 Parties Roulette",  discord.ButtonStyle.secondary, 5, 1),
            ("🃏 Parties Blackjack", discord.ButtonStyle.secondary, 6, 1),
            ("🎰 Parties Slots",     discord.ButtonStyle.secondary, 7, 1),
            ("🎮 Total Parties",     discord.ButtonStyle.secondary, 8, 1),
        ]
        for label, style, idx, row in cat_defs:
            btn = discord.ui.Button(label=label, style=style, row=row)
            btn.callback = self._make_cat_cb(idx)
            self.add_item(btn)
        syn_btn = discord.ui.Button(label="✨ Synergie", style=discord.ButtonStyle.blurple, row=2)
        syn_btn.callback = self._synergy_cb
        self.add_item(syn_btn)
        sp_btn = discord.ui.Button(label="👑 Spécial", style=discord.ButtonStyle.danger, row=2)
        sp_btn.callback = self._special_cb
        self.add_item(sp_btn)

    def _make_cat_cb(self, cat_idx: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
            data = load_casino()
            stats = get_player_stats(interaction.user.id, data)
            equipped = data["players"].get(str(interaction.user.id), {}).get("selected_title", "")
            embed = _build_gang_category_embed(stats, cat_idx, equipped)
            await interaction.response.edit_message(embed=embed, view=GangCatView(self.user_id, cat_idx))
        return callback

    async def _synergy_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
        data = load_casino()
        stats = get_player_stats(interaction.user.id, data)
        await interaction.response.edit_message(embed=_build_gang_synergy_embed(stats), view=GangSynergyNavView(self.user_id))

    async def _special_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
        data = load_casino()
        stats = get_player_stats(interaction.user.id, data)
        equipped = data["players"].get(str(interaction.user.id), {}).get("selected_title", "")
        await interaction.response.edit_message(embed=_build_gang_special_embed(stats, equipped), view=GangSpecialNavView(self.user_id))


class GangCatView(discord.ui.View):
    def __init__(self, user_id: int, cat_idx: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.cat_idx = cat_idx
        back_btn = discord.ui.Button(label="← Vue d'ensemble", style=discord.ButtonStyle.secondary, row=0)
        back_btn.callback = self._back_cb
        self.add_item(back_btn)
        prev_btn = discord.ui.Button(label="◀ Précédent", style=discord.ButtonStyle.secondary, row=0)
        prev_btn.callback = self._prev_cb
        self.add_item(prev_btn)
        next_btn = discord.ui.Button(label="▶ Suivant", style=discord.ButtonStyle.secondary, row=0)
        next_btn.callback = self._next_cb
        self.add_item(next_btn)
        data = load_casino()
        stats = get_player_stats(user_id, data)
        equipped = data["players"].get(str(user_id), {}).get("selected_title", "")
        cat_key = _CATEGORIES[cat_idx][0]
        for i, rank_info in enumerate(stats["category_progress"][cat_key]["ranks"]):
            row = 1 + (i // 5)
            is_unlocked = rank_info["is_unlocked"]
            label = rank_info["label"]
            if equipped == label:
                style = discord.ButtonStyle.success
            elif is_unlocked:
                style = discord.ButtonStyle.primary
            else:
                style = discord.ButtonStyle.secondary
            btn = discord.ui.Button(label=label, style=style, disabled=not is_unlocked, row=row)
            btn.callback = self._make_equip_cb(label)
            self.add_item(btn)

    def _make_equip_cb(self, title_name: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
            data = load_casino()
            data["players"][str(interaction.user.id)]["selected_title"] = title_name
            save_casino(data)
            stats = get_player_stats(interaction.user.id, data)
            embed = _build_gang_category_embed(stats, self.cat_idx, title_name)
            await interaction.response.edit_message(embed=embed, view=GangCatView(self.user_id, self.cat_idx))
            cog = interaction.client.get_cog("Casino")
            if cog: cog.trigger_leaderboard_update()
        return callback

    async def _back_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
        data = load_casino()
        stats = get_player_stats(interaction.user.id, data)
        await interaction.response.edit_message(embed=_build_gang_overview_embed(stats, interaction.user), view=GangOverviewView(self.user_id))

    async def _prev_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
        new_idx = (self.cat_idx - 1) % len(_CATEGORIES)
        data = load_casino()
        stats = get_player_stats(interaction.user.id, data)
        equipped = data["players"].get(str(interaction.user.id), {}).get("selected_title", "")
        await interaction.response.edit_message(embed=_build_gang_category_embed(stats, new_idx, equipped), view=GangCatView(self.user_id, new_idx))

    async def _next_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
        new_idx = (self.cat_idx + 1) % len(_CATEGORIES)
        data = load_casino()
        stats = get_player_stats(interaction.user.id, data)
        equipped = data["players"].get(str(interaction.user.id), {}).get("selected_title", "")
        await interaction.response.edit_message(embed=_build_gang_category_embed(stats, new_idx, equipped), view=GangCatView(self.user_id, new_idx))


class GangSynergyNavView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        back_btn = discord.ui.Button(label="← Vue d'ensemble", style=discord.ButtonStyle.secondary, row=0)
        back_btn.callback = self._back_cb
        self.add_item(back_btn)

    async def _back_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
        data = load_casino()
        stats = get_player_stats(interaction.user.id, data)
        await interaction.response.edit_message(embed=_build_gang_overview_embed(stats, interaction.user), view=GangOverviewView(self.user_id))


class GangSpecialNavView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        back_btn = discord.ui.Button(label="← Vue d'ensemble", style=discord.ButtonStyle.secondary, row=0)
        back_btn.callback = self._back_cb
        self.add_item(back_btn)
        data = load_casino()
        stats = get_player_stats(user_id, data)
        equipped = data["players"].get(str(user_id), {}).get("selected_title", "")
        for title, unlocked in [("Bras Droit", stats["rank"] <= 3), ("Boss", stats["rank"] == 1)]:
            if equipped == title:
                style = discord.ButtonStyle.success
            elif unlocked:
                style = discord.ButtonStyle.primary
            else:
                style = discord.ButtonStyle.secondary
            btn = discord.ui.Button(label=title, style=style, disabled=not unlocked, row=1)
            btn.callback = self._make_equip_cb(title)
            self.add_item(btn)

    def _make_equip_cb(self, title_name: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
            data = load_casino()
            data["players"][str(interaction.user.id)]["selected_title"] = title_name
            save_casino(data)
            stats = get_player_stats(interaction.user.id, data)
            await interaction.response.edit_message(embed=_build_gang_special_embed(stats, title_name), view=GangSpecialNavView(self.user_id))
            cog = interaction.client.get_cog("Casino")
            if cog: cog.trigger_leaderboard_update()
        return callback

    async def _back_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
        data = load_casino()
        stats = get_player_stats(interaction.user.id, data)
        await interaction.response.edit_message(embed=_build_gang_overview_embed(stats, interaction.user), view=GangOverviewView(self.user_id))

class CasinoWelcomeView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Cash", style=discord.ButtonStyle.success, custom_id="casino:cash")
    async def cash_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            return

        data = load_casino()
        uid = str(interaction.user.id)
        if uid not in data["players"]:
            data["players"][uid] = {
                "balance": 0, "freebets": 0,
                "last_hourly": 0,
                "username": interaction.user.display_name,
                "total_wagered_roulette": 0, "total_wagered_blackjack": 0,
                "total_games_roulette": 0, "total_games_blackjack": 0, "total_games_poker": 0,
                "cash_streak": 0,
                "selected_title": "Petit Joueur",
                "currency": "Freebets",
                "max_balance": 0,
            }
        p = data["players"][uid]

        stats = get_player_stats(interaction.user.id, data)
        now = time.time()
        cooldown = stats["cooldown"]
        last_claim = p.get("last_hourly", 0)

        # ── Streak update ──────────────────────────────────────
        if last_claim == 0:
            new_streak = 0
        elif now - last_claim <= 2 * cooldown:
            new_streak = min(p.get("cash_streak", 0) + 1, 10)
        else:
            new_streak = 0  # missed window — reset

        # Linear multipliers: ×1.0 at level 0 … ×2.0 at level 10
        streak_mult = 1.0 + 0.1 * new_streak

        # ── Compute totals ─────────────────────────────────────
        total_fb    = round(stats["base_total"] * stats["global_mult"] * streak_mult)
        jeton_bonus = round(total_fb * stats["jeton_frac"]) if stats["jeton_frac"] > 0 else 0

        # ── Preview message ────────────────────────────────────
        def _fmt_mult(m):
            return f"×{m:.1f}"

        msg_details = "\n\n### 📈 Tes Bonus Actifs :\n"
        msg_details += f"• **Base** : 1 000 Freebets 🎟️\n"
        if stats["titles_fb"] > 0:
            msg_details += f"• **Palier actif** (meilleur par catégorie) : +{stats['titles_fb']:,} Freebets 🎟️\n".replace(",", " ")
        if stats["completed_global_tiers"] > 0:
            msg_details += (
                f"• **Synergie ({stats['completed_global_tiers']}/10)** : "
                f"{_fmt_mult(stats['global_mult'])} × FB, -{stats['tier_cd_min']} min ⏳\n"
            )
        if new_streak > 0:
            msg_details += f"• **Streak ({new_streak}/10)** : {_fmt_mult(streak_mult)} × total\n"
        if jeton_bonus > 0:
            frac_txt = "3/4 Boss + 1/4 Bras Droit" if stats["jeton_frac"] == 1.0 else "1/4 Bras Droit"
            msg_details += f"• **{stats['rank_title']} (Rang #{stats['rank']})** : +{jeton_bonus:,} Jetons 🪙 ({frac_txt} du total FB)\n".replace(",", " ")
        msg_details += f"\n🏆 **Total** : {total_fb:,} Freebets 🎟️".replace(",", " ")
        if jeton_bonus > 0:
            msg_details += f" + {jeton_bonus:,} Jetons 🪙".replace(",", " ")
        msg_details += f"  (toutes les {cooldown // 60} min ⏳)"

        if now - last_claim < cooldown:
            rem = cooldown - (now - last_claim)
            return await interaction.followup.send(
                f"⏳ Patience ! Disponible dans **{int(rem//60)} min {int(rem%60)} sec**." + msg_details,
                ephemeral=True
            )

        # ── Apply claim ────────────────────────────────────────
        p["freebets"]    = p.get("freebets", 0) + total_fb
        p["last_hourly"] = now
        p["cash_streak"] = new_streak
        p["username"]    = interaction.user.display_name
        if jeton_bonus > 0:
            p["balance"] = p.get("balance", 0) + jeton_bonus
            if p["balance"] > p.get("max_balance", 0):
                p["max_balance"] = p["balance"]
        save_casino(data)

        streak_txt = f" 🔥 Streak {new_streak}" if new_streak > 0 else ""
        jeton_txt  = f" + **{jeton_bonus:,} Jetons 🪙**".replace(",", " ") if jeton_bonus > 0 else ""
        msg = f"💰 **Récompense Horaire{streak_txt}**\nTu as reçu **{total_fb:,} Freebets 🎟️**{jeton_txt} !\n".replace(",", " ") + msg_details
        await interaction.followup.send(msg, ephemeral=True)
        cog = self.bot.get_cog("Casino")
        if cog: cog.trigger_leaderboard_update()

    @discord.ui.button(label="Solde", style=discord.ButtonStyle.secondary, custom_id="casino:balance")
    async def balance_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            return

        data = load_casino()
        if str(interaction.user.id) not in data["players"]:
            return await interaction.followup.send("❌ **Tu n'as pas de profil Casino !** Clique d'abord sur **Cash** pour récupérer tes premiers freebets et t'enregistrer.", ephemeral=True)

        p = data["players"].get(str(interaction.user.id), {"balance": 0, "freebets": 0})
        stats = get_player_stats(interaction.user.id, data)
        sel = p.get("selected_title") or "Petit Joueur"
        
        msg = (
            f"💰 **TA FORTUNE**\n"
            f"--- \n"
            f"🏆 **Rang Global** : #{stats['rank']}\n"
            f"🪙 **Jetons** : {p['balance']:,}\n"
            f"🎟️ **Freebets** : {p['freebets']:,}\n"
            f"🎖️ **Titre Équipé** : `{sel}`\n"
            f"--- \n"
            f"*Mise des jetons pour monter dans le classement !*".replace(",", " ")
        )
        await interaction.followup.send(msg, ephemeral=True)
        cog = self.bot.get_cog("Casino")
        if cog: cog.trigger_leaderboard_update()

    @discord.ui.button(label="Gang", style=discord.ButtonStyle.primary, custom_id="casino:gang")
    async def gang_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            return

        data = load_casino()
        if str(interaction.user.id) not in data["players"]:
            return await interaction.followup.send("❌ **Tu n'as pas de profil Casino !** Clique d'abord sur **Cash** pour récupérer tes premiers Freebets 🎟️ et t'enregistrer.", ephemeral=True)

        stats = get_player_stats(interaction.user.id, data)
        embed = _build_gang_overview_embed(stats, interaction.user)
        await interaction.followup.send(embed=embed, view=GangOverviewView(interaction.user.id), ephemeral=True)

class Casino(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._panel_lock = asyncio.Lock()
        self._last_leaderboard_update = 0
        # Pending updates queue: key -> (embed, view)
        self._pending_updates: dict = {}

    async def cog_load(self):
        self.auto_setup_task.start()
        self.flush_updates_task.start()

    @tasks.loop(seconds=5.0)
    async def flush_updates_task(self):
        """Flush all pending message edits every 5 seconds to reduce Discord API calls."""
        if not self._pending_updates:
            return
        pending = dict(self._pending_updates)
        self._pending_updates.clear()
        for key, (embed, view) in pending.items():
            try:
                await self._do_upsert(key, embed=embed, view=view)
            except Exception as e:
                logger.warning("flush_updates_task: échec de l'upsert pour '%s': %s", key, e)

    @flush_updates_task.before_loop
    async def before_flush(self):
        await self.bot.wait_until_ready()

    @tasks.loop(count=1)
    async def auto_setup_task(self):
        await self.bot.wait_until_ready()
        self.bot._startup_queue.put_nowait(self._update_welcome_message)
        self.bot._startup_queue.put_nowait(self._update_leaderboard)
        self.bot._startup_queue.put_nowait(self._update_guide_message)

    async def upsert_panel_message(self, key: str, *, embed: discord.Embed, view: discord.ui.View | None = None):
        channel_id = PANEL_CHANNEL_MAP.get(key)
        if not channel_id: return None

        # Check if message exists; if not, send it immediately (first-time setup)
        data = load_casino()
        msg_id = data.get("messages", {}).get(key)
        if not msg_id:
            return await self._do_upsert(key, embed=embed, view=view)

        # Queue the update — will be flushed by flush_updates_task every 5s
        self._pending_updates[key] = (embed, view)
        # Return a lightweight placeholder so callers don't break
        channel = self.bot.get_channel(channel_id)
        if channel:
            try:
                return await channel.fetch_message(int(msg_id))
            except Exception:
                pass
        return None

    async def _do_upsert(self, key: str, *, embed: discord.Embed, view: discord.ui.View | None = None):
        """Actually perform the Discord API call to edit/send the panel message."""
        channel_id = PANEL_CHANNEL_MAP.get(key)
        if not channel_id: return None
        async with self._panel_lock:
            channel = self.bot.get_channel(channel_id)
            if not channel: return None
            data = load_casino()
            msg_id = data.get("messages", {}).get(key)
            if msg_id:
                try:
                    msg = await channel.fetch_message(int(msg_id))
                    await msg.edit(embed=embed, view=view)
                    return msg
                except Exception as e:
                    logger.warning("_do_upsert: échec de l'édition du message '%s': %s", key, e)
            msg = await channel.send(embed=embed, view=view)
            data.setdefault("messages", {})[key] = msg.id
            save_casino(data)
            return msg

    async def _update_welcome_message(self):
        embed = discord.Embed(
            title="✨  BIENVENUE AU CASINO SUPRÊME  ✨",
            description=(
                "### 🏮 **L'Antre de la Fortune et du Risque**\n"
                "Ici, les légendes naissent et les empires s'effondrent. "
                "Maîtrisez les devises pour devenir le nouveau parrain du crime.\n\n"
                "### 🪙 **Comprendre les Devises**\n"
                "• **Jetons** 🪙 : Ta fortune réelle. Utilisés pour miser partout, y compris au **Poker**. C'est ton score au classement.\n"
                "• **Freebets** 🎟️ : Jetons de 'test' offerts via le bouton **Cash**. "
                "Jouables à la **Roulette** et au **Blackjack**. Seul le profit net est converti en vrais Jetons 🪙 !\n\n"
                "### 💰 **Gagner des Devises**\n"
                "• **Cash** : Reçois **1 000 Freebets 🎟️** de base toutes les heures (60 min ⏳).\n"
                "• **Bonus Paliers** : Le palier le plus haut de chaque catégorie ajoute des Freebets (250 → 500 → … → 128 000 🎟️ par catégorie).\n"
                "• **Streak** : Clame ton Cash avant 2× le cooldown pour conserver ton streak 🔥 (×1.0 au départ → ×2.0 après 10 fois d'affilée) !\n\n"
                "### 👑 **Domination du Gang**\n"
                "• **7 Catégories** : Roulette/BJ misé, Total misé, Fortune, Parties Roulette/BJ, Total Parties — 10 paliers chacune.\n"
                "• **✨ Synergie** : Atteindre le même palier dans les 7 catégories → active ce palier en Synergie (×1.1 FB & -5 min ⏳) !\n"
                "• **Titres Spéciaux** : Sois Top 3 ou Top 1 au classement pour débloquer **Bras Droit** ou **Boss** et obtenir des bonus massifs.\n\n"
                "--- \n"
                "### 📍 **Nos Salons**\n"
                "🎡 <#1480224572275032135> (Roulette)\n"
                "🃏 <#1480224707575021769> (Blackjack)\n"
                "♠️ <#1480224841830236331> (Poker - *Jetons uniquement*)\n"
                "🎰 <#1486671925521551522> (Machines à Sous - *Jetons uniquement*)\n"
                "--- \n"
                "**Choisis ton destin et que la chance soit avec toi.**"
            ),
            color=discord.Color.from_rgb(255, 215, 0)
        )
        embed.set_footer(text="Bot Suprême • Système de Gang & Casino", icon_url=self.bot.user.display_avatar.url)
        await self.upsert_panel_message("welcome", embed=embed)

    async def _update_guide_message(self):
        embed = discord.Embed(
            title="🎮  COMMENT JOUER",
            description=(
                "Trois boutons disponibles en bas de ce message :\n\n"
                "💰 **Cash** — Réclame tes Freebets 🎟️ toutes les heures. "
                "Tes bonus augmentent selon ton Gang et ton Streak 🔥.\n\n"
                "📊 **Solde** — Consulte ta fortune actuelle (Jetons 🪙 & Freebets 🎟️) et ton rang au classement.\n\n"
                "🏴 **Gang** — Visualise tes paliers par catégorie, ta Synergie et tes titres débloqués."
            ),
            color=discord.Color.from_rgb(255, 215, 0)
        )
        embed.set_footer(text="Bot Suprême • Système de Gang & Casino", icon_url=self.bot.user.display_avatar.url)
        await self.upsert_panel_message("guide", embed=embed, view=CasinoWelcomeView(self.bot))

    async def _update_leaderboard(self):
        data = load_casino()
        combined = []
        for uid, p in data.get("players", {}).items():
            combined.append({
                "type": "player", "id": uid, 
                "name": p.get("username") or f"Joueur {uid[-4:]}", 
                "balance": p.get("balance", 0), 
                "freebets": p.get("freebets", 0), 
                "title": p.get("selected_title") or "Petit Joueur"
            })
        for npc in MAFIA_NPCS:
            combined.append({
                "type": "npc", "name": npc["name"], 
                "balance": npc["balance"], 
                "rank_key": npc["rank"], 
                "emoji": npc["emoji"],
                "freebets": 0,
                "title": npc["rank"]
            })
        
        combined.sort(key=lambda x: (x["balance"], x["freebets"]), reverse=True)
        
        embed = discord.Embed(
            title="🏆  CLASSEMENT DES GRANDS PARRAINS", 
            description="L'élite du crime et de la fortune. Classement sur **Jetons** puis **Freebets**.", 
            color=discord.Color.gold()
        )
        
        board_text = ""
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "11.", "12."]
        
        for i, item in enumerate(combined[:10]):
            medal = medals[i] if i < 10 else f"**{i+1}.**"
            name = item["name"]
            title = f"*{item['title']}*"
            bal = f"{item['balance']:,}".replace(",", " ")
            
            if item["type"] == "player":
                fb = f"{item['freebets']:,}".replace(",", " ")
                board_text += f"{medal} **{name}** | {title}\n ╰ 🪙 **{bal}** Jetons  •  🎟️ **{fb}** Freebets\n\n"
            else:
                board_text += f"{medal} {item['emoji']} **{name}** | {title}\n ╰ 🪙 **{bal}** Jetons\n\n"
        
        embed.description += f"\n\n{board_text if len(combined) > 0 else '*La rue est vide...*'}"
        await self.upsert_panel_message("leaderboard", embed=embed)

    def trigger_leaderboard_update(self):
        now = time.time()
        if now - self._last_leaderboard_update < 5: return
        self._last_leaderboard_update = now
        asyncio.create_task(self._update_leaderboard())

async def setup(bot):
    await bot.add_cog(Casino(bot))
