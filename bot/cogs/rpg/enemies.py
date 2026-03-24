"""
Définitions et génération des ennemis : monde, donjons, raids, world boss.
"""
from __future__ import annotations
import random
from bot.cogs.rpg.models import ALL_CLASSES, CLASS_EMOJI, BASE_STATS, LEVEL_GROWTH, CLASS_SPELLS

# ─── Génération ennemis Monde ──────────────────────────────────────────────

# Noms thématiques par zone
ZONE_THEMES = [
    ("Plaine Verdoyante", "🌿"), ("Forêt Ombreuse", "🌲"), ("Marais Pestilentiel", "🌫️"),
    ("Désert Ardent", "🏜️"),    ("Toundra Glacée", "❄️"),  ("Volcans Ardents", "🌋"),
    ("Cités en Ruines", "🏚️"),  ("Abysses Marines", "🌊"), ("Nécropole Maudite", "💀"),
    ("Royaume Céleste", "☁️"),
]

ENEMY_NAMES_BY_CLASS = {
    "Guerrier":         ["Berserker", "Paladin Noir", "Chevalier Déchu", "Colosse", "Titan"],
    "Assassin":         ["Rôdeur", "Ombre Tranchante", "Spectre Lame", "Fantôme Acéré", "Tueur Silencieux"],
    "Mage":             ["Sorcier", "Archimage Corrompu", "Nécromancien", "Mage du Chaos", "Élémentaliste"],
    "Tireur":           ["Archer Maudit", "Chasseur de Primes", "Sniper Fantôme", "Pistolier", "Garde d'Élite"],
    "Support":          ["Chaman Vénéneux", "Prêtre Obscur", "Gardien Maudit", "Moine Corrompu", "Oracle Sombre"],
    "Vampire":          ["Vampire Ancien", "Seigneur des Morts", "Suçeur d'Âmes", "Prince Ténébreux", "Goule Noble"],
    "Gardien du Temps": ["Chronomancien", "Gardien Temporel", "Distordeur du Temps", "Maître des Ères", "Briseur d'Âges"],
    "Ombre Venin":      ["Araignée Toxique", "Serpent Mortel", "Basilic", "Hydre Venimeuse", "Scorpion Géant"],
    "Pyromancien":      ["Élémentaire de Feu", "Salamandre", "Phénix Maudit", "Dragon de Lave", "Pyromage"],
    "Paladin":          ["Croisé Déchu", "Inquisiteur", "Chevalier Sacré Corrompu", "Défenseur Maudit", "Gardien Draconique"],
}

BOSS_PREFIXES = ["Seigneur", "Ancien", "Maître", "Grand", "Archonte", "Roi", "Prince", "Tyran"]
EMBLEMATIC_NAMES = [
    "Malachar l'Éternel", "Zephyros le Tempétueux", "Mordreth la Dévoreuse",
    "Xanathos l'Omniscient", "Valdris l'Implacable", "Sylvara la Tisseuse",
    "Grudnak le Colossal", "Elysia la Corrompue", "Tharax le Venimeux",
    "Drakonus le Chromate", "Abyssion le Profond", "Ignaris le Volcanique",
    "Glacialis le Glaçant", "Umbrath l'Ombral", "Pyrion l'Incandescent",
    "Temporis le Figé", "Necrosis la Putride", "Aetherion l'Astral",
    "Tenebris le Ténébreux", "Primordius l'Ancestral",
]
ANTIQUE_NAMES = [
    "Vrethax le Primordial", "Azkoth la Conscience Noire", "Solarius le Dévoreur d'Étoiles",
    "Mortifax l'Impérissable", "Chronaxis le Maître Absolu", "Nexuvor l'Indicible",
    "Erebos la Nuit Éternelle", "Pantheos le Dieu-Bête", "Ultharak l'Abomination",
    "Omegaris la Fin du Monde",
]
WORLD_BOSS_NAME  = "Bot Suprême"


# ─── Rotation de classes ────────────────────────────────────────────────────

def _class_by_index(n: int) -> str:
    """Retourne la classe selon l'index de rotation (0-9 cyclique)."""
    return ALL_CLASSES[n % 10]


_BOSS_SPELL_KEY: dict[str, str] = {
    "Guerrier":         "guerrier",
    "Assassin":         "assassin",
    "Mage":             "mage",
    "Tireur":           "tireur",
    "Support":          "support",
    "Vampire":          "vampire",
    "Gardien du Temps": "gardien_du_temps",
    "Ombre Venin":      "ombre_venin",
    "Pyromancien":      "pyromancien",
    "Paladin":          "paladin",
}


