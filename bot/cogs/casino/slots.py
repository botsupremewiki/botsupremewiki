"""bot/cogs/casino/slots.py — Machines à Sous publiques (10 machines)"""
from __future__ import annotations
import discord
from discord.ext import commands, tasks
import random
import asyncio
import time
import logging
from .core import load_casino, save_casino, _ensure_player, get_seated_game, set_seated_game

def _seated_game_label(game: str) -> str:
    if not game: return game
    if game.startswith("slots_"): return f"🎰 Machine à Sous #{game.split('_')[1]}"
    if game.startswith("poker_"): return f"♠️ Poker — Table {game.split('_', 1)[1]}"
    labels = {"roulette": "🎡 Roulette", "blackjack": "🃏 Blackjack"}
    return labels.get(game, game)

logger = logging.getLogger(__name__)

SLOT_CHANNEL_ID   = 1486671925521551522
INACTIVITY_TIMEOUT = 60   # secondes avant éjection automatique
SPIN_CD            = 5.5  # cooldown partagé : manuel ET boucle (même timer last_spin)
LOOP_DELAY         = SPIN_CD

# ─── Machine Definitions ─────────────────────────────────────────────────────

MACHINES: dict[int, dict] = {
    1: {
        "name": "La Classique", "emoji": "🍒", "theme": "Fruits Traditionnels",
        "desc": "La machine originale. 1 seule rangée, 1 seule chance — pure nostalgie.",
        "reels": 3, "rows": 1, "paylines": 1, "min_bet": 100, "max_bet": 5_000,
        "bets": [100, 250, 500, 1_000, 2_500, 5_000],
        "volatility": "Faible", "vol_emoji": "🟢", "rtp": 94,
        "special": None, "special_desc": "Aucune — Pure chance classique",
        "symbols": ["🍒", "🍋", "🍊", "🍇", "🍉", "⭐", "7️⃣"],
        "weights": [30, 25, 20, 15, 10, 5, 2],
        "pay3": [6.8, 11.4, 18.2, 27.4, 57.0, 136.8, 684.1],
        "pay2": [3.4, 4.6, 0, 0, 0, 0, 0],
        "color": 0xFF6B6B,
    },
    2: {
        "name": "Le Samouraï", "emoji": "⚔️", "theme": "Honneur Japonais",
        "desc": "Grille 3×3 classique. Le Wild ⚔️ remplace tout symbole.",
        "reels": 3, "rows": 3, "paylines": 5, "min_bet": 300, "max_bet": 15_000,
        "bets": [300, 750, 1_500, 3_000, 7_500, 15_000],
        "volatility": "Moyenne", "vol_emoji": "🟡", "rtp": 92,
        "special": "wild", "wild_idx": 6,
        "special_desc": "⚔️ Wild — remplace n'importe quel symbole",
        "symbols": ["🏯", "🎋", "🌸", "🎎", "🎐", "🗡️", "⚔️"],
        "weights": [28, 23, 18, 14, 10, 5, 2],
        "pay3": [1.0, 1.5, 2.4, 4.4, 8.7, 24.3, 145.6],
        "pay2": [0.6, 0.7, 0, 0, 0, 0, 0],
        "color": 0xDC143C,
    },
    3: {
        "name": "Le Dragon", "emoji": "🐉", "theme": "Furie du Dragon",
        "desc": "Grille 4×3. Chaque victoire amplifiée par un Multiplicateur de Feu ×2→×5.",
        "reels": 4, "rows": 3, "paylines": 8, "min_bet": 200, "max_bet": 10_000,
        "bets": [200, 500, 1_000, 2_500, 5_000, 10_000],
        "volatility": "Haute", "vol_emoji": "🔴", "rtp": 91,
        "special": "fire_mult", "fire_range": (2, 5),
        "special_desc": "🔥 Multiplicateur de Feu ×2→×5 aléatoire sur chaque victoire",
        "symbols": ["🏮", "🎴", "🀄", "💰", "⚡", "🔥", "🐉"],
        "weights": [28, 22, 18, 14, 10, 5, 3],
        "pay4": [0.4, 0.67, 1.07, 1.61, 3.75, 10.05, 53.61],
        "pay3": [0.27, 0.4, 0.67, 1.07, 2.41, 6.7, 33.51],
        "pay2": [0.16, 0, 0, 0, 0, 0, 0],
        "color": 0xFF4500,
    },
    4: {
        "name": "La Galaxie", "emoji": "🚀", "theme": "Exploration Spatiale",
        "desc": "Grille 5×3 — 10 paylines. 20% que le rouleau central devienne un Wild 🛸.",
        "reels": 5, "rows": 3, "paylines": 10, "min_bet": 100, "max_bet": 5_000,
        "bets": [100, 250, 500, 1_000, 2_500, 5_000],
        "volatility": "Moyenne", "vol_emoji": "🟡", "rtp": 93,
        "special": "expanding_wild", "wild_idx": 6, "ew_reel": 2, "ew_chance": 0.20,
        "special_desc": "🛸 Wild Galactique — 20% que le rouleau central soit un Wild",
        "symbols": ["👾", "🪐", "🌙", "⭐", "🌌", "🚀", "🛸"],
        "weights": [26, 22, 18, 14, 10, 6, 4],
        "pay3": [0.25, 0.38, 0.63, 1.0, 1.88, 5.01, 18.8],
        "pay4": [0.38, 0.63, 1.0, 1.88, 3.76, 10.03, 37.6],
        "pay5": [0.63, 1.0, 1.88, 3.13, 6.27, 18.8, 75.2],
        "pay2": [0.15, 0.19, 0, 0, 0, 0, 0],
        "color": 0x0A0A2E,
    },
    5: {
        "name": "Le Trèfle Chanceux", "emoji": "🍀", "theme": "Jardin de la Fortune",
        "desc": "Grille 3×2 — 3 paylines. Simple et généreux. Chaque victoire offre un Spin Gratuit.",
        "reels": 3, "rows": 2, "paylines": 3, "min_bet": 100, "max_bet": 3_000,
        "bets": [100, 250, 500, 1_000, 2_000, 3_000],
        "volatility": "Très Faible", "vol_emoji": "🟢", "rtp": 95,
        "special": "free_spin", "max_free_spins": 3,
        "special_desc": "🌟 Victoire = Spin Gratuit proposé (max 3 consécutifs)",
        "symbols": ["🌼", "🌺", "🌸", "🌻", "🌈", "✨", "🍀"],
        "weights": [28, 23, 18, 14, 10, 5, 2],
        "pay3": [1.47, 2.2, 3.67, 5.88, 11.02, 29.47, 132.5],
        "pay2": [0.94, 1.14, 0, 0, 0, 0, 0],
        "color": 0x00C851,
    },
    6: {
        "name": "Le Fantôme", "emoji": "👻", "theme": "Nuit des Spectres",
        "desc": "Grille 3×3 — 5 paylines. Chaque victoire déclenche un Quitte ou Double spectral.",
        "reels": 3, "rows": 3, "paylines": 5, "min_bet": 500, "max_bet": 15_000,
        "bets": [500, 1_000, 2_500, 5_000, 10_000, 15_000],
        "volatility": "Haute", "vol_emoji": "🔴", "rtp": 90,
        "special": "double_or_nothing",
        "special_desc": "👻 Quitte ou Double — 50/50 après chaque victoire",
        "symbols": ["🕸️", "🦇", "🌙", "🔮", "💀", "☠️", "👻"],
        "weights": [27, 22, 18, 14, 11, 5, 3],
        "pay3": [1.4, 2.2, 4.3, 7.2, 14.4, 57.5, 287.6],
        "pay2": [0.9, 0, 0, 0, 0, 0, 0],
        "color": 0x6A0DAD,
    },
    7: {
        "name": "Le Jackpot", "emoji": "🏆", "theme": "Jackpot Progressif",
        "desc": "Grille 4×3 — 8 paylines. 1% de chaque mise alimente la cagnotte commune.",
        "reels": 4, "rows": 3, "paylines": 8, "min_bet": 1_000, "max_bet": 50_000,
        "bets": [1_000, 2_500, 5_000, 10_000, 25_000, 50_000],
        "volatility": "Extrême", "vol_emoji": "🔴", "rtp": 88,
        "special": "jackpot", "jackpot_contrib": 0.01, "jackpot_seed": 50_000,
        "special_desc": "🏆 4× 🏆 sur une payline = Jackpot ! (1% de chaque mise l'alimente)",
        "symbols": ["🔔", "💵", "🤑", "💰", "🍀", "💎", "🏆"],
        "weights": [27, 22, 17, 14, 10, 7, 3],
        "pay4": [1.14, 2.28, 3.79, 6.83, 15.18, 56.91, 0.0],
        "pay3": [0.76, 1.52, 2.66, 4.55, 9.48, 37.94, 0.0],
        "pay2": [0.46, 0, 0, 0, 0, 0, 0],
        "color": 0xFFD700,
    },
    8: {
        "name": "L'Atlantide", "emoji": "🌊", "theme": "Cité des Profondeurs",
        "desc": "Grille 5×4 — 15 paylines. 3× 🌊 n'importe où = 5 Spins Gratuits ×2 !",
        "reels": 5, "rows": 4, "paylines": 15, "min_bet": 200, "max_bet": 10_000,
        "bets": [200, 500, 1_000, 2_500, 5_000, 10_000],
        "volatility": "Moyenne", "vol_emoji": "🟡", "rtp": 93,
        "special": "scatter_free_spins",
        "scatter_idx": 6, "scatter_trigger": 3,
        "free_spins_count": 5, "free_spins_mult": 2,
        "special_desc": "🌊 3× 🌊 partout = 5 Spins Gratuits ×2",
        "symbols": ["🐚", "🐙", "🦑", "🐠", "🐳", "🦈", "🌊"],
        "weights": [26, 22, 18, 14, 10, 6, 4],
        "pay3": [0.3, 0.4, 0.7, 1.3, 2.6, 7.1, 28.6],
        "pay4": [0.4, 0.7, 1.1, 2.1, 4.3, 11.4, 35.7],
        "pay5": [0.7, 1.1, 2.1, 3.6, 7.1, 21.4, 71.4],
        "pay2": [0.2, 0.2, 0, 0, 0, 0, 0],
        "color": 0x0099CC,
    },
    9: {
        "name": "Le Mystère", "emoji": "🔮", "theme": "Illusions & Arcanes",
        "desc": "Grille 4×2 — 6 paylines. Multiplicateur Mystère ×1→×10 sur chaque victoire.",
        "reels": 4, "rows": 2, "paylines": 6, "min_bet": 300, "max_bet": 8_000,
        "bets": [300, 750, 1_500, 3_000, 5_000, 8_000],
        "volatility": "Aléatoire", "vol_emoji": "🟣", "rtp": 92,
        "special": "mystery_mult", "mystery_max": 10,
        "special_desc": "🌀 Multiplicateur Mystère ×1→×10 sur chaque victoire",
        "symbols": ["🎲", "🃏", "🎪", "🎭", "🌀", "🎴", "❓"],
        "weights": [27, 22, 18, 14, 11, 6, 2],
        "pay4": [0.33, 0.54, 0.98, 1.63, 3.26, 9.78, 48.9],
        "pay3": [0.22, 0.33, 0.65, 1.09, 2.17, 6.52, 32.6],
        "pay2": [0.13, 0, 0, 0, 0, 0, 0],
        "color": 0x9B59B6,
    },
    10: {
        "name": "La Légendaire", "emoji": "👑", "theme": "Puissance Absolue",
        "desc": "Grille 5×4 — 20 paylines. 5× 🔱 sur une payline = Bonus ×50 !",
        "reels": 5, "rows": 4, "paylines": 20, "min_bet": 5_000, "max_bet": 200_000,
        "bets": [5_000, 10_000, 25_000, 50_000, 100_000, 200_000],
        "volatility": "Extrême", "vol_emoji": "🔴", "rtp": 89,
        "special": "legendary_bonus", "legendary_mult": 50,
        "special_desc": "👑 5× 🔱 sur une payline = Bonus ×50 !",
        "symbols": ["🔱", "⚡", "🌟", "🦄", "🌈", "💎", "👑"],
        "weights": [25, 20, 16, 13, 11, 9, 6],
        "pay3": [0.08, 0.13, 0.27, 0.54, 1.36, 4.07, 27.13],
        "pay4": [0.13, 0.22, 0.49, 0.94, 2.17, 6.78, 54.25],
        "pay5": [0.22, 0.41, 0.81, 1.62, 4.07, 13.56, 135.63],
        "pay2": [0.06, 0, 0, 0, 0, 0, 0],
        "color": 0xFFD700,
    },
}

