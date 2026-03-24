"""
Quêtes du RPG — Mode Histoire Linéaire.

Deux chaînes indépendantes, une quête active à la fois dans chaque chaîne :
  - MAIN_QUESTS    : progression solo (zones, niveaux, donjons, world boss)
  - SECONDARY_QUESTS : activités variées (métiers, commerce, raids, PvP)

Chaque quête :  id, name, emoji, desc, progress_key, threshold, xp, gold
  + optionnel : special {"type": ..., "value": ...}  pour les récompenses passives
"""
from __future__ import annotations

# ─── Quêtes Principales (42) ─────────────────────────────────────────────────
# World Boss disponible à partir de la zone 1000 → toutes les quêtes WB
# apparaissent après la quête "Porte du World Boss" (zone 1000).

MAIN_QUESTS: list[dict] = [
    {
        "id": "q01", "name": "L'Aventure Commence", "emoji": "🌱",
        "desc": "Atteins la **zone 5** dans le monde.",
        "progress_key": "zone", "threshold": 5,
        "xp": 500, "gold": 100,
        "special": {"type": "energy_on_win", "value": 0.05},
        "special_desc": "✨ Passif débloqué : **5% de chance** de gagner **+1 énergie** après chaque combat gagné.",
    },
    {
        "id": "q02", "name": "Premiers Combats", "emoji": "⚔️",
        "desc": "Atteins la **zone 20**.",
        "progress_key": "zone", "threshold": 20,
        "xp": 2_000, "gold": 500,
    },
    {
        "id": "q03", "name": "Forgé au Combat", "emoji": "🔥",
        "desc": "Atteins la **zone 50**.",
        "progress_key": "zone", "threshold": 50,
        "xp": 5_000, "gold": 1_000,
    },
    {
        "id": "q04", "name": "Guerrier Aguerri", "emoji": "🗡️",
        "desc": "Atteins le **niveau 10**.",
        "progress_key": "level", "threshold": 10,
        "xp": 8_000, "gold": 2_000,
    },
    {
        "id": "q05", "name": "Explorateur", "emoji": "🗺️",
        "desc": "Atteins la **zone 100**.",
        "progress_key": "zone", "threshold": 100,
        "xp": 15_000, "gold": 3_000,
    },
    {
        "id": "q06", "name": "Premier Donjon", "emoji": "🏰",
        "desc": "Complète un **donjon classique** (niveau 1 minimum).",
        "progress_key": "dungeon_best_classique", "threshold": 1,
        "xp": 20_000, "gold": 5_000,
    },
    {
        "id": "q07", "name": "Terres Inconnues", "emoji": "🌄",
        "desc": "Atteins la **zone 200**.",
        "progress_key": "zone", "threshold": 200,
        "xp": 30_000, "gold": 8_000,
    },
    {
        "id": "q08", "name": "Montée en Puissance", "emoji": "📈",
        "desc": "Atteins le **niveau 25**.",
        "progress_key": "level", "threshold": 25,
        "xp": 40_000, "gold": 10_000,
    },
    {
        "id": "q09", "name": "Habitué des Donjons", "emoji": "🔑",
        "desc": "Complète un **donjon classique niveau 10**.",
        "progress_key": "dungeon_best_classique", "threshold": 10,
        "xp": 50_000, "gold": 12_000,
    },
    {
        "id": "q10", "name": "Horizons Lointains", "emoji": "🌅",
        "desc": "Atteins la **zone 300**.",
        "progress_key": "zone", "threshold": 300,
        "xp": 60_000, "gold": 15_000,
    },
    {
        "id": "q11", "name": "Maître Classique", "emoji": "🏆",
        "desc": "Complète un **donjon classique niveau 30**.",
        "progress_key": "dungeon_best_classique", "threshold": 30,
        "xp": 100_000, "gold": 25_000,
    },
    {
        "id": "q12", "name": "Demi-Chemin", "emoji": "🛣️",
        "desc": "Atteins la **zone 500**.",
        "progress_key": "zone", "threshold": 500,
        "xp": 150_000, "gold": 40_000,
    },
    {
        "id": "q13", "name": "Guerrier Confirmé", "emoji": "⚡",
        "desc": "Atteins le **niveau 50**.",
        "progress_key": "level", "threshold": 50,
        "xp": 200_000, "gold": 50_000,
    },
    {
        "id": "q14", "name": "Premier Défi Élite", "emoji": "🟦",
        "desc": "Complète un **donjon élite** (niveau 1 minimum).",
        "progress_key": "dungeon_best_elite", "threshold": 1,
        "xp": 250_000, "gold": 60_000,
    },
    {
        "id": "q15", "name": "Grande Traversée", "emoji": "🏔️",
        "desc": "Atteins la **zone 750**.",
        "progress_key": "zone", "threshold": 750,
        "xp": 300_000, "gold": 75_000,
    },
    {
        "id": "q16", "name": "Conquérant Classique", "emoji": "👑",
        "desc": "Complète un **donjon classique niveau 50**.",
        "progress_key": "dungeon_best_classique", "threshold": 50,
        "xp": 350_000, "gold": 90_000,
    },
    {
        "id": "q17", "name": "Porte du World Boss", "emoji": "🌑",
        "desc": "Atteins la **zone 1 000**.",
        "progress_key": "zone", "threshold": 1_000,
        "xp": 500_000, "gold": 150_000,
    },
    # ── World Boss — débloqué à partir de la zone 1000 ────────────────────────
    {
        "id": "q18", "name": "Chasseur Mondial", "emoji": "🌍",
        "desc": "Attaque le **World Boss** pour la première fois.",
        "progress_key": "world_boss_count", "threshold": 1,
        "xp": 600_000, "gold": 180_000,
    },
    {
        "id": "q19", "name": "Centurion", "emoji": "🛡️",
        "desc": "Atteins le **niveau 100**.",
        "progress_key": "level", "threshold": 100,
        "xp": 800_000, "gold": 200_000,
    },
    {
        "id": "q20", "name": "Expert Élite", "emoji": "💎",
        "desc": "Complète un **donjon élite niveau 20**.",
        "progress_key": "dungeon_best_elite", "threshold": 20,
        "xp": 900_000, "gold": 220_000,
    },
    {
        "id": "q21", "name": "Chasseur Acharné", "emoji": "🎯",
        "desc": "Attaque le **World Boss 10 fois**.",
        "progress_key": "world_boss_count", "threshold": 10,
        "xp": 1_000_000, "gold": 250_000,
    },
    {
        "id": "q22", "name": "Légende Classique", "emoji": "🌟",
        "desc": "Complète un **donjon classique niveau 100**.",
        "progress_key": "dungeon_best_classique", "threshold": 100,
        "xp": 1_200_000, "gold": 300_000,
    },
    {
        "id": "q23", "name": "Terres des Anciens", "emoji": "🗿",
        "desc": "Atteins la **zone 1 500**.",
        "progress_key": "zone", "threshold": 1_500,
        "xp": 1_500_000, "gold": 400_000,
    },
    {
        "id": "q24", "name": "Maître Élite", "emoji": "🔱",
        "desc": "Complète un **donjon élite niveau 50**.",
        "progress_key": "dungeon_best_elite", "threshold": 50,
        "xp": 1_800_000, "gold": 450_000,
    },
    {
        "id": "q25", "name": "Ascension", "emoji": "🚀",
        "desc": "Atteins le **niveau 150**.",
        "progress_key": "level", "threshold": 150,
        "xp": 2_000_000, "gold": 500_000,
    },
    {
        "id": "q26", "name": "Plongeon dans l'Abîme", "emoji": "🟥",
        "desc": "Complète un **donjon abyssal** (niveau 1 minimum).",
        "progress_key": "dungeon_best_abyssal", "threshold": 1,
        "xp": 2_500_000, "gold": 600_000,
    },
    {
        "id": "q27", "name": "Monde Profond", "emoji": "🌊",
        "desc": "Atteins la **zone 2 000**.",
        "progress_key": "zone", "threshold": 2_000,
        "xp": 3_000_000, "gold": 750_000,
    },
    {
        "id": "q28", "name": "Tueur de Titans", "emoji": "💀",
        "desc": "Attaque le **World Boss 50 fois**.",
        "progress_key": "world_boss_count", "threshold": 50,
        "xp": 3_500_000, "gold": 900_000,
    },
    {
        "id": "q29", "name": "Légende Élite", "emoji": "⭐",
        "desc": "Complète un **donjon élite niveau 100**.",
        "progress_key": "dungeon_best_elite", "threshold": 100,
        "xp": 4_000_000, "gold": 1_000_000,
    },
    {
        "id": "q30", "name": "Maître de Guerre", "emoji": "⚔️",
        "desc": "Atteins le **niveau 200**.",
        "progress_key": "level", "threshold": 200,
        "xp": 4_500_000, "gold": 1_100_000,
    },
    {
        "id": "q31", "name": "Au-delà du Possible", "emoji": "🌌",
        "desc": "Atteins la **zone 3 000**.",
        "progress_key": "zone", "threshold": 3_000,
        "xp": 5_000_000, "gold": 1_300_000,
    },
    {
        "id": "q32", "name": "Dévoreur d'Abîmes", "emoji": "🕳️",
        "desc": "Complète un **donjon abyssal niveau 20**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 20,
        "xp": 6_000_000, "gold": 1_500_000,
    },
    {
        "id": "q33", "name": "Seigneur de Guerre", "emoji": "🔴",
        "desc": "Atteins le **niveau 300**.",
        "progress_key": "level", "threshold": 300,
        "xp": 7_000_000, "gold": 1_800_000,
    },
    {
        "id": "q34", "name": "Mi-Légende", "emoji": "🏅",
        "desc": "Atteins la **zone 5 000**.",
        "progress_key": "zone", "threshold": 5_000,
        "xp": 8_000_000, "gold": 2_000_000,
    },
    {
        "id": "q35", "name": "Maître de l'Abîme", "emoji": "🌀",
        "desc": "Complète un **donjon abyssal niveau 50**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 50,
        "xp": 9_000_000, "gold": 2_200_000,
    },
    {
        "id": "q36", "name": "Gardien du Monde", "emoji": "🌐",
        "desc": "Attaque le **World Boss 100 fois**.",
        "progress_key": "world_boss_count", "threshold": 100,
        "xp": 10_000_000, "gold": 2_500_000,
    },
    {
        "id": "q37", "name": "Demi-Dieu", "emoji": "✨",
        "desc": "Atteins le **niveau 500**.",
        "progress_key": "level", "threshold": 500,
        "xp": 12_000_000, "gold": 3_000_000,
    },
    {
        "id": "q38", "name": "Terres Mythiques", "emoji": "🗺️",
        "desc": "Atteins la **zone 7 000**.",
        "progress_key": "zone", "threshold": 7_000,
        "xp": 15_000_000, "gold": 4_000_000,
    },
    {
        "id": "q39", "name": "Seigneur de l'Abîme", "emoji": "👁️",
        "desc": "Complète un **donjon abyssal niveau 100**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 100,
        "xp": 18_000_000, "gold": 5_000_000,
    },
    {
        "id": "q40", "name": "Quasi-Divin", "emoji": "💫",
        "desc": "Atteins le **niveau 700**.",
        "progress_key": "level", "threshold": 700,
        "xp": 25_000_000, "gold": 7_000_000,
    },
    {
        "id": "q41", "name": "La Légende", "emoji": "🌠",
        "desc": "Atteins la **zone 10 000**.",
        "progress_key": "zone", "threshold": 10_000,
        "xp": 50_000_000, "gold": 10_000_000,
    },
    {
        "id": "q42", "name": "Dieu Vivant", "emoji": "👑",
        "desc": "Atteins le **niveau 1 000**.",
        "progress_key": "level", "threshold": 1_000,
        "xp": 100_000_000, "gold": 20_000_000,
    },
]