# ─── Passifs boss par classe et tier ────────────────────────────────────────

RUNIC_PASSIFS: dict[str, dict] = {
    "Guerrier":         {"name": "Furie Mineure",       "text": "+3% dégâts par tranche de 25% HP perdus (max +12%)",              "effects": {"enrage_per_25pct": 0.03, "enrage_max": 0.12}},
    "Assassin":         {"name": "Réflexes",            "text": "5% de chance d'esquiver une attaque physique",                    "effects": {"dodge_pct": 0.05}},
    "Mage":             {"name": "Résonance Arcanique", "text": "Ignore 8% de ta Déf. Mag.",                                       "effects": {"ignore_mdef_pct": 0.08}},
    "Tireur":           {"name": "Visée Précise",       "text": "+8% chance de critique",                                          "effects": {"bonus_crit_chance": 8.0}},
    "Support":          {"name": "Régénération",        "text": "Récupère 0.5% HP max au début de chaque tour",                    "effects": {"heal_per_turn_pct": 0.005}},
    "Vampire":          {"name": "Siphon Mineur",       "text": "Récupère 5% des dégâts infligés en HP",                           "effects": {"lifesteal_pct": 0.05}},
    "Gardien du Temps": {"name": "Distorsion Légère",   "text": "Ta vitesse réduite de 5%",                                        "effects": {"player_speed_debuff_pct": 0.05}},
    "Ombre Venin":      {"name": "Glandes Actives",     "text": "10% de chance de poison additionnel à chaque attaque",            "effects": {"bonus_poison_chance": 0.10}},
    "Pyromancien":      {"name": "Braises",             "text": "20% de chance d'appliquer 1 stack de brûlure à chaque attaque",   "effects": {"bonus_burn_chance": 0.20}},
    "Paladin":          {"name": "Résistance",          "text": "Dégâts reçus réduits de 5%",                                      "effects": {"dmg_reduction_pct": 0.05}},
}

EMBLEMATIC_PASSIFS: dict[str, dict] = {
    "Guerrier":         {"name": "Furie Guerrière",      "text": "+5% dégâts par tranche de 25% HP perdus (max +20%)",              "effects": {"enrage_per_25pct": 0.05, "enrage_max": 0.20}},
    "Assassin":         {"name": "Instinct",             "text": "10% de chance d'esquiver une attaque physique",                   "effects": {"dodge_pct": 0.10}},
    "Mage":             {"name": "Voile Arcanique",      "text": "Ignore 12% de ta Déf. Mag.",                                      "effects": {"ignore_mdef_pct": 0.12}},
    "Tireur":           {"name": "Œil Affûté",           "text": "+12% chance de critique",                                         "effects": {"bonus_crit_chance": 12.0}},
    "Support":          {"name": "Régénération Active",  "text": "Récupère 1% HP max/tour",                                         "effects": {"heal_per_turn_pct": 0.01}},
    "Vampire":          {"name": "Siphon de Vie",        "text": "Récupère 8% des dégâts infligés",                                 "effects": {"lifesteal_pct": 0.08}},
    "Gardien du Temps": {"name": "Ralentissement",       "text": "Ta vitesse réduite de 10%",                                       "effects": {"player_speed_debuff_pct": 0.10}},
    "Ombre Venin":      {"name": "Venin Persistant",     "text": "15% de chance de poison additionnel à chaque attaque",            "effects": {"bonus_poison_chance": 0.15}},
    "Pyromancien":      {"name": "Embrasement",          "text": "30% de chance d'appliquer 1 stack de brûlure à chaque attaque",   "effects": {"bonus_burn_chance": 0.30}},
    "Paladin":          {"name": "Aura Défensive",       "text": "Dégâts reçus réduits de 8%",                                      "effects": {"dmg_reduction_pct": 0.08}},
}

