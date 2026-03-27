"""
Définitions des items : matériaux, équipements, consommables, recettes.
"""
from __future__ import annotations
from bot.cogs.rpg.models import (
    RARITIES, RARITY_MULT, CLASS_SLOT_STAT_FOCUS, SLOTS,
    ALL_CLASSES, CLASSES_STANDARD, CLASSES_PREMIUM,
    SOURCE_POWER_MULT, SLOT_PREFIX_BY_CLASS,
)

# ─── Matériaux ─────────────────────────────────────────────────────────────
# 50 matériaux : 10 par métier de récolte
MATERIALS: dict[str, dict] = {
    # MINEUR — 10 matériaux, tiers 1-10 (un par tier, débloqué tous les 10 niveaux de récolte)
    "mat_fer":          {"name": "Minerai de Fer",       "profession": "mineur",      "tier": 1,  "emoji": "🪨"},
    "mat_acier":        {"name": "Minerai d'Acier",      "profession": "mineur",      "tier": 2,  "emoji": "⛏️"},
    "mat_mithril":      {"name": "Minerai de Mithril",   "profession": "mineur",      "tier": 3,  "emoji": "💎"},
    "mat_adamantium":   {"name": "Adamantium Brut",      "profession": "mineur",      "tier": 4,  "emoji": "🔷"},
    "mat_pierre_feu":   {"name": "Pierre de Feu",        "profession": "mineur",      "tier": 5,  "emoji": "🔥"},
    "mat_pierre_glace": {"name": "Pierre de Glace",      "profession": "mineur",      "tier": 6,  "emoji": "❄️"},
    "mat_orichalque":   {"name": "Orichalque",           "profession": "mineur",      "tier": 7,  "emoji": "🟠"},
    "mat_pierre_foudre":{"name": "Pierre de Foudre",     "profession": "mineur",      "tier": 8,  "emoji": "⚡"},
    "mat_cristal_brut": {"name": "Cristal Brut",         "profession": "mineur",      "tier": 9,  "emoji": "🔮"},
    "mat_diamant_brut": {"name": "Diamant Brut",         "profession": "mineur",      "tier": 10, "emoji": "💠"},
    # BÛCHERON — 10 matériaux, tiers 1-10
    "mat_bois_chene":   {"name": "Bois de Chêne",        "profession": "bucheron",    "tier": 1,  "emoji": "🌳"},
    "mat_bois_sapin":   {"name": "Bois de Sapin",        "profession": "bucheron",    "tier": 2,  "emoji": "🌲"},
    "mat_bois_ebene":   {"name": "Bois d'Ébène",         "profession": "bucheron",    "tier": 3,  "emoji": "🪵"},
    "mat_bois_teck":    {"name": "Bois de Teck",         "profession": "bucheron",    "tier": 4,  "emoji": "🪵"},
    "mat_bois_cedre":   {"name": "Bois de Cèdre",        "profession": "bucheron",    "tier": 5,  "emoji": "🪵"},
    "mat_bois_enchante":{"name": "Bois Enchanté",        "profession": "bucheron",    "tier": 6,  "emoji": "✨"},
    "mat_bois_sang":    {"name": "Bois de Sang",         "profession": "bucheron",    "tier": 7,  "emoji": "🔴"},
    "mat_bois_lune":    {"name": "Bois de Lune",         "profession": "bucheron",    "tier": 8,  "emoji": "🌙"},
    "mat_bois_feu":     {"name": "Bois de Feu",          "profession": "bucheron",    "tier": 9,  "emoji": "🔥"},
    "mat_bois_dragon":  {"name": "Bois de Dragon",       "profession": "bucheron",    "tier": 10, "emoji": "🐉"},
    # HERBORISTE — 10 matériaux, tiers 1-10
    "mat_herbe_soin":   {"name": "Herbe de Soin",        "profession": "herboriste",  "tier": 1,  "emoji": "🌿"},
    "mat_herbe_mana":   {"name": "Herbe de Mana",        "profession": "herboriste",  "tier": 2,  "emoji": "💧"},
    "mat_racine_force": {"name": "Racine de Force",      "profession": "herboriste",  "tier": 3,  "emoji": "🌱"},
    "mat_fleur_lune":   {"name": "Fleur de Lune",        "profession": "herboriste",  "tier": 4,  "emoji": "🌸"},
    "mat_pollen_dore":  {"name": "Pollen Doré",          "profession": "herboriste",  "tier": 5,  "emoji": "🌼"},
    "mat_champi_venin": {"name": "Champignon Vénéneux",  "profession": "herboriste",  "tier": 6,  "emoji": "🍄"},
    "mat_cristal_vegetal":{"name":"Cristal Végétal",     "profession": "herboriste",  "tier": 7,  "emoji": "🔮"},
    "mat_mousse_ancienne":{"name":"Mousse Ancienne",     "profession": "herboriste",  "tier": 8,  "emoji": "🌾"},
    "mat_epine_dragon": {"name": "Épine de Dragon",      "profession": "herboriste",  "tier": 9,  "emoji": "🌵"},
    "mat_lotus_ombre":  {"name": "Lotus de l'Ombre",     "profession": "herboriste",  "tier": 10, "emoji": "🖤"},
    # CHASSEUR — 10 matériaux, tiers 1-10
    "mat_cuir_loup":    {"name": "Cuir de Loup",         "profession": "chasseur",    "tier": 1,  "emoji": "🐺"},
    "mat_cuir_cerf":    {"name": "Cuir de Cerf",         "profession": "chasseur",    "tier": 2,  "emoji": "🦌"},
    "mat_ecailles":     {"name": "Écailles de Serpent",  "profession": "chasseur",    "tier": 3,  "emoji": "🐍"},
    "mat_plumes":       {"name": "Plumes de Phénix",     "profession": "chasseur",    "tier": 4,  "emoji": "🦅"},
    "mat_croc_goule":   {"name": "Croc de Goule",        "profession": "chasseur",    "tier": 5,  "emoji": "🦷"},
    "mat_griffe_griff": {"name": "Griffe de Griffon",    "profession": "chasseur",    "tier": 6,  "emoji": "🦁"},
    "mat_peau_dragon":  {"name": "Peau de Dragon",       "profession": "chasseur",    "tier": 7,  "emoji": "🐉"},
    "mat_os_chimere":   {"name": "Os de Chimère",        "profession": "chasseur",    "tier": 8,  "emoji": "💀"},
    "mat_venin_basil":  {"name": "Venin de Basilic",     "profession": "chasseur",    "tier": 9,  "emoji": "☠️"},
    "mat_coeur_bete":   {"name": "Cœur de Bête",         "profession": "chasseur",    "tier": 10, "emoji": "❤️"},
    # FERMIER — 10 matériaux, tiers 1-10
    "mat_ble":          {"name": "Blé",                  "profession": "fermier",     "tier": 1,  "emoji": "🌾"},
    "mat_orge":         {"name": "Orge",                 "profession": "fermier",     "tier": 2,  "emoji": "🌾"},
    "mat_farine_mais":  {"name": "Farine de Maïs",       "profession": "fermier",     "tier": 3,  "emoji": "🌽"},
    "mat_herbes_arom":  {"name": "Herbes Aromatiques",   "profession": "fermier",     "tier": 4,  "emoji": "🌿"},
    "mat_baies":        {"name": "Baies Sauvages",       "profession": "fermier",     "tier": 5,  "emoji": "🫐"},
    "mat_lait_licorne": {"name": "Lait de Licorne",      "profession": "fermier",     "tier": 6,  "emoji": "🦄"},
    "mat_miel_enchante":{"name": "Miel Enchanté",        "profession": "fermier",     "tier": 7,  "emoji": "🍯"},
    "mat_sel_mer":      {"name": "Sel de Mer",           "profession": "fermier",     "tier": 8,  "emoji": "🧂"},
    "mat_epices_rares": {"name": "Épices Rares",         "profession": "fermier",     "tier": 9,  "emoji": "🌶️"},
    "mat_fruit_paradis":{"name": "Fruit du Paradis",     "profession": "fermier",     "tier": 10, "emoji": "🍑"},
}

PROFESSION_MATERIALS: dict[str, list[str]] = {}
for mid, mdata in MATERIALS.items():
    prof = mdata["profession"]
    PROFESSION_MATERIALS.setdefault(prof, []).append(mid)

# ─── Matériaux par tier et famille (index = tier-1) ─────────────────────────
_PROF_TIER_MAT: dict[str, list[str]] = {
    "mineur":     ["mat_fer","mat_acier","mat_mithril","mat_adamantium","mat_pierre_feu",
                   "mat_pierre_glace","mat_orichalque","mat_pierre_foudre","mat_cristal_brut","mat_diamant_brut"],
    "bucheron":   ["mat_bois_chene","mat_bois_sapin","mat_bois_ebene","mat_bois_teck","mat_bois_cedre",
                   "mat_bois_enchante","mat_bois_sang","mat_bois_lune","mat_bois_feu","mat_bois_dragon"],
    "herboriste": ["mat_herbe_soin","mat_herbe_mana","mat_racine_force","mat_fleur_lune","mat_pollen_dore",
                   "mat_champi_venin","mat_cristal_vegetal","mat_mousse_ancienne","mat_epine_dragon","mat_lotus_ombre"],
    "chasseur":   ["mat_cuir_loup","mat_cuir_cerf","mat_ecailles","mat_plumes","mat_croc_goule",
                   "mat_griffe_griff","mat_peau_dragon","mat_os_chimere","mat_venin_basil","mat_coeur_bete"],
    "fermier":    ["mat_ble","mat_orge","mat_farine_mais","mat_herbes_arom","mat_baies",
                   "mat_lait_licorne","mat_miel_enchante","mat_sel_mer","mat_epices_rares","mat_fruit_paradis"],
}

# Chaque classe utilise une paire unique de familles (C(5,2) = 10 combinaisons uniques)
_CLASS_CRAFT_FAMILIES: dict[str, tuple[str, str]] = {
    "Guerrier":         ("mineur",     "bucheron"),
    "Mage":             ("herboriste", "mineur"),
    "Assassin":         ("chasseur",   "herboriste"),
    "Tireur":           ("bucheron",   "chasseur"),
    "Support":          ("mineur",     "fermier"),
    "Vampire":          ("chasseur",   "fermier"),
    "Gardien du Temps": ("bucheron",   "herboriste"),
    "Ombre Venin":      ("herboriste", "fermier"),
    "Pyromancien":      ("mineur",     "chasseur"),
    "Paladin":          ("bucheron",   "fermier"),
}

# Quantités (fam1, fam2) par tier — croissance progressive
_TIER_QTY: dict[int, tuple[int, int]] = {
    1: (3, 2), 2: (4, 2), 3: (4, 3), 4: (5, 3), 5: (5, 4),
    6: (6, 4), 7: (6, 5), 8: (7, 5), 9: (7, 6), 10: (8, 6),
}

# Tiers des recettes de craft : (level_req, tier)
_CRAFT_TIERS = [(1,1),(10,2),(20,3),(30,4),(40,5),(50,6),(60,7),(70,8),(80,9),(90,10)]

# Boost de taux de drop par niveau de métier de récolte (en %)
def harvest_drop_bonus(level: int) -> float:
    return min(level * 0.5, 50.0)  # max +50%

