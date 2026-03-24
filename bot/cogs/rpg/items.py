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

# Boost de taux de drop par niveau de métier de récolte (en %)
def harvest_drop_bonus(level: int) -> float:
    return min(level * 0.5, 50.0)  # max +50%

# ─── Consommables ──────────────────────────────────────────────────────────
CONSUMABLES: dict[str, dict] = {
    # ALCHIMISTE — Potion de Soin (6 paliers)
    "potion_soin_petite":      {"name": "Petite Potion de Soin",      "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 10,  "emoji": "🧪"},
    "potion_soin_moyenne":     {"name": "Potion de Soin",             "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 20,  "emoji": "🧪"},
    "potion_soin_grande":      {"name": "Grande Potion de Soin",      "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 40,  "emoji": "💊"},
    "potion_soin_tres_grande":  {"name": "Très Grande Potion de Soin","type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 60,  "emoji": "💊"},
    "potion_soin_giga":        {"name": "Giga Potion de Soin",        "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 80,  "emoji": "✨"},
    "potion_soin_ultime":      {"name": "Potion de Soin Ultime",      "type": "potion",  "profession": "alchimiste", "effect": "heal_pct",     "value": 100, "emoji": "🌟"},
    # ALCHIMISTE — Élixir de Force (6 paliers)
    "elixir_force_petit":      {"name": "Petit Élixir de Force",      "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 3,   "emoji": "💪"},
    "elixir_force_moyen":      {"name": "Élixir de Force",            "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 5,   "emoji": "💪"},
    "elixir_force_grand":      {"name": "Grand Élixir de Force",      "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 8,   "emoji": "💪"},
    "elixir_force_tres_grand": {"name": "Très Grand Élixir de Force", "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 12,  "emoji": "💪"},
    "elixir_force_giga":       {"name": "Giga Élixir de Force",       "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 16,  "emoji": "💪"},
    "elixir_force_ultime":     {"name": "Élixir de Force Ultime",     "type": "elixir",  "profession": "alchimiste", "effect": "p_atk_pct",   "value": 20,  "emoji": "💪"},
    # ALCHIMISTE — Élixir de Magie (6 paliers)
    "elixir_magie_petit":      {"name": "Petit Élixir de Magie",      "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 3,   "emoji": "🔮"},
    "elixir_magie_moyen":      {"name": "Élixir de Magie",            "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 5,   "emoji": "🔮"},
    "elixir_magie_grand":      {"name": "Grand Élixir de Magie",      "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 8,   "emoji": "🔮"},
    "elixir_magie_tres_grand": {"name": "Très Grand Élixir de Magie", "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 12,  "emoji": "🔮"},
    "elixir_magie_giga":       {"name": "Giga Élixir de Magie",       "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 16,  "emoji": "🔮"},
    "elixir_magie_ultime":     {"name": "Élixir de Magie Ultime",     "type": "elixir",  "profession": "alchimiste", "effect": "m_atk_pct",   "value": 20,  "emoji": "🔮"},
    # ALCHIMISTE — Élixir de Défense (6 paliers, boost p_def + m_def)
    "elixir_def_petit":        {"name": "Petit Élixir de Défense",    "type": "elixir",  "profession": "alchimiste", "effect": "def_pct",     "value": 2,   "emoji": "🛡️"},
    "elixir_def_moyen":        {"name": "Élixir de Défense",          "type": "elixir",  "profession": "alchimiste", "effect": "def_pct",     "value": 4,   "emoji": "🛡️"},
    "elixir_def_grand":        {"name": "Grand Élixir de Défense",    "type": "elixir",  "profession": "alchimiste", "effect": "def_pct",     "value": 6,   "emoji": "🛡️"},
    "elixir_def_tres_grand":   {"name": "Très Grand Élixir de Défense","type": "elixir", "profession": "alchimiste", "effect": "def_pct",     "value": 9,   "emoji": "🛡️"},
    "elixir_def_giga":         {"name": "Giga Élixir de Défense",     "type": "elixir",  "profession": "alchimiste", "effect": "def_pct",     "value": 12,  "emoji": "🛡️"},
    "elixir_def_ultime":       {"name": "Élixir de Défense Ultime",   "type": "elixir",  "profession": "alchimiste", "effect": "def_pct",     "value": 15,  "emoji": "🛡️"},
    # ALCHIMISTE — Élixir de Vitesse (6 paliers)
    "elixir_vit_petit":        {"name": "Petit Élixir de Vitesse",    "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 2,   "emoji": "⚡"},
    "elixir_vit_moyen":        {"name": "Élixir de Vitesse",          "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 4,   "emoji": "⚡"},
    "elixir_vit_grand":        {"name": "Grand Élixir de Vitesse",    "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 6,   "emoji": "⚡"},
    "elixir_vit_tres_grand":   {"name": "Très Grand Élixir de Vitesse","type": "elixir", "profession": "alchimiste", "effect": "speed_pct",   "value": 9,   "emoji": "⚡"},
    "elixir_vit_giga":         {"name": "Giga Élixir de Vitesse",     "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 12,  "emoji": "⚡"},
    "elixir_vit_ultime":       {"name": "Élixir de Vitesse Ultime",   "type": "elixir",  "profession": "alchimiste", "effect": "speed_pct",   "value": 15,  "emoji": "⚡"},
    # ALCHIMISTE — Élixir de Critique (6 paliers)
    "elixir_crit_petit":       {"name": "Petit Élixir de Critique",   "type": "elixir",  "profession": "alchimiste", "effect": "crit_pct",    "value": 5,   "emoji": "🎯"},
    "elixir_crit_moyen":       {"name": "Élixir de Critique",         "type": "elixir",  "profession": "alchimiste", "effect": "crit_pct",    "value": 10,  "emoji": "🎯"},
    "elixir_crit_grand":       {"name": "Grand Élixir de Critique",   "type": "elixir",  "profession": "alchimiste", "effect": "crit_pct",    "value": 15,  "emoji": "🎯"},
    "elixir_crit_tres_grand":  {"name": "Très Grand Élixir de Critique","type": "elixir","profession": "alchimiste", "effect": "crit_pct",    "value": 20,  "emoji": "🎯"},
    "elixir_crit_giga":        {"name": "Giga Élixir de Critique",    "type": "elixir",  "profession": "alchimiste", "effect": "crit_pct",    "value": 25,  "emoji": "🎯"},
    "elixir_crit_ultime":      {"name": "Élixir de Critique Ultime",  "type": "elixir",  "profession": "alchimiste", "effect": "crit_pct",    "value": 30,  "emoji": "🎯"},
    # ALCHIMISTE — Élixir Royal (6 paliers, toutes stats)
    "elixir_royal_petit":      {"name": "Petit Élixir Royal",         "type": "elixir",  "profession": "alchimiste", "effect": "all_pct",     "value": 2,   "emoji": "👑"},
    "elixir_royal_moyen":      {"name": "Élixir Royal",               "type": "elixir",  "profession": "alchimiste", "effect": "all_pct",     "value": 4,   "emoji": "👑"},
    "elixir_royal_grand":      {"name": "Grand Élixir Royal",         "type": "elixir",  "profession": "alchimiste", "effect": "all_pct",     "value": 6,   "emoji": "👑"},
    "elixir_royal_tres_grand": {"name": "Très Grand Élixir Royal",    "type": "elixir",  "profession": "alchimiste", "effect": "all_pct",     "value": 9,   "emoji": "👑"},
    "elixir_royal_giga":       {"name": "Giga Élixir Royal",          "type": "elixir",  "profession": "alchimiste", "effect": "all_pct",     "value": 12,  "emoji": "👑"},
    "elixir_royal_ultime":     {"name": "Élixir Royal Ultime",        "type": "elixir",  "profession": "alchimiste", "effect": "all_pct",     "value": 15,  "emoji": "👑"},
    # ALCHIMISTE — Potions spéciales
    "potion_renforcement":     {"name": "Potion de Renforcement",     "type": "potion",  "profession": "alchimiste", "effect": "no_death_penalty", "value": 1, "emoji": "🔰"},
    "potion_resurrection":     {"name": "Potion de Résurrection",     "type": "potion",  "profession": "alchimiste", "effect": "revive_half_hp",   "value": 1, "emoji": "❤️‍🔥"},
    "potion_protection_ultime":{"name": "Potion de Protection Ultime","type": "potion",  "profession": "alchimiste", "effect": "ignore_passive",   "value": 1, "emoji": "🛡️"},
    # BOULANGER — Type 1 : Pain (énergie directe, 6 paliers)
    "pain_p":              {"name": "Petit Pain",               "type": "food", "profession": "boulanger", "effect": "energy",         "value": 10,  "emoji": "🍞"},
    "pain_m":              {"name": "Miche de Pain",            "type": "food", "profession": "boulanger", "effect": "energy",         "value": 20,  "emoji": "🍞"},
    "pain_g":              {"name": "Pain Artisanal",           "type": "food", "profession": "boulanger", "effect": "energy",         "value": 35,  "emoji": "🥖"},
    "pain_tg":             {"name": "Pain des Anciens",         "type": "food", "profession": "boulanger", "effect": "energy",         "value": 55,  "emoji": "🥖"},
    "pain_x":              {"name": "Pain Enchanté",            "type": "food", "profession": "boulanger", "effect": "energy",         "value": 75,  "emoji": "✨"},
    "pain_u":              {"name": "Pain Divin",               "type": "food", "profession": "boulanger", "effect": "energy",         "value": 100, "emoji": "🌟"},
    # BOULANGER — Type 2 : Infusion (boost regen passive, 6 paliers)
    "infusion_p":          {"name": "Petite Infusion",          "type": "food", "profession": "boulanger", "effect": "energy_regen",   "value": 5,   "emoji": "🍵"},
    "infusion_m":          {"name": "Infusion",                 "type": "food", "profession": "boulanger", "effect": "energy_regen",   "value": 10,  "emoji": "🍵"},
    "infusion_g":          {"name": "Grande Infusion",          "type": "food", "profession": "boulanger", "effect": "energy_regen",   "value": 18,  "emoji": "🍵"},
    "infusion_tg":         {"name": "Très Grande Infusion",     "type": "food", "profession": "boulanger", "effect": "energy_regen",   "value": 28,  "emoji": "🫖"},
    "infusion_x":          {"name": "Giga Infusion",            "type": "food", "profession": "boulanger", "effect": "energy_regen",   "value": 40,  "emoji": "🫖"},
    "infusion_u":          {"name": "Infusion Légendaire",      "type": "food", "profession": "boulanger", "effect": "energy_regen",   "value": 60,  "emoji": "🌟"},
    # BOULANGER — Type 3 : Ration de Victoire (énergie par victoire, 6 paliers)
    "ration_vic_p":        {"name": "Petite Ration de Victoire","type": "food", "profession": "boulanger", "effect": "energy_on_win",  "value": 5,   "emoji": "🍱"},
    "ration_vic_m":        {"name": "Ration de Victoire",       "type": "food", "profession": "boulanger", "effect": "energy_on_win",  "value": 10,  "emoji": "🍱"},
    "ration_vic_g":        {"name": "Grande Ration de Victoire","type": "food", "profession": "boulanger", "effect": "energy_on_win",  "value": 18,  "emoji": "🍱"},
    "ration_vic_tg":       {"name": "Ration du Conquérant",     "type": "food", "profession": "boulanger", "effect": "energy_on_win",  "value": 28,  "emoji": "⚔️"},
    "ration_vic_x":        {"name": "Ration du Héros",          "type": "food", "profession": "boulanger", "effect": "energy_on_win",  "value": 40,  "emoji": "⚔️"},
    "ration_vic_u":        {"name": "Ration Légendaire",        "type": "food", "profession": "boulanger", "effect": "energy_on_win",  "value": 60,  "emoji": "🌟"},
    # BOULANGER — Type 4 : Soupe Fortifiante (énergie + def, 3 paliers)
    "soupe_fort_p":        {"name": "Soupe Fortifiante",        "type": "food", "profession": "boulanger", "effect": "energy_def_pct", "value": 15, "combat_value": 3,  "emoji": "🍲"},
    "soupe_fort_g":        {"name": "Grande Soupe Fortifiante", "type": "food", "profession": "boulanger", "effect": "energy_def_pct", "value": 35, "combat_value": 6,  "emoji": "🍲"},
    "soupe_fort_u":        {"name": "Soupe Ultime",             "type": "food", "profession": "boulanger", "effect": "energy_def_pct", "value": 70, "combat_value": 12, "emoji": "🌟"},
    # BOULANGER — Type 5 : Pâtisserie (énergie + speed, 3 paliers)
    "patisserie_p":        {"name": "Pâtisserie Légère",        "type": "food", "profession": "boulanger", "effect": "energy_speed_pct","value": 15, "combat_value": 3, "emoji": "🍰"},
    "patisserie_g":        {"name": "Grande Pâtisserie",        "type": "food", "profession": "boulanger", "effect": "energy_speed_pct","value": 35, "combat_value": 6, "emoji": "🍰"},
    "patisserie_u":        {"name": "Pâtisserie Enchantée",     "type": "food", "profession": "boulanger", "effect": "energy_speed_pct","value": 70, "combat_value": 12,"emoji": "🌟"},
    # BOULANGER — Type 6 : Repas du Guerrier (énergie + p_atk, 3 paliers)
    "repas_guerrier_p":    {"name": "Repas du Guerrier",        "type": "food", "profession": "boulanger", "effect": "energy_patk_pct","value": 15, "combat_value": 2,  "emoji": "🍖"},
    "repas_guerrier_g":    {"name": "Grand Repas du Guerrier",  "type": "food", "profession": "boulanger", "effect": "energy_patk_pct","value": 35, "combat_value": 5,  "emoji": "🍖"},
    "repas_guerrier_u":    {"name": "Repas du Berserker",       "type": "food", "profession": "boulanger", "effect": "energy_patk_pct","value": 70, "combat_value": 10, "emoji": "🌟"},
    # BOULANGER — Type 7 : Délice Mystique (énergie + m_atk, 3 paliers)
    "delice_mys_p":        {"name": "Délice Mystique",          "type": "food", "profession": "boulanger", "effect": "energy_matk_pct","value": 15, "combat_value": 2,  "emoji": "🧁"},
    "delice_mys_g":        {"name": "Grand Délice Mystique",    "type": "food", "profession": "boulanger", "effect": "energy_matk_pct","value": 35, "combat_value": 5,  "emoji": "🧁"},
    "delice_mys_u":        {"name": "Délice des Arcanes",       "type": "food", "profession": "boulanger", "effect": "energy_matk_pct","value": 70, "combat_value": 10, "emoji": "🌟"},
    # BOULANGER — Types 8-10 : spéciaux haut niveau (energy_all : energy+regen+win)
    "festin_aventurier":   {"name": "Festin de l'Aventurier",   "type": "food", "profession": "boulanger", "effect": "energy_all", "value": 50, "regen_bonus": 20, "win_bonus": 15, "emoji": "🍽️"},
    "banquet_champion":    {"name": "Banquet du Champion",      "type": "food", "profession": "boulanger", "effect": "energy_all", "value": 80, "regen_bonus": 35, "win_bonus": 25, "emoji": "🫕"},
    "repas_legendaire":    {"name": "Repas Légendaire",         "type": "food", "profession": "boulanger", "effect": "energy_all", "value": 120,"regen_bonus": 60, "win_bonus": 40, "emoji": "🌟"},
    # ENCHANTEUR — Rune de Force (p_atk, 6 paliers)
    "rune_force_p":        {"name": "Petite Rune de Force",        "type": "rune", "profession": "enchanteur", "effect": "p_atk",     "value": 30,   "emoji": "🔴"},
    "rune_force_m":        {"name": "Rune de Force",               "type": "rune", "profession": "enchanteur", "effect": "p_atk",     "value": 70,   "emoji": "🔴"},
    "rune_force_g":        {"name": "Grande Rune de Force",        "type": "rune", "profession": "enchanteur", "effect": "p_atk",     "value": 120,  "emoji": "🔴"},
    "rune_force_tg":       {"name": "Très Grande Rune de Force",   "type": "rune", "profession": "enchanteur", "effect": "p_atk",     "value": 180,  "emoji": "🔴"},
    "rune_force_x":        {"name": "Giga Rune de Force",          "type": "rune", "profession": "enchanteur", "effect": "p_atk",     "value": 260,  "emoji": "🔴"},
    "rune_force_u":        {"name": "Rune de Force Ultime",        "type": "rune", "profession": "enchanteur", "effect": "p_atk",     "value": 400,  "emoji": "🔴"},
    # ENCHANTEUR — Rune de Magie (m_atk, 6 paliers)
    "rune_magie_p":        {"name": "Petite Rune de Magie",        "type": "rune", "profession": "enchanteur", "effect": "m_atk",     "value": 30,   "emoji": "🔵"},
    "rune_magie_m":        {"name": "Rune de Magie",               "type": "rune", "profession": "enchanteur", "effect": "m_atk",     "value": 70,   "emoji": "🔵"},
    "rune_magie_g":        {"name": "Grande Rune de Magie",        "type": "rune", "profession": "enchanteur", "effect": "m_atk",     "value": 120,  "emoji": "🔵"},
    "rune_magie_tg":       {"name": "Très Grande Rune de Magie",   "type": "rune", "profession": "enchanteur", "effect": "m_atk",     "value": 180,  "emoji": "🔵"},
    "rune_magie_x":        {"name": "Giga Rune de Magie",          "type": "rune", "profession": "enchanteur", "effect": "m_atk",     "value": 260,  "emoji": "🔵"},
    "rune_magie_u":        {"name": "Rune de Magie Ultime",        "type": "rune", "profession": "enchanteur", "effect": "m_atk",     "value": 400,  "emoji": "🔵"},
    # ENCHANTEUR — Rune de Défense Physique (p_def, 6 paliers)
    "rune_def_p_p":        {"name": "Petite Rune de Déf. Physique","type": "rune", "profession": "enchanteur", "effect": "p_def",     "value": 25,   "emoji": "🟡"},
    "rune_def_p_m":        {"name": "Rune de Déf. Physique",       "type": "rune", "profession": "enchanteur", "effect": "p_def",     "value": 55,   "emoji": "🟡"},
    "rune_def_p_g":        {"name": "Grande Rune de Déf. Physique","type": "rune", "profession": "enchanteur", "effect": "p_def",     "value": 90,   "emoji": "🟡"},
    "rune_def_p_tg":       {"name": "Très Grande Rune de Déf. Phy.","type": "rune","profession": "enchanteur", "effect": "p_def",     "value": 135,  "emoji": "🟡"},
    "rune_def_p_x":        {"name": "Giga Rune de Déf. Physique",  "type": "rune", "profession": "enchanteur", "effect": "p_def",     "value": 195,  "emoji": "🟡"},
    "rune_def_p_u":        {"name": "Rune de Déf. Physique Ultime","type": "rune", "profession": "enchanteur", "effect": "p_def",     "value": 300,  "emoji": "🟡"},
    # ENCHANTEUR — Rune de Défense Magique (m_def, 6 paliers)
    "rune_def_m_p":        {"name": "Petite Rune de Déf. Magique", "type": "rune", "profession": "enchanteur", "effect": "m_def",     "value": 25,   "emoji": "🟢"},
    "rune_def_m_m":        {"name": "Rune de Déf. Magique",        "type": "rune", "profession": "enchanteur", "effect": "m_def",     "value": 55,   "emoji": "🟢"},
    "rune_def_m_g":        {"name": "Grande Rune de Déf. Magique", "type": "rune", "profession": "enchanteur", "effect": "m_def",     "value": 90,   "emoji": "🟢"},
    "rune_def_m_tg":       {"name": "Très Grande Rune de Déf. Mag.","type": "rune","profession": "enchanteur", "effect": "m_def",     "value": 135,  "emoji": "🟢"},
    "rune_def_m_x":        {"name": "Giga Rune de Déf. Magique",   "type": "rune", "profession": "enchanteur", "effect": "m_def",     "value": 195,  "emoji": "🟢"},
    "rune_def_m_u":        {"name": "Rune de Déf. Magique Ultime", "type": "rune", "profession": "enchanteur", "effect": "m_def",     "value": 300,  "emoji": "🟢"},
    # ENCHANTEUR — Rune de Vitesse (speed, 6 paliers)
    "rune_vit_p":          {"name": "Petite Rune de Vitesse",      "type": "rune", "profession": "enchanteur", "effect": "speed",     "value": 15,   "emoji": "⚡"},
    "rune_vit_m":          {"name": "Rune de Vitesse",             "type": "rune", "profession": "enchanteur", "effect": "speed",     "value": 35,   "emoji": "⚡"},
    "rune_vit_g":          {"name": "Grande Rune de Vitesse",      "type": "rune", "profession": "enchanteur", "effect": "speed",     "value": 60,   "emoji": "⚡"},
    "rune_vit_tg":         {"name": "Très Grande Rune de Vitesse", "type": "rune", "profession": "enchanteur", "effect": "speed",     "value": 90,   "emoji": "⚡"},
    "rune_vit_x":          {"name": "Giga Rune de Vitesse",        "type": "rune", "profession": "enchanteur", "effect": "speed",     "value": 130,  "emoji": "⚡"},
    "rune_vit_u":          {"name": "Rune de Vitesse Ultime",      "type": "rune", "profession": "enchanteur", "effect": "speed",     "value": 200,  "emoji": "⚡"},
    # ENCHANTEUR — Rune de Critique (crit_chance, 6 paliers)
    "rune_crit_p":         {"name": "Petite Rune de Critique",     "type": "rune", "profession": "enchanteur", "effect": "crit_chance","value": 2,   "emoji": "🎯"},
    "rune_crit_m":         {"name": "Rune de Critique",            "type": "rune", "profession": "enchanteur", "effect": "crit_chance","value": 5,   "emoji": "🎯"},
    "rune_crit_g":         {"name": "Grande Rune de Critique",     "type": "rune", "profession": "enchanteur", "effect": "crit_chance","value": 8,   "emoji": "🎯"},
    "rune_crit_tg":        {"name": "Très Grande Rune de Critique","type": "rune", "profession": "enchanteur", "effect": "crit_chance","value": 12,  "emoji": "🎯"},
    "rune_crit_x":         {"name": "Giga Rune de Critique",       "type": "rune", "profession": "enchanteur", "effect": "crit_chance","value": 18,  "emoji": "🎯"},
    "rune_crit_u":         {"name": "Rune de Critique Ultime",     "type": "rune", "profession": "enchanteur", "effect": "crit_chance","value": 28,  "emoji": "🎯"},
    # ENCHANTEUR — Rune de Pénétration Physique (p_pen, 6 paliers)
    "rune_pen_p_p":        {"name": "Petite Rune de Pén. Physique","type": "rune", "profession": "enchanteur", "effect": "p_pen",     "value": 20,   "emoji": "🟠"},
    "rune_pen_p_m":        {"name": "Rune de Pén. Physique",       "type": "rune", "profession": "enchanteur", "effect": "p_pen",     "value": 45,   "emoji": "🟠"},
    "rune_pen_p_g":        {"name": "Grande Rune de Pén. Physique","type": "rune", "profession": "enchanteur", "effect": "p_pen",     "value": 75,   "emoji": "🟠"},
    "rune_pen_p_tg":       {"name": "Très Grande Rune de Pén. Phy.","type": "rune","profession": "enchanteur", "effect": "p_pen",     "value": 115,  "emoji": "🟠"},
    "rune_pen_p_x":        {"name": "Giga Rune de Pén. Physique",  "type": "rune", "profession": "enchanteur", "effect": "p_pen",     "value": 165,  "emoji": "🟠"},
    "rune_pen_p_u":        {"name": "Rune de Pén. Physique Ultime","type": "rune", "profession": "enchanteur", "effect": "p_pen",     "value": 250,  "emoji": "🟠"},
    # ENCHANTEUR — Rune de Pénétration Magique (m_pen, 6 paliers)
    "rune_pen_m_p":        {"name": "Petite Rune de Pén. Magique", "type": "rune", "profession": "enchanteur", "effect": "m_pen",     "value": 20,   "emoji": "🟣"},
    "rune_pen_m_m":        {"name": "Rune de Pén. Magique",        "type": "rune", "profession": "enchanteur", "effect": "m_pen",     "value": 45,   "emoji": "🟣"},
    "rune_pen_m_g":        {"name": "Grande Rune de Pén. Magique", "type": "rune", "profession": "enchanteur", "effect": "m_pen",     "value": 75,   "emoji": "🟣"},
    "rune_pen_m_tg":       {"name": "Très Grande Rune de Pén. Mag.","type": "rune","profession": "enchanteur", "effect": "m_pen",     "value": 115,  "emoji": "🟣"},
    "rune_pen_m_x":        {"name": "Giga Rune de Pén. Magique",   "type": "rune", "profession": "enchanteur", "effect": "m_pen",     "value": 165,  "emoji": "🟣"},
    "rune_pen_m_u":        {"name": "Rune de Pén. Magique Ultime", "type": "rune", "profession": "enchanteur", "effect": "m_pen",     "value": 250,  "emoji": "🟣"},
    # ENCHANTEUR — Rune de Vie (hp, 6 paliers)
    "rune_vie_p":          {"name": "Petite Rune de Vie",          "type": "rune", "profession": "enchanteur", "effect": "hp",        "value": 100,  "emoji": "❤️"},
    "rune_vie_m":          {"name": "Rune de Vie",                 "type": "rune", "profession": "enchanteur", "effect": "hp",        "value": 250,  "emoji": "❤️"},
    "rune_vie_g":          {"name": "Grande Rune de Vie",          "type": "rune", "profession": "enchanteur", "effect": "hp",        "value": 500,  "emoji": "❤️"},
    "rune_vie_tg":         {"name": "Très Grande Rune de Vie",     "type": "rune", "profession": "enchanteur", "effect": "hp",        "value": 800,  "emoji": "❤️"},
    "rune_vie_x":          {"name": "Giga Rune de Vie",            "type": "rune", "profession": "enchanteur", "effect": "hp",        "value": 1200, "emoji": "❤️"},
    "rune_vie_u":          {"name": "Rune de Vie Ultime",          "type": "rune", "profession": "enchanteur", "effect": "hp",        "value": 2000, "emoji": "❤️"},
    # ENCHANTEUR — Rune Divine (all_stats, 1 palier, niv 100)
    "rune_divine":         {"name": "Rune Divine",                 "type": "rune", "profession": "enchanteur", "effect": "all_stats", "value": 30,   "emoji": "✨"},
}

# Récompense quotidienne par défaut (legacy)
DAILY_DEFAULT_POTION = "potion_soin_petite"
DAILY_DEFAULT_FOOD   = "pain_p"

# ─── Pools pondérés pour la récompense quotidienne ──────────────────────────
# Poids par palier (p, m, g, tg, x) — sans les ultimes
_DAILY_W = [50, 25, 14, 8, 3]

DAILY_POTION_POOL: list[tuple[str, int]] = list(zip([
    "potion_soin_petite", "potion_soin_moyenne", "potion_soin_grande",
    "potion_soin_tres_grande", "potion_soin_giga",
], _DAILY_W))

DAILY_FOOD_POOL: list[tuple[str, int]] = list(zip([
    "pain_p", "pain_m", "pain_g", "pain_tg", "pain_x",
], _DAILY_W))

# Runes : 9 types × 5 paliers (sans _u et sans rune_divine)
_RUNE_TIERS = [
    ("rune_force_p",  "rune_force_m",  "rune_force_g",  "rune_force_tg",  "rune_force_x"),
    ("rune_magie_p",  "rune_magie_m",  "rune_magie_g",  "rune_magie_tg",  "rune_magie_x"),
    ("rune_def_p_p",  "rune_def_p_m",  "rune_def_p_g",  "rune_def_p_tg",  "rune_def_p_x"),
    ("rune_def_m_p",  "rune_def_m_m",  "rune_def_m_g",  "rune_def_m_tg",  "rune_def_m_x"),
    ("rune_vit_p",    "rune_vit_m",    "rune_vit_g",    "rune_vit_tg",    "rune_vit_x"),
    ("rune_crit_p",   "rune_crit_m",   "rune_crit_g",   "rune_crit_tg",   "rune_crit_x"),
    ("rune_pen_p_p",  "rune_pen_p_m",  "rune_pen_p_g",  "rune_pen_p_tg",  "rune_pen_p_x"),
    ("rune_pen_m_p",  "rune_pen_m_m",  "rune_pen_m_g",  "rune_pen_m_tg",  "rune_pen_m_x"),
    ("rune_vie_p",    "rune_vie_m",    "rune_vie_g",    "rune_vie_tg",    "rune_vie_x"),
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
    # ALCHIMISTE — Potion de Soin
    "rec_soin_petite":        {"result": "potion_soin_petite",      "qty": 3, "profession": "alchimiste", "level_req": 1,   "ingredients": {"mat_herbe_soin": 3}},
    "rec_soin_moyenne":       {"result": "potion_soin_moyenne",     "qty": 2, "profession": "alchimiste", "level_req": 5,   "ingredients": {"mat_herbe_soin": 5, "mat_herbe_mana": 1}},
    "rec_soin_grande":        {"result": "potion_soin_grande",      "qty": 2, "profession": "alchimiste", "level_req": 15,  "ingredients": {"mat_herbe_soin": 8, "mat_racine_force": 3}},
    "rec_soin_tres_grande":   {"result": "potion_soin_tres_grande", "qty": 1, "profession": "alchimiste", "level_req": 25,  "ingredients": {"mat_racine_force": 5, "mat_fleur_lune": 3, "mat_herbe_soin": 5}},
    "rec_soin_giga":          {"result": "potion_soin_giga",        "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_fleur_lune": 5, "mat_cristal_vegetal": 4, "mat_champi_venin": 3}},
    "rec_soin_ultime":        {"result": "potion_soin_ultime",      "qty": 1, "profession": "alchimiste", "level_req": 55,  "ingredients": {"mat_lotus_ombre": 4, "mat_epine_dragon": 3, "mat_cristal_vegetal": 4}},
    # ALCHIMISTE — Élixir de Force
    "rec_force_petit":        {"result": "elixir_force_petit",      "qty": 2, "profession": "alchimiste", "level_req": 3,   "ingredients": {"mat_herbe_soin": 3, "mat_herbe_mana": 3}},
    "rec_force_moyen":        {"result": "elixir_force_moyen",      "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_racine_force": 6, "mat_herbe_mana": 3}},
    "rec_force_grand":        {"result": "elixir_force_grand",      "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_racine_force": 6, "mat_pollen_dore": 4}},
    "rec_force_tres_grand":   {"result": "elixir_force_tres_grand", "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_cristal_vegetal": 5, "mat_mousse_ancienne": 4, "mat_racine_force": 4}},
    "rec_force_giga":         {"result": "elixir_force_giga",       "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_epine_dragon": 4, "mat_cristal_vegetal": 4}},
    "rec_force_ultime":       {"result": "elixir_force_ultime",     "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_lotus_ombre": 5, "mat_epine_dragon": 4, "mat_cristal_vegetal": 3}},
    # ALCHIMISTE — Élixir de Magie
    "rec_magie_petit":        {"result": "elixir_magie_petit",      "qty": 2, "profession": "alchimiste", "level_req": 3,   "ingredients": {"mat_herbe_mana": 4}},
    "rec_magie_moyen":        {"result": "elixir_magie_moyen",      "qty": 1, "profession": "alchimiste", "level_req": 10,  "ingredients": {"mat_herbe_mana": 6, "mat_racine_force": 3}},
    "rec_magie_grand":        {"result": "elixir_magie_grand",      "qty": 1, "profession": "alchimiste", "level_req": 30,  "ingredients": {"mat_herbe_mana": 6, "mat_pollen_dore": 4}},
    "rec_magie_tres_grand":   {"result": "elixir_magie_tres_grand", "qty": 1, "profession": "alchimiste", "level_req": 50,  "ingredients": {"mat_cristal_vegetal": 6, "mat_pollen_dore": 4}},
    "rec_magie_giga":         {"result": "elixir_magie_giga",       "qty": 1, "profession": "alchimiste", "level_req": 60,  "ingredients": {"mat_cristal_vegetal": 5, "mat_epine_dragon": 3, "mat_pollen_dore": 3}},
    "rec_magie_ultime":       {"result": "elixir_magie_ultime",     "qty": 1, "profession": "alchimiste", "level_req": 70,  "ingredients": {"mat_lotus_ombre": 5, "mat_cristal_vegetal": 5, "mat_epine_dragon": 3}},
    # ALCHIMISTE — Élixir de Défense
    "rec_def_petit":          {"result": "elixir_def_petit",        "qty": 2, "profession": "alchimiste", "level_req": 5,   "ingredients": {"mat_herbe_soin": 5}},
    "rec_def_moyen":          {"result": "elixir_def_moyen",        "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_fleur_lune": 5, "mat_racine_force": 4}},
    "rec_def_grand":          {"result": "elixir_def_grand",        "qty": 1, "profession": "alchimiste", "level_req": 35,  "ingredients": {"mat_champi_venin": 5, "mat_pollen_dore": 4, "mat_racine_force": 4}},
    "rec_def_tres_grand":     {"result": "elixir_def_tres_grand",   "qty": 1, "profession": "alchimiste", "level_req": 45,  "ingredients": {"mat_mousse_ancienne": 6, "mat_champi_venin": 4, "mat_fleur_lune": 3}},
    "rec_def_giga":           {"result": "elixir_def_giga",         "qty": 1, "profession": "alchimiste", "level_req": 65,  "ingredients": {"mat_epine_dragon": 4, "mat_mousse_ancienne": 6}},
    "rec_def_ultime":         {"result": "elixir_def_ultime",       "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 6, "mat_lotus_ombre": 4, "mat_mousse_ancienne": 4}},
    # ALCHIMISTE — Élixir de Vitesse
    "rec_vit_petit":          {"result": "elixir_vit_petit",        "qty": 2, "profession": "alchimiste", "level_req": 5,   "ingredients": {"mat_herbe_mana": 4}},
    "rec_vit_moyen":          {"result": "elixir_vit_moyen",        "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_fleur_lune": 5, "mat_herbe_mana": 4}},
    "rec_vit_grand":          {"result": "elixir_vit_grand",        "qty": 1, "profession": "alchimiste", "level_req": 35,  "ingredients": {"mat_pollen_dore": 6, "mat_fleur_lune": 4}},
    "rec_vit_tres_grand":     {"result": "elixir_vit_tres_grand",   "qty": 1, "profession": "alchimiste", "level_req": 45,  "ingredients": {"mat_fleur_lune": 6, "mat_pollen_dore": 4}},
    "rec_vit_giga":           {"result": "elixir_vit_giga",         "qty": 1, "profession": "alchimiste", "level_req": 65,  "ingredients": {"mat_fleur_lune": 5, "mat_cristal_vegetal": 4, "mat_pollen_dore": 3}},
    "rec_vit_ultime":         {"result": "elixir_vit_ultime",       "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_lotus_ombre": 4, "mat_fleur_lune": 5, "mat_cristal_vegetal": 3}},
    # ALCHIMISTE — Élixir de Critique
    "rec_crit_petit":         {"result": "elixir_crit_petit",       "qty": 2, "profession": "alchimiste", "level_req": 5,   "ingredients": {"mat_racine_force": 4}},
    "rec_crit_moyen":         {"result": "elixir_crit_moyen",       "qty": 1, "profession": "alchimiste", "level_req": 20,  "ingredients": {"mat_pollen_dore": 5, "mat_fleur_lune": 3}},
    "rec_crit_grand":         {"result": "elixir_crit_grand",       "qty": 1, "profession": "alchimiste", "level_req": 35,  "ingredients": {"mat_champi_venin": 6, "mat_pollen_dore": 4}},
    "rec_crit_tres_grand":    {"result": "elixir_crit_tres_grand",  "qty": 1, "profession": "alchimiste", "level_req": 45,  "ingredients": {"mat_cristal_vegetal": 5, "mat_champi_venin": 4, "mat_pollen_dore": 3}},
    "rec_crit_giga":          {"result": "elixir_crit_giga",        "qty": 1, "profession": "alchimiste", "level_req": 65,  "ingredients": {"mat_epine_dragon": 5, "mat_cristal_vegetal": 4}},
    "rec_crit_ultime":        {"result": "elixir_crit_ultime",      "qty": 1, "profession": "alchimiste", "level_req": 80,  "ingredients": {"mat_epine_dragon": 6, "mat_lotus_ombre": 3, "mat_cristal_vegetal": 3}},
    # ALCHIMISTE — Élixir Royal
    "rec_royal_petit":        {"result": "elixir_royal_petit",      "qty": 1, "profession": "alchimiste", "level_req": 25,  "ingredients": {"mat_racine_force": 3, "mat_herbe_mana": 3, "mat_pollen_dore": 3}},
    "rec_royal_moyen":        {"result": "elixir_royal_moyen",      "qty": 1, "profession": "alchimiste", "level_req": 40,  "ingredients": {"mat_fleur_lune": 4, "mat_cristal_vegetal": 4, "mat_pollen_dore": 3}},
    "rec_royal_grand":        {"result": "elixir_royal_grand",      "qty": 1, "profession": "alchimiste", "level_req": 55,  "ingredients": {"mat_cristal_vegetal": 5, "mat_mousse_ancienne": 4, "mat_fleur_lune": 3}},
    "rec_royal_tres_grand":   {"result": "elixir_royal_tres_grand", "qty": 1, "profession": "alchimiste", "level_req": 75,  "ingredients": {"mat_epine_dragon": 4, "mat_cristal_vegetal": 5, "mat_mousse_ancienne": 3}},
    "rec_royal_giga":         {"result": "elixir_royal_giga",       "qty": 1, "profession": "alchimiste", "level_req": 85,  "ingredients": {"mat_lotus_ombre": 5, "mat_epine_dragon": 4, "mat_cristal_vegetal": 3}},
    "rec_royal_ultime":       {"result": "elixir_royal_ultime",     "qty": 1, "profession": "alchimiste", "level_req": 95,  "ingredients": {"mat_lotus_ombre": 7, "mat_epine_dragon": 5, "mat_fruit_paradis": 3}},
    # ALCHIMISTE — Potions spéciales
    "rec_renforcement":       {"result": "potion_renforcement",     "qty": 1, "profession": "alchimiste", "level_req": 15,  "ingredients": {"mat_herbe_soin": 8, "mat_racine_force": 5}},
    "rec_resurrection":       {"result": "potion_resurrection",     "qty": 1, "profession": "alchimiste", "level_req": 90,  "ingredients": {"mat_lotus_ombre": 6, "mat_fruit_paradis": 3, "mat_epine_dragon": 4}},
    "rec_protection_ultime":  {"result": "potion_protection_ultime","qty": 1, "profession": "alchimiste", "level_req": 100, "ingredients": {"mat_lotus_ombre": 8, "mat_fruit_paradis": 5, "mat_cristal_vegetal": 6}},
    # BOULANGER — Pain (énergie directe)
    "rec_pain_p":             {"result": "pain_p",             "qty": 5, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_ble": 3}},
    "rec_pain_m":             {"result": "pain_m",             "qty": 3, "profession": "boulanger", "level_req": 12, "ingredients": {"mat_ble": 5, "mat_orge": 2}},
    "rec_pain_g":             {"result": "pain_g",             "qty": 2, "profession": "boulanger", "level_req": 25, "ingredients": {"mat_orge": 6, "mat_farine_mais": 3}},
    "rec_pain_tg":            {"result": "pain_tg",            "qty": 1, "profession": "boulanger", "level_req": 40, "ingredients": {"mat_orge": 8, "mat_farine_mais": 5, "mat_herbes_arom": 3}},
    "rec_pain_x":             {"result": "pain_x",             "qty": 1, "profession": "boulanger", "level_req": 60, "ingredients": {"mat_farine_mais": 8, "mat_miel_enchante": 4, "mat_lait_licorne": 2}},
    "rec_pain_u":             {"result": "pain_u",             "qty": 1, "profession": "boulanger", "level_req": 82, "ingredients": {"mat_fruit_paradis": 3, "mat_miel_enchante": 5, "mat_lait_licorne": 3}},
    # BOULANGER — Infusion (regen énergie passive)
    "rec_infusion_p":         {"result": "infusion_p",         "qty": 3, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_herbes_arom": 3}},
    "rec_infusion_m":         {"result": "infusion_m",         "qty": 2, "profession": "boulanger", "level_req": 15, "ingredients": {"mat_herbes_arom": 4, "mat_baies": 2}},
    "rec_infusion_g":         {"result": "infusion_g",         "qty": 1, "profession": "boulanger", "level_req": 28, "ingredients": {"mat_baies": 4, "mat_miel_enchante": 3}},
    "rec_infusion_tg":        {"result": "infusion_tg",        "qty": 1, "profession": "boulanger", "level_req": 45, "ingredients": {"mat_miel_enchante": 5, "mat_sel_mer": 3}},
    "rec_infusion_x":         {"result": "infusion_x",         "qty": 1, "profession": "boulanger", "level_req": 65, "ingredients": {"mat_sel_mer": 4, "mat_epices_rares": 3}},
    "rec_infusion_u":         {"result": "infusion_u",         "qty": 1, "profession": "boulanger", "level_req": 85, "ingredients": {"mat_epices_rares": 5, "mat_lait_licorne": 3}},
    # BOULANGER — Ration de Victoire (énergie par victoire combat)
    "rec_ration_vic_p":       {"result": "ration_vic_p",       "qty": 3, "profession": "boulanger", "level_req": 5,  "ingredients": {"mat_ble": 3, "mat_herbes_arom": 3}},
    "rec_ration_vic_m":       {"result": "ration_vic_m",       "qty": 2, "profession": "boulanger", "level_req": 18, "ingredients": {"mat_farine_mais": 3, "mat_baies": 3}},
    "rec_ration_vic_g":       {"result": "ration_vic_g",       "qty": 1, "profession": "boulanger", "level_req": 32, "ingredients": {"mat_baies": 4, "mat_sel_mer": 3}},
    "rec_ration_vic_tg":      {"result": "ration_vic_tg",      "qty": 1, "profession": "boulanger", "level_req": 50, "ingredients": {"mat_lait_licorne": 3, "mat_sel_mer": 4}},
    "rec_ration_vic_x":       {"result": "ration_vic_x",       "qty": 1, "profession": "boulanger", "level_req": 70, "ingredients": {"mat_epices_rares": 3, "mat_lait_licorne": 4}},
    "rec_ration_vic_u":       {"result": "ration_vic_u",       "qty": 1, "profession": "boulanger", "level_req": 88, "ingredients": {"mat_fruit_paradis": 3, "mat_epices_rares": 4}},
    # BOULANGER — Soupe Fortifiante (énergie + défense physique %)
    "rec_soupe_fort_p":       {"result": "soupe_fort_p",       "qty": 2, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_orge": 4, "mat_herbes_arom": 3}},
    "rec_soupe_fort_g":       {"result": "soupe_fort_g",       "qty": 1, "profession": "boulanger", "level_req": 30, "ingredients": {"mat_sel_mer": 4, "mat_herbes_arom": 6, "mat_lait_licorne": 2}},
    "rec_soupe_fort_u":       {"result": "soupe_fort_u",       "qty": 1, "profession": "boulanger", "level_req": 70, "ingredients": {"mat_sel_mer": 6, "mat_epices_rares": 4, "mat_lait_licorne": 4}},
    # BOULANGER — Pâtisserie Légère (énergie + vitesse %)
    "rec_patisserie_p":       {"result": "patisserie_p",       "qty": 2, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_ble": 4, "mat_baies": 3}},
    "rec_patisserie_g":       {"result": "patisserie_g",       "qty": 1, "profession": "boulanger", "level_req": 30, "ingredients": {"mat_farine_mais": 5, "mat_baies": 5, "mat_miel_enchante": 2}},
    "rec_patisserie_u":       {"result": "patisserie_u",       "qty": 1, "profession": "boulanger", "level_req": 70, "ingredients": {"mat_miel_enchante": 6, "mat_epices_rares": 4, "mat_baies": 6}},
    # BOULANGER — Repas du Guerrier (énergie + attaque physique %)
    "rec_repas_guerrier_p":   {"result": "repas_guerrier_p",   "qty": 2, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_orge": 4, "mat_herbes_arom": 4}},
    "rec_repas_guerrier_g":   {"result": "repas_guerrier_g",   "qty": 1, "profession": "boulanger", "level_req": 30, "ingredients": {"mat_farine_mais": 6, "mat_herbes_arom": 5, "mat_baies": 3}},
    "rec_repas_guerrier_u":   {"result": "repas_guerrier_u",   "qty": 1, "profession": "boulanger", "level_req": 70, "ingredients": {"mat_lait_licorne": 4, "mat_epices_rares": 4, "mat_herbes_arom": 6}},
    # BOULANGER — Délice Mystique (énergie + attaque magique %)
    "rec_delice_mys_p":       {"result": "delice_mys_p",       "qty": 2, "profession": "boulanger", "level_req": 1,  "ingredients": {"mat_herbes_arom": 5, "mat_baies": 3}},
    "rec_delice_mys_g":       {"result": "delice_mys_g",       "qty": 1, "profession": "boulanger", "level_req": 30, "ingredients": {"mat_miel_enchante": 5, "mat_baies": 5, "mat_farine_mais": 3}},
    "rec_delice_mys_u":       {"result": "delice_mys_u",       "qty": 1, "profession": "boulanger", "level_req": 70, "ingredients": {"mat_miel_enchante": 6, "mat_epices_rares": 4, "mat_fruit_paradis": 2}},
    # BOULANGER — Spéciaux haut niveau (énergie + regen + win)
    "rec_festin_aventurier":  {"result": "festin_aventurier",  "qty": 1, "profession": "boulanger", "level_req": 75, "ingredients": {"mat_baies": 8, "mat_lait_licorne": 4, "mat_sel_mer": 3, "mat_herbes_arom": 5}},
    "rec_banquet_champion":   {"result": "banquet_champion",   "qty": 1, "profession": "boulanger", "level_req": 90, "ingredients": {"mat_lait_licorne": 5, "mat_miel_enchante": 5, "mat_epices_rares": 4, "mat_sel_mer": 4}},
    "rec_repas_legendaire":   {"result": "repas_legendaire",   "qty": 1, "profession": "boulanger", "level_req": 98, "ingredients": {"mat_fruit_paradis": 5, "mat_lait_licorne": 5, "mat_epices_rares": 5, "mat_miel_enchante": 5}},
    # ENCHANTEUR — Rune de Force (p_atk)
    "rec_rune_force_p":       {"result": "rune_force_p",       "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 4, "mat_cuir_loup": 3}},
    "rec_rune_force_m":       {"result": "rune_force_m",       "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_acier": 4, "mat_cuir_cerf": 3}},
    "rec_rune_force_g":       {"result": "rune_force_g",       "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_mithril": 4, "mat_ecailles": 3}},
    "rec_rune_force_tg":      {"result": "rune_force_tg",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_adamantium": 3, "mat_griffe_griff": 4}},
    "rec_rune_force_x":       {"result": "rune_force_x",       "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_orichalque": 3, "mat_croc_goule": 4}},
    "rec_rune_force_u":       {"result": "rune_force_u",       "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_pierre_foudre": 4, "mat_os_chimere": 4}},
    # ENCHANTEUR — Rune de Magie (m_atk)
    "rec_rune_magie_p":       {"result": "rune_magie_p",       "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 4, "mat_herbe_mana": 4}},
    "rec_rune_magie_m":       {"result": "rune_magie_m",       "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_acier": 4, "mat_racine_force": 3}},
    "rec_rune_magie_g":       {"result": "rune_magie_g",       "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_mithril": 4, "mat_pollen_dore": 4}},
    "rec_rune_magie_tg":      {"result": "rune_magie_tg",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_pierre_feu": 4, "mat_champi_venin": 4}},
    "rec_rune_magie_x":       {"result": "rune_magie_x",       "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_orichalque": 3, "mat_mousse_ancienne": 4}},
    "rec_rune_magie_u":       {"result": "rune_magie_u",       "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_cristal_brut": 4, "mat_lotus_ombre": 4}},
    # ENCHANTEUR — Rune de Défense Physique (p_def)
    "rec_rune_def_p_p":       {"result": "rune_def_p_p",       "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 5, "mat_cuir_loup": 3}},
    "rec_rune_def_p_m":       {"result": "rune_def_p_m",       "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_acier": 5, "mat_cuir_cerf": 3}},
    "rec_rune_def_p_g":       {"result": "rune_def_p_g",       "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_mithril": 4, "mat_ecailles": 4}},
    "rec_rune_def_p_tg":      {"result": "rune_def_p_tg",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_adamantium": 4, "mat_griffe_griff": 4}},
    "rec_rune_def_p_x":       {"result": "rune_def_p_x",       "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_orichalque": 3, "mat_croc_goule": 5}},
    "rec_rune_def_p_u":       {"result": "rune_def_p_u",       "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_pierre_foudre": 4, "mat_os_chimere": 4}},
    # ENCHANTEUR — Rune de Défense Magique (m_def)
    "rec_rune_def_m_p":       {"result": "rune_def_m_p",       "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 4, "mat_herbe_soin": 5}},
    "rec_rune_def_m_m":       {"result": "rune_def_m_m",       "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_acier": 4, "mat_herbe_mana": 4}},
    "rec_rune_def_m_g":       {"result": "rune_def_m_g",       "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_mithril": 4, "mat_fleur_lune": 4}},
    "rec_rune_def_m_tg":      {"result": "rune_def_m_tg",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_pierre_feu": 4, "mat_champi_venin": 4}},
    "rec_rune_def_m_x":       {"result": "rune_def_m_x",       "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_orichalque": 3, "mat_mousse_ancienne": 5}},
    "rec_rune_def_m_u":       {"result": "rune_def_m_u",       "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_cristal_brut": 4, "mat_lotus_ombre": 4}},
    # ENCHANTEUR — Rune de Vitesse (speed)
    "rec_rune_vit_p":         {"result": "rune_vit_p",         "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_cuir_loup": 4, "mat_herbe_mana": 3}},
    "rec_rune_vit_m":         {"result": "rune_vit_m",         "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_cuir_cerf": 4, "mat_racine_force": 3}},
    "rec_rune_vit_g":         {"result": "rune_vit_g",         "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_griffe_griff": 4, "mat_pollen_dore": 5}},
    "rec_rune_vit_tg":        {"result": "rune_vit_tg",        "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_croc_goule": 4, "mat_champi_venin": 4}},
    "rec_rune_vit_x":         {"result": "rune_vit_x",         "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_venin_basil": 3, "mat_epine_dragon": 4}},
    "rec_rune_vit_u":         {"result": "rune_vit_u",         "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_venin_basil": 4, "mat_lotus_ombre": 3, "mat_epine_dragon": 3}},
    # ENCHANTEUR — Rune de Critique (crit_chance)
    "rec_rune_crit_p":        {"result": "rune_crit_p",        "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_cuir_loup": 3, "mat_herbe_soin": 4}},
    "rec_rune_crit_m":        {"result": "rune_crit_m",        "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_ecailles": 4, "mat_pollen_dore": 3}},
    "rec_rune_crit_g":        {"result": "rune_crit_g",        "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_croc_goule": 4, "mat_champi_venin": 5}},
    "rec_rune_crit_tg":       {"result": "rune_crit_tg",       "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_croc_goule": 5, "mat_cristal_vegetal": 4}},
    "rec_rune_crit_x":        {"result": "rune_crit_x",        "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_os_chimere": 3, "mat_epine_dragon": 4}},
    "rec_rune_crit_u":        {"result": "rune_crit_u",        "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_os_chimere": 4, "mat_lotus_ombre": 4}},
    # ENCHANTEUR — Rune de Pénétration Physique (p_pen)
    "rec_rune_pen_p_p":       {"result": "rune_pen_p_p",       "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 4, "mat_cuir_loup": 4}},
    "rec_rune_pen_p_m":       {"result": "rune_pen_p_m",       "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_acier": 4, "mat_ecailles": 4}},
    "rec_rune_pen_p_g":       {"result": "rune_pen_p_g",       "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_mithril": 4, "mat_griffe_griff": 4}},
    "rec_rune_pen_p_tg":      {"result": "rune_pen_p_tg",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_adamantium": 4, "mat_croc_goule": 4}},
    "rec_rune_pen_p_x":       {"result": "rune_pen_p_x",       "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_orichalque": 4, "mat_croc_goule": 5}},
    "rec_rune_pen_p_u":       {"result": "rune_pen_p_u",       "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_pierre_foudre": 4, "mat_venin_basil": 4}},
    # ENCHANTEUR — Rune de Pénétration Magique (m_pen)
    "rec_rune_pen_m_p":       {"result": "rune_pen_m_p",       "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_fer": 4, "mat_herbe_mana": 3}},
    "rec_rune_pen_m_m":       {"result": "rune_pen_m_m",       "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_acier": 4, "mat_pollen_dore": 3}},
    "rec_rune_pen_m_g":       {"result": "rune_pen_m_g",       "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_mithril": 3, "mat_champi_venin": 4}},
    "rec_rune_pen_m_tg":      {"result": "rune_pen_m_tg",      "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_pierre_feu": 3, "mat_cristal_vegetal": 4}},
    "rec_rune_pen_m_x":       {"result": "rune_pen_m_x",       "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_orichalque": 4, "mat_epine_dragon": 4}},
    "rec_rune_pen_m_u":       {"result": "rune_pen_m_u",       "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_diamant_brut": 5, "mat_lotus_ombre": 4}},
    # ENCHANTEUR — Rune de Vie (hp)
    "rec_rune_vie_p":         {"result": "rune_vie_p",         "qty": 2, "profession": "enchanteur", "level_req": 1,  "ingredients": {"mat_cuir_loup": 4, "mat_herbe_soin": 4}},
    "rec_rune_vie_m":         {"result": "rune_vie_m",         "qty": 1, "profession": "enchanteur", "level_req": 15, "ingredients": {"mat_cuir_cerf": 4, "mat_fleur_lune": 3}},
    "rec_rune_vie_g":         {"result": "rune_vie_g",         "qty": 1, "profession": "enchanteur", "level_req": 30, "ingredients": {"mat_ecailles": 4, "mat_racine_force": 4}},
    "rec_rune_vie_tg":        {"result": "rune_vie_tg",        "qty": 1, "profession": "enchanteur", "level_req": 50, "ingredients": {"mat_griffe_griff": 4, "mat_mousse_ancienne": 4}},
    "rec_rune_vie_x":         {"result": "rune_vie_x",         "qty": 1, "profession": "enchanteur", "level_req": 70, "ingredients": {"mat_venin_basil": 4, "mat_epine_dragon": 4}},
    "rec_rune_vie_u":         {"result": "rune_vie_u",         "qty": 1, "profession": "enchanteur", "level_req": 90, "ingredients": {"mat_coeur_bete": 5, "mat_lotus_ombre": 4, "mat_epine_dragon": 3}},
    # ENCHANTEUR — Rune Divine (toutes stats, tier unique niv 100)
    "rec_rune_divine":        {"result": "rune_divine",        "qty": 1, "profession": "enchanteur", "level_req": 100, "ingredients": {"mat_os_chimere": 3, "mat_coeur_bete": 3, "mat_lotus_ombre": 4, "mat_diamant_brut": 5, "mat_cristal_brut": 5}},
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

        # Recettes de craft — uniquement pour la panoplie "craft"
        if source == "craft":
            for slot in SLOTS:
                craft_job = SLOT_TO_CRAFT_JOB.get(slot)
                if not craft_job:
                    continue
                recipe_id = f"crec_{set_key}_{slot}"
                ingredients = _craft_ingredients(class_name)
                CRAFT_RECIPES[recipe_id] = {
                    "result":      f"eq_{set_key}_{slot}",
                    "qty":         1,
                    "profession":  craft_job,
                    "level_req":   1,           # débloqué dès le niveau 1 du métier
                    "ingredients": ingredients,
                    "class":       class_name,
                    "set":         set_key,
                    # item_level produit = craft_level × 10  (calculé dans metiers.py)
                }