# ─── Paylines ────────────────────────────────────────────────────────────────
# Clé : (n_reels, n_rows) → dict{ payline_num: [(row, col), ...] }

_PAYLINES: dict[tuple[int,int], dict[int, list[tuple[int, int]]]] = {
    # ── 3 rouleaux × 1 rangée — La Classique ──────────────────
    (3, 1): {
        1: [(0,0),(0,1),(0,2)],           # ─── unique
    },
    # ── 3 rouleaux × 2 rangées — Le Trèfle ───────────────────
    (3, 2): {
        1: [(0,0),(0,1),(0,2)],           # ─── rangée haute
        2: [(1,0),(1,1),(1,2)],           # ─── rangée basse
        3: [(0,0),(1,1),(0,2)],           # ∧   V haut
    },
    # ── 3 rouleaux × 3 rangées — Samouraï & Fantôme ──────────
    (3, 3): {
        1: [(1,0),(1,1),(1,2)],           # ─── centrale
        2: [(0,0),(0,1),(0,2)],           # ─── haute
        3: [(2,0),(2,1),(2,2)],           # ─── basse
        4: [(0,0),(1,1),(2,2)],           # ╲   diagonale ↘
        5: [(2,0),(1,1),(0,2)],           # ╱   diagonale ↗
    },
    # ── 4 rouleaux × 2 rangées — Le Mystère ──────────────────
    (4, 2): {
        1: [(0,0),(0,1),(0,2),(0,3)],     # ─── haute
        2: [(1,0),(1,1),(1,2),(1,3)],     # ─── basse
        3: [(0,0),(1,1),(0,2),(1,3)],     # ~ zigzag
        4: [(1,0),(0,1),(1,2),(0,3)],     # ~ zigzag inverse
        5: [(0,0),(0,1),(1,2),(1,3)],     # escalier ↘
        6: [(1,0),(1,1),(0,2),(0,3)],     # escalier ↗
    },
    # ── 4 rouleaux × 3 rangées — Dragon & Jackpot ────────────
    (4, 3): {
        1: [(1,0),(1,1),(1,2),(1,3)],     # ─── centrale
        2: [(0,0),(0,1),(0,2),(0,3)],     # ─── haute
        3: [(2,0),(2,1),(2,2),(2,3)],     # ─── basse
        4: [(0,0),(1,1),(2,2),(1,3)],     # ∨ V bas
        5: [(2,0),(1,1),(0,2),(1,3)],     # ∧ V haut
        6: [(0,0),(0,1),(1,2),(2,3)],     # escalier ↘
        7: [(2,0),(2,1),(1,2),(0,3)],     # escalier ↗
        8: [(0,0),(1,1),(1,2),(0,3)],     # arc haut
    },
    # ── 5 rouleaux × 3 rangées — La Galaxie ──────────────────
    (5, 3): {
        1:  [(1,0),(1,1),(1,2),(1,3),(1,4)],  # ─── centrale
        2:  [(0,0),(0,1),(0,2),(0,3),(0,4)],  # ─── haute
        3:  [(2,0),(2,1),(2,2),(2,3),(2,4)],  # ─── basse
        4:  [(0,0),(1,1),(2,2),(1,3),(0,4)],  # W
        5:  [(2,0),(1,1),(0,2),(1,3),(2,4)],  # M
        6:  [(1,0),(0,1),(0,2),(0,3),(1,4)],  # ∩ arc haut
        7:  [(1,0),(2,1),(2,2),(2,3),(1,4)],  # ∪ arc bas
        8:  [(0,0),(0,1),(1,2),(2,3),(2,4)],  # escalier ↘
        9:  [(2,0),(2,1),(1,2),(0,3),(0,4)],  # escalier ↗
        10: [(1,0),(1,1),(0,2),(1,3),(1,4)],  # ondulation haute
    },
    # ── 5 rouleaux × 4 rangées — Atlantide & Légendaire ──────
    (5, 4): {
        1:  [(1,0),(1,1),(1,2),(1,3),(1,4)],  # ─── 2e rangée
        2:  [(2,0),(2,1),(2,2),(2,3),(2,4)],  # ─── 3e rangée
        3:  [(0,0),(0,1),(0,2),(0,3),(0,4)],  # ─── haute
        4:  [(3,0),(3,1),(3,2),(3,3),(3,4)],  # ─── basse
        5:  [(0,0),(1,1),(2,2),(1,3),(0,4)],  # W haut
        6:  [(3,0),(2,1),(1,2),(2,3),(3,4)],  # W bas
        7:  [(1,0),(0,1),(0,2),(0,3),(1,4)],  # ∩ arc haut
        8:  [(2,0),(3,1),(3,2),(3,3),(2,4)],  # ∪ arc bas
        9:  [(0,0),(1,1),(3,2),(1,3),(0,4)],  # deep W
        10: [(3,0),(2,1),(0,2),(2,3),(3,4)],  # deep M
        11: [(0,0),(0,1),(1,2),(2,3),(3,4)],  # escalier ↘
        12: [(3,0),(3,1),(2,2),(1,3),(0,4)],  # escalier ↗
        13: [(1,0),(2,1),(3,2),(2,3),(1,4)],  # V bas
        14: [(2,0),(1,1),(0,2),(1,3),(2,4)],  # V haut
        15: [(0,0),(2,1),(1,2),(3,3),(1,4)],  # zigzag complexe
        # paylines 16-20 — La Légendaire uniquement
        16: [(1,0),(1,1),(2,2),(1,3),(1,4)],  # légère descente
        17: [(2,0),(2,1),(1,2),(2,3),(2,4)],  # légère montée
        18: [(0,0),(1,1),(1,2),(1,3),(0,4)],  # arc plat haut
        19: [(3,0),(2,1),(2,2),(2,3),(3,4)],  # arc plat bas
        20: [(1,0),(3,1),(1,2),(3,3),(1,4)],  # alternance
    },
}