# ─── Consommables ──────────────────────────────────────────────────────────
CONSUMABLES: dict[str, dict] = {
    # ALCHIMISTE — Potion de Soin (10 paliers : +10 % / palier, niv 1/10/20…90)
    "potion_soin_t1":          {"name": "Infime Potion de Soin",      "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 10,  "emoji": "🧪"},
    "potion_soin_t2":          {"name": "Légère Potion de Soin",      "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 20,  "emoji": "🧪"},
    "potion_soin_t3":          {"name": "Petite Potion de Soin",      "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 30,  "emoji": "🧪"},
    "potion_soin_t4":          {"name": "Potion de Soin",             "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 40,  "emoji": "💊"},
    "potion_soin_t5":          {"name": "Grande Potion de Soin",      "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 50,  "emoji": "💊"},
    "potion_soin_t6":          {"name": "Forte Potion de Soin",       "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 60,  "emoji": "💊"},
    "potion_soin_t7":          {"name": "Puissante Potion de Soin",   "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 70,  "emoji": "✨"},
    "potion_soin_t8":          {"name": "Giga Potion de Soin",        "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 80,  "emoji": "✨"},
    "potion_soin_t9":          {"name": "Suprême Potion de Soin",     "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 90,  "emoji": "🌟"},
    "potion_soin_t10":         {"name": "Potion de Soin Ultime",      "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 100, "emoji": "🌟"},
    # ALCHIMISTE — Élixir de Force (p_atk_pct, 10 paliers : +2 % / palier, niv 1/11/21…91)
    "elixir_force_t1":     {"name": "Infime Élixir de Force",      "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 2,   "duration": 10, "emoji": "💪"},
    "elixir_force_t2":     {"name": "Mineur Élixir de Force",      "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 4,   "duration": 10, "emoji": "💪"},
    "elixir_force_t3":     {"name": "Petit Élixir de Force",       "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 6,   "duration": 10, "emoji": "💪"},
    "elixir_force_t4":     {"name": "Léger Élixir de Force",       "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 8,   "duration": 10, "emoji": "💪"},
    "elixir_force_t5":     {"name": "Élixir de Force",             "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 10,  "duration": 10, "emoji": "💪"},
    "elixir_force_t6":     {"name": "Grand Élixir de Force",       "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 12,  "duration": 10, "emoji": "💪"},
    "elixir_force_t7":     {"name": "Fort Élixir de Force",        "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 14,  "duration": 10, "emoji": "💪"},
    "elixir_force_t8":     {"name": "Puissant Élixir de Force",    "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 16,  "duration": 10, "emoji": "💪"},
    "elixir_force_t9":     {"name": "Giga Élixir de Force",        "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 18,  "duration": 10, "emoji": "💪"},
    "elixir_force_t10":    {"name": "Élixir de Force Ultime",      "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 20,  "duration": 10, "emoji": "💪"},
    # ALCHIMISTE — Élixir de Magie (m_atk_pct, 10 paliers)
    "elixir_magie_t1":     {"name": "Infime Élixir de Magie",      "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 2,   "duration": 10, "emoji": "🔮"},
    "elixir_magie_t2":     {"name": "Mineur Élixir de Magie",      "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 4,   "duration": 10, "emoji": "🔮"},
    "elixir_magie_t3":     {"name": "Petit Élixir de Magie",       "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 6,   "duration": 10, "emoji": "🔮"},
    "elixir_magie_t4":     {"name": "Léger Élixir de Magie",       "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 8,   "duration": 10, "emoji": "🔮"},
    "elixir_magie_t5":     {"name": "Élixir de Magie",             "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 10,  "duration": 10, "emoji": "🔮"},
    "elixir_magie_t6":     {"name": "Grand Élixir de Magie",       "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 12,  "duration": 10, "emoji": "🔮"},
    "elixir_magie_t7":     {"name": "Fort Élixir de Magie",        "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 14,  "duration": 10, "emoji": "🔮"},
    "elixir_magie_t8":     {"name": "Puissant Élixir de Magie",    "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 16,  "duration": 10, "emoji": "🔮"},
    "elixir_magie_t9":     {"name": "Giga Élixir de Magie",        "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 18,  "duration": 10, "emoji": "🔮"},
    "elixir_magie_t10":    {"name": "Élixir de Magie Ultime",      "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 20,  "duration": 10, "emoji": "🔮"},
    # ALCHIMISTE — Élixir de Défense Physique (p_def_pct, 10 paliers)
    "elixir_def_p_t1":     {"name": "Infime Élixir de Déf. Physique", "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 2,   "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t2":     {"name": "Mineur Élixir de Déf. Physique", "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 4,   "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t3":     {"name": "Petit Élixir de Déf. Physique",  "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 6,   "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t4":     {"name": "Léger Élixir de Déf. Physique",  "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 8,   "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t5":     {"name": "Élixir de Déf. Physique",        "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 10,  "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t6":     {"name": "Grand Élixir de Déf. Physique",  "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 12,  "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t7":     {"name": "Fort Élixir de Déf. Physique",   "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 14,  "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t8":     {"name": "Puissant Élixir de Déf. Phy.",   "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 16,  "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t9":     {"name": "Giga Élixir de Déf. Physique",   "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 18,  "duration": 10, "emoji": "🛡️"},
    "elixir_def_p_t10":    {"name": "Élixir de Déf. Physique Ultime", "type": "elixir", "profession": "alchimiste", "effect": "p_def_pct",  "value": 20,  "duration": 10, "emoji": "🛡️"},
    # ALCHIMISTE — Élixir de Défense Magique (m_def_pct, 10 paliers)
    "elixir_def_m_t1":     {"name": "Infime Élixir de Déf. Magique",  "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 2,   "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t2":     {"name": "Mineur Élixir de Déf. Magique",  "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 4,   "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t3":     {"name": "Petit Élixir de Déf. Magique",   "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 6,   "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t4":     {"name": "Léger Élixir de Déf. Magique",   "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 8,   "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t5":     {"name": "Élixir de Déf. Magique",         "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 10,  "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t6":     {"name": "Grand Élixir de Déf. Magique",   "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 12,  "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t7":     {"name": "Fort Élixir de Déf. Magique",    "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 14,  "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t8":     {"name": "Puissant Élixir de Déf. Mag.",   "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 16,  "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t9":     {"name": "Giga Élixir de Déf. Magique",    "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 18,  "duration": 10, "emoji": "🔮"},
    "elixir_def_m_t10":    {"name": "Élixir de Déf. Magique Ultime",  "type": "elixir", "profession": "alchimiste", "effect": "m_def_pct",  "value": 20,  "duration": 10, "emoji": "🔮"},
    # ALCHIMISTE — Élixir de Vitesse (speed_pct, 10 paliers)
    "elixir_vit_t1":       {"name": "Infime Élixir de Vitesse",    "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 2,   "duration": 10, "emoji": "⚡"},
    "elixir_vit_t2":       {"name": "Mineur Élixir de Vitesse",    "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 4,   "duration": 10, "emoji": "⚡"},
    "elixir_vit_t3":       {"name": "Petit Élixir de Vitesse",     "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 6,   "duration": 10, "emoji": "⚡"},
    "elixir_vit_t4":       {"name": "Léger Élixir de Vitesse",     "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 8,   "duration": 10, "emoji": "⚡"},
    "elixir_vit_t5":       {"name": "Élixir de Vitesse",           "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 10,  "duration": 10, "emoji": "⚡"},
    "elixir_vit_t6":       {"name": "Grand Élixir de Vitesse",     "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 12,  "duration": 10, "emoji": "⚡"},
    "elixir_vit_t7":       {"name": "Fort Élixir de Vitesse",      "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 14,  "duration": 10, "emoji": "⚡"},
    "elixir_vit_t8":       {"name": "Puissant Élixir de Vitesse",  "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 16,  "duration": 10, "emoji": "⚡"},
    "elixir_vit_t9":       {"name": "Giga Élixir de Vitesse",      "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 18,  "duration": 10, "emoji": "⚡"},
    "elixir_vit_t10":      {"name": "Élixir de Vitesse Ultime",    "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 20,  "duration": 10, "emoji": "⚡"},
    # ALCHIMISTE — Élixir de Dégâts Critiques (crit_dmg_pct, 10 paliers : +10 % / palier)
    "elixir_crit_t1":      {"name": "Infime Élixir de Dég. Crit.",  "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 10,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t2":      {"name": "Mineur Élixir de Dég. Crit.",  "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 20,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t3":      {"name": "Petit Élixir de Dég. Crit.",   "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 30,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t4":      {"name": "Léger Élixir de Dég. Crit.",   "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 40,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t5":      {"name": "Élixir de Dég. Critiques",     "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 50,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t6":      {"name": "Grand Élixir de Dég. Crit.",   "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 60,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t7":      {"name": "Fort Élixir de Dég. Crit.",    "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 70,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t8":      {"name": "Puissant Élixir de Dég. Crit.","type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 80,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t9":      {"name": "Giga Élixir de Dég. Crit.",    "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 90,  "duration": 10, "emoji": "🎯"},
    "elixir_crit_t10":     {"name": "Élixir de Dég. Crit. Ultime",  "type": "elixir",  "profession": "alchimiste", "effect": "crit_dmg_pct", "value": 100, "duration": 10, "emoji": "🎯"},
    # ALCHIMISTE — Élixir Royal (all_pct, unique, niv 100)
    "elixir_royal":        {"name": "Élixir Royal",                "type": "elixir",  "profession": "alchimiste", "effect": "all_pct",     "value": 20,  "duration": 10, "emoji": "👑"},
    # ALCHIMISTE — Potions spéciales
    "potion_renforcement":     {"name": "Potion de Renforcement",     "type": "potion",  "profession": "alchimiste", "effect": "no_death_penalty", "value": 1, "emoji": "🔰"},
    "potion_resurrection":     {"name": "Potion de Résurrection",     "type": "potion",  "profession": "alchimiste", "effect": "revive_half_hp",   "value": 1, "emoji": "❤️‍🔥"},
    "potion_affaiblissement":  {"name": "Potion d'Affaiblissement",  "type": "potion",  "profession": "alchimiste", "effect": "weaken_class_passive", "value": 1, "emoji": "⚗️"},
    # BOULANGER — Pain (énergie directe, 10 paliers : +10 / palier, niv 1/11/21…91)
    "pain_t1":             {"name": "Croûton",                  "type": "food", "profession": "boulanger", "effect": "energy",        "value": 10,  "emoji": "🍞"},
    "pain_t2":             {"name": "Petit Pain",               "type": "food", "profession": "boulanger", "effect": "energy",        "value": 20,  "emoji": "🍞"},
    "pain_t3":             {"name": "Pain",                     "type": "food", "profession": "boulanger", "effect": "energy",        "value": 30,  "emoji": "🥖"},
    "pain_t4":             {"name": "Miche de Pain",            "type": "food", "profession": "boulanger", "effect": "energy",        "value": 40,  "emoji": "🥖"},
    "pain_t5":             {"name": "Pain de Campagne",         "type": "food", "profession": "boulanger", "effect": "energy",        "value": 50,  "emoji": "🥖"},
    "pain_t6":             {"name": "Pain Artisanal",           "type": "food", "profession": "boulanger", "effect": "energy",        "value": 60,  "emoji": "🥖"},
    "pain_t7":             {"name": "Pain des Anciens",         "type": "food", "profession": "boulanger", "effect": "energy",        "value": 70,  "emoji": "✨"},
    "pain_t8":             {"name": "Pain Enchanté",            "type": "food", "profession": "boulanger", "effect": "energy",        "value": 80,  "emoji": "✨"},
    "pain_t9":             {"name": "Pain Sacré",               "type": "food", "profession": "boulanger", "effect": "energy",        "value": 90,  "emoji": "🌟"},
    "pain_t10":            {"name": "Pain Divin",               "type": "food", "profession": "boulanger", "effect": "energy",        "value": 100, "emoji": "🌟"},
    # BOULANGER — Infusion (boost regen énergie %, durée 1h, 10 paliers : +20 % / palier)
    "infusion_t1":         {"name": "Tisane Légère",            "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 20,  "duration": "1h", "emoji": "🍵"},
    "infusion_t2":         {"name": "Tisane",                   "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 40,  "duration": "1h", "emoji": "🍵"},
    "infusion_t3":         {"name": "Infusion Légère",          "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 60,  "duration": "1h", "emoji": "🍵"},
    "infusion_t4":         {"name": "Infusion",                 "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 80,  "duration": "1h", "emoji": "🫖"},
    "infusion_t5":         {"name": "Infusion des Herbes",      "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 100, "duration": "1h", "emoji": "🫖"},
    "infusion_t6":         {"name": "Grande Infusion",          "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 120, "duration": "1h", "emoji": "🫖"},
    "infusion_t7":         {"name": "Infusion des Anciens",     "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 140, "duration": "1h", "emoji": "✨"},
    "infusion_t8":         {"name": "Infusion Renforcée",       "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 160, "duration": "1h", "emoji": "✨"},
    "infusion_t9":         {"name": "Infusion Enchantée",       "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 180, "duration": "1h", "emoji": "🌟"},
    "infusion_t10":        {"name": "Infusion Légendaire",      "type": "food", "profession": "boulanger", "effect": "energy_regen",  "value": 200, "duration": "1h", "emoji": "🌟"},
    # BOULANGER — Ration de Victoire (énergie par victoire, durée 3 combats, 10 paliers)
    "ration_vic_t1":       {"name": "Mini Ration",              "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 5,   "duration": 3, "emoji": "🍱"},
    "ration_vic_t2":       {"name": "Petite Ration",            "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 10,  "duration": 3, "emoji": "🍱"},
    "ration_vic_t3":       {"name": "Ration de Victoire",       "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 15,  "duration": 3, "emoji": "🍱"},
    "ration_vic_t4":       {"name": "Ration du Soldat",         "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 20,  "duration": 3, "emoji": "⚔️"},
    "ration_vic_t5":       {"name": "Ration du Guerrier",       "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 25,  "duration": 3, "emoji": "⚔️"},
    "ration_vic_t6":       {"name": "Grande Ration de Victoire","type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 30,  "duration": 3, "emoji": "⚔️"},
    "ration_vic_t7":       {"name": "Ration du Conquérant",     "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 35,  "duration": 3, "emoji": "✨"},
    "ration_vic_t8":       {"name": "Ration du Héros",          "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 40,  "duration": 3, "emoji": "✨"},
    "ration_vic_t9":       {"name": "Ration du Champion",       "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 45,  "duration": 3, "emoji": "🌟"},
    "ration_vic_t10":      {"name": "Ration Légendaire",        "type": "food", "profession": "boulanger", "effect": "energy_on_win", "value": 50,  "duration": 3, "emoji": "🌟"},
    # BOULANGER — Festins spéciaux haut niveau (energy_all : énergie+regen+win, niv 90/95/100)
    "repas_legendaire":    {"name": "Repas Légendaire",         "type": "food", "profession": "boulanger", "effect": "energy_all", "value": 200,"regen_bonus": 400, "win_bonus": 100, "emoji": "🌟"},
    # ENCHANTEUR — Rune de Force (p_atk_pct, 10 paliers : +1 % / palier, niv 1/11/21…91)
    "rune_force_t1":       {"name": "Infime Rune de Force",        "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 1,    "emoji": "🔴"},
    "rune_force_t2":       {"name": "Mineure Rune de Force",       "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 2,    "emoji": "🔴"},
    "rune_force_t3":       {"name": "Petite Rune de Force",        "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 3,    "emoji": "🔴"},
    "rune_force_t4":       {"name": "Légère Rune de Force",        "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 4,    "emoji": "🔴"},
    "rune_force_t5":       {"name": "Rune de Force",               "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 5,    "emoji": "🔴"},
    "rune_force_t6":       {"name": "Grande Rune de Force",        "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 6,    "emoji": "🔴"},
    "rune_force_t7":       {"name": "Forte Rune de Force",         "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 7,    "emoji": "🔴"},
    "rune_force_t8":       {"name": "Puissante Rune de Force",     "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 8,    "emoji": "🔴"},
    "rune_force_t9":       {"name": "Giga Rune de Force",          "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 9,    "emoji": "🔴"},
    "rune_force_t10":      {"name": "Rune de Force Ultime",        "type": "rune", "profession": "enchanteur", "effect": "p_atk_pct", "value": 10,   "emoji": "🔴"},
    # ENCHANTEUR — Rune de Magie (m_atk_pct, 10 paliers)
    "rune_magie_t1":       {"name": "Infime Rune de Magie",        "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 1,    "emoji": "🔵"},
    "rune_magie_t2":       {"name": "Mineure Rune de Magie",       "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 2,    "emoji": "🔵"},
    "rune_magie_t3":       {"name": "Petite Rune de Magie",        "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 3,    "emoji": "🔵"},
    "rune_magie_t4":       {"name": "Légère Rune de Magie",        "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 4,    "emoji": "🔵"},
    "rune_magie_t5":       {"name": "Rune de Magie",               "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 5,    "emoji": "🔵"},
    "rune_magie_t6":       {"name": "Grande Rune de Magie",        "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 6,    "emoji": "🔵"},
    "rune_magie_t7":       {"name": "Forte Rune de Magie",         "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 7,    "emoji": "🔵"},
    "rune_magie_t8":       {"name": "Puissante Rune de Magie",     "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 8,    "emoji": "🔵"},
    "rune_magie_t9":       {"name": "Giga Rune de Magie",          "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 9,    "emoji": "🔵"},
    "rune_magie_t10":      {"name": "Rune de Magie Ultime",        "type": "rune", "profession": "enchanteur", "effect": "m_atk_pct", "value": 10,   "emoji": "🔵"},
    # ENCHANTEUR — Rune de Défense Physique (p_def_pct, 10 paliers)
    "rune_def_p_t1":       {"name": "Infime Rune de Déf. Physique","type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 1,    "emoji": "🟡"},
    "rune_def_p_t2":       {"name": "Mineure Rune de Déf. Physique","type": "rune","profession": "enchanteur", "effect": "p_def_pct", "value": 2,    "emoji": "🟡"},
    "rune_def_p_t3":       {"name": "Petite Rune de Déf. Physique","type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 3,    "emoji": "🟡"},
    "rune_def_p_t4":       {"name": "Légère Rune de Déf. Physique","type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 4,    "emoji": "🟡"},
    "rune_def_p_t5":       {"name": "Rune de Déf. Physique",       "type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 5,    "emoji": "🟡"},
    "rune_def_p_t6":       {"name": "Grande Rune de Déf. Physique","type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 6,    "emoji": "🟡"},
    "rune_def_p_t7":       {"name": "Forte Rune de Déf. Physique", "type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 7,    "emoji": "🟡"},
    "rune_def_p_t8":       {"name": "Puissante Rune de Déf. Phy.", "type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 8,    "emoji": "🟡"},
    "rune_def_p_t9":       {"name": "Giga Rune de Déf. Physique",  "type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 9,    "emoji": "🟡"},
    "rune_def_p_t10":      {"name": "Rune de Déf. Physique Ultime","type": "rune", "profession": "enchanteur", "effect": "p_def_pct", "value": 10,   "emoji": "🟡"},
    # ENCHANTEUR — Rune de Défense Magique (m_def_pct, 10 paliers)
    "rune_def_m_t1":       {"name": "Infime Rune de Déf. Magique", "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 1,    "emoji": "🟢"},
    "rune_def_m_t2":       {"name": "Mineure Rune de Déf. Magique","type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 2,    "emoji": "🟢"},
    "rune_def_m_t3":       {"name": "Petite Rune de Déf. Magique", "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 3,    "emoji": "🟢"},
    "rune_def_m_t4":       {"name": "Légère Rune de Déf. Magique", "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 4,    "emoji": "🟢"},
    "rune_def_m_t5":       {"name": "Rune de Déf. Magique",        "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 5,    "emoji": "🟢"},
    "rune_def_m_t6":       {"name": "Grande Rune de Déf. Magique", "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 6,    "emoji": "🟢"},
    "rune_def_m_t7":       {"name": "Forte Rune de Déf. Magique",  "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 7,    "emoji": "🟢"},
    "rune_def_m_t8":       {"name": "Puissante Rune de Déf. Mag.", "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 8,    "emoji": "🟢"},
    "rune_def_m_t9":       {"name": "Giga Rune de Déf. Magique",   "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 9,    "emoji": "🟢"},
    "rune_def_m_t10":      {"name": "Rune de Déf. Magique Ultime", "type": "rune", "profession": "enchanteur", "effect": "m_def_pct", "value": 10,   "emoji": "🟢"},
    # ENCHANTEUR — Rune de Vitesse (speed_pct, 10 paliers)
    "rune_vit_t1":         {"name": "Infime Rune de Vitesse",      "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 1,    "emoji": "⚡"},
    "rune_vit_t2":         {"name": "Mineure Rune de Vitesse",     "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 2,    "emoji": "⚡"},
    "rune_vit_t3":         {"name": "Petite Rune de Vitesse",      "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 3,    "emoji": "⚡"},
    "rune_vit_t4":         {"name": "Légère Rune de Vitesse",      "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 4,    "emoji": "⚡"},
    "rune_vit_t5":         {"name": "Rune de Vitesse",             "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 5,    "emoji": "⚡"},
    "rune_vit_t6":         {"name": "Grande Rune de Vitesse",      "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 6,    "emoji": "⚡"},
    "rune_vit_t7":         {"name": "Forte Rune de Vitesse",       "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 7,    "emoji": "⚡"},
    "rune_vit_t8":         {"name": "Puissante Rune de Vitesse",   "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 8,    "emoji": "⚡"},
    "rune_vit_t9":         {"name": "Giga Rune de Vitesse",        "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 9,    "emoji": "⚡"},
    "rune_vit_t10":        {"name": "Rune de Vitesse Ultime",      "type": "rune", "profession": "enchanteur", "effect": "speed_pct", "value": 10,   "emoji": "⚡"},
    # ENCHANTEUR — Rune de Critique (crit_pct, 10 paliers)
    "rune_crit_t1":        {"name": "Infime Rune de Critique",     "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 1,    "emoji": "🎯"},
    "rune_crit_t2":        {"name": "Mineure Rune de Critique",    "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 2,    "emoji": "🎯"},
    "rune_crit_t3":        {"name": "Petite Rune de Critique",     "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 3,    "emoji": "🎯"},
    "rune_crit_t4":        {"name": "Légère Rune de Critique",     "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 4,    "emoji": "🎯"},
    "rune_crit_t5":        {"name": "Rune de Critique",            "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 5,    "emoji": "🎯"},
    "rune_crit_t6":        {"name": "Grande Rune de Critique",     "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 6,    "emoji": "🎯"},
    "rune_crit_t7":        {"name": "Forte Rune de Critique",      "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 7,    "emoji": "🎯"},
    "rune_crit_t8":        {"name": "Puissante Rune de Critique",  "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 8,    "emoji": "🎯"},
    "rune_crit_t9":        {"name": "Giga Rune de Critique",       "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 9,    "emoji": "🎯"},
    "rune_crit_t10":       {"name": "Rune de Critique Ultime",     "type": "rune", "profession": "enchanteur", "effect": "crit_pct",  "value": 10,   "emoji": "🎯"},
    # ENCHANTEUR — Rune Divine (all_stats, 1 palier, niv 100)
    "rune_divine":         {"name": "Rune Divine",                 "type": "rune", "profession": "enchanteur", "effect": "all_stats", "value": 10,   "emoji": "✨"},
}

# Récompense quotidienne par défaut (legacy)
DAILY_DEFAULT_POTION = "potion_soin_t1"
DAILY_DEFAULT_FOOD   = "pain_t1"

# ─── Pools pondérés pour la récompense quotidienne ──────────────────────────
# Poids par palier (t1…t9) — sans le palier ultime (t10)
_DAILY_W = [50, 25, 15, 10, 6, 4, 3, 2, 1]
# Poids pour les potions de soin (9 paliers, sans ultime t10)
_DAILY_W_POTION = [50, 25, 15, 10, 6, 4, 3, 2, 1]

DAILY_POTION_POOL: list[tuple[str, int]] = list(zip([
    "potion_soin_t1", "potion_soin_t2", "potion_soin_t3",
    "potion_soin_t4", "potion_soin_t5", "potion_soin_t6",
    "potion_soin_t7", "potion_soin_t8", "potion_soin_t9",
], _DAILY_W_POTION))

DAILY_FOOD_POOL: list[tuple[str, int]] = list(zip([
    "pain_t1", "pain_t2", "pain_t3", "pain_t4", "pain_t5",
    "pain_t6", "pain_t7", "pain_t8", "pain_t9",
], _DAILY_W))

# Runes : 9 types × 9 paliers (t1…t9, sans t10 et sans rune_divine)
_RUNE_TIERS = [
    ("rune_force_t1",  "rune_force_t2",  "rune_force_t3",  "rune_force_t4",  "rune_force_t5",  "rune_force_t6",  "rune_force_t7",  "rune_force_t8",  "rune_force_t9"),
    ("rune_magie_t1",  "rune_magie_t2",  "rune_magie_t3",  "rune_magie_t4",  "rune_magie_t5",  "rune_magie_t6",  "rune_magie_t7",  "rune_magie_t8",  "rune_magie_t9"),
    ("rune_def_p_t1",  "rune_def_p_t2",  "rune_def_p_t3",  "rune_def_p_t4",  "rune_def_p_t5",  "rune_def_p_t6",  "rune_def_p_t7",  "rune_def_p_t8",  "rune_def_p_t9"),
    ("rune_def_m_t1",  "rune_def_m_t2",  "rune_def_m_t3",  "rune_def_m_t4",  "rune_def_m_t5",  "rune_def_m_t6",  "rune_def_m_t7",  "rune_def_m_t8",  "rune_def_m_t9"),
    ("rune_vit_t1",    "rune_vit_t2",    "rune_vit_t3",    "rune_vit_t4",    "rune_vit_t5",    "rune_vit_t6",    "rune_vit_t7",    "rune_vit_t8",    "rune_vit_t9"),
    ("rune_crit_t1",   "rune_crit_t2",   "rune_crit_t3",   "rune_crit_t4",   "rune_crit_t5",   "rune_crit_t6",   "rune_crit_t7",   "rune_crit_t8",   "rune_crit_t9"),
]
DAILY_RUNE_POOL: list[tuple[str, int]] = [
    (rid, w)
    for tiers in _RUNE_TIERS
    for rid, w in zip(tiers, _DAILY_W)
]

def pick_daily_item(pool: list[tuple[str, int]]) -> str:
    import random
    ids, weights = zip(*pool)
    return random.choices(ids, weights=weights, k=1)[0]

# ─── Recettes ──────────────────────────────────────────────────────────────
# 10 recettes par métier de conception = 30 recettes
CONCEPTION_RECIPES: dict[str, dict] = {
    # ALCHIMISTE — Potion de Soin (herboriste tier N, niv 1/10/20…90)
    "rec_soin_t1":            {"result": "potion_soin_t1",          "qty": 1, "profession": "alchimiste", "level_req": 1,   "ingredients": {"mat_herbe_soin": 3}},
    "rec_soin_t2":            {"result": "potion_soin_t2",          "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_herbe_mana": 4}},
    "rec_soin_t3":            {"result": "potion_soin_t3",          "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_racine_force": 4}},
    "rec_soin_t4":            {"result": "potion_soin_t4",          "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_fleur_lune": 5}},
    "rec_soin_t5":            {"result": "potion_soin_t5",          "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_pollen_dore": 5}},
    "rec_soin_t6":            {"result": "potion_soin_t6",          "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_champi_venin": 6}},
    "rec_soin_t7":            {"result": "potion_soin_t7",          "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_cristal_vegetal": 6}},
    "rec_soin_t8":            {"result": "potion_soin_t8",          "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_mousse_ancienne": 7}},
    "rec_soin_t9":            {"result": "potion_soin_t9",          "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 7}},
    "rec_soin_t10":           {"result": "potion_soin_t10",         "qty": 1, "profession": "alchimiste", "level_req": 90,  "ingredients": {"mat_lotus_ombre": 8}},
    # ALCHIMISTE — Élixir de Force (herboriste tier N, niv 1/11/21…91)
    "rec_force_t1":           {"result": "elixir_force_t1",         "qty": 1, "profession": "alchimiste", "level_req": 1,   "ingredients": {"mat_herbe_soin": 3}},
    "rec_force_t2":           {"result": "elixir_force_t2",         "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_herbe_mana": 4}},
    "rec_force_t3":           {"result": "elixir_force_t3",         "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_racine_force": 4}},
    "rec_force_t4":           {"result": "elixir_force_t4",         "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_fleur_lune": 5}},
    "rec_force_t5":           {"result": "elixir_force_t5",         "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_pollen_dore": 5}},
    "rec_force_t6":           {"result": "elixir_force_t6",         "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_champi_venin": 6}},
    "rec_force_t7":           {"result": "elixir_force_t7",         "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_cristal_vegetal": 6}},
    "rec_force_t8":           {"result": "elixir_force_t8",         "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_mousse_ancienne": 7}},
    "rec_force_t9":           {"result": "elixir_force_t9",         "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 7}},
    "rec_force_t10":          {"result": "elixir_force_t10",        "qty": 1, "profession": "alchimiste", "level_req": 90,  "ingredients": {"mat_lotus_ombre": 8}},
    # ALCHIMISTE — Élixir de Magie (herboriste tier N)
    "rec_magie_t1":           {"result": "elixir_magie_t1",         "qty": 1, "profession": "alchimiste", "level_req": 1,   "ingredients": {"mat_herbe_soin": 3}},
    "rec_magie_t2":           {"result": "elixir_magie_t2",         "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_herbe_mana": 4}},
    "rec_magie_t3":           {"result": "elixir_magie_t3",         "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_racine_force": 4}},
    "rec_magie_t4":           {"result": "elixir_magie_t4",         "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_fleur_lune": 5}},
    "rec_magie_t5":           {"result": "elixir_magie_t5",         "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_pollen_dore": 5}},
    "rec_magie_t6":           {"result": "elixir_magie_t6",         "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_champi_venin": 6}},
    "rec_magie_t7":           {"result": "elixir_magie_t7",         "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_cristal_vegetal": 6}},
    "rec_magie_t8":           {"result": "elixir_magie_t8",         "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_mousse_ancienne": 7}},
    "rec_magie_t9":           {"result": "elixir_magie_t9",         "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 7}},
    "rec_magie_t10":          {"result": "elixir_magie_t10",        "qty": 1, "profession": "alchimiste", "level_req": 90,  "ingredients": {"mat_lotus_ombre": 8}},
    # ALCHIMISTE — Élixir de Défense Physique (herboriste tier N + bûcheron tier N)
    "rec_def_p_t1":           {"result": "elixir_def_p_t1",         "qty": 1, "profession": "alchimiste", "level_req": 1,   "ingredients": {"mat_herbe_soin": 2,      "mat_bois_chene": 2}},
    "rec_def_p_t2":           {"result": "elixir_def_p_t2",         "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_herbe_mana": 3,      "mat_bois_sapin": 2}},
    "rec_def_p_t3":           {"result": "elixir_def_p_t3",         "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_racine_force": 3,    "mat_bois_ebene": 2}},
    "rec_def_p_t4":           {"result": "elixir_def_p_t4",         "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_fleur_lune": 4,      "mat_bois_teck": 2}},
    "rec_def_p_t5":           {"result": "elixir_def_p_t5",         "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_pollen_dore": 4,     "mat_bois_cedre": 2}},
    "rec_def_p_t6":           {"result": "elixir_def_p_t6",         "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_champi_venin": 5,    "mat_bois_enchante": 2}},
    "rec_def_p_t7":           {"result": "elixir_def_p_t7",         "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_cristal_vegetal": 5, "mat_bois_sang": 2}},
    "rec_def_p_t8":           {"result": "elixir_def_p_t8",         "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_mousse_ancienne": 6, "mat_bois_lune": 2}},
    "rec_def_p_t9":           {"result": "elixir_def_p_t9",         "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 6,    "mat_bois_feu": 2}},
    "rec_def_p_t10":          {"result": "elixir_def_p_t10",        "qty": 1, "profession": "alchimiste", "level_req": 90,  "ingredients": {"mat_lotus_ombre": 7,     "mat_bois_dragon": 2}},
    # ALCHIMISTE — Élixir de Défense Magique (m_def_pct, 10 paliers)
    "rec_def_m_t1":           {"result": "elixir_def_m_t1",         "qty": 1, "profession": "alchimiste", "level_req": 1,   "ingredients": {"mat_herbe_soin": 3}},
    "rec_def_m_t2":           {"result": "elixir_def_m_t2",         "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_herbe_mana": 4}},
    "rec_def_m_t3":           {"result": "elixir_def_m_t3",         "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_racine_force": 4}},
    "rec_def_m_t4":           {"result": "elixir_def_m_t4",         "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_fleur_lune": 5}},
    "rec_def_m_t5":           {"result": "elixir_def_m_t5",         "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_pollen_dore": 5}},
    "rec_def_m_t6":           {"result": "elixir_def_m_t6",         "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_champi_venin": 6}},
    "rec_def_m_t7":           {"result": "elixir_def_m_t7",         "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_cristal_vegetal": 6}},
    "rec_def_m_t8":           {"result": "elixir_def_m_t8",         "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_mousse_ancienne": 7}},
    "rec_def_m_t9":           {"result": "elixir_def_m_t9",         "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 7}},
    "rec_def_m_t10":          {"result": "elixir_def_m_t10",        "qty": 1, "profession": "alchimiste", "level_req": 90,  "ingredients": {"mat_lotus_ombre": 8}},
    # ALCHIMISTE — Élixir de Vitesse (herboriste tier N)
    "rec_vit_t1":             {"result": "elixir_vit_t1",           "qty": 1, "profession": "alchimiste", "level_req": 1,   "ingredients": {"mat_herbe_soin": 3}},
    "rec_vit_t2":             {"result": "elixir_vit_t2",           "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_herbe_mana": 4}},
    "rec_vit_t3":             {"result": "elixir_vit_t3",           "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_racine_force": 4}},
    "rec_vit_t4":             {"result": "elixir_vit_t4",           "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_fleur_lune": 5}},
    "rec_vit_t5":             {"result": "elixir_vit_t5",           "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_pollen_dore": 5}},
    "rec_vit_t6":             {"result": "elixir_vit_t6",           "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_champi_venin": 6}},
    "rec_vit_t7":             {"result": "elixir_vit_t7",           "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_cristal_vegetal": 6}},
    "rec_vit_t8":             {"result": "elixir_vit_t8",           "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_mousse_ancienne": 7}},
    "rec_vit_t9":             {"result": "elixir_vit_t9",           "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 7}},
    "rec_vit_t10":            {"result": "elixir_vit_t10",          "qty": 1, "profession": "alchimiste", "level_req": 90,  "ingredients": {"mat_lotus_ombre": 8}},
    # ALCHIMISTE — Élixir de Critique (herboriste tier N)
    "rec_crit_t1":            {"result": "elixir_crit_t1",          "qty": 1, "profession": "alchimiste", "level_req": 1,   "ingredients": {"mat_herbe_soin": 3}},
    "rec_crit_t2":            {"result": "elixir_crit_t2",          "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_herbe_mana": 4}},
    "rec_crit_t3":            {"result": "elixir_crit_t3",          "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_racine_force": 4}},
    "rec_crit_t4":            {"result": "elixir_crit_t4",          "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_fleur_lune": 5}},
    "rec_crit_t5":            {"result": "elixir_crit_t5",          "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_pollen_dore": 5}},
    "rec_crit_t6":            {"result": "elixir_crit_t6",          "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_champi_venin": 6}},
    "rec_crit_t7":            {"result": "elixir_crit_t7",          "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_cristal_vegetal": 6}},
    "rec_crit_t8":            {"result": "elixir_crit_t8",          "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_mousse_ancienne": 7}},
    "rec_crit_t9":            {"result": "elixir_crit_t9",          "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 7}},
    "rec_crit_t10":           {"result": "elixir_crit_t10",         "qty": 1, "profession": "alchimiste", "level_req": 90,  "ingredients": {"mat_lotus_ombre": 8}},
    # ALCHIMISTE — Potions spéciales
    # lv15→T2: herbe_mana, lv50→T6: champi_venin, lv100→T10: lotus_ombre
    "rec_renforcement":       {"result": "potion_renforcement",     "qty": 1, "profession": "alchimiste", "level_req": 15,  "ingredients": {"mat_herbe_mana": 5}},
    "rec_affaiblissement":    {"result": "potion_affaiblissement",  "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_champi_venin": 6}},
    "rec_resurrection":       {"result": "potion_resurrection",     "qty": 1, "profession": "alchimiste", "level_req": 100, "ingredients": {"mat_lotus_ombre": 80}},
    "rec_royal":              {"result": "elixir_royal",            "qty": 1, "profession": "alchimiste", "level_req": 100, "ingredients": {"mat_lotus_ombre": 80}},
    # BOULANGER — Pain (énergie directe, fermier tier N, niv 1/11/21…91)
    "rec_pain_t1":            {"result": "pain_t1",            "qty": 1, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_ble": 3}},
    "rec_pain_t2":            {"result": "pain_t2",            "qty": 1, "profession": "boulanger", "level_req": 10, "ingredients": {"mat_orge": 4}},
    "rec_pain_t3":            {"result": "pain_t3",            "qty": 1, "profession": "boulanger", "level_req": 20, "ingredients": {"mat_farine_mais": 4}},
    "rec_pain_t4":            {"result": "pain_t4",            "qty": 1, "profession": "boulanger", "level_req": 30, "ingredients": {"mat_herbes_arom": 5}},
    "rec_pain_t5":            {"result": "pain_t5",            "qty": 1, "profession": "boulanger", "level_req": 40, "ingredients": {"mat_baies": 5}},
    "rec_pain_t6":            {"result": "pain_t6",            "qty": 1, "profession": "boulanger", "level_req": 50, "ingredients": {"mat_lait_licorne": 6}},
    "rec_pain_t7":            {"result": "pain_t7",            "qty": 1, "profession": "boulanger", "level_req": 60, "ingredients": {"mat_miel_enchante": 4, "mat_bois_enchante": 2}},
    "rec_pain_t8":            {"result": "pain_t8",            "qty": 1, "profession": "boulanger", "level_req": 70, "ingredients": {"mat_sel_mer": 5,      "mat_bois_lune": 2}},
    "rec_pain_t9":            {"result": "pain_t9",            "qty": 1, "profession": "boulanger", "level_req": 80, "ingredients": {"mat_epices_rares": 5, "mat_bois_feu": 2}},
    "rec_pain_t10":           {"result": "pain_t10",           "qty": 1, "profession": "boulanger", "level_req": 90, "ingredients": {"mat_fruit_paradis": 6, "mat_bois_dragon": 2}},
    # BOULANGER — Infusion (regen énergie passive, fermier tier N)
    "rec_infusion_t1":        {"result": "infusion_t1",        "qty": 1, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_ble": 3}},
    "rec_infusion_t2":        {"result": "infusion_t2",        "qty": 1, "profession": "boulanger", "level_req": 10, "ingredients": {"mat_orge": 4}},
    "rec_infusion_t3":        {"result": "infusion_t3",        "qty": 1, "profession": "boulanger", "level_req": 20, "ingredients": {"mat_farine_mais": 4}},
    "rec_infusion_t4":        {"result": "infusion_t4",        "qty": 1, "profession": "boulanger", "level_req": 30, "ingredients": {"mat_herbes_arom": 5}},
    "rec_infusion_t5":        {"result": "infusion_t5",        "qty": 1, "profession": "boulanger", "level_req": 40, "ingredients": {"mat_baies": 5}},
    "rec_infusion_t6":        {"result": "infusion_t6",        "qty": 1, "profession": "boulanger", "level_req": 50, "ingredients": {"mat_lait_licorne": 6}},
    "rec_infusion_t7":        {"result": "infusion_t7",        "qty": 1, "profession": "boulanger", "level_req": 60, "ingredients": {"mat_miel_enchante": 6}},
    "rec_infusion_t8":        {"result": "infusion_t8",        "qty": 1, "profession": "boulanger", "level_req": 70, "ingredients": {"mat_sel_mer": 7}},
    "rec_infusion_t9":        {"result": "infusion_t9",        "qty": 1, "profession": "boulanger", "level_req": 80, "ingredients": {"mat_epices_rares": 7}},
    "rec_infusion_t10":       {"result": "infusion_t10",       "qty": 1, "profession": "boulanger", "level_req": 90, "ingredients": {"mat_fruit_paradis": 8}},
    # BOULANGER — Ration de Victoire (énergie par victoire, fermier tier N)
    "rec_ration_vic_t1":      {"result": "ration_vic_t1",      "qty": 1, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_ble": 3}},
    "rec_ration_vic_t2":      {"result": "ration_vic_t2",      "qty": 1, "profession": "boulanger", "level_req": 10, "ingredients": {"mat_orge": 4}},
    "rec_ration_vic_t3":      {"result": "ration_vic_t3",      "qty": 1, "profession": "boulanger", "level_req": 20, "ingredients": {"mat_farine_mais": 4}},
    "rec_ration_vic_t4":      {"result": "ration_vic_t4",      "qty": 1, "profession": "boulanger", "level_req": 30, "ingredients": {"mat_herbes_arom": 5}},
    "rec_ration_vic_t5":      {"result": "ration_vic_t5",      "qty": 1, "profession": "boulanger", "level_req": 40, "ingredients": {"mat_baies": 5}},
    "rec_ration_vic_t6":      {"result": "ration_vic_t6",      "qty": 1, "profession": "boulanger", "level_req": 50, "ingredients": {"mat_lait_licorne": 6}},
    "rec_ration_vic_t7":      {"result": "ration_vic_t7",      "qty": 1, "profession": "boulanger", "level_req": 60, "ingredients": {"mat_miel_enchante": 6}},
    "rec_ration_vic_t8":      {"result": "ration_vic_t8",      "qty": 1, "profession": "boulanger", "level_req": 70, "ingredients": {"mat_sel_mer": 7}},
    "rec_ration_vic_t9":      {"result": "ration_vic_t9",      "qty": 1, "profession": "boulanger", "level_req": 80, "ingredients": {"mat_epices_rares": 7}},
    "rec_ration_vic_t10":     {"result": "ration_vic_t10",     "qty": 1, "profession": "boulanger", "level_req": 90, "ingredients": {"mat_fruit_paradis": 8}},
    # BOULANGER — Repas Légendaire (unique, niv 100)
    "rec_repas_legendaire":   {"result": "repas_legendaire",   "qty": 1, "profession": "boulanger", "level_req": 100, "ingredients": {"mat_fruit_paradis": 50}},
    # ENCHANTEUR — Rune de Force (p_atk_pct) — mineur tier N + chasseur tier N, niv 1/11/21…91
    "rec_rune_force_t1":      {"result": "rune_force_t1",      "qty": 1, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 3, "mat_cuir_loup": 2}},
    "rec_rune_force_t2":      {"result": "rune_force_t2",      "qty": 1, "profession": "enchanteur", "level_req": 10, "ingredients": {"mat_acier": 4, "mat_cuir_cerf": 2}},
    "rec_rune_force_t3":      {"result": "rune_force_t3",      "qty": 1, "profession": "enchanteur", "level_req": 20, "ingredients": {"mat_mithril": 4, "mat_ecailles": 3}},
    "rec_rune_force_t4":      {"result": "rune_force_t4",      "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_adamantium": 5, "mat_plumes": 3}},
    "rec_rune_force_t5":      {"result": "rune_force_t5",      "qty": 1, "profession": "enchanteur", "level_req": 40, "ingredients": {"mat_pierre_feu": 5, "mat_croc_goule": 4}},
    "rec_rune_force_t6":      {"result": "rune_force_t6",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_pierre_glace": 6, "mat_griffe_griff": 4}},
    "rec_rune_force_t7":      {"result": "rune_force_t7",      "qty": 1, "profession": "enchanteur", "level_req": 60, "ingredients": {"mat_orichalque": 6, "mat_peau_dragon": 5}},
    "rec_rune_force_t8":      {"result": "rune_force_t8",      "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_pierre_foudre": 7, "mat_os_chimere": 5}},
    "rec_rune_force_t9":      {"result": "rune_force_t9",      "qty": 1, "profession": "enchanteur", "level_req": 80, "ingredients": {"mat_cristal_brut": 7, "mat_venin_basil": 6}},
    "rec_rune_force_t10":     {"result": "rune_force_t10",     "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_diamant_brut": 8, "mat_coeur_bete": 6}},
    # ENCHANTEUR — Rune de Magie (m_atk_pct) — mineur tier N + herboriste tier N
    "rec_rune_magie_t1":      {"result": "rune_magie_t1",      "qty": 1, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 3, "mat_herbe_soin": 2}},
    "rec_rune_magie_t2":      {"result": "rune_magie_t2",      "qty": 1, "profession": "enchanteur", "level_req": 10, "ingredients": {"mat_acier": 4, "mat_herbe_mana": 2}},
    "rec_rune_magie_t3":      {"result": "rune_magie_t3",      "qty": 1, "profession": "enchanteur", "level_req": 20, "ingredients": {"mat_mithril": 4, "mat_racine_force": 3}},
    "rec_rune_magie_t4":      {"result": "rune_magie_t4",      "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_adamantium": 5, "mat_fleur_lune": 3}},
    "rec_rune_magie_t5":      {"result": "rune_magie_t5",      "qty": 1, "profession": "enchanteur", "level_req": 40, "ingredients": {"mat_pierre_feu": 5, "mat_pollen_dore": 4}},
    "rec_rune_magie_t6":      {"result": "rune_magie_t6",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_pierre_glace": 6, "mat_champi_venin": 4}},
    "rec_rune_magie_t7":      {"result": "rune_magie_t7",      "qty": 1, "profession": "enchanteur", "level_req": 60, "ingredients": {"mat_orichalque": 6, "mat_cristal_vegetal": 5}},
    "rec_rune_magie_t8":      {"result": "rune_magie_t8",      "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_pierre_foudre": 7, "mat_mousse_ancienne": 5}},
    "rec_rune_magie_t9":      {"result": "rune_magie_t9",      "qty": 1, "profession": "enchanteur", "level_req": 80, "ingredients": {"mat_cristal_brut": 7, "mat_epine_dragon": 6}},
    "rec_rune_magie_t10":     {"result": "rune_magie_t10",     "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_diamant_brut": 8, "mat_lotus_ombre": 6}},
    # ENCHANTEUR — Rune de Défense Physique (p_def_pct) — mineur tier N + chasseur tier N
    "rec_rune_def_p_t1":      {"result": "rune_def_p_t1",      "qty": 1, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 3, "mat_cuir_loup": 2}},
    "rec_rune_def_p_t2":      {"result": "rune_def_p_t2",      "qty": 1, "profession": "enchanteur", "level_req": 10, "ingredients": {"mat_acier": 4, "mat_cuir_cerf": 2}},
    "rec_rune_def_p_t3":      {"result": "rune_def_p_t3",      "qty": 1, "profession": "enchanteur", "level_req": 20, "ingredients": {"mat_mithril": 4, "mat_ecailles": 3}},
    "rec_rune_def_p_t4":      {"result": "rune_def_p_t4",      "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_adamantium": 5, "mat_plumes": 3}},
    "rec_rune_def_p_t5":      {"result": "rune_def_p_t5",      "qty": 1, "profession": "enchanteur", "level_req": 40, "ingredients": {"mat_pierre_feu": 5, "mat_croc_goule": 4}},
    "rec_rune_def_p_t6":      {"result": "rune_def_p_t6",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_pierre_glace": 6, "mat_griffe_griff": 4}},
    "rec_rune_def_p_t7":      {"result": "rune_def_p_t7",      "qty": 1, "profession": "enchanteur", "level_req": 60, "ingredients": {"mat_orichalque": 6, "mat_peau_dragon": 5}},
    "rec_rune_def_p_t8":      {"result": "rune_def_p_t8",      "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_pierre_foudre": 7, "mat_os_chimere": 5}},
    "rec_rune_def_p_t9":      {"result": "rune_def_p_t9",      "qty": 1, "profession": "enchanteur", "level_req": 80, "ingredients": {"mat_cristal_brut": 7, "mat_venin_basil": 6}},
    "rec_rune_def_p_t10":     {"result": "rune_def_p_t10",     "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_diamant_brut": 8, "mat_coeur_bete": 6}},
    # ENCHANTEUR — Rune de Défense Magique (m_def_pct) — mineur tier N + herboriste tier N
    "rec_rune_def_m_t1":      {"result": "rune_def_m_t1",      "qty": 1, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 3, "mat_herbe_soin": 2}},
    "rec_rune_def_m_t2":      {"result": "rune_def_m_t2",      "qty": 1, "profession": "enchanteur", "level_req": 10, "ingredients": {"mat_acier": 4, "mat_herbe_mana": 2}},
    "rec_rune_def_m_t3":      {"result": "rune_def_m_t3",      "qty": 1, "profession": "enchanteur", "level_req": 20, "ingredients": {"mat_mithril": 4, "mat_racine_force": 3}},
    "rec_rune_def_m_t4":      {"result": "rune_def_m_t4",      "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_adamantium": 5, "mat_fleur_lune": 3}},
    "rec_rune_def_m_t5":      {"result": "rune_def_m_t5",      "qty": 1, "profession": "enchanteur", "level_req": 40, "ingredients": {"mat_pierre_feu": 5, "mat_pollen_dore": 4}},
    "rec_rune_def_m_t6":      {"result": "rune_def_m_t6",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_pierre_glace": 6, "mat_champi_venin": 4}},
    "rec_rune_def_m_t7":      {"result": "rune_def_m_t7",      "qty": 1, "profession": "enchanteur", "level_req": 60, "ingredients": {"mat_orichalque": 6, "mat_cristal_vegetal": 5}},
    "rec_rune_def_m_t8":      {"result": "rune_def_m_t8",      "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_pierre_foudre": 7, "mat_mousse_ancienne": 5}},
    "rec_rune_def_m_t9":      {"result": "rune_def_m_t9",      "qty": 1, "profession": "enchanteur", "level_req": 80, "ingredients": {"mat_cristal_brut": 7, "mat_epine_dragon": 6}},
    "rec_rune_def_m_t10":     {"result": "rune_def_m_t10",     "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_diamant_brut": 8, "mat_lotus_ombre": 6}},
    # ENCHANTEUR — Rune de Vitesse (speed_pct) — chasseur tier N + herboriste tier N
    "rec_rune_vit_t1":        {"result": "rune_vit_t1",        "qty": 1, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_cuir_loup": 3, "mat_herbe_soin": 2}},
    "rec_rune_vit_t2":        {"result": "rune_vit_t2",        "qty": 1, "profession": "enchanteur", "level_req": 10, "ingredients": {"mat_cuir_cerf": 4, "mat_herbe_mana": 2}},
    "rec_rune_vit_t3":        {"result": "rune_vit_t3",        "qty": 1, "profession": "enchanteur", "level_req": 20, "ingredients": {"mat_ecailles": 4, "mat_racine_force": 3}},
    "rec_rune_vit_t4":        {"result": "rune_vit_t4",        "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_plumes": 5, "mat_fleur_lune": 3}},
    "rec_rune_vit_t5":        {"result": "rune_vit_t5",        "qty": 1, "profession": "enchanteur", "level_req": 40, "ingredients": {"mat_croc_goule": 5, "mat_pollen_dore": 4}},
    "rec_rune_vit_t6":        {"result": "rune_vit_t6",        "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_griffe_griff": 6, "mat_champi_venin": 4}},
    "rec_rune_vit_t7":        {"result": "rune_vit_t7",        "qty": 1, "profession": "enchanteur", "level_req": 60, "ingredients": {"mat_peau_dragon": 6, "mat_cristal_vegetal": 5}},
    "rec_rune_vit_t8":        {"result": "rune_vit_t8",        "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_os_chimere": 7, "mat_mousse_ancienne": 5}},
    "rec_rune_vit_t9":        {"result": "rune_vit_t9",        "qty": 1, "profession": "enchanteur", "level_req": 80, "ingredients": {"mat_venin_basil": 7, "mat_epine_dragon": 6}},
    "rec_rune_vit_t10":       {"result": "rune_vit_t10",       "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_coeur_bete": 8, "mat_lotus_ombre": 6}},
    # ENCHANTEUR — Rune de Critique (crit_pct) — chasseur tier N + herboriste tier N
    "rec_rune_crit_t1":       {"result": "rune_crit_t1",       "qty": 1, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_cuir_loup": 3, "mat_herbe_soin": 2}},
    "rec_rune_crit_t2":       {"result": "rune_crit_t2",       "qty": 1, "profession": "enchanteur", "level_req": 10, "ingredients": {"mat_cuir_cerf": 4, "mat_herbe_mana": 2}},
    "rec_rune_crit_t3":       {"result": "rune_crit_t3",       "qty": 1, "profession": "enchanteur", "level_req": 20, "ingredients": {"mat_ecailles": 4, "mat_racine_force": 3}},
    "rec_rune_crit_t4":       {"result": "rune_crit_t4",       "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_plumes": 5, "mat_fleur_lune": 3}},
    "rec_rune_crit_t5":       {"result": "rune_crit_t5",       "qty": 1, "profession": "enchanteur", "level_req": 40, "ingredients": {"mat_croc_goule": 5, "mat_pollen_dore": 4}},
    "rec_rune_crit_t6":       {"result": "rune_crit_t6",       "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_griffe_griff": 6, "mat_champi_venin": 4}},
    "rec_rune_crit_t7":       {"result": "rune_crit_t7",       "qty": 1, "profession": "enchanteur", "level_req": 60, "ingredients": {"mat_peau_dragon": 6, "mat_cristal_vegetal": 5}},
    "rec_rune_crit_t8":       {"result": "rune_crit_t8",       "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_os_chimere": 7, "mat_mousse_ancienne": 5}},
    "rec_rune_crit_t9":       {"result": "rune_crit_t9",       "qty": 1, "profession": "enchanteur", "level_req": 80, "ingredients": {"mat_venin_basil": 7, "mat_epine_dragon": 6}},
    "rec_rune_crit_t10":      {"result": "rune_crit_t10",      "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_coeur_bete": 8, "mat_lotus_ombre": 6}},
    # ENCHANTEUR — Rune Divine (toutes stats, tier unique niv 100) — matériaux T10
    "rec_rune_divine":        {"result": "rune_divine",        "qty": 1, "profession": "enchanteur", "level_req": 100, "ingredients": {"mat_diamant_brut": 50, "mat_lotus_ombre": 40, "mat_coeur_bete": 40}},
}

# ─── Équipements ───────────────────────────────────────────────────────────
# Catalogue des équipements : 6 sources × 10 classes × 7 slots = 420 items
# Généré programmatiquement depuis SET_BONUSES (models.py).
#
# Chaque item stocké en base de données possède un champ "level" (1-1000)
# qui détermine sa puissance et le niveau minimum du joueur pour l'équiper.
# Le catalogue définit le TEMPLATE ; le niveau est propre à chaque instance droppée/craftée.

from bot.cogs.rpg.models import SET_BONUSES

EQUIPMENT_CATALOG: dict[str, dict] = {}

# Métiers de craft → slot d'équipement
CRAFT_SLOT: dict[str, str] = {
    "heaumier":   "casque",
    "armurier":   "plastron",
    "tailleur":   "pantalon",
    "cordonnier": "chaussures",
    "forgeron":   "arme",
    "joaillier":  "amulette",
    "orfèvre":    "anneau",
}
SLOT_TO_CRAFT_JOB: dict[str, str] = {v: k for k, v in CRAFT_SLOT.items()}

# Recettes de craft : 7 professions × 10 classes = 70 recettes (une par slot × classe).
# La profession craft un item de la panoplie "craft" de la classe choisie.
# Le niveau de l'item produit = niveau_métier × 10 (résolu dynamiquement dans metiers.py).
CRAFT_RECIPES: dict[str, dict] = {}


def _build_equipment_catalog() -> None:
    """Génère EQUIPMENT_CATALOG et CRAFT_RECIPES depuis SET_BONUSES."""
    global EQUIPMENT_CATALOG, CRAFT_RECIPES

    for set_key, set_data in SET_BONUSES.items():
        class_name = set_data["class"]
        source     = set_data["source"]
        theme      = set_data["theme"]
        prefixes   = SLOT_PREFIX_BY_CLASS.get(class_name, {})

        for slot in SLOTS:
            item_id = f"eq_{set_key}_{slot}"
            # Nom immersif : "{préfixe de slot propre à la classe} {thème de la panoplie}"
            prefix    = prefixes.get(slot, slot.capitalize())
            item_name = f"{prefix} {theme}"

            EQUIPMENT_CATALOG[item_id] = {
                "name":   item_name,
                "set":    set_key,      # clé dans SET_BONUSES — utilisée pour les bonus de panoplie
                "class":  class_name,
                "slot":   slot,
                "source": source,
                "emoji":  "⚔️" if slot == "arme" else "🛡️",
                # Pas de level_req fixe : le niveau requis = item.level (champ de l'instance)
            }

        # Recettes de craft — 10 tiers par slot×classe
        if source == "craft":
            for slot in SLOTS:
                craft_job = SLOT_TO_CRAFT_JOB.get(slot)
                if not craft_job:
                    continue
                for tier_level, tier in _CRAFT_TIERS:
                    recipe_id = f"crec_{set_key}_{slot}_t{tier}"
                    ingredients = _craft_ingredients(class_name, tier)
                    CRAFT_RECIPES[recipe_id] = {
                        "result":      f"eq_{set_key}_{slot}",
                        "qty":         1,
                        "profession":  craft_job,
                        "level_req":   tier_level,
                        "ingredients": ingredients,
                        "class":       class_name,
                        "set":         set_key,
                        "tier":        tier,
                    }


def _craft_ingredients(class_name: str, tier: int = 1) -> dict[str, int]:
    """Ingrédients pour crafter un item au tier donné — uniquement des matériaux de ce tier."""
    fam1, fam2 = _CLASS_CRAFT_FAMILIES.get(class_name, ("mineur", "bucheron"))
    mat1 = _PROF_TIER_MAT[fam1][tier - 1]
    mat2 = _PROF_TIER_MAT[fam2][tier - 1]
    qty1, qty2 = _TIER_QTY[tier]
    return {mat1: qty1, mat2: qty2}


_build_equipment_catalog()


def get_equipment_stats(item_id: str, rarity: str = "commun", enhancement: int = 0,
                         item_level: int = 1) -> dict:
    """
    Calcule les stats d'un item d'équipement.

    Formule :  stat = (item_level × growth + const) × source_mult × rarity_mult × enh_mult

    - item_level  : niveau de l'instance (1-1000), storé sur l'item en base de données
    - growth/const: calibrés pour que 7 items min à item_level=L ≈ stats moy. classe niveau L
    - source_mult : multiplicateur de puissance selon le mode de jeu (monde → raid)
    - rarity_mult : multiplicateur de rareté (commun → prismatique)
    - enh_mult    : +10% par niveau d'amélioration  (max +10 → ×2.0)
    """
    item_level = max(1, min(item_level, 10000))
    item = EQUIPMENT_CATALOG.get(item_id)
    if not item:
        return {}
    slot        = item["slot"]
    source      = item.get("source", "monde")
    source_mult = SOURCE_POWER_MULT.get(source, 1.0)
    rarity_mult = RARITY_MULT.get(rarity, 1.0)
    enh_mult    = 1 + enhancement * 0.1

    item_class = item.get("class", "")
    focus = CLASS_SLOT_STAT_FOCUS.get(item_class, {}).get(slot, {})
    stats = {}
    mult  = source_mult * rarity_mult * enh_mult

    for stat, (growth, const) in focus.items():
        raw = (item_level * growth + const) * mult
        if stat in ("crit_chance", "crit_damage"):
            stats[stat] = round(raw, 2)
        else:
            stats[stat] = round(raw)
    return stats


def get_enhancement_cost(current_enhancement: int) -> int:
    """Coût en gold pour améliorer un équipement."""
    costs = [500, 1500, 4000, 10000, 25000, 60000, 150000, 400000, 1000000, 3000000]
    if current_enhancement >= len(costs):
        return -1  # déjà au max
    return costs[current_enhancement]


def item_sell_price(item_id: str, rarity: str, enhancement: int, item_level: int = 1) -> int:
    """Prix de vente de base d'un équipement (sans hôtel des ventes)."""
    item = EQUIPMENT_CATALOG.get(item_id)
    if not item:
        return 10
    source_mult = SOURCE_POWER_MULT.get(item.get("source", "monde"), 1.0)
    rarity_idx  = RARITIES.index(rarity) if rarity in RARITIES else 0
    base        = int(50 * item_level * source_mult * (2 ** rarity_idx) / 100)
    return max(10, int(base * (1 + enhancement * 0.15)))


# ─── Valeurs de base (25% du prix marché joueur) ────────────────────────────
# Utilisées pour les coûts de banque, vente NPC, etc.
# Le marché joueur offre toujours un meilleur retour → encourage l'économie joueur.

# Matériaux : valeur par tier
_MATERIAL_TIER_VALUE: dict[int, int] = {
    1: 12, 2: 38, 3: 100, 4: 250, 5: 750,
    6: 2_000, 7: 5_000, 8: 15_000, 9: 40_000, 10: 120_000,
}

# Consommables : valeur fixe par item_id (25% du prix marché joueur)
# Formule : V_mat[tier] × facteur_type
#   Pain ×4, Infusion/Ration ×6, Potion soin ×5, Élixirs ×8, Élixir crit ×10, Runes ×12
# V_mat : 12/38/100/250/750/2000/5000/15000/40000/120000 (tiers 1→10)
_CONSUMABLE_BASE_VALUE: dict[str, int] = {
    # ALCHIMISTE — Potions de Soin (10 paliers)
    "potion_soin_t1":  60,          "potion_soin_t2":  190,         "potion_soin_t3":  500,
    "potion_soin_t4":  1_250,       "potion_soin_t5":  3_750,       "potion_soin_t6":  10_000,
    "potion_soin_t7":  25_000,      "potion_soin_t8":  75_000,      "potion_soin_t9":  200_000,
    "potion_soin_t10": 600_000,
    # ALCHIMISTE — Élixir de Force (10 paliers)
    "elixir_force_t1":  100,        "elixir_force_t2":  300,        "elixir_force_t3":  800,
    "elixir_force_t4":  2_000,      "elixir_force_t5":  6_000,      "elixir_force_t6":  16_000,
    "elixir_force_t7":  40_000,     "elixir_force_t8":  120_000,    "elixir_force_t9":  320_000,
    "elixir_force_t10": 960_000,
    # ALCHIMISTE — Élixir de Magie (10 paliers)
    "elixir_magie_t1":  100,        "elixir_magie_t2":  300,        "elixir_magie_t3":  800,
    "elixir_magie_t4":  2_000,      "elixir_magie_t5":  6_000,      "elixir_magie_t6":  16_000,
    "elixir_magie_t7":  40_000,     "elixir_magie_t8":  120_000,    "elixir_magie_t9":  320_000,
    "elixir_magie_t10": 960_000,
    # ALCHIMISTE — Élixir de Défense Physique (10 paliers)
    "elixir_def_p_t1":  100,        "elixir_def_p_t2":  300,        "elixir_def_p_t3":  800,
    "elixir_def_p_t4":  2_000,      "elixir_def_p_t5":  6_000,      "elixir_def_p_t6":  16_000,
    "elixir_def_p_t7":  40_000,     "elixir_def_p_t8":  120_000,    "elixir_def_p_t9":  320_000,
    "elixir_def_p_t10": 960_000,
    # ALCHIMISTE — Élixir de Défense Magique (10 paliers)
    "elixir_def_m_t1":  100,        "elixir_def_m_t2":  300,        "elixir_def_m_t3":  800,
    "elixir_def_m_t4":  2_000,      "elixir_def_m_t5":  6_000,      "elixir_def_m_t6":  16_000,
    "elixir_def_m_t7":  40_000,     "elixir_def_m_t8":  120_000,    "elixir_def_m_t9":  320_000,
    "elixir_def_m_t10": 960_000,
    # ALCHIMISTE — Élixir de Vitesse (10 paliers)
    "elixir_vit_t1":  100,          "elixir_vit_t2":  300,          "elixir_vit_t3":  800,
    "elixir_vit_t4":  2_000,        "elixir_vit_t5":  6_000,        "elixir_vit_t6":  16_000,
    "elixir_vit_t7":  40_000,       "elixir_vit_t8":  120_000,      "elixir_vit_t9":  320_000,
    "elixir_vit_t10": 960_000,
    # ALCHIMISTE — Élixir de Dégâts Critiques (10 paliers, ×10 sur V_mat)
    "elixir_crit_t1":  120,         "elixir_crit_t2":  375,         "elixir_crit_t3":  1_000,
    "elixir_crit_t4":  2_500,       "elixir_crit_t5":  7_500,       "elixir_crit_t6":  20_000,
    "elixir_crit_t7":  50_000,      "elixir_crit_t8":  150_000,     "elixir_crit_t9":  400_000,
    "elixir_crit_t10": 1_200_000,
    # ALCHIMISTE — Élixir Royal (unique endgame, toutes stats +20%)
    "elixir_royal": 3_000_000,
    # ALCHIMISTE — Potions spéciales
    "potion_renforcement":    50_000,
    "potion_resurrection":   500_000,
    "potion_affaiblissement": 100_000,
    # BOULANGER — Pain (énergie directe, 10 paliers)
    "pain_t1":  50,                 "pain_t2":  150,                "pain_t3":  400,
    "pain_t4":  1_000,              "pain_t5":  3_000,              "pain_t6":  8_000,
    "pain_t7":  20_000,             "pain_t8":  60_000,             "pain_t9":  160_000,
    "pain_t10": 480_000,
    # BOULANGER — Infusion (regen énergie passif 1h, 10 paliers)
    "infusion_t1":  75,             "infusion_t2":  225,            "infusion_t3":  600,
    "infusion_t4":  1_500,          "infusion_t5":  4_500,          "infusion_t6":  12_000,
    "infusion_t7":  30_000,         "infusion_t8":  90_000,         "infusion_t9":  240_000,
    "infusion_t10": 720_000,
    # BOULANGER — Ration de Victoire (énergie/victoire, 3 combats, 10 paliers)
    "ration_vic_t1":  75,           "ration_vic_t2":  225,          "ration_vic_t3":  600,
    "ration_vic_t4":  1_500,        "ration_vic_t5":  4_500,        "ration_vic_t6":  12_000,
    "ration_vic_t7":  30_000,       "ration_vic_t8":  90_000,       "ration_vic_t9":  240_000,
    "ration_vic_t10": 720_000,
    # BOULANGER — Repas Légendaire (unique endgame, énergie+regen+victoire)
    "repas_legendaire": 2_000_000,
    # ENCHANTEUR — Rune de Force (10 paliers)
    "rune_force_t1":  150,          "rune_force_t2":  450,          "rune_force_t3":  1_200,
    "rune_force_t4":  3_000,        "rune_force_t5":  9_000,        "rune_force_t6":  24_000,
    "rune_force_t7":  60_000,       "rune_force_t8":  180_000,      "rune_force_t9":  480_000,
    "rune_force_t10": 1_500_000,
    # ENCHANTEUR — Rune de Magie (10 paliers)
    "rune_magie_t1":  150,          "rune_magie_t2":  450,          "rune_magie_t3":  1_200,
    "rune_magie_t4":  3_000,        "rune_magie_t5":  9_000,        "rune_magie_t6":  24_000,
    "rune_magie_t7":  60_000,       "rune_magie_t8":  180_000,      "rune_magie_t9":  480_000,
    "rune_magie_t10": 1_500_000,
    # ENCHANTEUR — Rune de Défense Physique (10 paliers)
    "rune_def_p_t1":  150,          "rune_def_p_t2":  450,          "rune_def_p_t3":  1_200,
    "rune_def_p_t4":  3_000,        "rune_def_p_t5":  9_000,        "rune_def_p_t6":  24_000,
    "rune_def_p_t7":  60_000,       "rune_def_p_t8":  180_000,      "rune_def_p_t9":  480_000,
    "rune_def_p_t10": 1_500_000,
    # ENCHANTEUR — Rune de Défense Magique (10 paliers)
    "rune_def_m_t1":  150,          "rune_def_m_t2":  450,          "rune_def_m_t3":  1_200,
    "rune_def_m_t4":  3_000,        "rune_def_m_t5":  9_000,        "rune_def_m_t6":  24_000,
    "rune_def_m_t7":  60_000,       "rune_def_m_t8":  180_000,      "rune_def_m_t9":  480_000,
    "rune_def_m_t10": 1_500_000,
    # ENCHANTEUR — Rune de Vitesse (10 paliers)
    "rune_vit_t1":  150,            "rune_vit_t2":  450,            "rune_vit_t3":  1_200,
    "rune_vit_t4":  3_000,          "rune_vit_t5":  9_000,          "rune_vit_t6":  24_000,
    "rune_vit_t7":  60_000,         "rune_vit_t8":  180_000,        "rune_vit_t9":  480_000,
    "rune_vit_t10": 1_500_000,
    # ENCHANTEUR — Rune de Critique (10 paliers)
    "rune_crit_t1":  150,           "rune_crit_t2":  450,           "rune_crit_t3":  1_200,
    "rune_crit_t4":  3_000,         "rune_crit_t5":  9_000,         "rune_crit_t6":  24_000,
    "rune_crit_t7":  60_000,        "rune_crit_t8":  180_000,       "rune_crit_t9":  480_000,
    "rune_crit_t10": 1_500_000,
    # ENCHANTEUR — Rune Divine (unique endgame, toutes stats +10%)
    "rune_divine": 5_000_000,
}

# Multiplicateurs de rareté et de source pour les équipements
_RARITY_VALUE_MULT: dict[str, float] = {
    "commun":       1.0,
    "peu commun":   2.0,
    "rare":         5.0,
    "épique":       12.0,
    "légendaire":   30.0,
    "mythique":     80.0,
    "artefact":     200.0,
    "divin":        500.0,
    "transcendant": 1200.0,
    "prismatique":  3000.0,
}
_SOURCE_VALUE_MULT: dict[str, float] = {
    "monde": 1.0, "donjon_classique": 1.4, "craft": 1.8,
    "donjon_elite": 2.2, "donjon_abyssal": 3.0, "raid": 4.5,
}


def get_material_value(item_id: str) -> int:
    """Valeur de base d'un matériau (25% du prix marché joueur)."""
    tier = MATERIALS.get(item_id, {}).get("tier", 1)
    return _MATERIAL_TIER_VALUE.get(tier, 12)


def get_consumable_value(item_id: str) -> int:
    """Valeur de base d'un consommable (25% du prix marché joueur)."""
    return _CONSUMABLE_BASE_VALUE.get(item_id, 0)


def get_equipment_value(item_level: int, rarity: str, source: str = "monde",
                         enhancement: int = 0) -> int:
    """Valeur de base d'un équipement (25% du prix marché joueur).

    Formule : item_level × 25 × rarity_mult × source_mult × (1 + enhancement × 0.10)
    """
    rarity_mult = _RARITY_VALUE_MULT.get(rarity, 1.0)
    source_mult = _SOURCE_VALUE_MULT.get(source, 1.0)
    enh_bonus   = 1 + enhancement * 0.10
    return max(1, int(item_level * 25 * rarity_mult * source_mult * enh_bonus))


# ─── Loot tables ───────────────────────────────────────────────────────────
# Taux de drop des matériaux par zone (en %)
# Les équipements sont rares : max 1 par combat sauf boss emblématiques/antiques/raids

def get_material_drop_table(zone: int, harvest_profession: str = None, harvest_level: int = 0, tier_cap: int = 10) -> list[dict]:
    """
    Retourne une liste de drops avec leur chance effective (peut dépasser 100%).
    La quantité se calcule côté appelant via le mécanisme d'overflow :
      qty = int(chance / 100) + (1 si random < chance % 100)
    Ainsi 125% = 1 garanti + 25% pour un 2ème ; 350% = 3 garantis + 50% pour un 4ème.

    Multiplicateur linéaire :  1 + harvest_level / 10 + zone / 1000
    (harvest_level ≈ zone / 100, donc mult ≈ 1 + zone / 500 en pratique)

    Ton métier  : base élevée (23.5%→1% selon tier 1-10), débloqué par harvest_level (tier N = level (N-1)×10)
    Autre métier : base faible (2.35%→0.1%), limité au tier_cap
    tier_cap : tier maximum autorisé (tous métiers confondus). Calculé = harvest_level // 10 + 1.
    """
    drops = []

    # Multiplicateur linéaire — double contribution : harvest_level et zone
    multiplier = 1 + harvest_level / 10 + zone / 1000

    for mat_id, mat_data in MATERIALS.items():
        tier = mat_data["tier"]
        prof = mat_data["profession"]

        # Blocage global au tier_cap (évite les drops trop avancés pour le niveau du joueur)
        if tier > tier_cap:
            continue

        if harvest_profession == prof:
            min_level_for_tier = (tier - 1) * 10
            if harvest_level < min_level_for_tier:
                continue
            base_chance = max(0.25, (26 - tier * 2.5) / 2)  # tier1=11.75%, tier9=1.75%, tier10=0.5%
        else:
            # Hors métier : 10× plus rare
            base_chance = max(0.025, (26 - tier * 2.5) / 20)  # tier1=1.175%, tier9=0.175%, tier10=0.05%
        effective_chance = base_chance * multiplier

        drops.append({"item_id": mat_id, "chance": round(effective_chance, 2)})
    return drops


def max_ingredient_tier(ingredients: dict) -> int:
    """Retourne le tier maximum parmi tous les ingrédients d'une recette."""
    max_tier = 0
    for item_id in ingredients:
        mat = MATERIALS.get(item_id)
        if mat:
            max_tier = max(max_tier, mat["tier"])
    return max_tier



def _zone_rarity_weights(zone: int, is_emblematic: bool, is_antique: bool, raid_level: int = 0) -> list[float]:
    """Poids des raretés selon la zone et le type de combat.

    Distribution en cloche qui se déplace le long des raretés avec la zone.
    Interpolation linéaire par morceaux entre les keyframes :

    Zone     1 : [100,  0,  0,  0,  0,  0,  0,  0,  0,  0]  (100% commun)
    Zone  2000 : [ 20, 50, 20,  8,  2,  0,  0,  0,  0,  0]  (peu commun peak 50%)
    Zone  4000 : [  0, 10, 20, 20, 18, 15, 10,  5,  2,  0]  (rare/épique co-peak, cap 20%)
    Zone  6000 : [  0,  2, 10, 18, 20, 20, 18,  8,  3,  1]  (légend/mythique co-peak, cap 20%)
    Zone  8000 : [  0,  0,  8, 14, 18, 20, 20, 15,  4,  1]  (mythique/artefact, transcendant/prisma encore rares)
    Zone 10000 : [  0,  0,  5, 10, 15, 20, 20, 15, 10,  5]  (stable endgame, cap 20%)

    Boost raid : base [0, 0, 0.5, 1, 2, 3, 3, 3, 3, 2] × raid_level
    → progression croissante vers les hautes raretés, Raid 10 nettement meilleur que Zone 10000 monde.
    """
    _KEYFRAMES = [
        (    1, [100.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, 0.0]),
        ( 2000, [ 20.0, 50.0, 20.0,  8.0,  2.0,  0.0,  0.0,  0.0,  0.0, 0.0]),
        ( 4000, [  0.0, 10.0, 20.0, 20.0, 18.0, 15.0, 10.0,  5.0,  2.0, 0.0]),
        ( 6000, [  0.0,  2.0, 10.0, 18.0, 20.0, 20.0, 18.0,  8.0,  3.0, 1.0]),
        ( 8000, [  0.0,  0.0,  8.0, 14.0, 18.0, 20.0, 20.0, 15.0,  4.0, 1.0]),
        (10000, [  0.0,  0.0,  5.0, 10.0, 15.0, 20.0, 20.0, 15.0, 10.0, 5.0]),
    ]
    z = min(max(zone, 1), 10000)
    weights = _KEYFRAMES[-1][1][:]
    for i in range(len(_KEYFRAMES) - 1):
        z0, w0 = _KEYFRAMES[i]
        z1, w1 = _KEYFRAMES[i + 1]
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            weights = [a + (b - a) * t for a, b in zip(w0, w1)]
            break
    boost = [0.0] * 10
    if is_emblematic:
        boost = [0, 0, 2, 3, 5, 5, 4, 2, 0.5, 0.1]
    if is_antique:
        boost = [0, 0, 0, 2, 4, 6, 6, 5, 2, 0.5]
    if raid_level > 0:
        r = raid_level
        boost = [0, 0, 0.5*r, 1*r, 2*r, 3*r, 3*r, 3*r, 3*r, 2*r]
    return [max(0.01, w + b) for w, b in zip(weights, boost)]


def get_equipment_drops(
    zone: int,
    player_class: str,
    drop_type: str,
    drop_source: str = "monde",
    raid_level: int = 0,
) -> list[dict]:
    """
    Retourne une liste d'équipements droppés selon le type de rencontre.

    drop_type :
      - "monster"           → 10% same class, 1% other
      - "boss_classique"    → 50% same class, 10% other
      - "boss_emblematique" → 100% same class, 50% other
      - "boss_antique"      → 3× same class garanti, 1× other garanti
      - "dungeon"           → 1 item garanti : 80% same class, 20% other
      - "raid"              → 1 item par slot (7 total), classe 100% aléatoire
    """
    import random
    from bot.cogs.rpg.models import SET_BONUSES, SLOTS, RARITIES, ALL_CLASSES

    is_emblematic = drop_type == "boss_emblematique"
    is_antique    = drop_type == "boss_antique"

    def _make_item(use_player_class: bool, forced_slot: str = None) -> dict | None:
        if use_player_class:
            target_class = player_class
        else:
            others = [c for c in ALL_CLASSES if c != player_class]
            target_class = random.choice(others) if others else player_class

        candidate_sets = [
            sk for sk, sd in SET_BONUSES.items()
            if sd["class"] == target_class and sd["source"] == drop_source
        ]
        if not candidate_sets:
            candidate_sets = [sk for sk, sd in SET_BONUSES.items() if sd["class"] == target_class]
        if not candidate_sets:
            return None

        chosen_set  = random.choice(candidate_sets)
        chosen_slot = forced_slot if forced_slot is not None else random.choice(SLOTS)
        item_id     = f"eq_{chosen_set}_{chosen_slot}"

        rw = _zone_rarity_weights(zone, is_emblematic, is_antique, raid_level)
        rarity = random.choices(RARITIES, weights=rw, k=1)[0]

        # item_level = zone_equiv / 10 partout (linéaire) — capé à 1000 à zone 10 000
        item_level = max(1, min(zone // 10, 1000))

        return {"item_id": item_id, "rarity": rarity, "enhancement": 0, "level": item_level}

    results = []

    if drop_type == "monster":
        if random.random() * 100 < 10:
            item = _make_item(True)
            if item: results.append(item)
        if random.random() * 100 < 1:
            item = _make_item(False)
            if item: results.append(item)

    elif drop_type == "boss_classique":
        if random.random() * 100 < 50:
            item = _make_item(True)
            if item: results.append(item)
        if random.random() * 100 < 10:
            item = _make_item(False)
            if item: results.append(item)

    elif drop_type == "boss_emblematique":
        item = _make_item(True)
        if item: results.append(item)
        if random.random() * 100 < 50:
            item = _make_item(False)
            if item: results.append(item)

    elif drop_type == "boss_antique":
        for _ in range(3):
            item = _make_item(True)
            if item: results.append(item)
        item = _make_item(False)
        if item: results.append(item)

    elif drop_type == "dungeon":
        use_same = random.random() * 100 < 80
        item = _make_item(use_same)
        if item: results.append(item)

    elif drop_type == "raid":
        for slot in SLOTS:
            target_class = random.choice(ALL_CLASSES)
            item = _make_item(target_class == player_class, forced_slot=slot)
            if item: results.append(item)

    return results


_RUNE_STAT_EMOJI = {
    "hp": "❤️", "p_atk": "⚔️", "m_atk": "✨", "p_def": "🛡️", "m_def": "🔷",
    "p_pen": "🗡️", "m_pen": "💫", "speed": "⚡", "crit_chance": "🎯", "crit_damage": "💥",
    "all_stats": "🌟",
}

_RUNE_SUFFIX_TIER = {"_p": 1, "_m": 2, "_g": 3, "_tg": 4, "_x": 5, "_u": 6}

def _build_rune_tier_lookup() -> dict:
    """Construit un dict {(effect, value): tier} à partir de CONSUMABLES."""
    lookup = {}
    for rune_id, data in CONSUMABLES.items():
        if data.get("type") != "rune":
            continue
        effect = data.get("effect", "")
        value  = data.get("value", 0)
        tier   = None
        for suffix, t in _RUNE_SUFFIX_TIER.items():
            if rune_id.endswith(suffix):
                tier = t
                break
        if tier is not None:
            lookup[(effect, value)] = tier
    return lookup

_RUNE_TIER_LOOKUP: dict = {}  # rempli à la première utilisation


def _get_rune_tier(effect: str, value: int) -> str | None:
    """Retourne 'T1'…'T6' pour une rune, ou None si non trouvée."""
    global _RUNE_TIER_LOOKUP
    if not _RUNE_TIER_LOOKUP:
        _RUNE_TIER_LOOKUP = _build_rune_tier_lookup()
    t = _RUNE_TIER_LOOKUP.get((effect, value))
    return f"T{t}" if t is not None else None


def format_item_name(item_id: str, rarity: str = None, enhancement: int = 0, rune_bonuses: dict = None) -> str:
    """Retourne un nom formaté pour un item.
    Si rune_bonuses est fourni (dict non-vide), ajoute un résumé condensé en suffixe.
    """
    from bot.cogs.rpg.models import RARITY_EMOJI
    if item_id in EQUIPMENT_CATALOG:
        name = EQUIPMENT_CATALOG[item_id]["name"]
    elif item_id in MATERIALS:
        name = MATERIALS[item_id]["name"]
    elif item_id in CONSUMABLES:
        name = CONSUMABLES[item_id]["name"]
    else:
        name = item_id

    parts = []
    if rarity:
        parts.append(RARITY_EMOJI.get(rarity, ""))
    parts.append(name)
    if enhancement and enhancement > 0:
        parts.append(f"+{enhancement}")
    base = " ".join(p for p in parts if p)

    if rune_bonuses:
        rune_parts = []
        tier_label = None
        for k, v in rune_bonuses.items():
            rune_parts.append(f"{_RUNE_STAT_EMOJI.get(k, k)}+{v}")
            if tier_label is None:
                tier_label = _get_rune_tier(k, v)
        tier_txt = tier_label if tier_label else ""
        base += f" [🔮{tier_txt} {' '.join(rune_parts)}]"

    return base


def format_eq_name(item: dict) -> str:
    """Raccourci pour formater un item depuis son dict DB (parse rune_bonuses automatiquement)."""
    import json
    rb = json.loads(item.get("rune_bonuses") or "{}") or None
    return format_item_name(item["item_id"], item.get("rarity"), item.get("enhancement", 0), rb)
