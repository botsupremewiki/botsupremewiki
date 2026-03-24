"""
Constantes, dataclasses et formules de stats du RPG.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field

# ─── Rôles Discord ─────────────────────────────────────────────────────────
ROLE_PREMIUM    = 1463369524769460314
ROLE_RPG        = 1474444276136939663

# ─── Canaux Hub ────────────────────────────────────────────────────────────
HUB_CHANNELS = {
    "bienvenue":    1480619312715792535,
    "classe":       1465541336361996504,
    "profil":       1464542599867269252,
    "metiers":      1479293726667964517,
    "banque":       1479297760833437808,
    "monde":        1465432915612799109,
    "donjons":      1468959474151587871,
    "raids":        1479297621007798283,
    "world_boss":   1465433246727799038,
    "hotel_ventes": 1479297549977256057,
    "echanges":     1479297820706996254,
    "titres":       1465433147167477871,
    "pvp":          1480734240625918144,
    "classement":   1468963280218362019,
    "admin":        1476717910365044807,
    "quetes":       1481409415046365245,
}

# ─── Raretés ───────────────────────────────────────────────────────────────
RARITIES = [
    "commun", "peu commun", "rare", "épique",
    "légendaire", "mythique", "artefact", "divin",
    "transcendant", "prismatique"
]

RARITY_COLORS = {
    "commun":       0x9E9E9E,
    "peu commun":   0x4CAF50,
    "rare":         0x2196F3,
    "épique":       0x9C27B0,
    "légendaire":   0xFF9800,
    "mythique":     0xF44336,
    "artefact":     0xFF5722,
    "divin":        0xFFEB3B,
    "transcendant": 0x00BCD4,
    "prismatique":  0xE91E63,
}

RARITY_EMOJI = {
    "commun":       "⬜",
    "peu commun":   "🟩",
    "rare":         "🟦",
    "épique":       "🟪",
    "légendaire":   "🟧",
    "mythique":     "🟥",
    "artefact":     "🔶",
    "divin":        "🟡",
    "transcendant": "🩵",
    "prismatique":  "🌈",
}

RARITY_MULT = {
    "commun":       1.0,
    "peu commun":   1.2,
    "rare":         1.4,
    "épique":       1.6,
    "légendaire":   1.8,
    "mythique":     2.0,
    "artefact":     2.2,
    "divin":        2.4,
    "transcendant": 2.6,
    "prismatique":  3.0,
}

# Poids pour le craft (plus le niveau de métier est élevé, plus les raretés hautes sont accessibles)
RARITY_CRAFT_WEIGHTS = [
    [40, 30, 15, 8, 4, 2, 0.6, 0.3, 0.08, 0.02],   # level 1-10
    [25, 30, 20, 12, 7, 3, 1.5, 0.8, 0.25, 0.15],  # level 11-30
    [10, 20, 25, 20, 12, 7, 3.0, 1.8, 0.8, 0.4],   # level 31-60
    [5,  10, 20, 25, 20, 10, 5.0, 3.0, 1.5, 0.5],  # level 61-100
]

def get_craft_rarity_weights(level: int) -> list[float]:
    if level <= 10:
        return RARITY_CRAFT_WEIGHTS[0]
    elif level <= 30:
        return RARITY_CRAFT_WEIGHTS[1]
    elif level <= 60:
        return RARITY_CRAFT_WEIGHTS[2]
    else:
        return RARITY_CRAFT_WEIGHTS[3]

def roll_craft_rarity(level: int) -> str:
    weights = get_craft_rarity_weights(level)
    return random.choices(RARITIES, weights=weights, k=1)[0]

# ─── Slots d'équipement ────────────────────────────────────────────────────
SLOTS = ["casque", "plastron", "pantalon", "chaussures", "arme", "amulette", "anneau"]
SLOT_EMOJI = {
    "casque":      "⛑️",
    "plastron":    "🦺",
    "pantalon":    "👖",
    "chaussures":  "👟",
    "arme":        "⚔️",
    "amulette":    "📿",
    "anneau":      "💍",
}

# ─── Stats par slot, par classe ────────────────────────────────────────────
# Formule : stat = (item_level × growth + const) × source_mult × rarity_mult × enh_mult
# Chaque slot qui possède une stat reçoit une part ÉGALE : share = 1 / nb_slots_ayant_cette_stat.
# Résultat : si hp vient de 3 slots, chaque slot donne exactement stat_classe/3.
# Max mult = 1.8 × 3.0 × 2.0 = 10.8 → 7 items max = ×10.8 stats de classe.

# Stats de chaque slot armure (identique pour toutes les classes)
_ARMOR_SLOT_STATS: dict[str, list[str]] = {
    "casque":     ["hp", "p_def", "m_def"],
    "plastron":   ["hp", "p_def", "m_def"],
    "pantalon":   ["hp", "p_def", "m_def", "speed"],
    "chaussures": ["speed", "p_def", "m_def"],
}

# Stats de chaque slot offensif par classe
_OFFENSE_SLOT_STATS: dict[str, dict[str, list[str]]] = {
    "Guerrier": {
        "arme":     ["p_atk", "p_pen", "crit_chance", "crit_damage"],
        "amulette": ["p_atk"],
        "anneau":   ["p_atk", "p_pen"],
    },
    "Assassin": {
        "arme":     ["p_atk", "p_pen", "speed", "crit_chance", "crit_damage"],
        "amulette": ["speed", "crit_chance", "crit_damage"],
        "anneau":   ["p_atk", "p_pen", "crit_chance", "crit_damage"],
    },
    "Mage": {
        "arme":     ["m_atk", "m_pen", "crit_chance", "crit_damage"],
        "amulette": ["m_atk", "m_pen", "hp"],
        "anneau":   ["m_atk", "m_pen"],
    },
    "Tireur": {
        "arme":     ["p_atk", "p_pen", "crit_chance", "crit_damage"],
        "amulette": ["speed", "crit_chance", "crit_damage"],
        "anneau":   ["p_atk", "p_pen", "crit_chance", "crit_damage"],
    },
    "Support": {
        "arme":     ["p_atk", "m_atk", "p_pen", "m_pen"],
        "amulette": ["m_atk", "m_pen", "speed"],
        "anneau":   ["p_atk", "p_pen", "speed"],
    },
    "Vampire": {
        "arme":     ["p_atk", "p_pen", "crit_chance", "crit_damage"],
        "amulette": ["p_atk", "hp"],
        "anneau":   ["p_atk", "p_pen", "hp"],
    },
    "Gardien du Temps": {
        "arme":     ["p_atk", "m_atk", "p_pen", "m_pen"],
        "amulette": ["m_atk", "m_pen", "crit_chance", "crit_damage"],
        "anneau":   ["p_atk", "p_pen", "crit_chance", "crit_damage"],
    },
    "Ombre Venin": {
        "arme":     ["p_atk", "m_atk", "p_pen", "speed", "crit_chance"],
        "amulette": ["m_atk", "m_pen", "speed", "crit_chance"],
        "anneau":   ["p_atk", "p_pen", "crit_damage"],
    },
    "Pyromancien": {
        "arme":     ["m_atk", "m_pen", "crit_chance", "crit_damage"],
        "amulette": ["m_atk", "m_pen"],
        "anneau":   ["m_atk", "m_pen"],
    },
    "Paladin": {
        "arme":     ["p_atk", "p_pen", "crit_chance", "crit_damage"],
        "amulette": ["p_atk", "hp"],
        "anneau":   ["p_atk", "hp"],
    },
}


def _compute_class_slot_focus() -> dict:
    """Génère CLASS_SLOT_STAT_FOCUS : {classe → {slot → {stat → (growth, const)}}}
    Chaque stat est divisée équitablement entre tous les slots qui la possèdent :
    share = 1/n → chaque slot donne stat_classe/n à item_level=L."""
    result: dict = {}
    for class_name, base in BASE_STATS.items():
        # Construire la liste complète slot→stats pour cette classe
        slot_stats: dict[str, list[str]] = {}
        for slot, stats in _ARMOR_SLOT_STATS.items():
            slot_stats[slot] = list(stats)
        for slot, stats in _OFFENSE_SLOT_STATS.get(class_name, {}).items():
            slot_stats[slot] = list(stats)

        # Compter combien de slots ont chaque stat
        stat_count: dict[str, int] = {}
        for stats in slot_stats.values():
            for stat in stats:
                stat_count[stat] = stat_count.get(stat, 0) + 1

        # Calculer (growth, const) avec share = 1/n pour chaque slot×stat
        class_growth = LEVEL_GROWTH.get(class_name, {})
        result[class_name] = {}
        for slot, stats in slot_stats.items():
            result[class_name][slot] = {}
            for stat in stats:
                share = 1.0 / stat_count[stat]
                g = class_growth.get(stat, 0) * share
                c = (base.get(stat, 0) - class_growth.get(stat, 0)) * share
                result[class_name][slot][stat] = (round(g, 5), round(c, 3))
    return result


# ─── Classes ───────────────────────────────────────────────────────────────
CLASS_EMOJI = {
    "Guerrier":           "⚔️",
    "Assassin":           "🗡️",
    "Mage":               "🔮",
    "Tireur":             "🏹",
    "Support":            "🛡️",
    "Vampire":            "🧛",
    "Gardien du Temps":   "⏳",
    "Ombre Venin":        "☠️",
    "Pyromancien":        "🔥",
    "Paladin":            "✝️",
}

CLASSES_STANDARD = ["Guerrier", "Assassin", "Mage", "Tireur", "Support"]
CLASSES_PREMIUM  = ["Vampire", "Gardien du Temps", "Ombre Venin", "Pyromancien", "Paladin"]
ALL_CLASSES      = CLASSES_STANDARD + CLASSES_PREMIUM

CLASS_DESCRIPTION = {
    "Guerrier": (
        "Combattant brutal qui puise sa force dans sa souffrance.\n"
        "**Passif** : +0.5% de dégâts par % de HP manquants (max +50%).\n"
        "**Ressource** : 🔴 Rage (max 100, +10/tour, +5 par coup reçu)."
    ),
    "Assassin": (
        "Ombre rapide frappant avec une précision mortelle.\n"
        "**Passif** : 20% de chance d'esquiver une attaque ennemie.\n"
        "**Ressource** : 🟡 Combo (max 5, +1/tour)."
    ),
    "Mage": (
        "Maître de l'arcane dont la puissance croît avec sa vitalité.\n"
        "**Passif** : +0.5% de dégâts magiques par % de HP actuels (max +50%).\n"
        "**Ressource** : 🔵 Mana (max 100, +15/tour)."
    ),
    "Tireur": (
        "Archer agile capable de déchaîner une pluie de projectiles mortels.\n"
        "**Passif** : 25% de chance de doubler ses dégâts.\n"
        "**Ressource** : 🟡 Combo (max 5, +1/tour)."
    ),
    "Support": (
        "Protecteur polyvalent qui frappe et résiste à tout.\n"
        "**Passif** : 30% de chance de générer un bouclier (8% des HP max).\n"
        "**Ressource** : 🔵 Mana (max 100, +12/tour)."
    ),
    "Vampire": (
        "*(Premium)* Prédateur nocturne se nourrissant du sang ennemi.\n"
        "**Passif** : 25% de chance de vol de vie (30% des dégâts infligés).\n"
        "**Ressource** : 🔴 Rage (max 100, +10/tour, +5 par coup reçu)."
    ),
    "Gardien du Temps": (
        "*(Premium)* Manipulateur du destin qui distord le temps et l'espace.\n"
        "**Passif** : 35% de chance de réduire une stat ennemie aléatoire de 8% (max -50%).\n"
        "**Ressource** : 🟡 Combo (max 5, +1/tour)."
    ),
    "Ombre Venin": (
        "*(Premium)* Assassin venimeux dont le poison dévore ses proies de l'intérieur.\n"
        "**Passif** : 30% de chance d'appliquer du poison (3% HP max/tour).\n"
        "**Ressource** : 🔵 Mana (max 100, +12/tour)."
    ),
    "Pyromancien": (
        "*(Premium)* Sorcier des flammes dont la brûlure s'accumule inexorablement.\n"
        "**Passif** : 35% de chance d'appliquer 1 stack de brûlure (15% ATK Mag/stack).\n"
        "**Ressource** : 🔵 Mana (max 100, +15/tour)."
    ),
    "Paladin": (
        "*(Premium)* Chevalier sacré dont la résistance se renforce au fil du combat.\n"
        "**Passif** : 35% de chance d'augmenter une stat aléatoire de 5% (permanent ce combat).\n"
        "**Ressource** : 🔴 Rage (max 100, +10/tour, +5 par coup reçu)."
    ),
}

# Stats de base niveau 1 prestige 0
# Off-type stats = 0 pour les classes pures (ex: p_atk=0 pour Mage)
BASE_STATS: dict[str, dict] = {
    # Contraintes : hp ≥ 10× max(p_atk, m_atk) | pen ≤ 20% de l'attaque
    "Guerrier":         {"hp": 600,  "p_atk": 60,  "m_atk": 0,   "p_pen": 8,  "m_pen": 0,  "p_def": 28, "m_def": 6,  "speed": 80,  "crit_chance": 5.0,  "crit_damage": 150.0},
    "Assassin":         {"hp": 500,  "p_atk": 50,  "m_atk": 0,   "p_pen": 10, "m_pen": 0,  "p_def": 4,  "m_def": 3,  "speed": 160, "crit_chance": 20.0, "crit_damage": 175.0},
    "Mage":             {"hp": 400,  "p_atk": 0,   "m_atk": 40,  "p_pen": 0,  "m_pen": 8,  "p_def": 3,  "m_def": 10, "speed": 90,  "crit_chance": 12.0, "crit_damage": 175.0},
    "Tireur":           {"hp": 440,  "p_atk": 44,  "m_atk": 0,   "p_pen": 8,  "m_pen": 0,  "p_def": 4,  "m_def": 4,  "speed": 130, "crit_chance": 18.0, "crit_damage": 175.0},
    "Support":          {"hp": 600,  "p_atk": 34,  "m_atk": 34,  "p_pen": 6,  "m_pen": 6,  "p_def": 25, "m_def": 25, "speed": 55,  "crit_chance": 5.0,  "crit_damage": 140.0},
    "Vampire":          {"hp": 450,  "p_atk": 45,  "m_atk": 0,   "p_pen": 9,  "m_pen": 0,  "p_def": 12, "m_def": 7,  "speed": 90,  "crit_chance": 15.0, "crit_damage": 175.0},
    "Gardien du Temps": {"hp": 400,  "p_atk": 22,  "m_atk": 22,  "p_pen": 4,  "m_pen": 4,  "p_def": 15, "m_def": 15, "speed": 85,  "crit_chance": 8.0,  "crit_damage": 155.0},
    "Ombre Venin":      {"hp": 300,  "p_atk": 30,  "m_atk": 12,  "p_pen": 6,  "m_pen": 2,  "p_def": 5,  "m_def": 5,  "speed": 115, "crit_chance": 16.0, "crit_damage": 170.0},
    "Pyromancien":      {"hp": 400,  "p_atk": 0,   "m_atk": 40,  "p_pen": 0,  "m_pen": 8,  "p_def": 2,  "m_def": 10, "speed": 85,  "crit_chance": 12.0, "crit_damage": 175.0},
    "Paladin":          {"hp": 560,  "p_atk": 30,  "m_atk": 0,   "p_pen": 6,  "m_pen": 0,  "p_def": 35, "m_def": 22, "speed": 55,  "crit_chance": 5.0,  "crit_damage": 150.0},
}

# Croissance par niveau — dict par classe (valeurs 0 pour stats hors-type)
# Contraintes maintenues à tous les niveaux : hp ≥ 10× max(p_atk, m_atk) | pen = 20% atk
# Cibles niveau 1000 sans équipement :
# Guerrier  28k HP, 2800 pAtk, 560 pPen, 1500 pDef, 275 spd  (ratio 10x hp/atk)
# Assassin  25k HP, 2500 pAtk, 500 pPen, 500 spd, 30% cc     (ratio 10x — DPS via vitesse+crit)
# Mage      20k HP, 2000 mAtk, 400 mPen, 350 spd, 28% cc     (ratio 10x — DPS via crit+pen)
# Tireur    22k HP, 2200 pAtk, 440 pPen, 400 spd, 32% cc     (ratio 10x — DPS via crit+cadence)
# Support   34k HP, 1700 pAtk=mAtk, 1380 pDef=mDef, 250 spd  (ratio 20x — tank/soutien)
# Vampire   24k HP, 2400 pAtk, 480 pPen, 350 spd, 22% cc     (ratio 10x — sustain DPS)
# Gardien   22k HP, 1100 p+mAtk, 220 p+mPen, 330 spd         (ratio 20x — hybride tank)
# Ombre V.  20k HP, 2000 pAtk / 800 mAtk, 415 spd, 24% cc    (ratio 10x — hybride phys+venin)
# Pyro      20k HP, 2000 mAtk, 400 mPen, 330 spd, 25% cc     (ratio 10x — burst mag)
# Paladin   33k HP, 1650 pAtk, 330 pPen, 1900 pDef, 250 spd  (ratio 20x — tank défensif)
LEVEL_GROWTH: dict[str, dict] = {
    "Guerrier": {
        "hp": 27.46, "p_atk": 2.743, "m_atk": 0.0,   "p_pen": 0.552, "m_pen": 0.0,
        "p_def": 1.473, "m_def": 0.294, "speed": 0.195, "crit_chance": 0.007, "crit_damage": 0.025,
    },
    "Assassin": {
        "hp": 24.52, "p_atk": 2.452, "m_atk": 0.0,   "p_pen": 0.490, "m_pen": 0.0,
        "p_def": 0.256, "m_def": 0.197, "speed": 0.340, "crit_chance": 0.010, "crit_damage": 0.045,
    },
    "Mage": {
        "hp": 19.62, "p_atk": 0.0,   "m_atk": 1.962, "p_pen": 0.0,   "m_pen": 0.392,
        "p_def": 0.127, "m_def": 0.521, "speed": 0.260, "crit_chance": 0.016, "crit_damage": 0.035,
    },
    "Tireur": {
        "hp": 21.58, "p_atk": 2.158, "m_atk": 0.0,   "p_pen": 0.432, "m_pen": 0.0,
        "p_def": 0.161, "m_def": 0.161, "speed": 0.270, "crit_chance": 0.014, "crit_damage": 0.035,
    },
    "Support": {
        "hp": 33.43, "p_atk": 1.668, "m_atk": 1.668, "p_pen": 0.334, "m_pen": 0.334,
        "p_def": 1.356, "m_def": 1.356, "speed": 0.195, "crit_chance": 0.003, "crit_damage": 0.025,
    },
    "Vampire": {
        "hp": 23.57, "p_atk": 2.357, "m_atk": 0.0,   "p_pen": 0.471, "m_pen": 0.0,
        "p_def": 0.629, "m_def": 0.393, "speed": 0.260, "crit_chance": 0.007, "crit_damage": 0.025,
    },
    "Gardien du Temps": {
        "hp": 21.62, "p_atk": 1.079, "m_atk": 1.079, "p_pen": 0.216, "m_pen": 0.216,
        "p_def": 0.866, "m_def": 0.866, "speed": 0.245, "crit_chance": 0.010, "crit_damage": 0.030,
    },
    "Ombre Venin": {
        "hp": 19.72, "p_atk": 1.972, "m_atk": 0.789, "p_pen": 0.394, "m_pen": 0.158,
        "p_def": 0.255, "m_def": 0.255, "speed": 0.300, "crit_chance": 0.008, "crit_damage": 0.030,
    },
    "Pyromancien": {
        "hp": 19.62, "p_atk": 0.0,   "m_atk": 1.962, "p_pen": 0.0,   "m_pen": 0.392,
        "p_def": 0.098, "m_def": 0.420, "speed": 0.245, "crit_chance": 0.013, "crit_damage": 0.040,
    },
    "Paladin": {
        "hp": 32.47, "p_atk": 1.621, "m_atk": 0.0,   "p_pen": 0.324, "m_pen": 0.0,
        "p_def": 1.867, "m_def": 1.179, "speed": 0.195, "crit_chance": 0.003, "crit_damage": 0.005,
    },
}

# Computed after BASE_STATS and LEVEL_GROWTH are both defined
CLASS_SLOT_STAT_FOCUS: dict = _compute_class_slot_focus()

MAX_LEVEL    = 1000
MAX_ENERGY   = 2000
PASSIVE_REGEN_HP_PCT    = 3   # % des HP max récupérés toutes les 10 minutes
PASSIVE_REGEN_ENERGY    = 3   # énergie récupérée toutes les 10 minutes
PASSIVE_REGEN_INTERVAL  = 600 # secondes

# Coût en énergie par type de combat
ENERGY_COST = {
    "ennemi":           1,
    "boss_classique":   2,
    "boss_runique":     3,
    "boss_emblematique":5,
    "boss_antique":     10,
    "donjon_classique": 3,
    "donjon_elite":     5,
    "donjon_abyssal":   10,
    "raid":             100,
    "world_boss":       100,
    "pvp":              5,
}

# ─── Formules de stats ─────────────────────────────────────────────────────

def compute_class_stats(class_name: str, level: int, prestige_level: int) -> dict:
    """Calcule les stats de classe pour un niveau et prestige donné."""
    if class_name not in BASE_STATS:
        return {}
    base = dict(BASE_STATS[class_name])
    prestige_bonus = 1 + (prestige_level * 0.001)  # +0.1% par niveau de prestige
    class_growth = LEVEL_GROWTH.get(class_name, {})
    for stat, growth in class_growth.items():
        base[stat] = base.get(stat, 0) + growth * (level - 1)
        base[stat] = base[stat] * prestige_bonus
    # Arrondir
    for stat in base:
        if stat in ("crit_chance", "crit_damage"):
            base[stat] = round(base[stat], 2)
        else:
            base[stat] = int(base[stat])
    return base


def compute_equipment_stats(equipment_list: list[dict]) -> dict:
    """Additionne les stats de tous les équipements équipés."""
    total = {s: 0 for s in ["hp", "p_atk", "m_atk", "p_pen", "m_pen", "p_def", "m_def", "speed", "crit_chance", "crit_damage"]}
    from bot.cogs.rpg.items import get_equipment_stats
    for eq in equipment_list:
        if eq.get("slot_equipped"):
            stats = get_equipment_stats(
                eq["item_id"],
                eq.get("rarity", "commun"),
                eq.get("enhancement", 0),
                eq.get("level", 1),       # niveau de l'item instance
            )
            for k, v in stats.items():
                total[k] = total.get(k, 0) + v
    return total


def compute_total_stats(class_name: str, level: int, prestige_level: int,
                         equipment_list: list[dict], bonus_stats: dict = None) -> dict:
    """Calcule les stats totales combinant classe + équipements + bonus."""
    class_stats = compute_class_stats(class_name, level, prestige_level)
    eq_stats = compute_equipment_stats(equipment_list)
    total = {}
    all_keys = set(class_stats) | set(eq_stats)
    for k in all_keys:
        total[k] = class_stats.get(k, 0) + eq_stats.get(k, 0)
    if bonus_stats:
        for k, v in bonus_stats.items():
            total[k] = total.get(k, 0) + v
    # Planchers
    total["crit_chance"] = max(total.get("crit_chance", 0), 0)  # pas de plafond, utilisé pour le crit_damage
    total["crit_damage"] = max(total.get("crit_damage", 150), 150)
    total["speed"]       = max(total.get("speed", 1), 1)
    return total


def compute_max_hp(stats: dict) -> int:
    return max(1, int(stats.get("hp", 1)))


def xp_for_level(level: int) -> int:
    """XP nécessaire pour passer du niveau `level` au suivant."""
    return 1000 * level


def level_up(level: int, xp: int) -> tuple[int, int]:
    """Retourne (nouveau niveau, xp restant) après application des gains."""
    while level < MAX_LEVEL:
        needed = xp_for_level(level)
        if xp >= needed:
            xp -= needed
            level += 1
        else:
            break
    return level, xp


# ─── Récompenses de combat ─────────────────────────────────────────────────

_BOSS_XP_MULT = {
    "monster":           1,
    "boss_classique":    3,
    "boss_emblematique": 10,
    "boss_antique":      30,
}

_BOSS_GOLD_MULT = {
    "monster":           1,
    "boss_classique":    3,
    "boss_emblematique": 10,
    "boss_antique":      30,
}


def combat_xp_reward(zone: int, boss_type: str = "monster") -> int:
    """XP gagné après un combat (linéaire). boss_type : monster/boss_classique/boss_emblematique/boss_antique"""
    mult = _BOSS_XP_MULT.get(boss_type, 1)
    return max(1, zone * mult)


def combat_gold_reward(zone: int, boss_type: str = "monster") -> int:
    """Gold gagné après un combat (linéaire). boss_type : monster/boss_classique/boss_emblematique/boss_antique"""
    mult = _BOSS_GOLD_MULT.get(boss_type, 1)
    return max(1, (zone // 5) * mult)


# ─── Récompense quotidienne ────────────────────────────────────────────────

def daily_reward(streak: int, level: int = 1) -> dict:
    """Retourne les récompenses du jour selon la streak et le niveau."""
    mult = 1 + min(streak - 1, 29) * 0.1  # +10% par jour, plafonné jour 30
    item_count = 1 + streak // 7           # +1 item tous les 7 jours de streak
    return {
        "gold":       int(max(500, level * 80) * mult),
        "xp":         int(max(300, level * 30) * mult),
        "item_count": item_count,
    }


# ─── Panoplies ─────────────────────────────────────────────────────────────
# 6 panoplies par classe × 10 classes = 60 panoplies
# Chaque source correspond à un mode de jeu avec une puissance croissante.
# Les stats des bonus de set sont des valeurs BASE (rareté commun, source monde).
# Bonus réels = base × SOURCE_POWER_MULT[source] × RARITY_MULT[rareté_min_équipée]

SOURCE_POWER_MULT: dict[str, float] = {
    "monde":            1.0,
    "donjon_classique": 1.2,
    "craft":            1.5,   # valeur médiane — remplacée dynamiquement au craft (roll_craft_source_mult)
    "donjon_elite":     1.4,
    "donjon_abyssal":   1.6,
    "raid":             1.8,
}


def roll_craft_source_mult(craft_level: int) -> float:
    """
    Tire un source_mult aléatoire pour un item crafté selon le niveau de métier (1-100).

    Level 1  : tirage entre ×1.0 et ×1.4
    Level 100 : tirage entre ×1.4 et ×2.0
    Progression linéaire des deux bornes entre level 1 et 100.
    """
    t = (min(max(craft_level, 1), 100) - 1) / 99  # 0.0 → 1.0
    min_mult = 1.0 + t * 0.4   # 1.0 → 1.4
    max_mult = 1.4 + t * 0.6   # 1.4 → 2.0
    return round(random.uniform(min_mult, max_mult), 2)


# Préfixes de slot uniques par classe — aucun préfixe n'est partagé entre classes.
# Nom de l'item = SLOT_PREFIX_BY_CLASS[classe][slot] + " " + set_data["theme"]
SLOT_PREFIX_BY_CLASS: dict[str, dict[str, str]] = {
    "Guerrier":         {"casque": "Heaume",    "plastron": "Cuirasse",   "pantalon": "Braies",      "chaussures": "Sollerets",  "arme": "Épée",     "amulette": "Médaillon",  "anneau": "Chevalière"},
    "Assassin":         {"casque": "Capuche",   "plastron": "Mantelet",   "pantalon": "Grègues",     "chaussures": "Chaussons",  "arme": "Dague",    "amulette": "Pendentif",  "anneau": "Signet"},
    "Mage":             {"casque": "Chapeau",   "plastron": "Robe",       "pantalon": "Jupe",        "chaussures": "Sandales",   "arme": "Bâton",    "amulette": "Talisman",   "anneau": "Bague"},
    "Tireur":           {"casque": "Cagoule",   "plastron": "Veste",      "pantalon": "Jambières",   "chaussures": "Bottes",     "arme": "Arc",      "amulette": "Collier",    "anneau": "Jonc"},
    "Support":          {"casque": "Bassinet",  "plastron": "Brigandine", "pantalon": "Cuissardes",  "chaussures": "Grèves",     "arme": "Bouclier", "amulette": "Amulette",   "anneau": "Sceau"},
    "Vampire":          {"casque": "Masque",    "plastron": "Cape",       "pantalon": "Collant",     "chaussures": "Bottines",   "arme": "Crocs",    "amulette": "Breloque",   "anneau": "Cachet"},
    "Gardien du Temps": {"casque": "Couronne",  "plastron": "Manteau",    "pantalon": "Bas",         "chaussures": "Escarpes",   "arme": "Sablier",  "amulette": "Relique",    "anneau": "Alliance"},
    "Ombre Venin":      {"casque": "Voile",     "plastron": "Suaire",     "pantalon": "Guêtres",     "chaussures": "Mocassins",  "arme": "Aiguille", "amulette": "Fiole",      "anneau": "Annelet"},
    "Pyromancien":      {"casque": "Coiffe",    "plastron": "Tunique",    "pantalon": "Pantalon",    "chaussures": "Sabots",     "arme": "Torche",   "amulette": "Phylactère", "anneau": "Gemme"},
    "Paladin":          {"casque": "Armet",     "plastron": "Haubert",    "pantalon": "Tassettes",   "chaussures": "Éperons",    "arme": "Marteau",  "amulette": "Croix",      "anneau": "Insigne"},
}

# Structure : set_key → données de la panoplie
#   class   : classe concernée
#   source  : mode de jeu (monde / donjon_classique / craft / donjon_elite / donjon_abyssal / raid)
#   theme   : suffixe des noms d'items  →  "{prefix} {theme}"  ex. "Capuche de la Nuit"
#   name    : nom d'affichage de la panoplie
#   2pcs / 4pcs : bonus stats (valeurs BASE, multipliées à l'affichage)
#   7pcs    : bonus passif (texte fixe)
SET_BONUSES: dict[str, dict] = {

    # ═══════════════════════════════════════════════════════ GUERRIER ══
    # Builds : Équilibré | Tank Pur | Counter | Berserker | Brise-Armure | Colosse
    "guerrier_monde": {
        "class": "Guerrier", "source": "monde", "theme": "de Fer", "name": "Acier de Fer",
        "2pcs": {"hp": 30, "p_def": 14},
        "3pcs": {"passive": "Régénère 2% de tes HP max à la fin de chaque tour."},
        "4pcs": {"p_atk": 12, "p_pen": 4},
        "5pcs": {"hp": 22, "p_atk": 8},
        "6pcs": {"passive": "Réduit les dégâts reçus de 4% si HP > 50%."},
        "7pcs": {"passive": "Chaque ennemi vaincu régénère 8% de tes HP max. +5% dégâts physiques."},
    },
    "guerrier_donjon_classique": {
        "class": "Guerrier", "source": "donjon_classique", "theme": "du Rempart", "name": "Rempart de Fer",
        "2pcs": {"hp": 65, "p_def": 30},
        "3pcs": {"passive": "Réduit les dégâts reçus de 5%."},
        "4pcs": {"m_def": 22, "p_def": 12},
        "5pcs": {"hp": 50, "m_def": 16},
        "6pcs": {"passive": "Réduction dégâts reçus portée à 10% total."},
        "7pcs": {"passive": "Immunisé aux réductions de stats ennemies. Chaque attaque reçue régénère 2% HP max."},
    },
    "guerrier_craft": {
        "class": "Guerrier", "source": "craft", "theme": "Forgé", "name": "Métal Forgé",
        "2pcs": {"hp": 42, "p_def": 18},
        "3pcs": {"passive": "Chaque attaque physique reçue augmente tes dégâts de 2% (max +20%)."},
        "4pcs": {"p_atk": 22, "p_pen": 9},
        "5pcs": {"hp": 30, "p_pen": 8},
        "6pcs": {"passive": "Contre-attaque possible à chaque tour : 12% de chance de riposter."},
        "7pcs": {"passive": "Contre-attaque : après avoir reçu un coup, 25% de chance de riposter avec 60% de ton ATK Physique."},
    },
    "guerrier_donjon_elite": {
        "class": "Guerrier", "source": "donjon_elite", "theme": "du Titan", "name": "Titan Écarlate",
        "2pcs": {"p_atk": 30, "speed": 10},
        "3pcs": {"passive": "Si HP < 50% : tes dégâts physiques sont augmentés de 12%."},
        "4pcs": {"p_pen": 12, "crit_chance": 2},
        "5pcs": {"p_atk": 22, "crit_damage": 6},
        "6pcs": {"passive": "Chaque coup reçu quand HP < 50% génère +3% bonus dégâts permanents (max +30%)."},
        "7pcs": {"passive": "+2% dégâts physiques par 5% HP manquants. Dégâts critiques +30% quand HP < 30%."},
    },
    "guerrier_donjon_abyssal": {
        "class": "Guerrier", "source": "donjon_abyssal", "theme": "de l'Abîme", "name": "Seigneur de l'Abîme",
        "2pcs": {"p_atk": 42, "p_pen": 15},
        "3pcs": {"passive": "Ignore 10% de la DEF Physique ennemie."},
        "4pcs": {"crit_chance": 3, "crit_damage": 12},
        "5pcs": {"hp": 72, "p_def": 20},
        "6pcs": {"passive": "Les critiques appliquent une réduction DEF Physique de 8% pour 2 tours."},
        "7pcs": {"passive": "Ignore 25% DEF Physique ennemie. Chaque critique régénère 4% HP max."},
    },
    "guerrier_raid": {
        "class": "Guerrier", "source": "raid", "theme": "de Guerre", "name": "Colosse de Guerre",
        "2pcs": {"hp": 100, "p_def": 38, "p_atk": 28},
        "3pcs": {"passive": "+10% dégâts physiques et +5% réduction dégâts reçus."},
        "4pcs": {"p_pen": 18, "crit_chance": 2, "crit_damage": 8},
        "5pcs": {"p_atk": 22, "crit_damage": 12},
        "6pcs": {"passive": "Chaque critique réduit la DEF Physique ennemie de 10% (cumulable jusqu'à -30%)."},
        "7pcs": {"passive": "Immunité aux effets de stun. +20% dégâts quand HP < 30%. Régénère 5% HP max/tour."},
    },

    # ══════════════════════════════════════════════════════ ASSASSIN ══
    # Builds : Infiltrateur | Crit Pur | Esquiveur | Fantôme | Saigneur | Exécuteur
    "assassin_monde": {
        "class": "Assassin", "source": "monde", "theme": "des Ombres", "name": "Ombre Légère",
        "2pcs": {"speed": 10, "p_atk": 14},
        "3pcs": {"passive": "Le premier coup de chaque combat est toujours un critique."},
        "4pcs": {"p_pen": 6, "crit_chance": 1},
        "5pcs": {"speed": 8, "crit_damage": 8},
        "6pcs": {"passive": "Les 2 premiers coups de chaque combat sont des critiques garantis."},
        "7pcs": {"passive": "Le premier coup inflige +25% dégâts. Si l'ennemi est à plein HP, +50% à la place."},
    },
    "assassin_donjon_classique": {
        "class": "Assassin", "source": "donjon_classique", "theme": "du Crépuscule", "name": "Lame du Crépuscule",
        "2pcs": {"crit_chance": 4, "crit_damage": 12},
        "3pcs": {"passive": "Chaque critique consécutif augmente ton crit_damage de 5% (max +25%)."},
        "4pcs": {"p_atk": 16, "p_pen": 6},
        "5pcs": {"crit_chance": 2, "p_atk": 12},
        "6pcs": {"passive": "Chaque critique réduit la DEF Physique ennemie de 4% (max -20%)."},
        "7pcs": {"passive": "Après 3 critiques consécutifs, ta prochaine attaque ignore toute la DEF Physique ennemie."},
    },
    "assassin_craft": {
        "class": "Assassin", "source": "craft", "theme": "Trempé", "name": "Acier Trempé",
        "2pcs": {"speed": 14, "p_atk": 14},
        "3pcs": {"passive": "Chaque esquive réussie augmente tes dégâts de 6% pour 2 tours (max +30%)."},
        "4pcs": {"crit_chance": 2, "p_pen": 8},
        "5pcs": {"speed": 10, "crit_chance": 2},
        "6pcs": {"passive": "Chaque esquive ajoute +8% dégâts permanents jusqu'à la fin du combat."},
        "7pcs": {"passive": "Après une esquive, +15% de chance d'esquiver le prochain coup. Dégâts +40% si esquive active."},
    },
    "assassin_donjon_elite": {
        "class": "Assassin", "source": "donjon_elite", "theme": "du Fantôme", "name": "Fantôme Acéré",
        "2pcs": {"speed": 18, "p_atk": 20},
        "3pcs": {"passive": "+8% de chance d'esquive supplémentaires (cumul avec le passif de classe)."},
        "4pcs": {"crit_damage": 10, "p_pen": 10},
        "5pcs": {"p_atk": 16, "crit_damage": 8},
        "6pcs": {"passive": "+12% de chance d'esquive supplémentaires. Après esquive : +20% dégâts pendant 2 tours."},
        "7pcs": {"passive": "Après une esquive réussie, ta prochaine attaque inflige +40% dégâts et est toujours un critique."},
    },
    "assassin_donjon_abyssal": {
        "class": "Assassin", "source": "donjon_abyssal", "theme": "de Sang", "name": "Voile de Sang",
        "2pcs": {"p_atk": 38, "p_pen": 16},
        "3pcs": {"passive": "Chaque critique applique une saignée (1% HP max/tour, 3 tours). Stackable."},
        "4pcs": {"crit_chance": 4, "crit_damage": 14},
        "5pcs": {"p_atk": 28, "speed": 8},
        "6pcs": {"passive": "Les critiques appliquent 2 stacks de saignée au lieu d'1."},
        "7pcs": {"passive": "La saignée monte à 3% HP max/tour et stack jusqu'à 3 fois. Ennemis saignants subissent +10% dégâts physiques."},
    },
    "assassin_raid": {
        "class": "Assassin", "source": "raid", "theme": "de l'Exécuteur", "name": "Exécuteur des Ombres",
        "2pcs": {"p_atk": 45, "p_pen": 20, "crit_chance": 4},
        "3pcs": {"passive": "Dégâts +20% sur les cibles à moins de 30% HP."},
        "4pcs": {"speed": 16, "crit_damage": 18},
        "5pcs": {"p_atk": 32, "crit_damage": 14},
        "6pcs": {"passive": "Dégâts +25% sur cibles à moins de 30% HP. Chaque kill régénère 20% énergie."},
        "7pcs": {"passive": "Dégâts +40% sur ennemis à moins de 20% HP. Chaque coup critique régénère 2 combo."},
    },

    # ═══════════════════════════════════════════════════════════ MAGE ══
    # Builds : Blast | Tank-Mage | Crit-Mage | Pénétration | Arcane Brûlure | Omnimage
    "mage_monde": {
        "class": "Mage", "source": "monde", "theme": "Arcane", "name": "Novice Arcane",
        "2pcs": {"m_atk": 18, "m_pen": 6},
        "3pcs": {"passive": "Tes sorts ont 10% de chance de ne pas consommer de tour."},
        "4pcs": {"crit_chance": 2, "crit_damage": 5},
        "5pcs": {"m_atk": 14, "m_pen": 4},
        "6pcs": {"passive": "Tes sorts ont 15% de chance de ne pas consommer de tour."},
        "7pcs": {"passive": "Chaque sort lancé augmente ton ATK Magique de 2% (max +20%). Reset à chaque combat."},
    },
    "mage_donjon_classique": {
        "class": "Mage", "source": "donjon_classique", "theme": "Astral", "name": "Manteau Astral",
        "2pcs": {"hp": 55, "m_def": 22},
        "3pcs": {"passive": "+0.2% dégâts magiques par % de HP actuels (max +20%)."},
        "4pcs": {"m_atk": 18, "p_def": 14},
        "5pcs": {"hp": 40, "m_atk": 14},
        "6pcs": {"passive": "À plein HP : +20% dégâts magiques (cumulatif avec le bonus final)."},
        "7pcs": {"passive": "À plein HP : +30% dégâts magiques. Le passif de classe commence à +0.8%/% HP."},
    },
    "mage_craft": {
        "class": "Mage", "source": "craft", "theme": "Enchanté", "name": "Tissu Enchanté",
        "2pcs": {"crit_chance": 4, "crit_damage": 12},
        "3pcs": {"passive": "Chaque sort accumule 1 charge de Focale. À 3 charges, la prochaine attaque est un critique garanti."},
        "4pcs": {"m_atk": 22, "m_pen": 8},
        "5pcs": {"crit_chance": 2, "m_atk": 16},
        "6pcs": {"passive": "Critique garanti disponible dès 2 charges de Focale (au lieu de 3)."},
        "7pcs": {"passive": "Les critiques magiques infligent +20% dégâts supplémentaires et réinitialisent les charges de Focale."},
    },
    "mage_donjon_elite": {
        "class": "Mage", "source": "donjon_elite", "theme": "du Prophète", "name": "Voile du Prophète",
        "2pcs": {"m_pen": 16, "m_atk": 25},
        "3pcs": {"passive": "Ignore 10% de la DEF Magique ennemie."},
        "4pcs": {"crit_chance": 2, "m_def": 15},
        "5pcs": {"m_pen": 12, "crit_damage": 10},
        "6pcs": {"passive": "Ignore 18% de la DEF Magique ennemie (progression vers le bonus final)."},
        "7pcs": {"passive": "Ignore 25% DEF Magique ennemie. Chaque 3e sort inflige +60% dégâts magiques."},
    },
    "mage_donjon_abyssal": {
        "class": "Mage", "source": "donjon_abyssal", "theme": "Primordial", "name": "Suaire Primordial",
        "2pcs": {"m_atk": 44, "m_pen": 15},
        "3pcs": {"passive": "Tes critiques magiques appliquent une brûlure arcane (5% ATK Magique/tour, 2 tours)."},
        "4pcs": {"crit_chance": 3, "crit_damage": 12},
        "5pcs": {"m_atk": 32, "m_def": 18},
        "6pcs": {"passive": "Brûlure arcane dure 1 tour supplémentaire et réduit aussi la DEF Magique de 8%."},
        "7pcs": {"passive": "Brûlure arcane monte à 10% ATK Magique/tour. Elle réduit aussi la DEF Magique ennemie de 12% pour 2 tours."},
    },
    "mage_raid": {
        "class": "Mage", "source": "raid", "theme": "du Nexus", "name": "Nexus Primordial",
        "2pcs": {"m_atk": 58, "m_pen": 22, "crit_chance": 3},
        "3pcs": {"passive": "+25% dégâts magiques sur les ennemis avec moins de 50% HP."},
        "4pcs": {"m_def": 22, "hp": 55, "crit_damage": 14},
        "5pcs": {"m_atk": 45, "crit_damage": 16},
        "6pcs": {"passive": "+30% dégâts magiques sur tous les ennemis. Tes sorts ont 20% de chance de rejouer."},
        "7pcs": {"passive": "+25% dégâts magiques permanents. Tes sorts brûlent l'ennemi (5% ATK Magique/tour, 2 tours). 15% de chance de rejouer."},
    },

    # ══════════════════════════════════════════════════════════ TIREUR ══
    # Builds : Speed DPS | Multi-Hit | Critique | Sniper | Burst | Ouragan
    "tireur_monde": {
        "class": "Tireur", "source": "monde", "theme": "de Chasse", "name": "Carquois de Chasse",
        "2pcs": {"speed": 10, "p_atk": 14},
        "3pcs": {"passive": "+8% de chance de double coup supplémentaires."},
        "4pcs": {"p_pen": 5, "crit_chance": 1},
        "5pcs": {"speed": 8, "p_pen": 4},
        "6pcs": {"passive": "Si Vitesse > ennemi : +20% chance de double coup supplémentaires. +5% dégâts sur chaque tir."},
        "7pcs": {"passive": "Chaque double coup inflige +15% dégâts sur le second tir. Si Vitesse > ennemi : double coup garanti."},
    },
    "tireur_donjon_classique": {
        "class": "Tireur", "source": "donjon_classique", "theme": "du Faucon", "name": "Arc du Faucon",
        "2pcs": {"crit_chance": 4, "crit_damage": 12},
        "3pcs": {"passive": "Le double coup a 25% de chance de devenir un triple coup."},
        "4pcs": {"p_atk": 16, "p_pen": 6},
        "5pcs": {"p_atk": 12, "crit_chance": 2},
        "6pcs": {"passive": "Triple coup disponible à 35%. Chaque tir supplémentaire +8% dégâts."},
        "7pcs": {"passive": "Triple coup disponible à chaque attaque (25%). Chaque coup supplémentaire inflige +10% dégâts additionnels."},
    },
    "tireur_craft": {
        "class": "Tireur", "source": "craft", "theme": "Taillé", "name": "Bois Taillé",
        "2pcs": {"crit_chance": 5, "crit_damage": 10},
        "3pcs": {"passive": "Chaque attaque consécutive sans rater de critique ajoute +3% dégâts (max +30%)."},
        "4pcs": {"p_atk": 18, "p_pen": 8},
        "5pcs": {"crit_chance": 3, "p_atk": 14},
        "6pcs": {"passive": "À 7 critiques consécutifs (au lieu de 10), le tir chargé est disponible."},
        "7pcs": {"passive": "À 10 critiques consécutifs, ta prochaine attaque est un tir chargé : +100% dégâts et ignore la DEF Physique."},
    },
    "tireur_donjon_elite": {
        "class": "Tireur", "source": "donjon_elite", "theme": "de la Tempête", "name": "Tempête d'Acier",
        "2pcs": {"speed": 18, "p_atk": 24},
        "3pcs": {"passive": "Attaque toujours en premier si vitesse égale à l'ennemi."},
        "4pcs": {"p_pen": 12, "crit_chance": 2},
        "5pcs": {"p_atk": 20, "speed": 10},
        "6pcs": {"passive": "Chaque double coup réduit la vitesse ennemie de 8%. +20% dégâts sur cibles ralenties."},
        "7pcs": {"passive": "Chaque double coup réduit la vitesse ennemie de 12%. +30% dégâts sur cibles ralenties."},
    },
    "tireur_donjon_abyssal": {
        "class": "Tireur", "source": "donjon_abyssal", "theme": "de l'Horizon", "name": "Œil de l'Horizon",
        "2pcs": {"p_atk": 42, "p_pen": 16},
        "3pcs": {"passive": "Dégâts critiques +20% supplémentaires."},
        "4pcs": {"crit_damage": 16, "crit_chance": 3},
        "5pcs": {"p_atk": 30, "p_pen": 12},
        "6pcs": {"passive": "Tous les coups d'un double coup sont critiques si le premier l'est."},
        "7pcs": {"passive": "Si tu fais un critique lors d'un double coup, les deux tirs sont critiques. +30% dégâts sur cibles à moins de 50% HP."},
    },
    "tireur_raid": {
        "class": "Tireur", "source": "raid", "theme": "de l'Ouragan", "name": "Ouragan d'Acier",
        "2pcs": {"p_atk": 55, "p_pen": 22, "speed": 14},
        "3pcs": {"passive": "+30% dégâts physiques. Double coup garanti au premier tour."},
        "4pcs": {"crit_chance": 5, "crit_damage": 20},
        "5pcs": {"p_atk": 40, "crit_damage": 16},
        "6pcs": {"passive": "Triple coup disponible à 40%. Vitesse > ennemi : triple coup garanti au premier tour."},
        "7pcs": {"passive": "Triple coup possible à chaque attaque (25%). Double coup garanti à chaque tour. Chaque tir supplémentaire +15% dégâts."},
    },

    # ══════════════════════════════════════════════════════ SUPPORT ══
    # Builds : Tank | Bouclier Offensif | Anti-Magie | Explosif | Heal-Tank | Intouchable
    "support_monde": {
        "class": "Support", "source": "monde", "theme": "du Novice", "name": "Médaillon du Novice",
        "2pcs": {"hp": 45, "p_def": 18},
        "3pcs": {"passive": "+5% de chance de bouclier supplémentaires. Le bouclier absorbe 10% HP max."},
        "4pcs": {"m_def": 16, "speed": 4},
        "5pcs": {"hp": 35, "m_def": 12},
        "6pcs": {"passive": "Le bouclier se régénère automatiquement 1 fois par combat s'il est brisé."},
        "7pcs": {"passive": "Si bouclier actif en début de tour, régénère 3% HP max. Bouclier = 12% HP max."},
    },
    "support_donjon_classique": {
        "class": "Support", "source": "donjon_classique", "theme": "du Défenseur", "name": "Armure du Défenseur",
        "2pcs": {"p_def": 26, "m_def": 22},
        "3pcs": {"passive": "Chaque bouclier généré augmente tes dégâts de 8% pour le tour suivant."},
        "4pcs": {"p_atk": 20, "m_atk": 20},
        "5pcs": {"p_def": 18, "m_def": 15},
        "6pcs": {"passive": "Les boucliers durent 2 tours et augmentent tes dégâts de 10% en permanence."},
        "7pcs": {"passive": "Les boucliers durent 2 tours. Un bouclier actif augmente tes dégâts de 15% en permanence."},
    },
    "support_craft": {
        "class": "Support", "source": "craft", "theme": "Béni", "name": "Métal Béni",
        "2pcs": {"hp": 62, "p_def": 24},
        "3pcs": {"passive": "Le bouclier absorbe également 40% des dégâts magiques reçus."},
        "4pcs": {"m_def": 22, "speed": 5},
        "5pcs": {"hp": 46, "speed": 4},
        "6pcs": {"passive": "Le bouclier absorbe 55% des dégâts magiques. Si bouclier actif, réduit dégâts reçus de 3%."},
        "7pcs": {"passive": "Le bouclier absorbe 70% des dégâts magiques. Réduit les dégâts reçus de 5% supplémentaires."},
    },
    "support_donjon_elite": {
        "class": "Support", "source": "donjon_elite", "theme": "Sacré", "name": "Bénédiction Sacrée",
        "2pcs": {"hp": 90, "p_def": 30, "m_def": 25},
        "3pcs": {"passive": "Si le bouclier tient 2 tours, il explose et inflige 10% de tes HP max en dégâts purs."},
        "4pcs": {"speed": 8, "p_atk": 15, "m_atk": 15},
        "5pcs": {"hp": 68, "p_def": 22},
        "6pcs": {"passive": "Si le bouclier tient 1 tour seulement, l'explosion inflige quand même 7% HP max."},
        "7pcs": {"passive": "Bouclier explosif monte à 18% HP max. L'explosion réduit la vitesse ennemie de 15% pour 2 tours."},
    },
    "support_donjon_abyssal": {
        "class": "Support", "source": "donjon_abyssal", "theme": "du Gardien", "name": "Bouclier du Gardien",
        "2pcs": {"p_def": 38, "m_def": 34, "hp": 115},
        "3pcs": {"passive": "Chaque bouclier généré soigne 4% HP max."},
        "4pcs": {"p_atk": 24, "m_atk": 24, "speed": 8},
        "5pcs": {"p_def": 28, "m_def": 24},
        "6pcs": {"passive": "Bouclier = 12% HP max. Chaque bouclier soigne également 2% HP max à l'activation."},
        "7pcs": {"passive": "Bouclier = 14% HP max et soigne 6% HP max à la génération. Si bouclier actif, réduit les dégâts reçus de 15%."},
    },
    "support_raid": {
        "class": "Support", "source": "raid", "theme": "de la Lumière", "name": "Lumière Éternelle",
        "2pcs": {"hp": 180, "p_def": 52, "m_def": 48},
        "3pcs": {"passive": "Bouclier = 15% HP max. +20% HP max total."},
        "4pcs": {"speed": 12, "p_atk": 28, "m_atk": 28},
        "5pcs": {"hp": 140, "speed": 8},
        "6pcs": {"passive": "Bouclier = 18% HP max. +25% HP max total. Si bouclier actif, réduit les dégâts reçus de 5%."},
        "7pcs": {"passive": "Bouclier se régénère automatiquement toutes les 2 tours. Si bouclier actif : soin de 4% HP max/tour et réduit les dégâts reçus de 12%."},
    },

    # ══════════════════════════════════════════════════════ VAMPIRE ══
    # Builds : Vol de Vie Pur | Crit-Drain | Speed-Drain | Survie | Burst-Drain | Immortel
    "vampire_monde": {
        "class": "Vampire", "source": "monde", "theme": "de la Nuit", "name": "Crocs de la Nuit",
        "2pcs": {"p_atk": 16, "hp": 32},
        "3pcs": {"passive": "+8% vol de vie supplémentaires (total 33%)."},
        "4pcs": {"p_pen": 6, "crit_chance": 1},
        "5pcs": {"p_atk": 12, "hp": 24},
        "6pcs": {"passive": "Le bouclier du vol de vie absorbe aussi les dégâts magiques à 50%."},
        "7pcs": {"passive": "Le vol de vie génère aussi un bouclier de 20% du soin effectué. +5% vol de vie supplémentaires."},
    },
    "vampire_donjon_classique": {
        "class": "Vampire", "source": "donjon_classique", "theme": "Maudit", "name": "Manteau Maudit",
        "2pcs": {"crit_chance": 4, "crit_damage": 14},
        "3pcs": {"passive": "Chaque critique draine 5% HP max ennemi directement (en plus du vol de vie normal)."},
        "4pcs": {"p_atk": 18, "p_pen": 6},
        "5pcs": {"crit_chance": 3, "p_atk": 14},
        "6pcs": {"passive": "Drain critique actif sur toutes les attaques à 50% de l'effet normal."},
        "7pcs": {"passive": "Drain critique monte à 8% HP max. 3 critiques consécutifs → régénère 15% HP max instantanément."},
    },
    "vampire_craft": {
        "class": "Vampire", "source": "craft", "theme": "Ensanglanté", "name": "Acier Ensanglanté",
        "2pcs": {"speed": 14, "p_atk": 22},
        "3pcs": {"passive": "Le vol de vie génère un bouclier pour 50% du soin reçu."},
        "4pcs": {"crit_chance": 2, "p_pen": 8},
        "5pcs": {"speed": 10, "p_pen": 6},
        "6pcs": {"passive": "Bouclier du vol de vie = 65% du soin. Si bouclier actif, réduit les dégâts reçus de 5%."},
        "7pcs": {"passive": "Bouclier du vol de vie monte à 80% du soin. Si bouclier actif, +15% dégâts physiques."},
    },
    "vampire_donjon_elite": {
        "class": "Vampire", "source": "donjon_elite", "theme": "des Ténèbres", "name": "Suaire des Ténèbres",
        "2pcs": {"hp": 62, "p_def": 18, "m_def": 16},
        "3pcs": {"passive": "Si HP > 80% : +20% dégâts. Vol de vie augmenté de +10%."},
        "4pcs": {"p_atk": 20, "crit_damage": 8},
        "5pcs": {"p_atk": 16, "crit_chance": 2},
        "6pcs": {"passive": "Seuil actif abaissé à HP > 70%. Vol de vie +15% quand actif."},
        "7pcs": {"passive": "Régénère 3% HP max/tour. Vol de vie total = 40%. Si HP > 80%, +30% dégâts physiques."},
    },
    "vampire_donjon_abyssal": {
        "class": "Vampire", "source": "donjon_abyssal", "theme": "du Seigneur", "name": "Seigneur des Ténèbres",
        "2pcs": {"p_atk": 44, "crit_damage": 14},
        "3pcs": {"passive": "Chaque critique pompe 4% HP max ennemi directement."},
        "4pcs": {"hp": 82, "p_pen": 16},
        "5pcs": {"p_atk": 34, "crit_damage": 10},
        "6pcs": {"passive": "Drain critique actif sur toutes les attaques. Dégâts +15% sur cibles à moins de 50% HP."},
        "7pcs": {"passive": "Drain critique monte à 6% HP max. Dégâts +20% sur cibles à moins de 50% HP. Vol de vie +15%."},
    },
    "vampire_raid": {
        "class": "Vampire", "source": "raid", "theme": "Immortel", "name": "Prince Immortel",
        "2pcs": {"p_atk": 58, "hp": 130, "crit_chance": 4},
        "3pcs": {"passive": "Vol de vie = 40% dégâts. +10% dégâts par 10% HP manquants (cumul avec passif de classe)."},
        "4pcs": {"p_pen": 20, "crit_damage": 20},
        "5pcs": {"p_atk": 42, "hp": 100},
        "6pcs": {"passive": "Vol de vie = 50% dégâts. Chaque drain soigne en plus 2% HP max supplémentaires."},
        "7pcs": {"passive": "Une fois par combat, si tu meurs, reviens à 25% HP et soigne instantanément via le vol de vie sur le prochain coup."},
    },

    # ══════════════════════════════════════════════ GARDIEN DU TEMPS ══
    # Builds : Debuff Défensif | Multi-Debuff | Début Avantageux | Debuff Lock | Burst-Debuff | Maître
    "gardien_monde": {
        "class": "Gardien du Temps", "source": "monde", "theme": "Brisé", "name": "Brisé",
        "2pcs": {"hp": 35, "p_def": 14, "m_def": 14},
        "3pcs": {"passive": "Les debuffs de réduction de stats durent 1 tour supplémentaire."},
        "4pcs": {"speed": 6, "p_atk": 10, "m_atk": 10},
        "5pcs": {"p_atk": 8, "m_atk": 8, "speed": 4},
        "6pcs": {"passive": "Les debuffs actifs sur l'ennemi augmentent tes dégâts de 2% chacun (max +15%)."},
        "7pcs": {"passive": "Les debuffs actifs sur l'ennemi augmentent tes dégâts de 3% chacun (max +30%)."},
    },
    "gardien_donjon_classique": {
        "class": "Gardien du Temps", "source": "donjon_classique", "theme": "Fractal", "name": "Horloge Fractale",
        "2pcs": {"p_atk": 16, "m_atk": 16, "speed": 8},
        "3pcs": {"passive": "25% de chance de réduire 2 stats ennemies au lieu d'une par tour."},
        "4pcs": {"hp": 46, "p_def": 15},
        "5pcs": {"p_atk": 12, "m_atk": 12, "hp": 35},
        "6pcs": {"passive": "Chance de double debuff monte à 30%. Chaque stat réduite = +3% dégâts."},
        "7pcs": {"passive": "Chance de double debuff monte à 40%. Chaque stat réduite amplifie tes dégâts de 4%."},
    },
    "gardien_craft": {
        "class": "Gardien du Temps", "source": "craft", "theme": "Temporel", "name": "Tissu Temporel",
        "2pcs": {"hp": 52, "p_def": 20, "m_def": 20},
        "3pcs": {"passive": "Au début du combat, réduit immédiatement 2 stats ennemies de 8% chacune."},
        "4pcs": {"p_atk": 18, "m_atk": 18},
        "5pcs": {"hp": 40, "p_def": 16},
        "6pcs": {"passive": "Début de combat : réduit immédiatement 3 stats ennemies de 7% chacune."},
        "7pcs": {"passive": "Début de combat : réduit 3 stats ennemies de 8% pour toute la durée du combat."},
    },
    "gardien_donjon_elite": {
        "class": "Gardien du Temps", "source": "donjon_elite", "theme": "Chronique", "name": "Chrono Maudit",
        "2pcs": {"p_atk": 25, "m_atk": 25, "speed": 12},
        "3pcs": {"passive": "Les stats réduites de l'ennemi ne peuvent pas être restaurées pendant le combat."},
        "4pcs": {"crit_chance": 3, "p_pen": 8, "m_pen": 8},
        "5pcs": {"p_atk": 20, "m_atk": 20},
        "6pcs": {"passive": "Les stats réduites bloquent 1 tour supplémentaire avant restauration."},
        "7pcs": {"passive": "Debuffs permanents ET chaque nouvelle réduction s'ajoute aux précédentes sans limite de -50%."},
    },
    "gardien_donjon_abyssal": {
        "class": "Gardien du Temps", "source": "donjon_abyssal", "theme": "du Paradoxe", "name": "Paradoxe Temporel",
        "2pcs": {"p_atk": 36, "m_atk": 36},
        "3pcs": {"passive": "Chaque 10% de stat réduite chez l'ennemi t'octroie +5% dégâts (max +50%)."},
        "4pcs": {"speed": 14, "crit_damage": 12},
        "5pcs": {"p_atk": 28, "m_atk": 28, "speed": 10},
        "6pcs": {"passive": "Chaque 8% de stat réduite = +4% dégâts (max +40%)."},
        "7pcs": {"passive": "À -50% de réduction atteinte, l'ennemi perd 1 action par tour. Dégâts doublés contre les ennemis à -50%."},
    },
    "gardien_raid": {
        "class": "Gardien du Temps", "source": "raid", "theme": "du Destin", "name": "Maître du Destin",
        "2pcs": {"p_atk": 52, "m_atk": 52, "speed": 16},
        "3pcs": {"passive": "Réduction max passe à 75%. Chaque debuff appliqué soigne 3% HP max."},
        "4pcs": {"crit_chance": 4, "crit_damage": 16},
        "5pcs": {"p_atk": 40, "m_atk": 40},
        "6pcs": {"passive": "Réduction max passe à 65% dès 6pcs. Les debuffs initiaux durent 3 tours supplémentaires."},
        "7pcs": {"passive": "Dégâts +15% par debuff actif (max +60%). L'ennemi à -75% de stats perd 1 action par tour. Dégâts garantis non-esquivables."},
    },

    # ═══════════════════════════════════════════════════ OMBRE VENIN ══
    # Builds : Poison Pur | Vitesse-Poison | Burst Initial | Crit-Poison | Poison-Debuff | Nécrosis
    "ombre_monde": {
        "class": "Ombre Venin", "source": "monde", "theme": "Vénéneux", "name": "Distillat Vénéneux",
        "2pcs": {"p_atk": 12, "m_atk": 10},
        "3pcs": {"passive": "Le poison inflige +1% HP max ennemi/tour supplémentaire (4% au lieu de 3%)."},
        "4pcs": {"p_pen": 5, "m_pen": 5},
        "5pcs": {"p_atk": 10, "m_pen": 4},
        "6pcs": {"passive": "Le poison inflige +1% HP max/tour supplémentaire (5% total à 5 stacks)."},
        "7pcs": {"passive": "Le poison monte à 5% HP max/tour. Chaque tour empoisonné, l'ennemi subit -2% à une stat aléatoire."},
    },
    "ombre_donjon_classique": {
        "class": "Ombre Venin", "source": "donjon_classique", "theme": "Toxique", "name": "Aiguille Toxique",
        "2pcs": {"speed": 14, "p_atk": 18},
        "3pcs": {"passive": "30% de chance d'appliquer une dose de poison supplémentaire par attaque."},
        "4pcs": {"p_pen": 8, "crit_chance": 2},
        "5pcs": {"speed": 10, "crit_chance": 2},
        "6pcs": {"passive": "50% de chance d'appliquer une dose de poison supplémentaire par attaque."},
        "7pcs": {"passive": "Chaque attaque empoisonne à coup sûr (dose supplémentaire). Le poison s'applique avant les dégâts physiques."},
    },
    "ombre_craft": {
        "class": "Ombre Venin", "source": "craft", "theme": "Distillé", "name": "Venin Distillé",
        "2pcs": {"p_atk": 24, "m_atk": 18},
        "3pcs": {"passive": "Le premier poison appliqué inflige directement 8% HP max en dégâts instantanés."},
        "4pcs": {"p_pen": 9, "m_pen": 7},
        "5pcs": {"p_atk": 18, "p_pen": 7},
        "6pcs": {"passive": "Chaque dose de poison supplémentaire inflige aussi +3% HP max instantanément."},
        "7pcs": {"passive": "Chaque re-application de poison inflige +5% HP max instantanément. Stack infini."},
    },
    "ombre_donjon_elite": {
        "class": "Ombre Venin", "source": "donjon_elite", "theme": "de Brume", "name": "Brume Toxique",
        "2pcs": {"crit_chance": 4, "crit_damage": 12},
        "3pcs": {"passive": "Chaque critique applique automatiquement 1 dose de poison."},
        "4pcs": {"p_atk": 24, "p_pen": 10},
        "5pcs": {"crit_chance": 2, "p_atk": 18},
        "6pcs": {"passive": "Le poison par critique inflige 5% HP max/tour. Dégâts critiques +15% sur cibles empoisonnées."},
        "7pcs": {"passive": "Le poison appliqué par les critiques inflige 6% HP max/tour. Dégâts critiques +15% sur cibles empoisonnées."},
    },
    "ombre_donjon_abyssal": {
        "class": "Ombre Venin", "source": "donjon_abyssal", "theme": "Corrompu", "name": "Essence Corrompue",
        "2pcs": {"p_atk": 40, "speed": 12},
        "3pcs": {"passive": "Le poison réduit la DEF Physique et la DEF Magique ennemies de 5% par tour de poison actif (max -25%)."},
        "4pcs": {"m_pen": 14, "p_pen": 12},
        "5pcs": {"p_atk": 30, "m_pen": 10},
        "6pcs": {"passive": "Réduction DEF du poison = 6%/tour (max -30%). +12% dégâts sur cibles affaiblies."},
        "7pcs": {"passive": "Réduction DEF du poison monte à 8%/tour (max -40%). Dégâts physiques +15% sur cibles dont la DEF est réduite."},
    },
    "ombre_raid": {
        "class": "Ombre Venin", "source": "raid", "theme": "de la Nécrosis", "name": "Nécrosis Primordiale",
        "2pcs": {"p_atk": 54, "m_atk": 38, "speed": 14},
        "3pcs": {"passive": "Le poison peut stacker 3 fois (3% + 6% + 9% HP max ennemi/tour)."},
        "4pcs": {"p_pen": 20, "m_pen": 18, "crit_chance": 4},
        "5pcs": {"p_atk": 40, "m_atk": 28, "p_pen": 14},
        "6pcs": {"passive": "Au max de stacks, l'ennemi subit -20% à toutes ses stats. Poison = 12% HP max/tour."},
        "7pcs": {"passive": "Au max de stacks, l'ennemi est en nécrosis : perd 20% HP max/tour et toutes ses stats sont réduites de 15%."},
    },

    # ═════════════════════════════════════════════════ PYROMANCIEN ══
    # Builds : Stack Rapide | Crit-Feu | ATK Magique Pure | Brûlure Longue | Explosive | Phénix
    "pyro_monde": {
        "class": "Pyromancien", "source": "monde", "theme": "Ardent", "name": "Tison Ardent",
        "2pcs": {"m_atk": 18, "m_pen": 6},
        "3pcs": {"passive": "La brûlure peut monter jusqu'à 6 stacks au lieu de 5."},
        "4pcs": {"hp": 22, "crit_chance": 2},
        "5pcs": {"m_atk": 14, "crit_damage": 6},
        "6pcs": {"passive": "La brûlure peut monter jusqu'à 7 stacks."},
        "7pcs": {"passive": "La brûlure inflige +2% ATK Magique/stack supplémentaires. Au max, inflige instantanément 20% ATK Magique."},
    },
    "pyro_donjon_classique": {
        "class": "Pyromancien", "source": "donjon_classique", "theme": "Enflammé", "name": "Flamme Enflammée",
        "2pcs": {"crit_chance": 4, "crit_damage": 14},
        "3pcs": {"passive": "Chaque critique ajoute automatiquement 1 stack de brûlure."},
        "4pcs": {"m_atk": 20, "m_pen": 7},
        "5pcs": {"crit_chance": 2, "m_atk": 16},
        "6pcs": {"passive": "Les critiques appliquent 2 stacks de brûlure. Dégâts critiques +6% par stack actif."},
        "7pcs": {"passive": "Les critiques appliquent 2 stacks de brûlure au lieu d'1. Dégâts critiques +10% par stack actif."},
    },
    "pyro_craft": {
        "class": "Pyromancien", "source": "craft", "theme": "Incandescent", "name": "Pierre Incandescente",
        "2pcs": {"m_atk": 32, "m_pen": 12},
        "3pcs": {"passive": "Tes sorts ont 20% de chance d'appliquer directement 2 stacks de brûlure."},
        "4pcs": {"crit_chance": 2, "crit_damage": 8},
        "5pcs": {"m_atk": 24, "m_pen": 10},
        "6pcs": {"passive": "ATK Magique +2% par stack de brûlure actif. 25% de chance d'appliquer 2 stacks sur sorts."},
        "7pcs": {"passive": "ATK Magique +3% par stack de brûlure actif. Sorts : 30% de chance d'appliquer 2 stacks. Double lancé 10% du temps."},
    },
    "pyro_donjon_elite": {
        "class": "Pyromancien", "source": "donjon_elite", "theme": "Infernal", "name": "Brasier Infernal",
        "2pcs": {"m_atk": 34, "m_def": 16},
        "3pcs": {"passive": "La brûlure dure 1 tour supplémentaire avant de se dissiper."},
        "4pcs": {"hp": 38, "m_pen": 11},
        "5pcs": {"m_atk": 26, "hp": 28},
        "6pcs": {"passive": "La brûlure ne commence à se dissiper qu'après 2 tours sans attaque."},
        "7pcs": {"passive": "La brûlure ne se dissipe jamais tant que l'ennemi reste en vie. À 5 stacks, l'ennemi perd 4 points de speed/tour."},
    },
    "pyro_donjon_abyssal": {
        "class": "Pyromancien", "source": "donjon_abyssal", "theme": "Volcanique", "name": "Âme Volcanique",
        "2pcs": {"m_atk": 46, "m_pen": 16},
        "3pcs": {"passive": "Au max de stacks, l'ennemi subit +20% dégâts magiques supplémentaires."},
        "4pcs": {"crit_chance": 4, "crit_damage": 15},
        "5pcs": {"m_atk": 36, "crit_damage": 12},
        "6pcs": {"passive": "Au max de stacks, +25% dégâts magiques. Chaque critique ajoute 1 stack."},
        "7pcs": {"passive": "Brûlure max = 7 stacks. Au max, la brûlure inflige 25% ATK Magique/stack au lieu de 15%. Chaque critique ajoute 1 stack."},
    },
    "pyro_raid": {
        "class": "Pyromancien", "source": "raid", "theme": "du Phénix", "name": "Phénix Éternel",
        "2pcs": {"m_atk": 68, "m_pen": 24, "crit_chance": 4},
        "3pcs": {"passive": "Brûlure max = 8 stacks. Au max, l'ennemi prend +30% dégâts magiques."},
        "4pcs": {"crit_damage": 22, "hp": 58},
        "5pcs": {"m_atk": 52, "crit_damage": 18},
        "6pcs": {"passive": "Brûlure max = 9 stacks. Au max, +35% dégâts magiques et brûlure inflige 18% ATK Magique/tour."},
        "7pcs": {"passive": "Une fois par combat, si tu meurs, ressuscite à 30% HP et applique immédiatement 8 stacks de brûlure à l'ennemi."},
    },

    # ══════════════════════════════════════════════════════ PALADIN ══
    # Builds : Tank-Ramp | Ramp Rapide | Défense Profonde | Ramp Max | Indestructible | Avatar
    "paladin_monde": {
        "class": "Paladin", "source": "monde", "theme": "Consacré", "name": "Armure Consacrée",
        "2pcs": {"hp": 42, "p_def": 18},
        "3pcs": {"passive": "Le ramp du passif démarre à +5% dès le tour 1 au lieu de 0%."},
        "4pcs": {"m_def": 16, "p_atk": 8},
        "5pcs": {"hp": 32, "p_def": 14},
        "6pcs": {"passive": "Le ramp démarre à +8% dès le tour 1."},
        "7pcs": {"passive": "Le ramp démarre à +10%. Régénère 2% HP max/tour grâce à la foi."},
    },
    "paladin_donjon_classique": {
        "class": "Paladin", "source": "donjon_classique", "theme": "du Croisé", "name": "Vœu du Croisé",
        "2pcs": {"p_atk": 22, "m_atk": 14, "speed": 6},
        "3pcs": {"passive": "Le ramp augmente de +4% par tour au lieu de +3% (max atteint plus vite)."},
        "4pcs": {"p_def": 18, "m_def": 15},
        "5pcs": {"p_def": 14, "m_def": 12},
        "6pcs": {"passive": "Ramp à +4.5%/tour. S'applique également aux dégâts magiques."},
        "7pcs": {"passive": "Ramp à +4%/tour. Le ramp offensif s'applique aussi aux dégâts magiques."},
    },
    "paladin_craft": {
        "class": "Paladin", "source": "craft", "theme": "Sanctifié", "name": "Métal Sanctifié",
        "2pcs": {"hp": 66, "p_def": 28},
        "3pcs": {"passive": "Réduit les dégâts reçus de 4% supplémentaires par tour de combat (max -30%)."},
        "4pcs": {"m_def": 24, "p_atk": 14},
        "5pcs": {"hp": 52, "m_def": 18},
        "6pcs": {"passive": "Réduction dégâts de +5%/tour. Plafond porté à -35%."},
        "7pcs": {"passive": "+8% au ramp défensif de départ. La réduction dégâts par tour ne plafonne plus à -30% mais à -45%."},
    },
    "paladin_donjon_elite": {
        "class": "Paladin", "source": "donjon_elite", "theme": "Divin", "name": "Lumière Divine",
        "2pcs": {"hp": 86, "p_def": 32, "m_def": 28},
        "3pcs": {"passive": "Le ramp max passe à +40%/+40% en réduction et dégâts."},
        "4pcs": {"p_atk": 24, "m_atk": 18, "speed": 6},
        "5pcs": {"p_atk": 18, "speed": 4},
        "6pcs": {"passive": "Ramp max +45%. Tes attaques ignorent 8% DEF ennemie à mi-ramp."},
        "7pcs": {"passive": "Ramp max +40%. Dégâts sacrés : tes attaques ignorent 10% DEF ennemie quand le ramp est au max."},
    },
    "paladin_donjon_abyssal": {
        "class": "Paladin", "source": "donjon_abyssal", "theme": "de la Foi", "name": "Bouclier de la Foi",
        "2pcs": {"p_def": 42, "m_def": 40, "hp": 122},
        "3pcs": {"passive": "La réduction de dégâts du ramp s'applique aussi aux dégâts purs."},
        "4pcs": {"p_atk": 35, "m_atk": 28},
        "5pcs": {"p_def": 32, "m_def": 30},
        "6pcs": {"passive": "Reflète 8% des dégâts reçus. La réduction de dégâts purs commence dès 2pcs."},
        "7pcs": {"passive": "Dégâts purs réduits par le ramp. Reflète 15% des dégâts reçus à l'ennemi."},
    },
    "paladin_raid": {
        "class": "Paladin", "source": "raid", "theme": "de l'Avatar", "name": "Avatar Sacré",
        "2pcs": {"hp": 212, "p_def": 58, "m_def": 55, "p_atk": 40},
        "3pcs": {"passive": "Ramp max +50%/+50%. Le ramp ne se réinitialise pas entre les vagues de donjon."},
        "4pcs": {"m_atk": 32, "speed": 9, "crit_chance": 2},
        "5pcs": {"hp": 160, "p_atk": 30},
        "6pcs": {"passive": "Ramp max +55%/+55%. Reflète 25% des dégâts reçus quand ramp > 25%."},
        "7pcs": {"passive": "Une fois par combat, reflète 30% des dégâts reçus. Au max du ramp, chaque attaque soigne 5% HP max."},
    },
}


def get_set_bonus(items_equipped: list[dict]) -> dict:
    """
    Calcule les bonus de panoplie selon les items équipés.
    Bonus réels = valeur_base × SOURCE_POWER_MULT[source] × RARITY_MULT[rareté_min].
    La rareté de la pièce la moins rare limite toute la panoplie.
    """
    from bot.cogs.rpg.items import EQUIPMENT_CATALOG
    set_counts:        dict[str, int] = {}
    min_rarity_per_set: dict[str, str] = {}

    for eq in items_equipped:
        if not eq.get("slot_equipped"):
            continue
        item_data = EQUIPMENT_CATALOG.get(eq["item_id"])
        if not item_data:
            continue
        set_key = item_data.get("set")
        if not set_key:
            continue
        set_counts[set_key] = set_counts.get(set_key, 0) + 1
        r = eq.get("rarity", "commun")
        if set_key not in min_rarity_per_set:
            min_rarity_per_set[set_key] = r
        elif RARITIES.index(r) < RARITIES.index(min_rarity_per_set[set_key]):
            min_rarity_per_set[set_key] = r

    bonus_stats    = {}
    bonus_passives = []

    for set_key, count in set_counts.items():
        set_data = SET_BONUSES.get(set_key)
        if not set_data:
            continue
        rarity       = min_rarity_per_set.get(set_key, "commun")
        rarity_mult  = RARITY_MULT[rarity]
        source_mult  = SOURCE_POWER_MULT.get(set_data.get("source", "monde"), 1.0)
        multiplier   = min(rarity_mult * source_mult, 30.0)  # plafond anti-abus hautes raretés

        if count >= 2:
            for k, v in set_data.get("2pcs", {}).items():
                bonus_stats[k] = bonus_stats.get(k, 0) + int(v * multiplier)
        if count >= 3:
            passive_3 = set_data.get("3pcs", {}).get("passive")
            if passive_3:
                display_name = set_data.get("name", set_key)
                bonus_passives.append(f"**{display_name}** (3 pcs) : {passive_3}")
        if count >= 4:
            for k, v in set_data.get("4pcs", {}).items():
                bonus_stats[k] = bonus_stats.get(k, 0) + int(v * multiplier)
        if count >= 5:
            for k, v in set_data.get("5pcs", {}).items():
                bonus_stats[k] = bonus_stats.get(k, 0) + int(v * multiplier)
        if count >= 6:
            passive_6 = set_data.get("6pcs", {}).get("passive")
            if passive_6:
                display_name = set_data.get("name", set_key)
                bonus_passives.append(f"**{display_name}** (6 pcs) : {passive_6}")
        if count >= 7:
            passive = set_data.get("7pcs", {}).get("passive")
            if passive:
                display_name = set_data.get("name", set_key)
                bonus_passives.append(f"**{display_name}** (7 pcs) : {passive}")

    return {"stats": bonus_stats, "passives": bonus_passives}


# ─── Reliques ──────────────────────────────────────────────────────────────
# Une seule relique "Relique du Bot Suprême" déclinée en 10 raretés.
# Chaque relique donne TOUS les 6 effets simultanément, les valeurs
# scalent avec le multiplicateur de rareté.
# Effets :
#   vol_vie       — % de vol de vie sur dégâts infligés
#   reduction_dmg — % de réduction des dégâts reçus
#   bonus_dmg     — % d'amplification des dégâts infligés
#   reflet        — % des dégâts reçus renvoyés en dégâts purs
#   double_frappe — % de chance de frapper deux fois au tour joueur
#   regen_hp      — % des HP max régénérés au début du tour joueur
RELICS: dict[str, dict] = {
    "relic_bot_supreme_commun": {
        "name": "Relique du Bot Suprême", "rarity": "commun", "emoji": "⬜",
        "effects": {"vol_vie": 0.30, "reduction_dmg": 0.20, "bonus_dmg": 0.30, "reflet": 0.40, "double_frappe": 0.20, "regen_hp": 0.15},
    },
    "relic_bot_supreme_peu_commun": {
        "name": "Relique du Bot Suprême", "rarity": "peu commun", "emoji": "🟩",
        "effects": {"vol_vie": 0.35, "reduction_dmg": 0.25, "bonus_dmg": 0.35, "reflet": 0.45, "double_frappe": 0.25, "regen_hp": 0.20},
    },
    "relic_bot_supreme_rare": {
        "name": "Relique du Bot Suprême", "rarity": "rare", "emoji": "🟦",
        "effects": {"vol_vie": 0.40, "reduction_dmg": 0.30, "bonus_dmg": 0.40, "reflet": 0.50, "double_frappe": 0.30, "regen_hp": 0.20},
    },
    "relic_bot_supreme_epique": {
        "name": "Relique du Bot Suprême", "rarity": "épique", "emoji": "🟪",
        "effects": {"vol_vie": 0.50, "reduction_dmg": 0.35, "bonus_dmg": 0.50, "reflet": 0.65, "double_frappe": 0.35, "regen_hp": 0.25},
    },
    "relic_bot_supreme_legendaire": {
        "name": "Relique du Bot Suprême", "rarity": "légendaire", "emoji": "🟧",
        "effects": {"vol_vie": 0.60, "reduction_dmg": 0.40, "bonus_dmg": 0.60, "reflet": 0.80, "double_frappe": 0.40, "regen_hp": 0.30},
    },
    "relic_bot_supreme_mythique": {
        "name": "Relique du Bot Suprême", "rarity": "mythique", "emoji": "🟥",
        "effects": {"vol_vie": 0.70, "reduction_dmg": 0.50, "bonus_dmg": 0.70, "reflet": 0.90, "double_frappe": 0.50, "regen_hp": 0.35},
    },
    "relic_bot_supreme_artefact": {
        "name": "Relique du Bot Suprême", "rarity": "artefact", "emoji": "🔶",
        "effects": {"vol_vie": 0.85, "reduction_dmg": 0.60, "bonus_dmg": 0.85, "reflet": 1.10, "double_frappe": 0.60, "regen_hp": 0.45},
    },
    "relic_bot_supreme_divin": {
        "name": "Relique du Bot Suprême", "rarity": "divin", "emoji": "🟡",
        "effects": {"vol_vie": 1.00, "reduction_dmg": 0.70, "bonus_dmg": 1.00, "reflet": 1.35, "double_frappe": 0.70, "regen_hp": 0.50},
    },
    "relic_bot_supreme_transcendant": {
        "name": "Relique du Bot Suprême", "rarity": "transcendant", "emoji": "🩵",
        "effects": {"vol_vie": 1.20, "reduction_dmg": 0.85, "bonus_dmg": 1.20, "reflet": 1.60, "double_frappe": 0.85, "regen_hp": 0.65},
    },
    "relic_bot_supreme_prismatique": {
        "name": "Relique du Bot Suprême", "rarity": "prismatique", "emoji": "🌈",
        "effects": {"vol_vie": 1.50, "reduction_dmg": 1.00, "bonus_dmg": 1.50, "reflet": 2.00, "double_frappe": 1.00, "regen_hp": 0.75},
    },
}

# Plafonds (caps) des effets de reliques
RELIC_CAPS: dict[str, float] = {
    "vol_vie":       8.0,    # max 8% vol de vie
    "reduction_dmg": 6.0,    # max 6% réduction dégâts
    "bonus_dmg":     10.0,   # max 10% amplification dégâts
    "reflet":        5.0,    # max 5% renvoi
    "double_frappe": 15.0,   # max 15% chance double frappe
    "regen_hp":      4.0,    # max 4% regen HP/tour
}

WB_RANK_REWARDS = {
    1:  {"relic": "relic_bot_supreme_prismatique",   "gold": 50_000},
    2:  {"relic": "relic_bot_supreme_transcendant",  "gold": 30_000},
    3:  {"relic": "relic_bot_supreme_divin",         "gold": 20_000},
    4:  {"relic": "relic_bot_supreme_artefact",      "gold": 12_000},
    5:  {"relic": "relic_bot_supreme_mythique",      "gold": 8_000},
    6:  {"relic": "relic_bot_supreme_legendaire",    "gold": 5_000},
    7:  {"relic": "relic_bot_supreme_epique",        "gold": 3_000},
    8:  {"relic": "relic_bot_supreme_rare",          "gold": 2_000},
    9:  {"relic": "relic_bot_supreme_peu_commun",    "gold": 1_000},
    10: {"relic": "relic_bot_supreme_peu_commun",    "gold": 500},
    # Rang 11+ (tous les participants) → commun + 200 gold
    "default": {"relic": "relic_bot_supreme_commun", "gold": 200},
}

# ─── Spell system ──────────────────────────────────────────────────────────────
# Structure par sort :
#   name        : str   — nom affiché
#   emoji       : str
#   description : str   — description courte
#   resource    : str   — "rage" | "mana" | "combo"
#   cost        : int   — coût en ressource
#   cooldown    : int   — tours avant réutilisation (0 = pas de CD)
#   min_turn    : int   — tour minimum pour utiliser (1 = dès le début)
#   type        : str   — "damage" | "heal" | "buff" | "debuff" | "utility"
#   is_ultimate : bool
#
# Effets (dans "effects" dict) :
#   dmg_mult        : float  — multiplicateur sur p_atk ou m_atk
#   magic           : bool   — utilise m_atk au lieu de p_atk
#   hits            : int    — nombre de coups
#   guaranteed_crit : bool
#   pen_pct         : float  — % de pénétration d'armor ignorée
#   ignore_mdef     : bool
#   lifesteal       : float  — fraction des dégâts récupérés en HP
#   heal_pct        : float  — soin = heal_pct × max_hp
#   heal_last_dmg   : bool   — soin = dernier dégât reçu
#   shield_pct      : float  — bouclier = shield_pct × max_hp
#   stat_buff       : dict   — {stat: pct} appliqué au joueur (ex: {"p_atk": 30})
#   stat_debuff     : dict   — {stat: pct} appliqué à l'ennemi
#   buff_turns      : int    — durée du buff/debuff
#   dot             : str    — "burn" | "poison"
#   dot_stacks      : int    — nb stacks de DoT ajoutés
#   stun            : int    — nb tours de stun (ennemi ne peut pas attaquer)
#   speed_debuff    : float  — réduction de vitesse ennemi (fraction)
#   speed_debuff_turns : int
#   no_heal_turns   : int    — joueur ne peut pas se soigner pendant N tours
#   damage_amp      : float  — les dégâts reçus sont multipliés (debuff ennemi)
#   damage_amp_turns: int
#   dot_amp         : float  — multiplicateur sur les DoT existants
#   dot_amp_turns   : int
#   explode_dots    : bool   — explose tous les DoT actifs
#   explode_mult    : float  — multiplicateur lors de l'explosion
#   damage_reduction: float  — réduction des dégâts reçus (buff joueur)
#   dmg_reduction_turns: int
#   resurrection    : bool   — survit à la mort avec 1 HP
#   poison_stacks_mult: int  — multiplie les stacks de poison actifs
CLASS_SPELLS: dict[str, dict] = {
    # ── Guerrier (Rage) ────────────────────────────────────────────────────────
    "guerrier": {
        "resource": "rage",
        "resource_max": 100,
        "resource_per_turn": 10,
        "resource_on_hit": 5,
        "s1": {
            "name": "Châtiment Sanglant",
            "emoji": "⚔️",
            "description": "Sacrifie 15% de ses PV pour infliger ×2.5 dégâts physiques.",
            "cost": 25, "cooldown": 2, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 2.5, "self_damage_pct": 0.15},
        },
        "s2": {
            "name": "Contre-Attaque",
            "emoji": "🔄",
            "description": "Riposte automatiquement à chaque attaque ennemie pendant 2 tours.",
            "cost": 30, "cooldown": 4, "min_turn": 1, "type": "utility", "is_ultimate": False,
            "effects": {"contre_attaque_turns": 2},
        },
        "ultimate": {
            "name": "Immortalité",
            "emoji": "💢",
            "description": "Devient immortel pendant 3 tours — impossible de tomber sous 1 PV.",
            "cost": 80, "cooldown": 8, "min_turn": 3, "type": "utility", "is_ultimate": True,
            "effects": {"undying_turns": 3},
        },
    },
    # ── Assassin (Combo) ───────────────────────────────────────────────────────
    "assassin": {
        "resource": "combo",
        "resource_max": 5,
        "resource_per_turn": 1,
        "resource_on_hit": 0,
        "s1": {
            "name": "Frappe de l'Ombre",
            "emoji": "🗡️",
            "description": "Inflige ×1.8 dégâts physiques. Double les chances d'esquive pour la prochaine attaque ennemie.",
            "cost": 1, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.8, "double_dodge_next": True},
        },
        "s2": {
            "name": "Lame Perçante",
            "emoji": "✴️",
            "description": "Inflige ×1.6 dégâts physiques en ignorant 60% de la Déf.Phy. ennemie.",
            "cost": 2, "cooldown": 2, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.6, "pen_pct": 0.60},
        },
        "ultimate": {
            "name": "Exécution",
            "emoji": "💀",
            "description": "Dégâts ×2.0 → ×4.0 selon les PV manquants de l'ennemi (×4.0 à 0% PV).",
            "cost": 5, "cooldown": 6, "min_turn": 3, "type": "damage", "is_ultimate": True,
            "effects": {"execute_scaling": True, "execute_base_mult": 2.0, "execute_max_mult": 4.0},
        },
    },
    # ── Mage (Mana) ────────────────────────────────────────────────────────────
    "mage": {
        "resource": "mana",
        "resource_max": 100,
        "resource_per_turn": 15,
        "resource_on_hit": 0,
        "s1": {
            "name": "Soif Arcane",
            "emoji": "⚡",
            "description": "Inflige ×1.2 dégâts magiques et récupère 20 mana supplémentaire.",
            "cost": 15, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.2, "magic": True, "bonus_resource": 20},
        },
        "s2": {
            "name": "Écran Magique",
            "emoji": "🔵",
            "description": "Inflige ×1.4 dégâts magiques et réduit les dégâts subis de 25% pendant 2 tours.",
            "cost": 25, "cooldown": 3, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.4, "magic": True, "damage_reduction": 0.25, "dmg_reduction_turns": 2},
        },
        "ultimate": {
            "name": "Nova Primordiale",
            "emoji": "☄️",
            "description": "Inflige ×4.5 dégâts magiques en ignorant toute la Déf.Mag.",
            "cost": 80, "cooldown": 7, "min_turn": 3, "type": "damage", "is_ultimate": True,
            "effects": {"dmg_mult": 4.5, "magic": True, "ignore_mdef": True},
        },
    },
    # ── Tireur (Combo) ─────────────────────────────────────────────────────────
    "tireur": {
        "resource": "combo",
        "resource_max": 5,
        "resource_per_turn": 1,
        "resource_on_hit": 0,
        "s1": {
            "name": "Tir Rapide",
            "emoji": "🏹",
            "description": "Inflige ×1.2 dégâts physiques et augmente sa vitesse de +30% pendant 2 tours.",
            "cost": 1, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.2, "stat_buff": {"speed": 30}, "buff_turns": 2},
        },
        "s2": {
            "name": "Tir Marqué",
            "emoji": "🎯",
            "description": "Inflige ×1.0 dégâts et marque l'ennemi — il subit +20% dégâts pendant 3 tours.",
            "cost": 2, "cooldown": 3, "min_turn": 1, "type": "debuff", "is_ultimate": False,
            "effects": {"dmg_mult": 1.0, "mark_enemy": True, "mark_dmg_bonus_pct": 20, "mark_turns": 3},
        },
        "ultimate": {
            "name": "Tir Fatal",
            "emoji": "💥",
            "description": "Inflige ×3.5 dégâts physiques en ignorant toute la Déf.Phy. ennemie.",
            "cost": 5, "cooldown": 6, "min_turn": 3, "type": "damage", "is_ultimate": True,
            "effects": {"dmg_mult": 3.5, "pen_pct": 1.0},
        },
    },
    # ── Support (Mana) ─────────────────────────────────────────────────────────
    "support": {
        "resource": "mana",
        "resource_max": 100,
        "resource_per_turn": 12,
        "resource_on_hit": 0,
        "s1": {
            "name": "Frappe Régénérante",
            "emoji": "💚",
            "description": "Inflige ×0.7 dégâts physiques et magiques combinés, puis se soigne de 15% des PV max.",
            "cost": 15, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 0.7, "dual_type": True, "heal_pct": 0.15},
        },
        "s2": {
            "name": "Frappe d'Affaiblissement",
            "emoji": "💫",
            "description": "Inflige ×0.8 dégâts (physiques + magiques) et réduit les dégâts ennemis de 20% pendant 2 tours.",
            "cost": 20, "cooldown": 3, "min_turn": 1, "type": "debuff", "is_ultimate": False,
            "effects": {"dmg_mult": 0.8, "dual_type": True, "damage_reduction": 0.20, "dmg_reduction_turns": 2},
        },
        "ultimate": {
            "name": "Renvoi Sacré",
            "emoji": "🌟",
            "description": "Bouclier 3 tours : renvoie 25% des dégâts reçus à l'ennemi et réduit 25% des dégâts restants.",
            "cost": 80, "cooldown": 7, "min_turn": 3, "type": "utility", "is_ultimate": True,
            "effects": {"reflect_pct": 0.25, "reflect_turns": 3, "damage_reduction": 0.25, "dmg_reduction_turns": 3},
        },
    },
    # ── Vampire (Rage) ─────────────────────────────────────────────────────────
    "vampire": {
        "resource": "rage",
        "resource_max": 100,
        "resource_per_turn": 10,
        "resource_on_hit": 5,
        "s1": {
            "name": "Morsure",
            "emoji": "🦷",
            "description": "Inflige ×1.5 dégâts physiques et récupère 40% des dégâts infligés en PV.",
            "cost": 20, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.5, "lifesteal": 0.40},
        },
        "s2": {
            "name": "Marque de Sang",
            "emoji": "🩸",
            "description": "Sacrifie 15% de ses PV, inflige ×2.0 dégâts et applique Marque de Sang 3 tours (50% vol de vie).",
            "cost": 30, "cooldown": 4, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 2.0, "self_damage_pct": 0.15, "blood_mark": True, "blood_mark_turns": 3, "blood_mark_heal_pct": 0.50},
        },
        "ultimate": {
            "name": "Festin Sanglant",
            "emoji": "💀",
            "description": "Inflige ×3.0 dégâts + stun 1 tour. Si Marque de Sang active : dégâts ×3.5 à la place.",
            "cost": 80, "cooldown": 7, "min_turn": 3, "type": "damage", "is_ultimate": True,
            "effects": {"blood_mark_ultime": True, "base_mult": 3.0, "bonus_mult": 3.5, "stun_after": 1},
        },
    },
    # ── Gardien du Temps (Combo) ───────────────────────────────────────────────
    "gardien_du_temps": {
        "resource": "combo",
        "resource_max": 5,
        "resource_per_turn": 1,
        "resource_on_hit": 0,
        "s1": {
            "name": "Accélération Temporelle",
            "emoji": "⚡",
            "description": "Inflige ×1.2 dégâts et augmente sa vitesse de +35% pendant 2 tours.",
            "cost": 1, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.2, "stat_buff": {"speed": 35}, "buff_turns": 2},
        },
        "s2": {
            "name": "Fissure du Temps",
            "emoji": "⏳",
            "description": "Inflige ×1.3 dégâts et réduit la Déf.Phy. et Mag. ennemie de 20% pendant 2 tours.",
            "cost": 2, "cooldown": 3, "min_turn": 1, "type": "debuff", "is_ultimate": False,
            "effects": {"dmg_mult": 1.3, "stat_debuff": {"p_def": 20, "m_def": 20}, "buff_turns": 2},
        },
        "ultimate": {
            "name": "Arrêt du Temps",
            "emoji": "⏱️",
            "description": "Étourdit l'ennemi pendant 2 tours — il ne peut pas agir.",
            "cost": 5, "cooldown": 7, "min_turn": 3, "type": "utility", "is_ultimate": True,
            "effects": {"stun": 2},
        },
    },
    # ── Ombre Venin (Mana) ─────────────────────────────────────────────────────
    "ombre_venin": {
        "resource": "combo",
        "resource_max": 5,
        "resource_per_turn": 0,
        "resource_on_hit": 1,
        "s1": {
            "name": "Injection",
            "emoji": "☠️",
            "description": "Inflige ×1.0 dégâts magiques et applique 2 stacks de poison (+12% dégâts par stack).",
            "cost": 1, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.0, "dot": "poison", "dot_stacks": 2},
        },
        "s2": {
            "name": "Brume Toxique",
            "emoji": "💨",
            "description": "Inflige ×0.8 dégâts magiques, applique 3 stacks de poison et réduit la Déf. Mag. ennemie de 20% pendant 2 tours.",
            "cost": 2, "cooldown": 3, "min_turn": 1, "type": "debuff", "is_ultimate": False,
            "effects": {"dmg_mult": 0.8, "dot": "poison", "dot_stacks": 3, "stat_debuff": {"m_def": 20}, "buff_turns": 2},
        },
        "ultimate": {
            "name": "Nécrose",
            "emoji": "💀",
            "description": "Inflige ×2.5 dégâts magiques + ×1.5 ATK Mag par stack de poison. Consomme tous les stacks.",
            "cost": 5, "cooldown": 7, "min_turn": 3, "type": "damage", "is_ultimate": True,
            "effects": {"dmg_mult": 2.5, "explode_dots": True, "explode_mult": 1.5},
        },
    },
    # ── Pyromancien (Mana) ─────────────────────────────────────────────────────
    "pyromancien": {
        "resource": "mana",
        "resource_max": 100,
        "resource_per_turn": 15,
        "resource_on_hit": 0,
        "s1": {
            "name": "Flammèche",
            "emoji": "🔥",
            "description": "Inflige ×0.8 dégâts magiques et applique 1 stack de brûlure.",
            "cost": 15, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 0.8, "magic": True, "dot": "burn", "dot_stacks": 1},
        },
        "s2": {
            "name": "Brasier",
            "emoji": "💥",
            "description": "Réduit la Déf.Mag. ennemie de 20% (2 tours), inflige ×1.0 dégâts magiques et applique 2 stacks de brûlure.",
            "cost": 25, "cooldown": 3, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.0, "magic": True, "dot": "burn", "dot_stacks": 2, "stat_debuff": {"m_def": 20}, "buff_turns": 2},
        },
        "ultimate": {
            "name": "Inferno",
            "emoji": "🌋",
            "description": "Inflige ×3.0 dégâts magiques + 0.7×ATK Mag par stack. Bonus ×1.5 sur le bonus brûlure si ≥5 stacks actifs.",
            "cost": 80, "cooldown": 7, "min_turn": 3, "type": "damage", "is_ultimate": True,
            "effects": {"dmg_mult": 3.0, "magic": True, "bonus_per_burn": 0.7, "burn_threshold_mult": 1.5, "burn_threshold": 5},
        },
    },
    # ── Paladin (Rage) ─────────────────────────────────────────────────────────
    "paladin": {
        "resource": "rage",
        "resource_max": 100,
        "resource_per_turn": 10,
        "resource_on_hit": 5,
        "s1": {
            "name": "Frappe Sacrée",
            "emoji": "✝️",
            "description": "Inflige ×1.3 dégâts physiques et génère un bouclier égal à 15% des PV max.",
            "cost": 20, "cooldown": 0, "min_turn": 1, "type": "damage", "is_ultimate": False,
            "effects": {"dmg_mult": 1.3, "shield_pct": 0.15},
        },
        "s2": {
            "name": "Pénitence",
            "emoji": "⚖️",
            "description": "Réduit sa vitesse de -30% mais augmente ATK Phy, Déf Phy+Mag, Pén Phy de +20% pendant 2 tours.",
            "cost": 30, "cooldown": 4, "min_turn": 1, "type": "buff", "is_ultimate": False,
            "effects": {"stat_buff": {"speed": -30, "p_atk": 20, "p_def": 20, "m_def": 20, "p_pen": 20}, "buff_turns": 2},
        },
        "ultimate": {
            "name": "Châtiment Divin",
            "emoji": "⚡",
            "description": "Inflige des dégâts égaux à la somme de toutes ses stats de combat (ignore la défense).",
            "cost": 80, "cooldown": 7, "min_turn": 3, "type": "damage", "is_ultimate": True,
            "effects": {"all_stats_damage": True},
        },
    },
}

def compute_relic_effects(relics: list[dict]) -> dict:
    """
    Calcule les effets globaux des reliques avec diminishing returns.
    Chaque copie supplémentaire de la même rareté apporte 5% de moins
    (1ère=100%, 2ème=95%, 3ème=90%, ...).
    Des plafonds (RELIC_CAPS) empêchent les effets de casser le jeu.
    """
    rarity_counts: dict[str, int] = {}
    effect_totals: dict[str, float] = {}

    for relic in relics:
        relic_id = relic["relic_id"]
        relic_data = RELICS.get(relic_id)
        if not relic_data:
            continue
        count = rarity_counts.get(relic_id, 0)
        # -5% d'efficacité par copie supplémentaire de la même rareté
        effectiveness = max(0.0, 1.0 - 0.05 * count)
        rarity_counts[relic_id] = count + 1

        for effect, value in relic_data["effects"].items():
            effect_totals[effect] = effect_totals.get(effect, 0) + value * effectiveness

    # Appliquer les plafonds
    for effect, cap in RELIC_CAPS.items():
        if effect in effect_totals:
            effect_totals[effect] = min(effect_totals[effect], cap)

    return effect_totals


# ─── Titres ────────────────────────────────────────────────────────────────
# Structure : name, cat, req, req_type, bonus_type, bonus_value, reward_gold
# bonus_type peut être None (cosmétique PvP), ou un des types ci-dessous :
#   xp_pct, prestige_bonus_pct, gold_pct, monde_loot_pct,
#   djc_stats_pct, dje_stats_pct, dja_stats_pct, raid_stats_pct, wb_stats_pct,
#   met_xp_pct (nécessite champ "metier"), hdv_discount_pct
TITLES: dict[str, dict] = {
    # ── Global — Niveau (×10 → +50% XP global cumulé) ────────────────────────
    "t_niv_100":  {"name": "L'Éveillé",          "cat": "global", "req": 100,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 500},
    "t_niv_200":  {"name": "L'Expérimenté",       "cat": "global", "req": 200,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 1000},
    "t_niv_300":  {"name": "L'Aguerri",           "cat": "global", "req": 300,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 2000},
    "t_niv_400":  {"name": "Le Valeureux",        "cat": "global", "req": 400,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 3000},
    "t_niv_500":  {"name": "L'Intrépide",         "cat": "global", "req": 500,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 5000},
    "t_niv_600":  {"name": "Le Téméraire",        "cat": "global", "req": 600,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 8000},
    "t_niv_700":  {"name": "L'Illustre",          "cat": "global", "req": 700,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 12000},
    "t_niv_800":  {"name": "Le Mythique",         "cat": "global", "req": 800,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 18000},
    "t_niv_900":  {"name": "L'Éternel",           "cat": "global", "req": 900,  "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 25000},
    "t_niv_1000": {"name": "Le Transcendant",     "cat": "global", "req": 1000, "req_type": "level", "bonus_type": "xp_pct", "bonus_value": 5,  "reward_gold": 50000},
    # ── Global — Prestige (×10 → bonus prestige ×2 au prestige 1000) ─────────
    "t_pres_100":  {"name": "L'Honoré",           "cat": "global", "req": 100,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 2000},
    "t_pres_200":  {"name": "Le Respecté",        "cat": "global", "req": 200,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 5000},
    "t_pres_300":  {"name": "L'Éminent",          "cat": "global", "req": 300,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 10000},
    "t_pres_400":  {"name": "Le Distingué",       "cat": "global", "req": 400,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 20000},
    "t_pres_500":  {"name": "Le Glorieux",        "cat": "global", "req": 500,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 35000},
    "t_pres_600":  {"name": "L'Exalté",           "cat": "global", "req": 600,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 50000},
    "t_pres_700":  {"name": "Le Vénéré",          "cat": "global", "req": 700,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 75000},
    "t_pres_800":  {"name": "Le Sacré",           "cat": "global", "req": 800,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 100000},
    "t_pres_900":  {"name": "L'Ascendant",        "cat": "global", "req": 900,  "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 150000},
    "t_pres_1000": {"name": "Le Divin",           "cat": "global", "req": 1000, "req_type": "prestige", "bonus_type": "prestige_bonus_pct", "bonus_value": 10, "reward_gold": 250000},
    # ── Global — Gold (×10 → +30% gold global cumulé) ────────────────────────
    "t_gold_1":  {"name": "Le Débrouillard",      "cat": "global", "req": 10_000,        "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 500},
    "t_gold_2":  {"name": "L'Économe",            "cat": "global", "req": 50_000,        "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 1000},
    "t_gold_3":  {"name": "Le Négociant",         "cat": "global", "req": 200_000,       "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 2000},
    "t_gold_4":  {"name": "L'Opulent",            "cat": "global", "req": 500_000,       "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 5000},
    "t_gold_5":  {"name": "Le Prospère",          "cat": "global", "req": 1_000_000,     "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 10000},
    "t_gold_6":  {"name": "Le Fortuné",           "cat": "global", "req": 5_000_000,     "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 25000},
    "t_gold_7":  {"name": "Le Magnat",            "cat": "global", "req": 10_000_000,    "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 50000},
    "t_gold_8":  {"name": "Le Ploutocrate",       "cat": "global", "req": 50_000_000,    "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 100000},
    "t_gold_9":  {"name": "Le Milliardaire",      "cat": "global", "req": 100_000_000,   "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 200000},
    "t_gold_10": {"name": "Le Seigneur de l'Or",  "cat": "global", "req": 1_000_000_000, "req_type": "total_gold", "bonus_type": "gold_pct", "bonus_value": 3, "reward_gold": 500000},
    # ── Monde — Zone (×10 → +20% loot chance cumulé) ─────────────────────────
    "t_zone_1000":  {"name": "L'Explorateur",            "cat": "monde", "req": 1000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 1000},
    "t_zone_2000":  {"name": "L'Aventurier du Monde",    "cat": "monde", "req": 2000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 3000},
    "t_zone_3000":  {"name": "Le Conquérant",            "cat": "monde", "req": 3000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 6000},
    "t_zone_4000":  {"name": "L'Intrépide Voyageur",     "cat": "monde", "req": 4000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 10000},
    "t_zone_5000":  {"name": "Le Maître du Monde",       "cat": "monde", "req": 5000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 20000},
    "t_zone_6000":  {"name": "Le Ravageur des Terres",   "cat": "monde", "req": 6000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 35000},
    "t_zone_7000":  {"name": "Le Dévastateur des Zones", "cat": "monde", "req": 7000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 55000},
    "t_zone_8000":  {"name": "Le Fléau du Monde",        "cat": "monde", "req": 8000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 80000},
    "t_zone_9000":  {"name": "L'Éternel Marcheur",       "cat": "monde", "req": 9000,  "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 120000},
    "t_zone_10000": {"name": "Le Chromate Vivant",       "cat": "monde", "req": 10000, "req_type": "zone", "bonus_type": "monde_loot_pct", "bonus_value": 2, "reward_gold": 200000},
    # ── Donjons — Classiques (×10 → +50% stats donjons classiques) ───────────
    "t_djc_1":  {"name": "Le Plongeur",              "cat": "donjons", "req": 10,   "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 500},
    "t_djc_2":  {"name": "L'Infiltrateur",           "cat": "donjons", "req": 25,   "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 1000},
    "t_djc_3":  {"name": "Le Fouilleur",             "cat": "donjons", "req": 50,   "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 2000},
    "t_djc_4":  {"name": "Le Vétéran des Donjons",  "cat": "donjons", "req": 100,  "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 4000},
    "t_djc_5":  {"name": "L'Expert des Gouffres",   "cat": "donjons", "req": 200,  "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 8000},
    "t_djc_6":  {"name": "Le Maître des Donjons",   "cat": "donjons", "req": 300,  "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 15000},
    "t_djc_7":  {"name": "L'Ancien des Cryptes",    "cat": "donjons", "req": 500,  "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 25000},
    "t_djc_8":  {"name": "Le Champion des Abîmes",  "cat": "donjons", "req": 750,  "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 40000},
    "t_djc_9":  {"name": "La Légende des Donjons",  "cat": "donjons", "req": 1000, "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 60000},
    "t_djc_10": {"name": "Le Seigneur des Cryptes", "cat": "donjons", "req": 2000, "req_type": "dungeon_clears", "bonus_type": "djc_stats_pct", "bonus_value": 5, "reward_gold": 100000},
    # ── Donjons — Élites (×10 → +50% stats donjons élites) ───────────────────
    "t_dje_1":  {"name": "L'Initié d'Élite",           "cat": "donjons", "req": 5,    "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 1000},
    "t_dje_2":  {"name": "Le Combattant Élite",        "cat": "donjons", "req": 15,   "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 2500},
    "t_dje_3":  {"name": "L'Assaillant des Hauts Lieux","cat": "donjons","req": 30,   "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 5000},
    "t_dje_4":  {"name": "Le Chasseur d'Élite",        "cat": "donjons", "req": 60,   "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 10000},
    "t_dje_5":  {"name": "Le Vainqueur d'Élite",       "cat": "donjons", "req": 100,  "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 20000},
    "t_dje_6":  {"name": "L'Expert des Hauts Faits",   "cat": "donjons", "req": 200,  "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 35000},
    "t_dje_7":  {"name": "Le Maître d'Élite",          "cat": "donjons", "req": 300,  "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 55000},
    "t_dje_8":  {"name": "Le Conquérant d'Élite",      "cat": "donjons", "req": 500,  "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 80000},
    "t_dje_9":  {"name": "La Terreur Élite",           "cat": "donjons", "req": 750,  "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 120000},
    "t_dje_10": {"name": "Le Seigneur d'Élite",        "cat": "donjons", "req": 1000, "req_type": "elite_clears", "bonus_type": "dje_stats_pct", "bonus_value": 5, "reward_gold": 200000},
    # ── Donjons — Abyssaux (×10 → +50% stats donjons abyssaux) ──────────────
    "t_dja_1":  {"name": "L'Abyssal Débutant",         "cat": "donjons", "req": 1,    "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 2000},
    "t_dja_2":  {"name": "L'Explorateur des Abysses",  "cat": "donjons", "req": 5,    "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 5000},
    "t_dja_3":  {"name": "Le Plongeur des Abysses",    "cat": "donjons", "req": 10,   "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 10000},
    "t_dja_4":  {"name": "Le Chasseur d'Abysses",      "cat": "donjons", "req": 25,   "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 20000},
    "t_dja_5":  {"name": "Le Vétéran des Abysses",     "cat": "donjons", "req": 50,   "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 35000},
    "t_dja_6":  {"name": "L'Expert Abyssal",           "cat": "donjons", "req": 100,  "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 60000},
    "t_dja_7":  {"name": "Le Maître des Abysses",      "cat": "donjons", "req": 200,  "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 100000},
    "t_dja_8":  {"name": "L'Élu des Profondeurs",      "cat": "donjons", "req": 300,  "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 150000},
    "t_dja_9":  {"name": "La Terreur Abyssale",        "cat": "donjons", "req": 500,  "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 225000},
    "t_dja_10": {"name": "Le Seigneur des Abysses",    "cat": "donjons", "req": 1000, "req_type": "abyssal_clears", "bonus_type": "dja_stats_pct", "bonus_value": 5, "reward_gold": 350000},
    # ── Raids (×10 → +50% stats raids) ───────────────────────────────────────
    "t_raid_1":  {"name": "Le Raider Débutant",     "cat": "raids", "req": 1,    "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 1000},
    "t_raid_2":  {"name": "L'Assaillant de Raid",   "cat": "raids", "req": 5,    "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 3000},
    "t_raid_3":  {"name": "Le Combattant de Raid",  "cat": "raids", "req": 10,   "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 7000},
    "t_raid_4":  {"name": "Le Vétéran de Raid",     "cat": "raids", "req": 25,   "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 15000},
    "t_raid_5":  {"name": "L'Expert de Raid",       "cat": "raids", "req": 50,   "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 30000},
    "t_raid_6":  {"name": "Le Maître de Raid",      "cat": "raids", "req": 100,  "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 60000},
    "t_raid_7":  {"name": "La Terreur des Raids",   "cat": "raids", "req": 200,  "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 100000},
    "t_raid_8":  {"name": "L'Impitoyable",          "cat": "raids", "req": 300,  "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 150000},
    "t_raid_9":  {"name": "La Légende du Raid",     "cat": "raids", "req": 500,  "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 225000},
    "t_raid_10": {"name": "Le Seigneur des Raids",  "cat": "raids", "req": 1000, "req_type": "raid_clears", "bonus_type": "raid_stats_pct", "bonus_value": 5, "reward_gold": 400000},
    # ── World Boss — Dégâts (×10 → +30% stats WB) ────────────────────────────
    "t_wbd_1":  {"name": "Le Piquant",              "cat": "wb", "req": 10_000,        "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 500},
    "t_wbd_2":  {"name": "Le Blesseur",             "cat": "wb", "req": 50_000,        "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 1500},
    "t_wbd_3":  {"name": "Le Maraudeur",            "cat": "wb", "req": 200_000,       "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 4000},
    "t_wbd_4":  {"name": "Le Dévastateur",          "cat": "wb", "req": 500_000,       "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 10000},
    "t_wbd_5":  {"name": "L'Exterminateur",         "cat": "wb", "req": 1_000_000,     "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 20000},
    "t_wbd_6":  {"name": "Le Ravageur",             "cat": "wb", "req": 5_000_000,     "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 50000},
    "t_wbd_7":  {"name": "La Calamité",             "cat": "wb", "req": 10_000_000,    "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 100000},
    "t_wbd_8":  {"name": "Le Fléau du Boss",        "cat": "wb", "req": 50_000_000,    "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 200000},
    "t_wbd_9":  {"name": "L'Annihilateur",          "cat": "wb", "req": 100_000_000,   "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 350000},
    "t_wbd_10": {"name": "Le Destructeur Suprême",  "cat": "wb", "req": 1_000_000_000, "req_type": "wb_total_damage", "bonus_type": "wb_stats_pct", "bonus_value": 3, "reward_gold": 600000},
    # ── World Boss — Attaques (×10 → +20% stats WB) ───────────────────────────
    "t_wba_1":  {"name": "Le Challenger",           "cat": "wb", "req": 10,   "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 300},
    "t_wba_2":  {"name": "Le Combattant de Boss",   "cat": "wb", "req": 25,   "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 800},
    "t_wba_3":  {"name": "L'Assaillant Persistant", "cat": "wb", "req": 50,   "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 2000},
    "t_wba_4":  {"name": "Le Guerrier du Boss",     "cat": "wb", "req": 100,  "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 5000},
    "t_wba_5":  {"name": "Le Vétéran du Boss",      "cat": "wb", "req": 200,  "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 12000},
    "t_wba_6":  {"name": "Le Destructeur",          "cat": "wb", "req": 300,  "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 25000},
    "t_wba_7":  {"name": "La Terreur du Boss",      "cat": "wb", "req": 500,  "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 50000},
    "t_wba_8":  {"name": "L'Implacable",            "cat": "wb", "req": 750,  "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 90000},
    "t_wba_9":  {"name": "Le Fléau Suprême",        "cat": "wb", "req": 1000, "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 140000},
    "t_wba_10": {"name": "L'Éternel Assaillant",    "cat": "wb", "req": 2000, "req_type": "wb_attacks", "bonus_type": "wb_stats_pct", "bonus_value": 2, "reward_gold": 250000},
    # ── World Boss — Rang #1 (+10% stats WB) ──────────────────────────────────
    "t_wb_rank1": {"name": "Champion du Boss",      "cat": "wb", "req": 1, "req_type": "wb_rank1", "bonus_type": "wb_stats_pct", "bonus_value": 10, "reward_gold": 10000},
    # ── Métiers — Récolte (harvest_level, ×10 → +50% XP récolte) ────────────
    "t_met_rec_1":  {"name": "Apprenti Récolteur",       "cat": "metiers", "req": 10,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 200},
    "t_met_rec_2":  {"name": "Récolteur Confirmé",       "cat": "metiers", "req": 20,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 400},
    "t_met_rec_3":  {"name": "Récolteur Expérimenté",    "cat": "metiers", "req": 30,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 700},
    "t_met_rec_4":  {"name": "Récolteur Aguerri",        "cat": "metiers", "req": 40,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 1100},
    "t_met_rec_5":  {"name": "Récolteur Chevronné",      "cat": "metiers", "req": 50,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 1600},
    "t_met_rec_6":  {"name": "Expert Récolteur",         "cat": "metiers", "req": 60,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 2200},
    "t_met_rec_7":  {"name": "Maître Récolteur",         "cat": "metiers", "req": 70,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 3000},
    "t_met_rec_8":  {"name": "Grand Maître Récolteur",   "cat": "metiers", "req": 80,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 4000},
    "t_met_rec_9":  {"name": "Légende de la Récolte",    "cat": "metiers", "req": 90,  "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 5500},
    "t_met_rec_10": {"name": "Seigneur des Ressources",  "cat": "metiers", "req": 100, "req_type": "harvest_level", "bonus_type": "harvest_xp_pct", "bonus_value": 5, "reward_gold": 7500},
    # ── Métiers — Artisanat (craft_level, ×10 → +50% XP artisanat) ──────────
    "t_met_cra_1":  {"name": "Apprenti Artisan",         "cat": "metiers", "req": 10,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 200},
    "t_met_cra_2":  {"name": "Artisan Confirmé",         "cat": "metiers", "req": 20,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 400},
    "t_met_cra_3":  {"name": "Artisan Expérimenté",      "cat": "metiers", "req": 30,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 700},
    "t_met_cra_4":  {"name": "Artisan Aguerri",          "cat": "metiers", "req": 40,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 1100},
    "t_met_cra_5":  {"name": "Artisan Chevronné",        "cat": "metiers", "req": 50,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 1600},
    "t_met_cra_6":  {"name": "Expert Artisan",           "cat": "metiers", "req": 60,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 2200},
    "t_met_cra_7":  {"name": "Maître Artisan",           "cat": "metiers", "req": 70,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 3000},
    "t_met_cra_8":  {"name": "Grand Maître Artisan",     "cat": "metiers", "req": 80,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 4000},
    "t_met_cra_9":  {"name": "Légende de l'Artisanat",   "cat": "metiers", "req": 90,  "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 5500},
    "t_met_cra_10": {"name": "Seigneur du Forge",        "cat": "metiers", "req": 100, "req_type": "craft_level", "bonus_type": "craft_xp_pct", "bonus_value": 5, "reward_gold": 7500},
    # ── Métiers — Conception (conception_level, ×10 → +50% XP conception) ───
    "t_met_con_1":  {"name": "Apprenti Concepteur",      "cat": "metiers", "req": 10,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 200},
    "t_met_con_2":  {"name": "Concepteur Confirmé",      "cat": "metiers", "req": 20,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 400},
    "t_met_con_3":  {"name": "Concepteur Expérimenté",   "cat": "metiers", "req": 30,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 700},
    "t_met_con_4":  {"name": "Concepteur Aguerri",       "cat": "metiers", "req": 40,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 1100},
    "t_met_con_5":  {"name": "Concepteur Chevronné",     "cat": "metiers", "req": 50,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 1600},
    "t_met_con_6":  {"name": "Expert Concepteur",        "cat": "metiers", "req": 60,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 2200},
    "t_met_con_7":  {"name": "Maître Concepteur",        "cat": "metiers", "req": 70,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 3000},
    "t_met_con_8":  {"name": "Grand Maître Concepteur",  "cat": "metiers", "req": 80,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 4000},
    "t_met_con_9":  {"name": "Légende de la Conception", "cat": "metiers", "req": 90,  "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 5500},
    "t_met_con_10": {"name": "Seigneur des Créations",   "cat": "metiers", "req": 100, "req_type": "conception_level", "bonus_type": "conception_xp_pct", "bonus_value": 5, "reward_gold": 7500},
    # ── HDV (×10 → commission 5% → 1%) ───────────────────────────────────────
    "t_hdv_1":  {"name": "Le Petit Commerçant",      "cat": "hdv", "req": 10,   "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 300},
    "t_hdv_2":  {"name": "Le Vendeur Régulier",      "cat": "hdv", "req": 25,   "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 700},
    "t_hdv_3":  {"name": "Le Marchand Actif",        "cat": "hdv", "req": 50,   "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 1500},
    "t_hdv_4":  {"name": "Le Commerçant Établi",     "cat": "hdv", "req": 100,  "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 3000},
    "t_hdv_5":  {"name": "Le Négociant Expérimenté", "cat": "hdv", "req": 200,  "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 6000},
    "t_hdv_6":  {"name": "Le Marchand Prospère",     "cat": "hdv", "req": 300,  "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 10000},
    "t_hdv_7":  {"name": "L'Expert du Commerce",     "cat": "hdv", "req": 500,  "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 17000},
    "t_hdv_8":  {"name": "Le Maître Marchand",       "cat": "hdv", "req": 750,  "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 27000},
    "t_hdv_9":  {"name": "Le Grand Commerçant",      "cat": "hdv", "req": 1000, "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 40000},
    "t_hdv_10": {"name": "Le Seigneur du Marché",    "cat": "hdv", "req": 2000, "req_type": "market_sales", "bonus_type": "hdv_discount_pct", "bonus_value": 0.4, "reward_gold": 60000},
    # ── PvP — cosmétiques (aucun bonus) ──────────────────────────────────────
    "t_pvpw_1": {"name": "Battant",                  "cat": "pvp", "req": 10,   "req_type": "pvp_wins", "bonus_type": None, "bonus_value": 0, "reward_gold": 300},
    "t_pvpw_2": {"name": "L'Indomptable",            "cat": "pvp", "req": 50,   "req_type": "pvp_wins", "bonus_type": None, "bonus_value": 0, "reward_gold": 1000},
    "t_pvpw_3": {"name": "Le Dévastateur",           "cat": "pvp", "req": 100,  "req_type": "pvp_wins", "bonus_type": None, "bonus_value": 0, "reward_gold": 3000},
    "t_pvpw_4": {"name": "L'Implacable",             "cat": "pvp", "req": 200,  "req_type": "pvp_wins", "bonus_type": None, "bonus_value": 0, "reward_gold": 8000},
    "t_pvpw_5": {"name": "Le Fléau des Arènes",      "cat": "pvp", "req": 500,  "req_type": "pvp_wins", "bonus_type": None, "bonus_value": 0, "reward_gold": 20000},
    "t_pvpw_6": {"name": "L'Élu du Combat",          "cat": "pvp", "req": 1000, "req_type": "pvp_wins", "bonus_type": None, "bonus_value": 0, "reward_gold": 75000},
    "t_pvpe_1": {"name": "Fer Trempé",               "cat": "pvp", "req": 1000, "req_type": "pvp_elo",  "bonus_type": None, "bonus_value": 0, "reward_gold": 500},
    "t_pvpe_2": {"name": "Diamant",                  "cat": "pvp", "req": 1200, "req_type": "pvp_elo",  "bonus_type": None, "bonus_value": 0, "reward_gold": 2000},
    "t_pvpe_3": {"name": "Maître",                   "cat": "pvp", "req": 1500, "req_type": "pvp_elo",  "bonus_type": None, "bonus_value": 0, "reward_gold": 8000},
    "t_pvpe_4": {"name": "Grand Maître",             "cat": "pvp", "req": 2000, "req_type": "pvp_elo",  "bonus_type": None, "bonus_value": 0, "reward_gold": 25000},
    "t_pvpe_5": {"name": "Challenger Suprême",       "cat": "pvp", "req": 2500, "req_type": "pvp_elo",  "bonus_type": None, "bonus_value": 0, "reward_gold": 80000},
    # ── Spéciaux — cosmétiques pur, noms de prestige, aucun bonus ────────────
    # Obtenus en atteignant le seuil maximum d'une catégorie ou un exploit unique.
    "t_spec_niv_max":     {"name": "L'Être au-Delà",              "cat": "special", "req": 1000,          "req_type": "level",          "bonus_type": None, "bonus_value": 0, "reward_gold": 100_000},
    "t_spec_pres_max":    {"name": "L'Absolu",                    "cat": "special", "req": 1000,          "req_type": "prestige",       "bonus_type": None, "bonus_value": 0, "reward_gold": 500_000},
    "t_spec_zone_max":    {"name": "Maître des Dix Mille Mondes", "cat": "special", "req": 10_000,        "req_type": "zone",           "bonus_type": None, "bonus_value": 0, "reward_gold": 250_000},
    "t_spec_djc_max":     {"name": "L'Éternel du Gouffre",        "cat": "special", "req": 2000,          "req_type": "dungeon_clears", "bonus_type": None, "bonus_value": 0, "reward_gold": 200_000},
    "t_spec_dje_max":     {"name": "Seigneur des Hauts Faits",    "cat": "special", "req": 1000,          "req_type": "elite_clears",   "bonus_type": None, "bonus_value": 0, "reward_gold": 300_000},
    "t_spec_dja_max":     {"name": "L'Abyssal Immortel",          "cat": "special", "req": 1000,          "req_type": "abyssal_clears", "bonus_type": None, "bonus_value": 0, "reward_gold": 500_000},
    "t_spec_raid_max":    {"name": "Dieu des Légions",            "cat": "special", "req": 1000,          "req_type": "raid_clears",    "bonus_type": None, "bonus_value": 0, "reward_gold": 500_000},
    "t_spec_wb_max":      {"name": "Le Destructeur Primordial",   "cat": "special", "req": 1_000_000_000, "req_type": "wb_total_damage","bonus_type": None, "bonus_value": 0, "reward_gold": 750_000},
    "t_spec_gold_max":    {"name": "Le Maître des Richesses",     "cat": "special", "req": 1_000_000_000, "req_type": "total_gold",     "bonus_type": None, "bonus_value": 0, "reward_gold": 500_000},
    "t_spec_global_top1": {"name": "Légende Vivante",             "cat": "special", "req": 1,             "req_type": "global_rank1",   "bonus_type": None, "bonus_value": 0, "reward_gold": 50_000},
    "t_spec_pvp_top1":    {"name": "L'Intouchable",               "cat": "special", "req": 1,             "req_type": "pvp_rank1",      "bonus_type": None, "bonus_value": 0, "reward_gold": 50_000},
    "t_spec_wb_top1":     {"name": "Tueur de Titans",             "cat": "special", "req": 1,             "req_type": "wb_rank1",       "bonus_type": None, "bonus_value": 0, "reward_gold": 50_000},
}

TITLE_CATEGORIES = {
    "global":   "🌍 Global",
    "monde":    "⚔️ Monde",
    "donjons":  "🏰 Donjons",
    "raids":    "👥 Raids",
    "wb":       "🐉 World Boss",
    "pvp":      "🥊 PvP",
    "metiers":  "🔨 Métiers",
    "hdv":      "🏪 Hôtel des Ventes",
    "special":  "⭐ Spéciaux",
}

# ─── Affichage joueur ───────────────────────────────────────────────────────

STAT_FR: dict[str, str] = {
    "hp":           "Points de Vie",
    "p_atk":        "Attaque Physique",
    "m_atk":        "Attaque Magique",
    "p_def":        "Défense Physique",
    "m_def":        "Défense Magique",
    "p_pen":        "Pénétration Physique",
    "m_pen":        "Pénétration Magique",
    "speed":        "Vitesse",
    "crit_chance":  "Chance Critique",
    "crit_damage":  "Dégâts Critiques",
    "all_stats":    "Toutes les Stats",
    "energy":       "Énergie",
    "p_atk_pct":    "Attaque Physique",
    "m_atk_pct":    "Attaque Magique",
    "def_pct":      "Défense",
    "speed_pct":    "Vitesse",
    "crit_pct":     "Chance Critique",
    "all_pct":      "Toutes les Stats",
    "heal_pct":     "Soin",
}

STAT_EMOJI: dict[str, str] = {
    "hp":           "❤️",
    "p_atk":        "⚔️",
    "m_atk":        "🔮",
    "p_def":        "🛡️",
    "m_def":        "🔷",
    "p_pen":        "🗡️",
    "m_pen":        "💫",
    "speed":        "⚡",
    "crit_chance":  "🎯",
    "crit_damage":  "💥",
    "all_stats":    "✨",
    "energy":       "⚡",
    "p_atk_pct":    "⚔️",
    "m_atk_pct":    "🔮",
    "def_pct":      "🛡️",
    "speed_pct":    "⚡",
    "crit_pct":     "🎯",
    "all_pct":      "✨",
    "heal_pct":     "💚",
}

# Suffixes de palier : _p=T1, _m=T2, _g=T3, _tg=T4, _x=T5, _u=T6
_TIER_SUFFIX = {"_p": "T1", "_m": "T2", "_g": "T3", "_tg": "T4", "_x": "T5", "_u": "T6"}

def item_tier_label(item_id: str) -> str:
    """Retourne 'T1'…'T6' selon le suffixe de l'item, '' sinon."""
    for suffix, label in _TIER_SUFFIX.items():
        if item_id.endswith(suffix):
            return label
    return ""

def stat_display(key: str, value, unit: str = "") -> str:
    """Ex: stat_display('p_atk', 120) → '⚔️ Attaque Physique : +120'"""
    emoji = STAT_EMOJI.get(key, "")
    name  = STAT_FR.get(key, key)
    val_str = f"+{value}{unit}" if isinstance(value, (int, float)) and value >= 0 else f"{value}{unit}"
    return f"{emoji} {name} : {val_str}"