_PAYLINE_NAMES = {
    1: "Ligne centrale", 2: "Ligne haute", 3: "Ligne basse",
    4: "Diagonale ↘", 5: "Diagonale ↗",
    6: "Arc haut ∩", 7: "Arc bas ∪", 8: "Escalier ↘", 9: "Escalier ↗",
    10: "Ondulation ⌒", 11: "Ondulation ⌣", 12: "V haut", 13: "V bas",
    14: "Zigzag ⊤", 15: "Zigzag ⊥", 16: "Vague ~", 17: "Vague ~",
    18: "Alter. haute", 19: "Alter. basse", 20: "Arc double",
}

# ─── Spin Logic ──────────────────────────────────────────────────────────────

def _spin_grid(m: dict) -> list[list[str]]:
    """Spin each reel independently → rows × reels grid."""
    n_rows = m["rows"]
    cols = [random.choices(m["symbols"], weights=m["weights"], k=n_rows) for _ in range(m["reels"])]
    return [[cols[c][r] for c in range(m["reels"])] for r in range(n_rows)]


def _match_line(line_syms: list[str], m: dict) -> tuple[int, int]:
    """Returns (consecutive_from_left, symbol_idx). 0 = no win."""
    wild = m["symbols"][m["wild_idx"]] if "wild_idx" in m else None
    target = next((s for s in line_syms if s != wild), None)
    if target is None:
        return (len(line_syms), len(m["symbols"]) - 1)
    idx = m["symbols"].index(target)
    count = 0
    for s in line_syms:
        if s == target or s == wild:
            count += 1
        else:
            break
    return (count, idx) if count >= 2 else (0, -1)


def _payout_mult(match: int, sym_idx: int, m: dict) -> float:
    if match == 0:
        return 0.0
    n = m["reels"]
    if n == 5:
        if match == 5: return m.get("pay5", m["pay3"])[sym_idx]
        if match == 4: return m.get("pay4", m["pay3"])[sym_idx]
        if match == 3: return m["pay3"][sym_idx]
        if match == 2: return m.get("pay2", [0.0]*7)[sym_idx]
    elif n == 4:
        if match == 4: return m.get("pay4", m["pay3"])[sym_idx]
        if match == 3: return m["pay3"][sym_idx]
        if match == 2: return m.get("pay2", [0.0]*7)[sym_idx]
    else:
        if match == 3: return m["pay3"][sym_idx]
        if match == 2: return m.get("pay2", [0.0]*7)[sym_idx]
    return 0.0


def _evaluate_spin(grid: list[list[str]], machine_id: int, bet: int,
                   extra_mult: float = 1.0, data: dict | None = None) -> dict:
    """
    Evaluate all active paylines. Returns full result dict.
    data is needed for jackpot pool read (machine 7).
    """
    m = MACHINES[machine_id]

    # Expanding wild: replace middle column with wild (machine 4)
    ew_triggered = False
    if m.get("special") == "expanding_wild" and random.random() < m["ew_chance"]:
        ew_triggered = True
        wild_sym = m["symbols"][m["wild_idx"]]
        for row in grid:
            row[m["ew_reel"]] = wild_sym

    # Scatter count (machine 8) — whole grid
    scatter_count = 0
    if m.get("special") == "scatter_free_spins":
        sc_sym = m["symbols"][m["scatter_idx"]]
        scatter_count = sum(row.count(sc_sym) for row in grid)

    # Check each active payline
    active_paylines = _PAYLINES.get((m["reels"], m["rows"]), {})
    winning_lines: list[dict] = []
    total_base_win = 0
    jackpot_hit = False

    for pl_num in range(1, m["paylines"] + 1):
        coords = active_paylines.get(pl_num)
        if not coords:
            continue
        line_syms = [grid[r][c] for (r, c) in coords]
        match, sym_idx = _match_line(line_syms, m)
        if match == 0:
            continue
        pl_mult = _payout_mult(match, sym_idx, m)
        # Check jackpot symbol (pay3[last] == 0 triggers jackpot)
        if m.get("special") == "jackpot" and sym_idx == len(m["symbols"]) - 1 and match == m["reels"]:
            jackpot_hit = True
            pl_mult = 0.0
        if pl_mult > 0:
            win = int(bet * pl_mult * extra_mult)
            winning_lines.append({
                "num": pl_num,
                "name": _PAYLINE_NAMES.get(pl_num, f"Ligne {pl_num}"),
                "match": match,
                "sym_idx": sym_idx,
                "symbols": line_syms,
                "win": win,
            })
            total_base_win += win

    # Post-win specials
    fire_mult: int | None = None
    mystery_mult: int | None = None
    legendary = False

    if total_base_win > 0:
        if m.get("special") == "fire_mult":
            fire_mult = random.randint(*m["fire_range"])
            total_base_win = int(total_base_win * fire_mult)
            for wl in winning_lines:
                wl["win"] = int(wl["win"] * fire_mult)

        if m.get("special") == "mystery_mult":
            mystery_mult = random.randint(1, m["mystery_max"])
            total_base_win = int(total_base_win * mystery_mult)
            for wl in winning_lines:
                wl["win"] = int(wl["win"] * mystery_mult)

        if m.get("special") == "legendary_bonus":
            # Check if any payline hit 5× first symbol
            if any(wl["match"] == 5 and wl["sym_idx"] == 0 for wl in winning_lines):
                legendary = True
                total_base_win = int(total_base_win * m["legendary_mult"])
                for wl in winning_lines:
                    if wl["match"] == 5 and wl["sym_idx"] == 0:
                        wl["win"] = int(wl["win"] * m["legendary_mult"])

    # Jackpot pool win
    jackpot_val = 0
    if jackpot_hit and data is not None:
        jackpot_val = data.get("slot_jackpot", m["jackpot_seed"])
        total_base_win = jackpot_val

    return {
        "grid": grid,
        "winning_lines": winning_lines,
        "total_win": total_base_win,
        "fire_mult": fire_mult,
        "mystery_mult": mystery_mult,
        "jackpot_hit": jackpot_hit,
        "jackpot_val": jackpot_val,
        "scatter_count": scatter_count,
        "expanding_wild": ew_triggered,
        "legendary": legendary,
    }