def _craft_ingredients(class_name: str) -> dict[str, int]:
    """Ingrédients de base pour crafter un item (niveau déterminé dynamiquement)."""
    class_to_mats: dict[str, list[str]] = {
        "Guerrier":         ["mat_fer",        "mat_acier",        "mat_mithril"],
        "Assassin":         ["mat_cuir_loup",  "mat_ecailles",     "mat_griffe_griff"],
        "Mage":             ["mat_herbe_mana",  "mat_cristal_vegetal", "mat_diamant_brut"],
        "Tireur":           ["mat_bois_chene",  "mat_bois_ebene",   "mat_bois_enchante"],
        "Support":          ["mat_fer",         "mat_mithril",      "mat_adamantium"],
        "Vampire":          ["mat_cuir_loup",   "mat_croc_goule",   "mat_coeur_bete"],
        "Gardien du Temps": ["mat_cristal_brut","mat_pierre_foudre","mat_diamant_brut"],
        "Ombre Venin":      ["mat_champi_venin","mat_venin_basil",  "mat_lotus_ombre"],
        "Pyromancien":      ["mat_pierre_feu",  "mat_cristal_vegetal","mat_epine_dragon"],
        "Paladin":          ["mat_fer",         "mat_adamantium",   "mat_diamant_brut"],
    }
    mats = class_to_mats.get(class_name, ["mat_fer", "mat_acier", "mat_mithril"])
    # Quantités fixes — le coût réel sera mis à l'échelle du niveau dans metiers.py
    return {mats[0]: 5, mats[1]: 3, "mat_orge": 3}


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
            stats[stat] = int(raw)
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