# ─── Quêtes Secondaires (30) ──────────────────────────────────────────────────

SECONDARY_QUESTS: list[dict] = [
    {
        "id": "s01", "name": "Premier Métier", "emoji": "🌾",
        "desc": "Choisis une **profession de récolte**.",
        "progress_key": "has_harvest", "threshold": 1,
        "xp": 5_000, "gold": 1_000,
    },
    {
        "id": "s02", "name": "L'Artisan", "emoji": "🔨",
        "desc": "Choisis un **métier de craft**.",
        "progress_key": "has_craft", "threshold": 1,
        "xp": 5_000, "gold": 1_000,
    },
    {
        "id": "s03", "name": "Le Concepteur", "emoji": "📐",
        "desc": "Choisis un **métier de conception**.",
        "progress_key": "has_conception", "threshold": 1,
        "xp": 5_000, "gold": 1_000,
    },
    {
        "id": "s04", "name": "Mains dans la Terre", "emoji": "🌿",
        "desc": "Atteins le **niveau 10** en récolte.",
        "progress_key": "harvest_level", "threshold": 10,
        "xp": 20_000, "gold": 5_000,
    },
    {
        "id": "s05", "name": "Façonneur", "emoji": "⚒️",
        "desc": "Atteins le **niveau 10** en craft.",
        "progress_key": "craft_level", "threshold": 10,
        "xp": 20_000, "gold": 5_000,
    },
    {
        "id": "s06", "name": "L'Inventeur", "emoji": "💡",
        "desc": "Atteins le **niveau 10** en conception.",
        "progress_key": "conception_level", "threshold": 10,
        "xp": 20_000, "gold": 5_000,
    },
    {
        "id": "s07", "name": "Premier Échange", "emoji": "🤝",
        "desc": "Réalise un **échange** avec un autre joueur.",
        "progress_key": "trade_count", "threshold": 1,
        "xp": 10_000, "gold": 2_000,
    },
    {
        "id": "s08", "name": "Marchand Débutant", "emoji": "🏪",
        "desc": "Réalise une **vente** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 1,
        "xp": 10_000, "gold": 2_000,
    },
    {
        "id": "s09", "name": "Acheteur Avisé", "emoji": "🛒",
        "desc": "Réalise un **achat** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 1,
        "xp": 10_000, "gold": 2_000,
    },
    {
        "id": "s10", "name": "Récolte Intermédiaire", "emoji": "🌻",
        "desc": "Atteins le **niveau 50** en récolte.",
        "progress_key": "harvest_level", "threshold": 50,
        "xp": 100_000, "gold": 25_000,
    },
    {
        "id": "s11", "name": "Artisan Intermédiaire", "emoji": "🔧",
        "desc": "Atteins le **niveau 50** en craft.",
        "progress_key": "craft_level", "threshold": 50,
        "xp": 100_000, "gold": 25_000,
    },
    {
        "id": "s12", "name": "Concepteur Intermédiaire", "emoji": "📋",
        "desc": "Atteins le **niveau 50** en conception.",
        "progress_key": "conception_level", "threshold": 50,
        "xp": 100_000, "gold": 25_000,
    },
    {
        "id": "s13", "name": "Réseau de Marchands", "emoji": "🔗",
        "desc": "Réalise **10 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 10,
        "xp": 50_000, "gold": 10_000,
    },
    {
        "id": "s14", "name": "La Bonne Affaire", "emoji": "💰",
        "desc": "Réalise **10 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 10,
        "xp": 50_000, "gold": 10_000,
    },
    {
        "id": "s15", "name": "Collectionneur", "emoji": "📦",
        "desc": "Réalise **50 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 50,
        "xp": 200_000, "gold": 50_000,
    },
    {
        "id": "s16", "name": "Baptême du Feu", "emoji": "👥",
        "desc": "Complète ton **premier raid** en équipe.",
        "progress_key": "raid_max_completed", "threshold": 1,
        "xp": 500_000, "gold": 150_000,
    },
    {
        "id": "s17", "name": "Commerçant Aguerri", "emoji": "🤜",
        "desc": "Réalise **50 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 50,
        "xp": 200_000, "gold": 50_000,
    },
    {
        "id": "s18", "name": "Marchand Prospère", "emoji": "💹",
        "desc": "Réalise **50 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 50,
        "xp": 200_000, "gold": 50_000,
    },
    {
        "id": "s19", "name": "Dans l'Arène", "emoji": "⚔️",
        "desc": "Réalise ton **premier combat PvP**.",
        "progress_key": "pvp_fights", "threshold": 1,
        "xp": 30_000, "gold": 8_000,
    },
    {
        "id": "s20", "name": "Raid Avancé", "emoji": "🔥",
        "desc": "Complète un **raid niveau 3**.",
        "progress_key": "raid_max_completed", "threshold": 3,
        "xp": 1_500_000, "gold": 400_000,
    },
    {
        "id": "s21", "name": "Récolte Experte", "emoji": "🌳",
        "desc": "Atteins le **niveau 100** en récolte.",
        "progress_key": "harvest_level", "threshold": 100,
        "xp": 500_000, "gold": 100_000,
    },
    {
        "id": "s22", "name": "Artisan Expert", "emoji": "🛠️",
        "desc": "Atteins le **niveau 100** en craft.",
        "progress_key": "craft_level", "threshold": 100,
        "xp": 500_000, "gold": 100_000,
    },
    {
        "id": "s23", "name": "Concepteur Expert", "emoji": "🔬",
        "desc": "Atteins le **niveau 100** en conception.",
        "progress_key": "conception_level", "threshold": 100,
        "xp": 500_000, "gold": 100_000,
    },
    {
        "id": "s24", "name": "Gladiateur", "emoji": "🏟️",
        "desc": "Réalise **10 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 10,
        "xp": 100_000, "gold": 25_000,
    },
    {
        "id": "s25", "name": "Champion", "emoji": "🥇",
        "desc": "Remporte **10 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 10,
        "xp": 300_000, "gold": 75_000,
    },
    {
        "id": "s26", "name": "Raid Élite", "emoji": "💪",
        "desc": "Complète un **raid niveau 5**.",
        "progress_key": "raid_max_completed", "threshold": 5,
        "xp": 3_000_000, "gold": 800_000,
    },
    {
        "id": "s27", "name": "Maître de l'Arène", "emoji": "🏆",
        "desc": "Remporte **50 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 50,
        "xp": 1_000_000, "gold": 250_000,
    },
    {
        "id": "s28", "name": "Raid Légendaire", "emoji": "🌟",
        "desc": "Complète un **raid niveau 7**.",
        "progress_key": "raid_max_completed", "threshold": 7,
        "xp": 6_000_000, "gold": 1_500_000,
    },
    {
        "id": "s29", "name": "Maître de tous les Métiers", "emoji": "🎓",
        "desc": "Atteins le **niveau 100** dans les **3 métiers**.",
        "progress_key": "all_prof_100", "threshold": 100,
        "xp": 5_000_000, "gold": 1_000_000,
    },
    {
        "id": "s30", "name": "Légende du Raid", "emoji": "👑",
        "desc": "Complète un **raid niveau 10**.",
        "progress_key": "raid_max_completed", "threshold": 10,
        "xp": 15_000_000, "gold": 5_000_000,
    },
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_progress_value(quest: dict, player: dict, prof: dict, stats: dict) -> int:
    """Retourne la valeur actuelle de progression pour une quête."""
    key = quest["progress_key"]
    if key == "zone":
        return player.get("zone", 1)
    if key == "level":
        return player.get("level", 1)
    if key == "pvp_wins":
        return player.get("pvp_wins", 0)
    if key == "pvp_fights":
        return player.get("pvp_wins", 0) + player.get("pvp_losses", 0)
    if key == "has_harvest":
        return 1 if (prof and prof.get("harvest_type")) else 0
    if key == "has_craft":
        return 1 if (prof and prof.get("craft_type")) else 0
    if key == "has_conception":
        return 1 if (prof and prof.get("conception_type")) else 0
    if key == "harvest_level":
        return prof.get("harvest_level", 0) if prof else 0
    if key == "craft_level":
        return prof.get("craft_level", 0) if prof else 0
    if key == "conception_level":
        return prof.get("conception_level", 0) if prof else 0
    if key == "all_prof_100":
        if not prof:
            return 0
        return min(prof.get("harvest_level", 0), prof.get("craft_level", 0), prof.get("conception_level", 0))
    if key == "market_total":
        return stats.get("market_sells", 0) + stats.get("market_buys", 0)
    # Colonnes directes dans player_quest_stats
    return stats.get(key, 0)


def get_active_quest(quest_list: list[dict], claimed_ids: set[str]) -> dict | None:
    """Retourne la première quête non encore réclamée dans la chaîne."""
    for q in quest_list:
        if q["id"] not in claimed_ids:
            return q
    return None  # Toutes les quêtes sont complétées


def progress_bar(current: int, target: int, length: int = 12) -> str:
    """Barre de progression ASCII."""
    ratio = min(current / target, 1.0) if target > 0 else 1.0
    filled = int(ratio * length)
    bar = "█" * filled + "░" * (length - filled)
    pct = int(ratio * 100)
    return f"`{bar}` {pct}%"