ANTIQUE_PASSIFS: dict[str, dict] = {
    "Guerrier":         {"name": "Rage Ancienne",         "text": "+8% dégâts par 25% HP perdus (max +32%) + immunité aux stuns",            "effects": {"enrage_per_25pct": 0.08, "enrage_max": 0.32, "stun_immune": True}},
    "Assassin":         {"name": "Ombre Persistante",     "text": "15% esquive + ses critiques ignorent 15% de ta Déf. Phy.",                "effects": {"dodge_pct": 0.15, "crit_pen_pct": 0.15}},
    "Mage":             {"name": "Annihilation Partielle","text": "Ignore 20% de ta Déf. Mag. + tous les 5 tours : dégâts purs 10% HP max",  "effects": {"ignore_mdef_pct": 0.20, "pure_dmg_interval": 5, "pure_dmg_pct": 0.10}},
    "Tireur":           {"name": "Salve Précise",         "text": "+18% chance de critique + tes défenses physiques -10%",                   "effects": {"bonus_crit_chance": 18.0, "player_pdef_debuff_pct": 0.10}},
    "Support":          {"name": "Bastion",               "text": "Récupère 1.5% HP max/tour + dégâts reçus -10%",                          "effects": {"heal_per_turn_pct": 0.015, "dmg_reduction_pct": 0.10}},
    "Vampire":          {"name": "Avidité Sanguine",      "text": "Récupère 12% des dégâts infligés + te vole 1% HP max/tour",               "effects": {"lifesteal_pct": 0.12, "drain_player_pct": 0.01}},
    "Gardien du Temps": {"name": "Distorsion Temporelle", "text": "Ta vitesse -15%, sa vitesse +15%",                                        "effects": {"player_speed_debuff_pct": 0.15, "enemy_speed_buff_pct": 0.15}},
    "Ombre Venin":      {"name": "Nuée Venimeuse",        "text": "20% de chance de poison additionnel + dégâts DoT ×1.2",                   "effects": {"bonus_poison_chance": 0.20}},
    "Pyromancien":      {"name": "Combustion",            "text": "40% de chance d'appliquer 1 stack de brûlure + dégâts brûlure ×1.2",     "effects": {"bonus_burn_chance": 0.40}},
    "Paladin":          {"name": "Jugement",              "text": "Dégâts reçus -12% + tous les 5 tours : dégâts purs 8% HP max",            "effects": {"dmg_reduction_pct": 0.12, "pure_dmg_interval": 5, "pure_dmg_pct": 0.08}},
}