# ─── Display Helpers ─────────────────────────────────────────────────────────

def _fmt(n: int) -> str:
    return f"{n:,}".replace(",", "\u202f")


def _format_grid(grid: list[list[str]], winning_line_nums: set[int],
                 n_reels: int, n_rows: int, n_paylines: int) -> str:
    """Render the rows×reels grid with markers for winning horizontal paylines."""
    active = _PAYLINES.get((n_reels, n_rows), {})
    rows = []
    for row_idx, row in enumerate(grid):
        cells = "  ".join(row)
        # Mark row if it corresponds to a winning horizontal payline
        marker = ""
        for pl_num in winning_line_nums:
            coords = active.get(pl_num, [])
            if coords and all(r == row_idx for r, c in coords):
                marker = "  ✨"
                break
        rows.append(f"{cells}{marker}")
    return "\n".join(rows)


def _get_state(machine_id: int, data: dict) -> dict:
    return data.setdefault("slot_machines", {}).setdefault(str(machine_id), {})


def _build_hub_embed(data: dict) -> discord.Embed:
    """Embed affiché dans le salon — liste toutes les machines avec leur statut."""
    embed = discord.Embed(
        title="🎰 SALLE DES MACHINES À SOUS",
        description="Clique sur le bouton d'une machine pour t'y asseoir.",
        color=0xFFD700,
    )
    for mid, m in MACHINES.items():
        state = _get_state(mid, data)
        seated_uid  = state.get("seated_user")
        seated_name = state.get("seated_username", "Joueur")
        loop_running = state.get("loop_running", False)
        if loop_running:
            status = f"🔄 **{seated_name}** — boucle en cours"
        elif seated_uid:
            expiry_ts = int(state.get("last_action", time.time()) + INACTIVITY_TIMEOUT)
            status = f"🔒 **{seated_name}** — éjection <t:{expiry_ts}:R>"
        else:
            status = "✅ Libre"
        embed.add_field(
            name=f"{m['emoji']} #{mid} — {m['name']}",
            value=(
                f"*{m['desc']}*\n"
                f"{m['vol_emoji']} Volatilité : **{m['volatility']}**\n"
                f"🎰 **{m['reels']}** colonnes × **{m['rows']}** rangées\n"
                f"💰 **{_fmt(m['min_bet'])}** – **{_fmt(m['max_bet'])}** 🪙\n"
                f"{status}"
            ),
            inline=True,
        )
    return embed


def _build_game_embed(machine_id: int, data: dict) -> discord.Embed:
    m = MACHINES[machine_id]
    state = _get_state(machine_id, data)
    seated_uid = state.get("seated_user")
    seated_name = state.get("seated_username", "Joueur")
    loop_running = state.get("loop_running", False)
    last_result = state.get("last_result")
    current_bet = state.get("current_bet", m["bets"][0])
    don_pending = state.get("don_pending_win")
    scatter_spins = state.get("scatter_spins_left", 0)

    color = m["color"]
    if loop_running:
        color = 0x00FF88
    elif don_pending:
        color = 0x9B59B6

    embed = discord.Embed(
        title=f"{m['emoji']}  Machine #{machine_id} — {m['name']}",
        color=color,
    )

    # ── Status bar ──────────────────────────────────────────────
    if loop_running:
        spins = state.get("loop_spins_done", 0)
        won = state.get("loop_total_won", 0)
        lost = state.get("loop_total_lost", 0)
        cur_sym = "🎟️" if state.get("currency") == "freebets" else "🪙"
        embed.description = (
            f"🔄 **BOUCLE EN COURS** — {seated_name}\n"
            f"Spins : **{spins}** | Gains : **+{_fmt(won)}** 🪙 | Pertes : **-{_fmt(lost)}** {cur_sym}"
        )
    elif seated_uid:
        expiry_ts = int(state.get("last_action", time.time()) + INACTIVITY_TIMEOUT)
        embed.description = f"🪑 **{seated_name}** est assis(e) — ⏱️ éjection <t:{expiry_ts}:R>"
    else:
        embed.description = f"*{m['desc']}*\n🟢 **Machine disponible**"

    # ── Reel grid ───────────────────────────────────────────────
    if last_result:
        grid = last_result["grid"]
        winning_nums = {wl["num"] for wl in last_result["winning_lines"]}
        grid_text = _format_grid(grid, winning_nums, m["reels"], m["rows"], m["paylines"])
        embed.add_field(name="🎰 Rouleaux", value=f"```\n{grid_text}\n```", inline=False)

        # Winning lines summary
        if last_result["winning_lines"]:
            lines_text = []
            for wl in last_result["winning_lines"]:
                syms = " ".join(wl["symbols"][:m["reels"]])
                match_label = {2:"PAIRE",3:"TRIPLE",4:"QUADRUPLE",5:"QUINTUPLE"}.get(wl["match"],"WIN")
                lines_text.append(f"✅ {wl['name']} — {match_label} → +{_fmt(wl['win'])} 🪙")
            extras = []
            if last_result.get("fire_mult"):    extras.append(f"🔥 ×{last_result['fire_mult']}")
            if last_result.get("mystery_mult"): extras.append(f"🌀 ×{last_result['mystery_mult']}")
            if last_result.get("expanding_wild"): extras.append("🛸 Wild Galactique !")
            if last_result.get("legendary"):    extras.append(f"👑 LÉGENDAIRE ×{m['legendary_mult']}")
            if last_result.get("jackpot_hit"):  lines_text = [f"🏆 **JACKPOT !** +{_fmt(last_result['jackpot_val'])} 🪙"]
            summary = "\n".join(lines_text)
            if extras:
                summary += f"\n*{', '.join(extras)}*"
            embed.add_field(name="Résultat", value=summary, inline=False)
        elif last_result.get("scatter_count", 0) >= m.get("scatter_trigger", 99):
            embed.add_field(name="Résultat",
                value=f"🌊 **{last_result['scatter_count']}× Vagues** — Spins Gratuits activés !",
                inline=False)
        else:
            embed.add_field(name="Résultat", value="❌ Aucune combinaison gagnante", inline=False)

        # DoN pending
        if don_pending:
            embed.add_field(
                name="👻 Quitte ou Double !",
                value=f"Gain en jeu : **{_fmt(don_pending)} 🪙**\nDoubles ou perds tout ?",
                inline=False,
            )

        # Scatter spins remaining
        if scatter_spins > 0:
            embed.add_field(
                name="⚡ Spins Gratuits ×2",
                value=f"**{scatter_spins}** spin(s) gratuit(s) restant(s)",
                inline=True,
            )
    else:
        # No result yet — show paytable
        pay_lines = []
        for i in range(len(m["symbols"]) - 1, -1, -1):
            p3 = m["pay3"][i]
            sym = m["symbols"][i]
            if p3 > 0:
                pay_lines.append(f"{sym}{sym}{sym} → ×{p3:.0f}")
            elif m.get("special") == "jackpot" and i == len(m["symbols"]) - 1:
                pay_lines.append(f"{sym}{sym}{sym} → 🏆 **JACKPOT**")
            if len(pay_lines) >= 4:
                break
        if pay_lines:
            embed.add_field(name="💎 Top gains", value="\n".join(pay_lines), inline=True)

    # ── Machine info ────────────────────────────────────────────
    if machine_id == 7:
        jackpot_val = data.get("slot_jackpot", m["jackpot_seed"])
        embed.add_field(name="🏆 Jackpot actuel", value=f"**{_fmt(jackpot_val)} 🪙**", inline=True)

    if seated_uid:
        currency = state.get("currency", "jetons")
        p = data.get("players", {}).get(seated_uid, {})
        cur_sym = "🪙" if currency == "jetons" else "🎟️"
        embed.add_field(
            name="📊 Session",
            value=(
                f"🪙 Jetons : **{_fmt(p.get('balance', 0))}**\n"
                f"🎟️ Freebets : **{_fmt(p.get('freebets', 0))}**\n"
                f"🎲 Mise : **{_fmt(current_bet)}** {cur_sym}\n"
                f"💸 Jetons misés : **{_fmt(state.get('session_jetons_spent', 0))}**\n"
                f"🎫 Freebets misés : **{_fmt(state.get('session_freebets_spent', 0))}**\n"
                f"📈 Gains session : **+{_fmt(state.get('session_gains', 0))}** 🪙"
            ),
            inline=True,
        )

    if m.get("special"):
        embed.add_field(name="✨ Spécial", value=m["special_desc"], inline=False)

    embed.set_footer(
        text=f"Machine #{machine_id} • RTP {m['rtp']}% • {m['vol_emoji']} {m['volatility']} "
             f"• {m['reels']} rouleaux × {m['rows']} rangées • {m['paylines']} paylines"
    )
    return embed