# Consommables : valeur fixe par item_id
_CONSUMABLE_BASE_VALUE: dict[str, int] = {
    # ALCHIMISTE — Potions de Soin
    "potion_soin_petite": 50,       "potion_soin_moyenne": 150,     "potion_soin_grande": 375,
    "potion_soin_tres_grande": 1_000, "potion_soin_giga": 2_500,    "potion_soin_ultime": 6_250,
    # ALCHIMISTE — Élixirs (Force, Magie, Défense, Vitesse, Critique)
    "elixir_force_petit": 75,       "elixir_force_moyen": 200,      "elixir_force_grand": 500,
    "elixir_force_tres_grand": 1_250, "elixir_force_giga": 3_000,   "elixir_force_ultime": 7_500,
    "elixir_magie_petit": 75,       "elixir_magie_moyen": 200,      "elixir_magie_grand": 500,
    "elixir_magie_tres_grand": 1_250, "elixir_magie_giga": 3_000,   "elixir_magie_ultime": 7_500,
    "elixir_def_petit": 75,         "elixir_def_moyen": 200,        "elixir_def_grand": 500,
    "elixir_def_tres_grand": 1_250, "elixir_def_giga": 3_000,       "elixir_def_ultime": 7_500,
    "elixir_vit_petit": 75,         "elixir_vit_moyen": 200,        "elixir_vit_grand": 500,
    "elixir_vit_tres_grand": 1_250, "elixir_vit_giga": 3_000,       "elixir_vit_ultime": 7_500,
    "elixir_crit_petit": 75,        "elixir_crit_moyen": 200,       "elixir_crit_grand": 500,
    "elixir_crit_tres_grand": 1_250, "elixir_crit_giga": 3_000,     "elixir_crit_ultime": 7_500,
    # ALCHIMISTE — Élixir Royal (toutes stats)
    "elixir_royal_petit": 200,      "elixir_royal_moyen": 500,      "elixir_royal_grand": 1_250,
    "elixir_royal_tres_grand": 3_000, "elixir_royal_giga": 7_500,   "elixir_royal_ultime": 20_000,
    # ALCHIMISTE — Spéciaux
    "potion_renforcement": 1_250,   "potion_resurrection": 15_000,  "potion_protection_ultime": 30_000,
    # BOULANGER — Pain (énergie directe)
    "pain_p": 50,   "pain_m": 150,  "pain_g": 375,  "pain_tg": 1_000, "pain_x": 2_500, "pain_u": 6_250,
    # BOULANGER — Infusion (regen passif)
    "infusion_p": 75,   "infusion_m": 225,  "infusion_g": 625,
    "infusion_tg": 1_500, "infusion_x": 3_750, "infusion_u": 10_000,
    # BOULANGER — Ration de Victoire (énergie/victoire)
    "ration_vic_p": 75,   "ration_vic_m": 225,  "ration_vic_g": 625,
    "ration_vic_tg": 1_500, "ration_vic_x": 3_750, "ration_vic_u": 10_000,
    # BOULANGER — Soupe, Pâtisserie, Repas, Délice (énergie + stat combat, 3 paliers)
    "soupe_fort_p": 375,    "soupe_fort_g": 2_500,    "soupe_fort_u": 12_500,
    "patisserie_p": 375,    "patisserie_g": 2_500,    "patisserie_u": 12_500,
    "repas_guerrier_p": 375, "repas_guerrier_g": 2_500, "repas_guerrier_u": 12_500,
    "delice_mys_p": 375,    "delice_mys_g": 2_500,    "delice_mys_u": 12_500,
    # BOULANGER — Spéciaux haut niveau (energy_all)
    "festin_aventurier": 10_000, "banquet_champion": 25_000, "repas_legendaire": 62_500,
    # ENCHANTEUR — Runes Force / Magie (p_atk / m_atk)
    "rune_force_p": 150,    "rune_force_m": 500,    "rune_force_g": 1_500,
    "rune_force_tg": 3_750, "rune_force_x": 10_000, "rune_force_u": 25_000,
    "rune_magie_p": 150,    "rune_magie_m": 500,    "rune_magie_g": 1_500,
    "rune_magie_tg": 3_750, "rune_magie_x": 10_000, "rune_magie_u": 25_000,
    # ENCHANTEUR — Runes Déf Physique / Magique
    "rune_def_p_p": 125,    "rune_def_p_m": 375,    "rune_def_p_g": 1_250,
    "rune_def_p_tg": 3_000, "rune_def_p_x": 7_500,  "rune_def_p_u": 20_000,
    "rune_def_m_p": 125,    "rune_def_m_m": 375,    "rune_def_m_g": 1_250,
    "rune_def_m_tg": 3_000, "rune_def_m_x": 7_500,  "rune_def_m_u": 20_000,
    # ENCHANTEUR — Rune Vitesse
    "rune_vit_p": 125,    "rune_vit_m": 375,    "rune_vit_g": 1_250,
    "rune_vit_tg": 3_000, "rune_vit_x": 7_500,  "rune_vit_u": 20_000,
    # ENCHANTEUR — Rune Critique
    "rune_crit_p": 175,    "rune_crit_m": 625,    "rune_crit_g": 2_000,
    "rune_crit_tg": 5_000, "rune_crit_x": 13_750, "rune_crit_u": 35_000,
    # ENCHANTEUR — Runes Pénétration Physique / Magique
    "rune_pen_p_p": 125,    "rune_pen_p_m": 375,    "rune_pen_p_g": 1_250,
    "rune_pen_p_tg": 3_000, "rune_pen_p_x": 7_500,  "rune_pen_p_u": 20_000,
    "rune_pen_m_p": 125,    "rune_pen_m_m": 375,    "rune_pen_m_g": 1_250,
    "rune_pen_m_tg": 3_000, "rune_pen_m_x": 7_500,  "rune_pen_m_u": 20_000,
    # ENCHANTEUR — Rune de Vie
    "rune_vie_p": 100,    "rune_vie_m": 300,    "rune_vie_g": 875,
    "rune_vie_tg": 2_250, "rune_vie_x": 5_500,  "rune_vie_u": 13_750,
    # ENCHANTEUR — Rune Divine
    "rune_divine": 150_000,
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
            base_chance = max(0.5, 26 - tier * 2.5)  # tier1=23.5%, tier9=3.5%, tier10=1%
        else:
            # Hors métier : 10× plus rare
            base_chance = max(0.05, (26 - tier * 2.5) / 10)  # tier1=2.35%, tier9=0.35%, tier10=0.1%
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



def _zone_rarity_weights(zone: int, is_emblematic: bool, is_antique: bool, is_raid: bool) -> list[float]:
    """Poids des raretés selon la zone et le type de combat."""
    base = [40, 25, 15, 10, 5, 3, 1.5, 0.4, 0.08, 0.02]
    # Amélioration progressive avec la zone (max à zone 10 000)
    prog = min(zone / 10000, 1.0)
    weights = [max(0.01, b - b * prog * 0.7) for b in base]
    boost = [0] * 10
    if is_emblematic:
        boost = [0, 0, 2, 3, 5, 5, 4, 2, 0.5, 0.1]
    if is_antique:
        boost = [0, 0, 0, 2, 4, 6, 6, 5, 2, 0.5]
    if is_raid:
        boost = [0, 0, 1, 2, 4, 5, 5, 4, 2, 0.3]
    return [max(0.01, w + b) for w, b in zip(weights, boost)]


def get_equipment_drops(
    zone: int,
    player_class: str,
    drop_type: str,
    drop_source: str = "monde",
) -> list[dict]:
    """
    Retourne une liste d'équipements droppés selon le type de rencontre.

    drop_type :
      - "monster"           → 10% same class, 1% other
      - "boss_classique"    → 50% same class, 10% other
      - "boss_emblematique" → 100% same class, 50% other
      - "boss_antique"      → 3× same class garanti, 1× other garanti
      - "dungeon"           → 1 item garanti : 80% same class, 20% other
      - "raid"              → 7 items aléatoires (classe 100% random)
    """
    import random
    from bot.cogs.rpg.models import SET_BONUSES, SLOTS, RARITIES, ALL_CLASSES

    is_emblematic = drop_type == "boss_emblematique"
    is_antique    = drop_type == "boss_antique"
    is_raid       = drop_type == "raid"

    def _make_item(use_player_class: bool) -> dict | None:
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
        chosen_slot = random.choice(SLOTS)
        item_id     = f"eq_{chosen_set}_{chosen_slot}"

        rw = _zone_rarity_weights(zone, is_emblematic, is_antique, is_raid)
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
        for _ in range(7):
            use_same = random.random() < 0.5
            item = _make_item(use_same)
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