def get_zone_theme(zone: int) -> tuple[str, str]:
    idx = ((zone - 1) // 1000) % len(ZONE_THEMES)
    return ZONE_THEMES[idx]


def enemy_class_for_stage(stage: int) -> str:
    """Retourne la classe de l'ennemi pour un stage donné (1-10)."""
    return ALL_CLASSES[(stage - 1) % len(ALL_CLASSES)]


def generate_enemy(zone: int, stage: int) -> dict:
    """
    Génère les stats d'un ennemi classique pour la zone X stage Y.
    """
    enemy_class = _class_by_index(stage - 1)
    theme_name, theme_emoji = get_zone_theme(zone)
    names = ENEMY_NAMES_BY_CLASS.get(enemy_class, ["Ennemi"])
    name = random.choice(names)

    stats = compute_enemy_stats(zone, enemy_class)
    xp   = int(zone * 15) + stage
    gold = int(zone * 8) + stage

    return {
        "name":        name,
        "class":       enemy_class,
        "zone":        zone,
        "stage":       stage,
        "type":        "ennemi",
        "theme":       theme_name,
        "theme_emoji": theme_emoji,
        "xp":          max(xp, 1),
        "gold":        max(gold, 1),
        **stats,
    }


def generate_boss(zone: int) -> dict:
    """Génère le boss classique d'une zone (stage 10+)."""
    boss_class = _class_by_index(zone - 1)
    theme_name, theme_emoji = get_zone_theme(zone)
    prefix = random.choice(BOSS_PREFIXES)
    base_name = random.choice(ENEMY_NAMES_BY_CLASS.get(boss_class, ["Gardien"]))
    name = f"{prefix} {base_name}"

    stats = compute_enemy_stats(zone, boss_class)
    stats["hp"] = int(stats["hp"] * 1.2)
    stats["max_hp"] = stats["hp"]
    xp   = int(zone * 18)
    gold = int(zone * 10)

    return {
        "name":        name,
        "class":       boss_class,
        "zone":        zone,
        "stage":       "Boss",
        "type":        "boss_classique",
        "theme":       theme_name,
        "theme_emoji": theme_emoji,
        "xp":          max(xp, 3),
        "gold":        max(gold, 2),
        **stats,
    }


def generate_runic_boss(zone: int) -> dict:
    """Boss runique (toutes les 10 zones, sauf emblématiques/antiques)."""
    boss_class = _class_by_index(zone // 10 - 1)
    theme_name, theme_emoji = get_zone_theme(zone)
    prefix = random.choice(BOSS_PREFIXES)
    base_name = random.choice(ENEMY_NAMES_BY_CLASS.get(boss_class, ["Gardien"]))
    name = f"{prefix} {base_name}"

    stats = compute_enemy_stats(zone, boss_class)
    stats["hp"] = int(stats["hp"] * 1.5)
    stats["max_hp"] = stats["hp"]

    passif_data = RUNIC_PASSIFS.get(boss_class, {})
    passif_text = passif_data.get("name", "") + " : " + passif_data.get("text", "") if passif_data else ""

    cls_key = _BOSS_SPELL_KEY.get(boss_class, "")
    spell_keys = [s for s in ["s1"] if CLASS_SPELLS.get(cls_key, {}).get(s)]

    xp   = int(zone * 23)
    gold = int(zone * 12)

    return {
        "name":               name,
        "class":              boss_class,
        "zone":               zone,
        "stage":              "Boss Runique",
        "type":               "boss_runique",
        "theme":              theme_name,
        "theme_emoji":        "🔮",
        "passif":             passif_text,
        "passif_effects":     passif_data.get("effects", {}),
        "boss_spells":        spell_keys,
        "boss_spell_cls_key": cls_key,
        "boss_spell_turn_mod": 3,
        "xp":                 max(xp, 5),
        "gold":               max(gold, 3),
        **stats,
    }


def generate_emblematic_boss(zone: int) -> dict:
    """Boss emblématique (toutes les 100 zones, sauf antiques)."""
    idx = zone // 100 - 1
    boss_class = _class_by_index(idx)
    name = EMBLEMATIC_NAMES[idx % len(EMBLEMATIC_NAMES)]

    stats = compute_enemy_stats(zone, boss_class)
    stats["hp"] = int(stats["hp"] * 2)
    stats["max_hp"] = stats["hp"]

    passif_data = EMBLEMATIC_PASSIFS.get(boss_class, {})
    passif_text = passif_data.get("name", "") + " : " + passif_data.get("text", "") if passif_data else ""

    cls_key = _BOSS_SPELL_KEY.get(boss_class, "")
    spell_keys = [s for s in ["s1", "s2"] if CLASS_SPELLS.get(cls_key, {}).get(s)]

    xp   = int(zone * 30)
    gold = int(zone * 16)

    return {
        "name":               name,
        "class":              boss_class,
        "zone":               zone,
        "stage":              "Boss Emblématique",
        "type":               "boss_emblematique",
        "theme":              "Boss Emblématique",
        "theme_emoji":        "🌟",
        "passif":             passif_text,
        "passif_effects":     passif_data.get("effects", {}),
        "boss_spells":        spell_keys,
        "boss_spell_cls_key": cls_key,
        "boss_spell_turn_mod": 3,
        "xp":                 max(xp, 50),
        "gold":               max(gold, 30),
        **stats,
    }


def generate_antique_boss(zone: int) -> dict:
    """Boss antique (tous les 1000 zones)."""
    idx = zone // 1000 - 1
    boss_class = _class_by_index(idx)
    name = ANTIQUE_NAMES[idx % len(ANTIQUE_NAMES)]

    stats = compute_enemy_stats(zone, boss_class)
    stats["hp"] = int(stats["hp"] * 3)
    stats["max_hp"] = stats["hp"]

    passif_data = ANTIQUE_PASSIFS.get(boss_class, {})
    passif_text = passif_data.get("name", "") + " : " + passif_data.get("text", "") if passif_data else ""

    cls_key = _BOSS_SPELL_KEY.get(boss_class, "")
    spell_keys = [s for s in ["s1", "s2", "ultimate"] if CLASS_SPELLS.get(cls_key, {}).get(s)]

    xp   = int(zone * 45)
    gold = int(zone * 24)

    return {
        "name":               name,
        "class":              boss_class,
        "zone":               zone,
        "stage":              "Boss Antique",
        "type":               "boss_antique",
        "theme":              "Boss Antique",
        "theme_emoji":        "⚠️",
        "passif":             passif_text,
        "passif_effects":     passif_data.get("effects", {}),
        "boss_spells":        spell_keys,
        "boss_spell_cls_key": cls_key,
        "boss_spell_turn_mod": 4,
        "xp":                 max(xp, 200),
        "gold":               max(gold, 100),
        **stats,
    }


# ─── World Boss ─────────────────────────────────────────────────────────────

def generate_world_boss(turn: int = 0) -> dict:
    """World Boss — stats basées sur la zone équivalente du tour personnel.
    Tour 0 → zone 1000, tour 1 → zone 1300, tour 2 → zone 1690, etc. (×1.3/tour).
    HP normaux (non multipliés) : les HP collectifs sont gérés séparément dans world_boss.py.
    """
    zone_equiv = round(1000 * (1.3 ** turn))
    # Moyenne de toutes les classes pour la zone équivalente
    all_stats = [compute_enemy_stats(zone_equiv, cls) for cls in ALL_CLASSES]
    stats = {k: int(sum(s[k] for s in all_stats) / len(all_stats)) for k in all_stats[0]}
    stats["max_hp"] = stats["hp"]

    return {
        "name":        WORLD_BOSS_NAME,
        "class":       "Titan",
        "zone":        zone_equiv,
        "type":        "world_boss",
        "theme":       "World Boss",
        "theme_emoji": "🐉",
        **stats,
    }


# ─── Donjons ───────────────────────────────────────────────────────────────

DUNGEON_BOSSES = [
    # 7 donjons — un par slot d'équipement (casque, plastron, pantalon, chaussures, arme, amulette, anneau)
    {
        "id": "d_casque", "slot": "casque", "name": "Gardien des Crânes", "stat_boost": "p_def", "emoji": "🪖",
        "passif": "Protection Céphalique : réduit les dégâts critiques reçus de 20%.",
        "passif_effects": {"crit_dmg_reduction_pct": 0.20},
    },
    {
        "id": "d_plastron", "slot": "plastron", "name": "Titan Cuirassé", "stat_boost": "hp", "emoji": "🛡️",
        "passif": "Endurance Absolue : récupère 3% de ses HP max au début de chaque tour.",
        "passif_effects": {"heal_per_turn_pct": 0.03},
    },
    {
        "id": "d_pantalon", "slot": "pantalon", "name": "Danseur de Guerre", "stat_boost": "speed", "emoji": "🌪️",
        "passif": "Esquive Naturelle : 10% de chance d'éviter complètement une attaque.",
        "passif_effects": {"dodge_pct": 0.10},
    },
    {
        "id": "d_chaussures", "slot": "chaussures", "name": "Spectre Fulgurant", "stat_boost": "speed", "emoji": "⚡",
        "passif": "Foulée Redoublée : 20% de chance d'attaquer deux fois lors de son tour.",
        "passif_effects": {"double_attack_chance": 0.20},
    },
    {
        "id": "d_arme", "slot": "arme", "name": "Lame Dévastatrice", "stat_boost": "p_atk", "emoji": "⚔️",
        "passif": "Tranchant Absolu : ignore 20% de ta Défense Physique et 20% de ta Défense Magique.",
        "passif_effects": {"ignore_def_pct": 0.20},
    },
    {
        "id": "d_amulette", "slot": "amulette", "name": "Mystique Absolu", "stat_boost": "m_atk", "emoji": "📿",
        "passif": "Renvoi Mystique : renvoie 8% des dégâts reçus sous forme de dégâts purs (avant défense).",
        "passif_effects": {"dmg_reflect_pct": 0.08},
    },
    {
        "id": "d_anneau", "slot": "anneau", "name": "Catalyseur Éternel", "stat_boost": "crit_chance", "emoji": "💍",
        "passif": "Empowerment Runique : gagne +2.5% dégâts par tour (cumulé, max 10 fois, +25% au maximum).",
        "passif_effects": {"dmg_ramp_per_turn": 0.025, "dmg_ramp_max_stacks": 10},
    },
]


def generate_dungeon_boss(boss_id: str, difficulty: str, level: int) -> dict:
    """
    Génère un boss de donjon.
    difficulty: 'classique', 'elite', 'abyssal'
    level: 1-100

    Équivalences zone (stats scalées de 30% à 100% vers zone 10000) :
      classique : zone 33 → 3300  (level × 33)
      elite     : zone 3366 → 6633 (3333 + level × 33)
      abyssal   : zone 6699 → 9999 (6666 + level × 33)

    Classe du boss : rotation par niveau de donjon (level 1=Guerrier, 2=Assassin, ...)
    Niveau recommandé : zone_equiv // 10
    """
    boss_template = next((b for b in DUNGEON_BOSSES if b["id"] == boss_id), DUNGEON_BOSSES[0])

    zone_offsets = {"classique": 0, "elite": 3333, "abyssal": 6666}
    zone_equiv = zone_offsets.get(difficulty, 0) + level * 33

    # Classe déterminée par la rotation selon le niveau de donjon
    boss_class = _class_by_index(level - 1)
    stats = compute_enemy_stats(zone_equiv, boss_class)

    # Multiplicateur de difficulté appliqué à toutes les stats
    diff_mult = {"classique": 1.2, "elite": 1.5, "abyssal": 2.0}.get(difficulty, 1.0)
    for stat in list(stats):
        if stat in ("crit_chance", "crit_damage"):
            stats[stat] = round(stats[stat] * diff_mult, 2)
        elif stat != "max_hp":
            stats[stat] = int(stats[stat] * diff_mult)
    stats["max_hp"] = stats["hp"]

    # Amplifier la stat spéciale du boss (×1.5 supplémentaire)
    stat_boost = boss_template["stat_boost"]
    if stat_boost in stats:
        stats[stat_boost] = int(stats[stat_boost] * 1.5)
        if stat_boost == "hp":
            stats["max_hp"] = stats["hp"]

    level_min_recommended = zone_equiv // 10
    reward_mult = {"classique": 2, "elite": 3, "abyssal": 4}.get(difficulty, 2)
    xp   = int(zone_equiv * 15 * reward_mult)
    gold = int(zone_equiv * 8  * reward_mult)

    cls_key = _BOSS_SPELL_KEY.get(boss_class, "")
    available_by_diff = {
        "classique": ["s1"],
        "elite":     ["s1", "s2"],
        "abyssal":   ["s1", "s2", "ultimate"],
    }
    boss_spells = [s for s in available_by_diff.get(difficulty, ["s1"])
                   if CLASS_SPELLS.get(cls_key, {}).get(s)]
    spell_turn_mod = 3

    return {
        "name":                  boss_template["name"],
        "class":                 boss_class,
        "dungeon_id":            boss_id,
        "difficulty":            difficulty,
        "level":                 level,
        "type":                  f"donjon_{difficulty}",
        "theme":                 f"Donjon {difficulty.capitalize()} Niv.{level}",
        "theme_emoji":           boss_template["emoji"],
        "passif":                boss_template["passif"],
        "passif_effects":        boss_template.get("passif_effects", {}),
        "boss_spells":           boss_spells,
        "boss_spell_cls_key":    cls_key,
        "boss_spell_turn_mod":   spell_turn_mod,
        "level_min_recommended": level_min_recommended,
        "xp":                    max(xp, 1),
        "gold":                  max(gold, 1),
        **stats,
    }


# ─── Raids ─────────────────────────────────────────────────────────────────

RAID_BOSSES = [
    {
        "id": "raid_1", "name": "Vorgath l'Implacable", "emoji": "🐉", "raid_level": 1,
        "level_req": 100, "class": "Guerrier",
        "spells": {
            "s1": {
                "name": "Frappe de Guerre", "emoji": "⚔️",
                "effects": {"dmg_mult": 1.5},
            },
            "ultimate": {
                "name": "Rage Ancienne", "emoji": "💢",
                "effects": {"purge_self": True, "self_dmg_buff": 0.40, "self_dmg_buff_turns": 3, "dmg_mult": 2.0},
            },
        },
    },
    {
        "id": "raid_2", "name": "Shivra l'Ombre Mortelle", "emoji": "🗡️", "raid_level": 2,
        "level_req": 200, "class": "Assassin",
        "spells": {
            "s1": {
                "name": "Lames Volantes", "emoji": "🌀",
                "effects": {"dmg_mult": 1.2, "stat_debuff": {"speed": 20}},
            },
            "ultimate": {
                "name": "Carnage Fantôme", "emoji": "💀",
                "effects": {"purge_self": True, "dmg_mult": 3.0},
            },
        },
    },
    {
        "id": "raid_3", "name": "Zyrex l'Archmage", "emoji": "⚡", "raid_level": 3,
        "level_req": 300, "class": "Mage",
        "spells": {
            "s1": {
                "name": "Décharge Électrique", "emoji": "🔮",
                "effects": {"dmg_mult": 2.0, "magic": True},
            },
            "ultimate": {
                "name": "Tempête Arcanique", "emoji": "🌩️",
                "effects": {"purge_self": True, "dmg_mult": 3.0, "magic": True, "stat_debuff": {"m_def": 30}},
            },
        },
    },
    {
        "id": "raid_4", "name": "Karek le Chasseur", "emoji": "🏹", "raid_level": 4,
        "level_req": 400, "class": "Tireur",
        "spells": {
            "s1": {
                "name": "Pluie de Flèches", "emoji": "🎯",
                "effects": {"dmg_mult": 1.5, "mark_player": 20},
            },
            "ultimate": {
                "name": "Salve Finale", "emoji": "💥",
                "effects": {"purge_self": True, "dmg_mult": 2.0, "dmg_mult_if_marked": 1.5},
            },
        },
    },
    {
        "id": "raid_5", "name": "Serath le Corrupteur", "emoji": "🕸️", "raid_level": 5,
        "level_req": 500, "class": "Support",
        "spells": {
            "s1": {
                "name": "Malédiction Collective", "emoji": "🩸",
                "effects": {"dmg_mult": 1.0, "heal_reduce": 0.50},
            },
            "ultimate": {
                "name": "Drain Collectif", "emoji": "⬛",
                "effects": {"purge_self": True, "drain_pct": 0.15},
            },
        },
    },
    {
        "id": "raid_6", "name": "Mordas le Sans-Âme", "emoji": "🧛", "raid_level": 6,
        "level_req": 600, "class": "Vampire",
        "spells": {
            "s1": {
                "name": "Morsure Collective", "emoji": "🩸",
                "effects": {"dmg_mult": 1.5, "lifesteal_pct": 0.15},
            },
            "ultimate": {
                "name": "Festin de Sang", "emoji": "🔴",
                "effects": {"purge_self": True, "dmg_mult": 2.0, "lifesteal_pct": 0.40},
            },
        },
    },
    {
        "id": "raid_7", "name": "Chronovex l'Invariant", "emoji": "⏳", "raid_level": 7,
        "level_req": 700, "class": "Gardien du Temps",
        "spells": {
            "s1": {
                "name": "Distorsion Temporelle", "emoji": "🌀",
                "effects": {"stat_debuff": {"speed": 30}},
            },
            "ultimate": {
                "name": "Boucle Temporelle", "emoji": "♾️",
                "effects": {"purge_self": True, "cancel_player_buffs": True, "dmg_mult": 2.0},
            },
        },
    },
    {
        "id": "raid_8", "name": "Nyxara la Corrompue", "emoji": "🐍", "raid_level": 8,
        "level_req": 800, "class": "Ombre Venin",
        "spells": {
            "s1": {
                "name": "Nuage Toxique", "emoji": "☠️",
                "effects": {"dot_player_poison": 2},
            },
            "ultimate": {
                "name": "Épidémie", "emoji": "🦠",
                "effects": {"purge_self": True, "dot_player_poison": 3, "dmg_mult": 1.5, "magic": True},
            },
        },
    },
    {
        "id": "raid_9", "name": "Ignareth le Phénix", "emoji": "🔥", "raid_level": 9,
        "level_req": 900, "class": "Pyromancien",
        "spells": {
            "s1": {
                "name": "Brasier Collectif", "emoji": "🌋",
                "effects": {"dot_player_burn": 2},
            },
            "ultimate": {
                "name": "Inferno Collectif", "emoji": "☄️",
                "effects": {"purge_self": True, "dmg_mult": 2.0, "magic": True, "resurrection_25": True},
            },
        },
    },
    {
        "id": "raid_10", "name": "Omnifax le Divin", "emoji": "🌑", "raid_level": 10,
        "level_req": 1000, "class": "Paladin",
        "spells": {
            "s1": {
                "name": "Jugement Sacré", "emoji": "⚖️",
                "effects": {"dmg_mult": 2.0, "stat_debuff": {"p_def": 20}},
            },
            "ultimate": {
                "name": "Châtiment Divin", "emoji": "✨",
                "effects": {"purge_self": True, "dmg_mult": 4.0, "heal_pct": 0.25},
            },
        },
    },
]

# Zone équivalente par niveau de raid (calibrée pour 5 joueurs avec équipements épiques)
RAID_LEVEL_ZONE_EQUIV = {i: i * 1000 for i in range(1, 11)}
# Raid N = zone N×1000 (raid 1 = zone 1000 = niveau 100, raid 10 = zone 10 000 = niveau 1000)

# Source d'équipement par niveau de raid (drop_source pour get_equipment_drops)
# item_level = (raid_level × 1000) // 10 = raid_level × 100
RAID_DROP_SOURCE = {
    1: "donjon_classique",  2: "donjon_classique",
    3: "donjon_elite",      4: "donjon_elite",
    5: "donjon_elite",      6: "donjon_abyssal",
    7: "donjon_abyssal",    8: "donjon_abyssal",
    9: "donjon_abyssal",   10: "raid",
}


def generate_raid_boss(raid_id: str, raid_number: int = 1) -> dict:
    """Génère un boss de raid calibré pour 5 joueurs au niveau raid_number×100."""
    boss = next((b for b in RAID_BOSSES if b["id"] == raid_id), RAID_BOSSES[0])
    raid_number = boss.get("raid_level", raid_number)
    zone_equiv = RAID_LEVEL_ZONE_EQUIV.get(raid_number, 225)

    boss_class = boss.get("class", "Guerrier")
    stats = compute_enemy_stats(zone_equiv, boss_class)

    # Stats ×2.5 pour un boss de raid (combat 5 joueurs)
    for k in list(stats):
        if k in ("crit_chance", "crit_damage"):
            stats[k] = round(stats[k] * 2.5, 2)
        elif k != "max_hp":
            stats[k] = int(stats[k] * 2.5)
    # HP ×4 supplémentaire → HP total ×10 vs ennemi de zone équivalente
    stats["hp"] = int(stats["hp"] * 4)
    stats["max_hp"] = stats["hp"]

    if raid_id == "raid_10":  # Boss final raid — stats offensives doublées
        for k in stats:
            if k not in ("hp", "max_hp", "speed", "crit_chance", "crit_damage"):
                stats[k] = int(stats[k] * 2)
        stats["max_hp"] = stats["hp"]

    xp   = int(zone_equiv * 150)
    gold = int(zone_equiv * 50)

    return {
        "name":               boss["name"],
        "class":              boss["class"],
        "raid_id":            raid_id,
        "raid_level":         raid_number,
        "level_req":          boss.get("level_req", 100),
        "type":               "raid",
        "theme":              "Raid",
        "theme_emoji":        boss["emoji"],
        "boss_spells":        ["s1", "ultimate"],
        "boss_spell_turn_mod": 4,
        "boss_custom_spells": boss.get("spells", {}),
        "xp":                 xp,
        "gold":               gold,
        "max_players":        5,
        **stats,
    }


# ─── Utilitaires ───────────────────────────────────────────────────────────

def compute_enemy_stats(level: int, class_name: str) -> dict:
    """
    Stats d'ennemi = stats joueur de niveau `level` × pct.
    pct = 30% au niveau 1 → 100% au niveau 10000 (linéaire).
    Utilise BASE_STATS + LEVEL_GROWTH de la classe (fallback: Guerrier).
    """
    level = max(1, min(level, 10000))
    pct   = 0.3 + 0.7 * (level - 1) / 9999
    resolved = class_name if class_name in BASE_STATS else "Guerrier"
    base  = BASE_STATS[resolved]
    class_growth = LEVEL_GROWTH.get(resolved) or LEVEL_GROWTH["Guerrier"]
    stats = {}
    for stat, growth in class_growth.items():
        player_val = base.get(stat, 0) + growth * (level - 1)
        if stat in ("crit_chance", "crit_damage"):
            stats[stat] = round(player_val * pct, 2)
        else:
            stats[stat] = int(player_val * pct)
    stats["max_hp"] = stats["hp"]
    return stats


def get_enemy_for_zone(zone: int, stage) -> dict:
    """
    Retourne l'ennemi approprié pour une zone/stage.
    Les boss s'enchaînent comme stages séparés après les ennemis classiques :
      1-10 → 'boss' (classique) → 'boss_runique' (×10) → 'boss_emblematique' (×100) → 'boss_antique' (×1000)
    """
    if stage == "boss":
        return generate_boss(zone)
    if stage == "boss_runique":
        return generate_runic_boss(zone)
    if stage == "boss_emblematique":
        return generate_emblematic_boss(zone)
    if stage == "boss_antique":
        return generate_antique_boss(zone)
    return generate_enemy(zone, stage)


def format_enemy_stats(enemy: dict) -> str:
    """Formate les stats d'un ennemi pour l'affichage."""
    lines = [
        f"❤️ **Points de Vie** : {enemy.get('hp', 0):,}",
        f"⚔️ **Attaque Physique** : {enemy.get('p_atk', 0):,}   🔮 **Attaque Magique** : {enemy.get('m_atk', 0):,}",
        f"🛡️ **Défense Physique** : {enemy.get('p_def', 0):,}   🔷 **Défense Magique** : {enemy.get('m_def', 0):,}",
        f"🗡️ **Pénétration Physique** : {enemy.get('p_pen', 0):,}   💫 **Pénétration Magique** : {enemy.get('m_pen', 0):,}",
        f"⚡ **Vitesse** : {enemy.get('speed', 0):,}   🎯 **Chance Critique** : {enemy.get('crit_chance', 0):.1f}%   💥 **Dégâts Critiques** : {enemy.get('crit_damage', 150):.0f}%",
    ]
    if passif := enemy.get("passif"):
        lines.append(f"💡 Passif : *{passif}*")
    return "\n".join(lines)