# ─── Views ───────────────────────────────────────────────────────────────────

class SlotBetSelect(discord.ui.Select):
    def __init__(self, machine_id: int, current_bet: int):
        m = MACHINES[machine_id]
        options = [
            discord.SelectOption(label=f"{_fmt(b)} 🪙 / 🎟️", value=str(b), default=(b == current_bet))
            for b in m["bets"]
        ]
        super().__init__(
            placeholder="Choisir la mise…",
            options=options,
            custom_id=f"slot_bet_{machine_id}",
            row=0,
        )
        self.machine_id = machine_id

    async def callback(self, interaction: discord.Interaction):
        data = load_casino()
        state = _get_state(self.machine_id, data)
        if state.get("seated_user") != str(interaction.user.id):
            return await interaction.response.send_message("❌ Tu n'es pas assis(e) ici !", ephemeral=True)
        state["current_bet"] = int(self.values[0])
        state["last_action"] = time.time()
        save_casino(data)
        await interaction.response.defer()
        cog: SlotsCog = interaction.client.cogs.get("SlotsCog")
        embed = _build_game_embed(self.machine_id, data)
        view = SlotGameView(self.machine_id, cog, data)
        await interaction.edit_original_response(embed=embed, view=view)


class SlotLoopModal(discord.ui.Modal):
    """Modal de configuration de la boucle — remplace le message éphémère."""

    max_spins_input = discord.ui.TextInput(
        label="Nombre de spins (0 = illimité)",
        placeholder="Ex: 50  |  0 = jouer jusqu'aux fonds insuffisants",
        default="0",
        min_length=1,
        max_length=4,
        required=True,
    )

    def __init__(self, machine_id: int, currency: str):
        cur_label = "Jetons 🪙" if currency == "jetons" else "Freebets 🎟️"
        super().__init__(title=f"🔄 Boucle {cur_label} — Machine #{machine_id}")
        self.machine_id = machine_id
        self.currency = currency

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.max_spins_input.value.strip()
        if not raw.isdigit():
            return await interaction.response.send_message(
                "❌ Valeur invalide — entre un nombre entier (0 = illimité).", ephemeral=True
            )
        max_spins = int(raw) or None  # 0 → None = illimité
        data = load_casino()
        state = _get_state(self.machine_id, data)
        if state.get("seated_user") != str(interaction.user.id):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        cog: SlotsCog = interaction.client.cogs.get("SlotsCog")
        # Acquitter le modal silencieusement — on garde l'interaction sit existante
        # pour continuer à éditer le même message éphémère (évite la disparition)
        await interaction.response.defer(ephemeral=True)
        await cog._start_loop(self.machine_id, interaction.user.id, self.currency, max_spins)


class SlotHubView(discord.ui.View):
    """Persistent hub view — un bouton par machine dans le message public."""

    def __init__(self):
        super().__init__(timeout=None)
        for mid in MACHINES:
            m = MACHINES[mid]
            btn = discord.ui.Button(
                label=f"{m['emoji']} Machine #{mid}",
                custom_id=f"slot_hub_{mid}",
                style=discord.ButtonStyle.primary,
                row=(mid - 1) // 5,
            )
            btn.callback = self._make_sit_cb(mid)
            self.add_item(btn)

        info_btn = discord.ui.Button(
            label="ℹ️ Informations",
            style=discord.ButtonStyle.secondary,
            custom_id="slot_hub_info",
            row=2,
        )
        info_btn.callback = self._info_cb
        self.add_item(info_btn)

    async def _info_cb(self, interaction: discord.Interaction):
        def _describe_pl(coords: list) -> str:
            rows_used = [r for r, c in coords]
            if len(set(rows_used)) == 1:
                names = {0: "rangée haute", 1: "rangée centrale", 2: "rangée basse", 3: "rangée basse"}
                return names.get(rows_used[0], f"rangée {rows_used[0]}")
            if rows_used == sorted(rows_used):
                return "diagonale ↘"
            if rows_used == sorted(rows_used, reverse=True):
                return "diagonale ↗"
            return "zigzag"

        embed = discord.Embed(
            title="ℹ️ Informations — Machines à Sous",
            color=0xFFD700,
        )
        embed.add_field(
            name="📊 Volatilités",
            value=(
                "🟢 **Très Faible** — Gains très fréquents, petits montants\n"
                "🟢 **Faible** — Gains fréquents, montants modestes\n"
                "🟡 **Moyenne** — Équilibre entre fréquence et montant\n"
                "🔴 **Haute** — Gains rares mais élevés\n"
                "🔴 **Extrême** — Gains très rares, montants énormes\n"
                "🟣 **Aléatoire** — Imprévisible, tout peut arriver"
            ),
            inline=False,
        )
        for mid, m in MACHINES.items():
            key = (m["reels"], m["rows"])
            paylines_def = _PAYLINES.get(key, {})
            pl_lines = "\n".join(
                f"`#{num}` {_describe_pl(coords)}"
                for num, coords in sorted(paylines_def.items())
            ) or "*—*"
            embed.add_field(
                name=f"{m['emoji']} #{mid} — {m['name']} ({m['vol_emoji']} {m['volatility']})",
                value=(
                    f"🎰 {m['reels']} col. × {m['rows']} rang. — **{m['paylines']} paylines**\n"
                    f"{pl_lines}\n"
                    f"✨ {m.get('special_desc', 'Aucun')}"
                ),
                inline=True,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def _make_sit_cb(self, machine_id: int):
        async def _sit_cb(interaction: discord.Interaction):
            data = load_casino()
            state = _get_state(machine_id, data)
            now  = time.time()
            uid  = str(interaction.user.id)
            cog: SlotsCog = interaction.client.cogs.get("SlotsCog")

            # Machine occupée ?
            if state.get("seated_user"):
                elapsed = now - state.get("last_action", 0)
                if elapsed < INACTIVITY_TIMEOUT:
                    # C'est le joueur lui-même → reprendre la session éphémère
                    if state.get("seated_user") == uid:
                        cog.sit_interactions[machine_id] = interaction
                        embed = _build_game_embed(machine_id, data)
                        view  = SlotGameView(machine_id, cog, data)
                        return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
                    # Quelqu'un d'autre
                    expiry_ts = int(state.get("last_action", 0) + INACTIVITY_TIMEOUT)
                    name = state.get("seated_username", "quelqu'un")
                    return await interaction.response.send_message(
                        f"🔒 Machine occupée par **{name}** (éjection auto <t:{expiry_ts}:R>)", ephemeral=True
                    )
                # Joueur inactif → éjection auto (fall-through)

            # Déjà assis à un autre jeu non-slots ?
            seated_game = get_seated_game(uid, data)
            if seated_game and not seated_game.startswith("slots_"):
                label = _seated_game_label(seated_game)
                return await interaction.response.send_message(
                    f"❌ Tu es déjà assis(e) à **{label}**. Lève-toi d'abord !", ephemeral=True
                )

            # Déjà assis à une autre machine → bloquer si boucle, sinon auto-désassoir
            for other_mid, other_state in data.get("slot_machines", {}).items():
                other_mid_int = int(other_mid)
                if other_mid_int != machine_id and other_state.get("seated_user") == uid:
                    if other_state.get("loop_running"):
                        return await interaction.response.send_message(
                            f"❌ Une boucle est en cours sur la **Machine #{other_mid_int}** — arrête-la avant de changer de machine !",
                            ephemeral=True,
                        )
                    data["slot_machines"][other_mid] = {}
                    cog.sit_interactions.pop(other_mid_int, None)

            _ensure_player(data, uid)
            data["players"][uid]["username"] = interaction.user.display_name
            m = MACHINES[machine_id]
            state.update({
                "seated_user":          uid,
                "seated_username":      interaction.user.display_name,
                "last_action":          now,
                "current_bet":          m["bets"][0],
                "loop_running":         False,
                "loop_spins_done":      0,
                "loop_total_won":       0,
                "loop_total_lost":      0,
                "don_pending_win":      None,
                "scatter_spins_left":   0,
                "free_spin_offered":    False,
                "last_result":          None,
                "last_spin":            0,
                "currency":             "jetons",
                "session_jetons_spent": 0,
                "session_freebets_spent": 0,
                "session_gains":        0,
            })
            set_seated_game(uid, f"slots_{machine_id}", data)
            save_casino(data)

            # Stocker l'interaction pour les mises à jour en arrière-plan (boucle)
            cog.sit_interactions[machine_id] = interaction

            # Mettre à jour le hub public
            await cog._refresh_hub(data)

            # Envoyer le panneau de jeu éphémère
            embed = _build_game_embed(machine_id, data)
            view  = SlotGameView(machine_id, cog, data)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        return _sit_cb


class SlotGameView(discord.ui.View):
    """Vue éphémère de jeu pour un joueur assis à une machine."""

    def __init__(self, machine_id: int, cog: "SlotsCog", data: dict | None = None):
        super().__init__(timeout=None)
        self.machine_id = machine_id
        self.cog        = cog
        if data is None:
            data = load_casino()
        state            = _get_state(machine_id, data)
        loop_running     = state.get("loop_running", False)
        don_pending      = state.get("don_pending_win")
        scatter_spins    = state.get("scatter_spins_left", 0)
        free_spin_offered = state.get("free_spin_offered", False)
        current_bet      = state.get("current_bet", MACHINES[machine_id]["bets"][0])

        if loop_running:
            stop = discord.ui.Button(
                label="⏹ Arrêter la boucle",
                style=discord.ButtonStyle.danger,
                custom_id=f"slotg_stop_{machine_id}",
                row=0,
            )
            stop.callback = self._stop_loop_cb
            self.add_item(stop)

        elif don_pending:
            dbl  = discord.ui.Button(label="👻 DOUBLER !", style=discord.ButtonStyle.danger,
                                      custom_id=f"slotg_don_double_{machine_id}", row=0)
            keep = discord.ui.Button(label="💰 Garder le gain", style=discord.ButtonStyle.success,
                                      custom_id=f"slotg_don_keep_{machine_id}", row=0)
            dbl.callback  = self._don_double_cb
            keep.callback = self._don_keep_cb
            self.add_item(dbl)
            self.add_item(keep)

        elif scatter_spins > 0:
            fs = discord.ui.Button(
                label=f"⚡ Spin Gratuit ×2 ({scatter_spins} restant(s))",
                style=discord.ButtonStyle.primary,
                custom_id=f"slotg_freespin_{machine_id}",
                row=0,
            )
            fs.callback = self._free_spin_cb
            self.add_item(fs)

        elif free_spin_offered:
            yes = discord.ui.Button(label="🌟 Spin Gratuit !", style=discord.ButtonStyle.success,
                                     custom_id=f"slotg_fsoffer_yes_{machine_id}", row=0)
            no  = discord.ui.Button(label="Non merci", style=discord.ButtonStyle.secondary,
                                     custom_id=f"slotg_fsoffer_no_{machine_id}", row=0)
            yes.callback = self._fsoffer_yes_cb
            no.callback  = self._fsoffer_no_cb
            self.add_item(yes)
            self.add_item(no)

        else:
            self.add_item(SlotBetSelect(machine_id, current_bet))
            in_cd = time.time() - state.get("last_spin", 0) < SPIN_CD
            for label, cid, style, cb, disabled in [
                ("🪙 Jeton",           f"slotg_spin1j_{machine_id}",  discord.ButtonStyle.primary,   self._spin1j_cb, in_cd),
                ("🎟️ Freebet",         f"slotg_spin1f_{machine_id}",  discord.ButtonStyle.secondary, self._spin1f_cb, in_cd),
                ("🔄 Boucle Jetons",   f"slotg_loopj_{machine_id}",   discord.ButtonStyle.primary,   self._loopj_cb,  False),
                ("🔄 Boucle Freebets", f"slotg_loopf_{machine_id}",   discord.ButtonStyle.secondary, self._loopf_cb,  False),
                ("🚪 Se lever",        f"slotg_leave_{machine_id}",   discord.ButtonStyle.danger,    self._leave_cb,  False),
            ]:
                btn = discord.ui.Button(label=label, style=style, custom_id=cid, row=1, disabled=disabled)
                btn.callback = cb
                self.add_item(btn)

    # ── Helpers ─────────────────────────────────────────────────

    def _check_seated(self, interaction: discord.Interaction) -> bool:
        data  = load_casino()
        state = _get_state(self.machine_id, data)
        return state.get("seated_user") == str(interaction.user.id)

    async def _edit_game(self, interaction: discord.Interaction, data: dict) -> None:
        embed = _build_game_embed(self.machine_id, data)
        view  = SlotGameView(self.machine_id, self.cog, data)
        await interaction.edit_original_response(embed=embed, view=view)

    # ── Se lever ────────────────────────────────────────────────

    async def _leave_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        data = load_casino()
        uid  = str(interaction.user.id)
        data["slot_machines"][str(self.machine_id)] = {}
        set_seated_game(uid, None, data)
        save_casino(data)
        self.cog.sit_interactions.pop(self.machine_id, None)
        await self.cog._refresh_hub(data)
        await interaction.edit_original_response(
            embed=discord.Embed(
                title="🚪 Machine quittée",
                description="Tu as quitté la machine. À bientôt !",
                color=0x95A5A6,
            ),
            view=None,
        )

    # ── Stop loop ───────────────────────────────────────────────

    async def _stop_loop_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        task = self.cog.active_loops.get(self.machine_id)
        if task and not task.done():
            task.cancel()
        data  = load_casino()
        state = _get_state(self.machine_id, data)
        state["loop_running"] = False
        state["last_action"]  = time.time()
        save_casino(data)
        await self._edit_game(interaction, data)

    # ── Spin once ───────────────────────────────────────────────

    async def _spin1j_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        ok, data = await self.cog._do_panel_spin(self.machine_id, interaction.user.id, "jetons")
        if data:
            await self._edit_game(interaction, data)

    async def _spin1f_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        ok, data = await self.cog._do_panel_spin(self.machine_id, interaction.user.id, "freebets")
        if data:
            await self._edit_game(interaction, data)

    # ── Loop buttons ────────────────────────────────────────────

    async def _loopj_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.send_modal(SlotLoopModal(self.machine_id, "jetons"))

    async def _loopf_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.send_modal(SlotLoopModal(self.machine_id, "freebets"))

    # ── Double or Nothing ───────────────────────────────────────

    async def _don_double_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        data  = load_casino()
        state = _get_state(self.machine_id, data)
        uid   = str(interaction.user.id)
        pending = state.get("don_pending_win", 0)
        p = data["players"][uid]
        if random.random() < 0.5:
            final = pending * 2
            p["balance"] += final
            p["max_balance"] = max(p.get("max_balance", 0), p["balance"])
            state["don_note"] = f"👻 DOUBLEMENT ! +{_fmt(final)} 🪙"
        else:
            state["don_note"] = "💀 Les spectres ont tout emporté…"
        state["don_pending_win"] = None
        state["last_action"]     = time.time()
        save_casino(data)
        casino = self.cog.bot.get_cog("Casino")
        if casino: casino.trigger_leaderboard_update()
        await self._edit_game(interaction, data)

    async def _don_keep_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        data  = load_casino()
        state = _get_state(self.machine_id, data)
        uid   = str(interaction.user.id)
        pending = state.get("don_pending_win", 0)
        p = data["players"][uid]
        p["balance"]     += pending
        p["max_balance"]  = max(p.get("max_balance", 0), p["balance"])
        state["don_pending_win"] = None
        state["don_note"]        = f"💰 Gain conservé : +{_fmt(pending)} 🪙"
        state["last_action"]     = time.time()
        save_casino(data)
        casino = self.cog.bot.get_cog("Casino")
        if casino: casino.trigger_leaderboard_update()
        await self._edit_game(interaction, data)

    # ── Free spin (Atlantide scatter) ───────────────────────────

    async def _free_spin_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        ok, data = await self.cog._do_panel_spin(self.machine_id, interaction.user.id, "jetons",
                                                   is_free=True, free_mult=2.0)
        if data:
            await self._edit_game(interaction, data)

    # ── Free spin offer (Trèfle Chanceux) ───────────────────────

    async def _fsoffer_yes_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        data  = load_casino()
        state = _get_state(self.machine_id, data)
        state["free_spin_offered"] = False
        save_casino(data)
        ok, data = await self.cog._do_panel_spin(self.machine_id, interaction.user.id, "jetons", is_free=True)
        if data:
            await self._edit_game(interaction, data)

    async def _fsoffer_no_cb(self, interaction: discord.Interaction):
        if not self._check_seated(interaction):
            return await interaction.response.send_message("❌ Tu n'es plus assis(e) ici !", ephemeral=True)
        await interaction.response.defer()
        data  = load_casino()
        state = _get_state(self.machine_id, data)
        state["free_spin_offered"] = False
        state["last_action"]       = time.time()
        save_casino(data)
        await self._edit_game(interaction, data)


# ─── Cog ─────────────────────────────────────────────────────────────────────

class SlotsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_loops: dict[int, asyncio.Task] = {}
        self.sit_interactions: dict[int, discord.Interaction] = {}

    async def cog_load(self):
        # Clear stale loop states from previous run
        data = load_casino()
        for mid in MACHINES:
            state = data.get("slot_machines", {}).get(str(mid), {})
            if state.get("loop_running"):
                state["loop_running"] = False
        save_casino(data)
        # Register single persistent hub view
        self.bot.add_view(SlotHubView())
        self.setup_panels_task.start()
        self.inactivity_task.start()

    async def cog_unload(self):
        for task in self.active_loops.values():
            task.cancel()
        self.inactivity_task.cancel()

    # ── Hub management ──────────────────────────────────────────

    async def _upsert_hub_panel(self, data: dict | None = None) -> None:
        channel = self.bot.get_channel(SLOT_CHANNEL_ID)
        if not channel:
            return
        if data is None:
            data = load_casino()
        msg_id = data.get("messages", {}).get("slot_hub")
        embed = _build_hub_embed(data)
        view  = SlotHubView()
        if msg_id:
            try:
                msg = await channel.fetch_message(int(msg_id))
                await msg.edit(embed=embed, view=view)
                return
            except Exception:
                pass
        msg = await channel.send(embed=embed, view=view)
        data.setdefault("messages", {})["slot_hub"] = msg.id
        save_casino(data)

    async def _refresh_hub(self, data: dict | None = None) -> None:
        """Edit the hub message with current state."""
        channel = self.bot.get_channel(SLOT_CHANNEL_ID)
        if not channel:
            return
        if data is None:
            data = load_casino()
        msg_id = data.get("messages", {}).get("slot_hub")
        if not msg_id:
            await self._upsert_hub_panel(data)
            return
        try:
            msg = await channel.fetch_message(int(msg_id))
            await msg.edit(embed=_build_hub_embed(data), view=SlotHubView())
        except Exception as e:
            logger.warning("slots: refresh hub failed: %s", e)

    async def _refresh_game_ephemeral(self, machine_id: int, data: dict) -> None:
        """Update the ephemeral game message via stored sit interaction."""
        sit_inter = self.sit_interactions.get(machine_id)
        if not sit_inter:
            return
        try:
            embed = _build_game_embed(machine_id, data)
            view  = SlotGameView(machine_id, self, data)
            await sit_inter.edit_original_response(embed=embed, view=view)
        except Exception as e:
            logger.debug("slots: ephemeral refresh #%d failed: %s", machine_id, e)

    # ── Core spin ───────────────────────────────────────────────

    async def _do_panel_spin(
        self,
        machine_id: int,
        user_id: int,
        currency: str,
        is_free: bool = False,
        free_mult: float = 1.0,
    ) -> tuple[bool, dict | None]:
        """Execute one spin, update casino.json, refresh hub. Returns (ok, data) or (False, None)."""
        m = MACHINES[machine_id]
        data = load_casino()
        uid = str(user_id)
        _ensure_player(data, uid)
        p = data["players"][uid]
        state = _get_state(machine_id, data)
        bet = state.get("current_bet", m["bets"][0])

        if not is_free:
            balance_key = "balance" if currency == "jetons" else "freebets"
            if p.get(balance_key, 0) < bet:
                state["last_action"] = time.time()
                state["loop_running"] = False
                save_casino(data)
                await self._refresh_hub(data)
                await self._refresh_game_ephemeral(machine_id, data)
                return False, None
            p[balance_key] -= bet
            state["loop_total_lost"] = state.get("loop_total_lost", 0) + bet
            if currency == "jetons":
                state["session_jetons_spent"] = state.get("session_jetons_spent", 0) + bet
            else:
                state["session_freebets_spent"] = state.get("session_freebets_spent", 0) + bet
            # Tracking gang stats (jetons uniquement, pas les freebets)
            if currency == "jetons":
                p["total_wagered_slots"] = p.get("total_wagered_slots", 0) + bet
                p["total_games_slots"]   = p.get("total_games_slots", 0) + 1

        # Jackpot pool contribution
        if m.get("special") == "jackpot" and not is_free:
            contrib = int(bet * m["jackpot_contrib"])
            data["slot_jackpot"] = data.get("slot_jackpot", m["jackpot_seed"]) + contrib

        grid = _spin_grid(m)
        result = _evaluate_spin(grid, machine_id, bet, extra_mult=free_mult, data=data)
        win = result["total_win"]

        # Apply win
        if result["jackpot_hit"]:
            p["balance"] += win
            p["max_balance"] = max(p.get("max_balance", 0), p["balance"])
            data["slot_jackpot"] = m["jackpot_seed"]
        elif win > 0 and m.get("special") != "double_or_nothing":
            net = win - bet if currency == "freebets" else win
            if net > 0:
                p["balance"] = p.get("balance", 0) + net
                p["max_balance"] = max(p.get("max_balance", 0), p["balance"])

        state["last_result"] = result
        state["last_action"] = time.time()
        state["last_spin"]   = time.time()
        state["currency"] = currency
        state["loop_spins_done"] = state.get("loop_spins_done", 0) + 1
        net_win = (win - bet if currency == "freebets" else win) if win > 0 else 0
        if net_win > 0:
            state["loop_total_won"] = state.get("loop_total_won", 0) + net_win
            state["session_gains"]  = state.get("session_gains", 0) + net_win

        # Handle specials that require player action
        state["don_pending_win"] = None
        state["scatter_spins_left"] = state.get("scatter_spins_left", 0)
        state["free_spin_offered"] = False

        if win > 0 and m.get("special") == "double_or_nothing" and not is_free:
            don_amount = win - bet if currency == "freebets" else win
            if don_amount > 0:
                state["don_pending_win"] = don_amount

        if m.get("special") == "scatter_free_spins" and result["scatter_count"] >= m["scatter_trigger"]:
            if not is_free:
                state["scatter_spins_left"] = m["free_spins_count"]

        if state.get("scatter_spins_left", 0) > 0 and is_free:
            state["scatter_spins_left"] = max(0, state["scatter_spins_left"] - 1)

        if win > 0 and m.get("special") == "free_spin" and not is_free:
            fs_done = state.get("free_spins_consecutive", 0) + 1
            state["free_spins_consecutive"] = fs_done
            if fs_done <= m.get("max_free_spins", 3):
                state["free_spin_offered"] = True
        else:
            state["free_spins_consecutive"] = 0

        save_casino(data)
        casino = self.bot.get_cog("Casino")
        if casino: casino.trigger_leaderboard_update()
        await self._refresh_hub(data)
        # Re-enable spin buttons after cooldown (skip during loop to avoid redundant edits)
        if not state.get("loop_running"):
            asyncio.create_task(self._delayed_refresh(machine_id, SPIN_CD))
        return True, data

    async def _delayed_refresh(self, machine_id: int, delay: float) -> None:
        await asyncio.sleep(delay)
        data = load_casino()
        await self._refresh_game_ephemeral(machine_id, data)

    # ── Loop management ─────────────────────────────────────────

    async def _start_loop(self, machine_id: int, user_id: int,
                           currency: str, max_spins: int | None) -> None:
        data = load_casino()
        state = _get_state(machine_id, data)
        state["loop_running"] = True
        state["loop_spins_done"] = 0
        state["loop_total_won"] = 0
        state["loop_total_lost"] = 0
        state["last_action"] = time.time()
        save_casino(data)
        await self._refresh_hub(data)
        await self._refresh_game_ephemeral(machine_id, data)

        # Cancel any existing loop for this machine
        old = self.active_loops.get(machine_id)
        if old and not old.done():
            old.cancel()

        self.active_loops[machine_id] = asyncio.create_task(
            self._run_loop_task(machine_id, user_id, currency, max_spins)
        )

    async def _consume_free_spins_in_loop(self, machine_id: int, user_id: int, currency: str) -> None:
        """Pendant une boucle, consomme automatiquement les free spins en attente."""
        m_def = MACHINES[machine_id]
        fs_chain = 0
        while True:
            data = load_casino()
            state = _get_state(machine_id, data)
            if not state.get("loop_running"):
                break

            # M8 (Atlantide) : scatter free spins ×2
            if state.get("scatter_spins_left", 0) > 0:
                ok, data = await self._do_panel_spin(machine_id, user_id, currency, is_free=True, free_mult=2.0)
                if data:
                    await self._refresh_game_ephemeral(machine_id, data)
                await asyncio.sleep(LOOP_DELAY)
                continue

            # M5 (Trèfle) : free spin offert après une victoire (avec chaîne jusqu'au max)
            if state.get("free_spin_offered"):
                fs_chain += 1
                ok, data = await self._do_panel_spin(machine_id, user_id, currency, is_free=True)
                if data:
                    new_state = _get_state(machine_id, data)
                    # Chaîner si le free spin a gagné et qu'on n'a pas atteint le max
                    if (new_state.get("last_result", {}).get("total_win", 0) > 0
                            and m_def.get("special") == "free_spin"
                            and fs_chain < m_def.get("max_free_spins", 3)):
                        new_state["free_spin_offered"] = True
                        save_casino(data)
                    await self._refresh_game_ephemeral(machine_id, data)
                await asyncio.sleep(LOOP_DELAY)
                continue

            break

    async def _run_loop_task(self, machine_id: int, user_id: int,
                              currency: str, max_spins: int | None) -> None:
        spins = 0
        try:
            while True:
                data = load_casino()
                state = _get_state(machine_id, data)
                if not state.get("loop_running") or state.get("seated_user") != str(user_id):
                    break
                if max_spins and spins >= max_spins:
                    break
                ok, data = await self._do_panel_spin(machine_id, user_id, currency)
                if not ok:
                    break
                spins += 1
                # Consommer les free spins gagnés avant le prochain spin régulier
                await self._consume_free_spins_in_loop(machine_id, user_id, currency)
                data = load_casino()
                await self._refresh_game_ephemeral(machine_id, data)
                await asyncio.sleep(LOOP_DELAY)
        except asyncio.CancelledError:
            pass
        finally:
            data = load_casino()
            state = _get_state(machine_id, data)
            state["loop_running"] = False
            state["last_action"] = time.time()
            save_casino(data)
            await self._refresh_hub(data)
            await self._refresh_game_ephemeral(machine_id, data)

    # ── Inactivity timer ────────────────────────────────────────

    @tasks.loop(seconds=15)
    async def inactivity_task(self):
        now = time.time()
        data = load_casino()
        changed = False
        for mid in MACHINES:
            state = data.get("slot_machines", {}).get(str(mid), {})
            if not state.get("seated_user"):
                continue
            if state.get("loop_running"):
                continue
            elapsed = now - state.get("last_action", now)
            if elapsed >= INACTIVITY_TIMEOUT:
                uid = state.get("seated_user")
                self.sit_interactions.pop(mid, None)
                data["slot_machines"][str(mid)] = {}
                if uid:
                    set_seated_game(uid, None, data)
                changed = True
        if changed:
            save_casino(data)
            try:
                await self._refresh_hub(data)
            except Exception:
                pass

    @inactivity_task.before_loop
    async def before_inactivity(self):
        await self.bot.wait_until_ready()

    # ── Setup ───────────────────────────────────────────────────

    @tasks.loop(count=1)
    async def setup_panels_task(self):
        await self.bot.wait_until_ready()
        self.bot._startup_queue.put_nowait(self._upsert_hub_panel)

    @setup_panels_task.before_loop
    async def before_setup(self):
        await self.bot.wait_until_ready()
