"""
Wiki Generator — Bot Ultime RPG
Reads directly from game data and generates MkDocs markdown pages under docs/.

Usage (from project root):
    py tools/generate_wiki.py
"""
from __future__ import annotations
import sys
import types
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

# ─── Import game data via importlib (bypass package __init__ + discord) ───────
import importlib.util


def _load_file(module_name: str, file_path: Path):
    """Load a single .py file without triggering any package __init__."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


RPG = ROOT / "bot" / "cogs" / "rpg"
sys.path.insert(0, str(ROOT))

# Pre-register package stubs so intra-package imports resolve without __init__
for _pkg in ("bot", "bot.cogs", "bot.cogs.rpg"):
    if _pkg not in sys.modules:
        _m = types.ModuleType(_pkg)
        _m.__path__ = [str(ROOT / _pkg.replace(".", "/"))]
        _m.__package__ = _pkg
        sys.modules[_pkg] = _m

# Load data modules directly (no discord needed)
_models  = _load_file("bot.cogs.rpg.models",  RPG / "models.py")
_items   = _load_file("bot.cogs.rpg.items",   RPG / "items.py")
_quests  = _load_file("bot.cogs.rpg.quests",  RPG / "quests.py")
_enemies = _load_file("bot.cogs.rpg.enemies", RPG / "enemies.py")

# Re-export
CLASS_EMOJI            = _models.CLASS_EMOJI
CLASS_DESCRIPTION      = _models.CLASS_DESCRIPTION
BASE_STATS             = _models.BASE_STATS
CLASSES_STANDARD       = _models.CLASSES_STANDARD
CLASSES_PREMIUM        = _models.CLASSES_PREMIUM
ALL_CLASSES            = _models.ALL_CLASSES
ENERGY_COST            = _models.ENERGY_COST
MAX_ENERGY             = _models.MAX_ENERGY
PASSIVE_REGEN_HP_PCT   = _models.PASSIVE_REGEN_HP_PCT
PASSIVE_REGEN_ENERGY   = _models.PASSIVE_REGEN_ENERGY
PASSIVE_REGEN_INTERVAL = _models.PASSIVE_REGEN_INTERVAL
TITLES                 = _models.TITLES
TITLE_CATEGORIES       = _models.TITLE_CATEGORIES
RELICS                 = _models.RELICS
RARITIES               = _models.RARITIES
RARITY_EMOJI           = _models.RARITY_EMOJI
RARITY_MULT            = _models.RARITY_MULT
CLASS_SPELLS           = _models.CLASS_SPELLS
compute_class_stats    = _models.compute_class_stats
WB_RANK_REWARDS        = _models.WB_RANK_REWARDS
RELIC_CAPS             = _models.RELIC_CAPS

CONSUMABLES            = _items.CONSUMABLES
CONCEPTION_RECIPES     = _items.CONCEPTION_RECIPES
MATERIALS              = _items.MATERIALS
PROFESSION_MATERIALS   = _items.PROFESSION_MATERIALS

MAIN_QUESTS            = _quests.MAIN_QUESTS
SECONDARY_QUESTS       = _quests.SECONDARY_QUESTS

ZONE_THEMES            = _enemies.ZONE_THEMES
ENEMY_NAMES_BY_CLASS   = _enemies.ENEMY_NAMES_BY_CLASS
RUNIC_PASSIFS          = _enemies.RUNIC_PASSIFS
EMBLEMATIC_PASSIFS     = _enemies.EMBLEMATIC_PASSIFS
ANTIQUE_PASSIFS        = _enemies.ANTIQUE_PASSIFS
DUNGEON_BOSSES         = _enemies.DUNGEON_BOSSES
RAID_BOSSES            = _enemies.RAID_BOSSES
EMBLEMATIC_NAMES       = _enemies.EMBLEMATIC_NAMES
ANTIQUE_NAMES          = _enemies.ANTIQUE_NAMES
compute_enemy_stats    = _enemies.compute_enemy_stats
generate_world_boss    = _enemies.generate_world_boss


# ─── Classe metadata ─────────────────────────────────────────────────────────

CLASS_SLUG = {
    "Guerrier":           "guerrier",
    "Assassin":           "assassin",
    "Mage":               "mage",
    "Tireur":             "tireur",
    "Support":            "support",
    "Vampire":            "vampire",
    "Gardien du Temps":   "gardien",
    "Ombre Venin":        "ombre",
    "Pyromancien":        "pyromancien",
    "Paladin":            "paladin",
}

CLASS_SPELL_KEY = {
    "Guerrier":           "guerrier",
    "Assassin":           "assassin",
    "Mage":               "mage",
    "Tireur":             "tireur",
    "Support":            "support",
    "Vampire":            "vampire",
    "Gardien du Temps":   "gardien_du_temps",
    "Ombre Venin":        "ombre_venin",
    "Pyromancien":        "pyromancien",
    "Paladin":            "paladin",
}

CLASS_DIFFICULTY = {
    "Guerrier":           2,
    "Assassin":           3,
    "Mage":               3,
    "Tireur":             2,
    "Support":            4,
    "Vampire":            3,
    "Gardien du Temps":   5,
    "Ombre Venin":        4,
    "Pyromancien":        3,
    "Paladin":            2,
}

CLASS_ROLE = {
    "Guerrier":           "DPS Physique / Tank",
    "Assassin":           "DPS Physique / Esquive",
    "Mage":               "DPS Magique / Burst",
    "Tireur":             "DPS Physique / Cadence",
    "Support":            "Tank / Soutien Hybride",
    "Vampire":            "DPS Physique / Régénération",
    "Gardien du Temps":   "Contrôle / Hybride",
    "Ombre Venin":        "DPS DoT / Poison",
    "Pyromancien":        "DPS Magique / Brûlure",
    "Paladin":            "Tank Défensif / Burst",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _stars(n: int, max_n: int = 5) -> str:
    return "⭐" * n + "☆" * (max_n - n)


def _fmt_num(n: int | float) -> str:
    if isinstance(n, float) and n != int(n):
        return f"{n:,.1f}"
    return f"{int(n):,}"


def _fmt_req(req: int) -> str:
    if req >= 1_000_000_000:
        return f"{req // 1_000_000_000}G"
    if req >= 1_000_000:
        return f"{req // 1_000_000}M"
    if req >= 1_000:
        return f"{req // 1_000}k"
    return str(req)


def _req_type_label(rt: str) -> str:
    labels = {
        "level":           "Niveau joueur",
        "prestige":        "Niveau de prestige",
        "zone":            "Zone atteinte",
        "dungeon_clears":  "Donjons classiques",
        "elite_clears":    "Donjons élites",
        "abyssal_clears":  "Donjons abyssaux",
        "raid_clears":     "Raids complétés",
        "wb_total_damage": "Dégâts WB totaux",
        "wb_attacks":      "Attaques WB",
        "wb_rank1":        "Top 1 WB hebdo",
        "harvest_level":   "Niveau récolte",
        "craft_level":     "Niveau artisanat",
        "conception_level":"Niveau conception",
        "market_sales":    "Ventes HDV",
        "pvp_wins":        "Victoires PvP",
        "pvp_elo":         "Élo PvP",
        "total_gold":      "Gold accumulé",
        "global_rank1":    "Top 1 classement général hebdo",
        "pvp_rank1":       "Top 1 PvP hebdo",
    }
    return labels.get(rt, rt)


def _resource_label(resource: str) -> str:
    return {"rage": "🔴 Rage", "mana": "🔵 Mana", "combo": "🟡 Combo"}.get(resource, resource)


def write(filename: str, content: str) -> None:
    path = DOCS / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  OK {filename}")


def _stats_row(cls: str, level: int) -> str:
    """Return a table row with stats for a class at a given level."""
    s = compute_class_stats(cls, level, 0)
    hp      = _fmt_num(s.get("hp", 0))
    p_atk   = _fmt_num(s.get("p_atk", 0)) if s.get("p_atk") else "—"
    m_atk   = _fmt_num(s.get("m_atk", 0)) if s.get("m_atk") else "—"
    p_def   = _fmt_num(s.get("p_def", 0))
    m_def   = _fmt_num(s.get("m_def", 0))
    speed   = _fmt_num(s.get("speed", 0))
    crit    = f"{s.get('crit_chance', 0):.0f}%"
    return f"| Niv. {level} | {hp} | {p_atk} | {m_atk} | {p_def} | {m_def} | {speed} | {crit} |"


def _enemy_stats_line(zone: int, cls: str) -> str:
    """Compact stats line for an enemy."""
    s = compute_enemy_stats(zone, cls)
    return (f"❤️ {_fmt_num(s['hp'])}  "
            f"⚔️ {_fmt_num(s['p_atk'])}  "
            f"🔮 {_fmt_num(s['m_atk'])}  "
            f"🛡️ {_fmt_num(s['p_def'])}  "
            f"⚡ {_fmt_num(s['speed'])}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : index.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_index() -> None:
    n_classes = len(ALL_CLASSES)
    n_titles  = len(TITLES)
    n_items   = len(CONSUMABLES)
    n_quests  = len(MAIN_QUESTS) + len(SECONDARY_QUESTS)
    n_mats    = len(MATERIALS)

    content = f"""# 🏆 Bienvenue sur le Wiki — Bot Suprême RPG

> **Bot Suprême** est un jeu de rôle complet jouable directement sur Discord.
> Choisis ta classe, explore le monde, affronte des boss légendaires et défie d'autres joueurs !

---

## 📊 Le jeu en chiffres

| Catégorie            | Total |
|----------------------|------:|
| 🗡️ Classes           | {n_classes} |
| 🌍 Zones             | 10 000 |
| 🏆 Niveau maximum    | 1 000 |
| 🏰 Donjons           | 7 types × 3 difficultés |
| 👥 Raids             | 10 |
| 🎖️ Titres            | {n_titles} |
| 🧪 Consommables      | {n_items} |
| 🌿 Matériaux         | {n_mats} |
| 📜 Quêtes            | {n_quests} |

---

## 🗺️ Navigation rapide

| Section | Description |
|---------|-------------|
| 📖 [Guide Débutant](debutant.md) | Par où commencer — énergie, niveaux, progression |
| ⚔️ [Classes](classes/index.md) | Les {n_classes} classes avec leurs sorts et statistiques |
| 🌍 [Modes de Jeu](modes/index.md) | Monde, Donjons, Raids, World Boss, PvP |
| 🔨 [Métiers](metiers/index.md) | Récolte, Artisanat, Conception — matériaux et recettes |
| 📦 [Équipements](equipements/index.md) | Panoplies, raretés, améliorations |
| 🧪 [Objets](objets/potions.md) | Potions, Nourriture, Runes, Reliques |
| 📜 [Quêtes](quetes.md) | Toutes les quêtes et leurs récompenses |
| 🎖️ [Titres](titres.md) | Titres débloquables et leurs bonus permanents |
| ⚔️ [Mécanique de Combat](combat/mecanique.md) | Comment fonctionne un combat |

---

!!! info "Wiki généré automatiquement"
    Ce wiki est généré directement depuis le code du jeu et reste toujours à jour.
    Toutes les statistiques affichées sont exactes.
"""
    write("index.md", content)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : debutant.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_debutant() -> None:
    cost_monde = ENERGY_COST.get("ennemi", 1)
    cost_boss  = ENERGY_COST.get("boss_classique", 2)
    cost_djc   = ENERGY_COST.get("donjon_classique", 3)
    regen_int  = PASSIVE_REGEN_INTERVAL // 60

    content = f"""# 📖 Guide du Débutant

Bienvenue sur **Bot Suprême** ! Ce guide t'explique les bases pour démarrer efficacement.

---

## 1️⃣ Choisir sa classe

Rends-toi dans le canal **#classe** et sélectionne ta classe parmi les {len(ALL_CLASSES)} disponibles.

- ⚔️ **{len(CLASSES_STANDARD)} classes standard** — gratuites, accessibles à tous
- 💎 **{len(CLASSES_PREMIUM)} classes premium** — nécessitent le rôle Premium

!!! warning "Choix définitif"
    Le choix de classe est **permanent** — tu ne pourras pas en changer. Consulte la page [Classes](classes/index.md) pour comparer avant de décider !

---

## 2️⃣ L'Énergie ⚡

L'énergie est la ressource centrale du jeu. Chaque action en consomme.

| Action | Coût ⚡ |
|--------|--------:|
| Attaquer un ennemi | {cost_monde} |
| Boss classique | {cost_boss} |
| Boss runique | {ENERGY_COST.get('boss_runique', 3)} |
| Boss emblématique | {ENERGY_COST.get('boss_emblematique', 5)} |
| Boss antique | {ENERGY_COST.get('boss_antique', 10)} |
| Donjon classique | {cost_djc} |
| Donjon élite | {ENERGY_COST.get('donjon_elite', 5)} |
| Donjon abyssal | {ENERGY_COST.get('donjon_abyssal', 10)} |
| Raid | {ENERGY_COST.get('raid', 100)} |
| World Boss | {ENERGY_COST.get('world_boss', 100)} |
| PvP | {ENERGY_COST.get('pvp', 5)} |

**Énergie maximum :** {_fmt_num(MAX_ENERGY)} ⚡
**Régénération passive :** +{PASSIVE_REGEN_ENERGY} ⚡ toutes les {regen_int} minutes
**Régénération HP passive :** +{PASSIVE_REGEN_HP_PCT}% HP max toutes les {regen_int} minutes

---

## 3️⃣ Progresser dans le Monde 🌍

Dans le canal **#monde** :

1. **Attaque** les ennemis de ta zone pour gagner de l'XP et du Gold
2. Chaque zone a **4 stages d'ennemis** puis un **boss**
3. **Bats le boss** pour passer à la zone suivante
4. Active le **mode auto** pour farmer automatiquement (toutes les 3 secondes)

Les zones vont de 1 à **10 000**. Ton niveau détermine les zones accessibles *(zone ≈ niveau × 9)*.

---

## 4️⃣ L'XP et les Niveaux

- XP nécessaire pour passer au niveau suivant = **1 000 × niveau actuel**
  *(exemple : passer du niveau 10 au 11 demande 10 000 XP)*
- **Niveau maximum : 1 000**
- Après le niveau 1 000 → accès au **[Prestige](prestige.md)**

---

## 5️⃣ Les Métiers 🔨

Tu peux rejoindre jusqu'à **3 métiers** (un de chaque branche) :

| Branche | Exemples de métiers |
|---------|---------------------|
| 🌾 Récolte | Mineur, Herboriste, Chasseur, Fermier, Bûcheron |
| 🔨 Artisanat | Forgeron, Charpentier, Alchimiste artisan |
| ⚗️ Conception | Alchimiste, Boulanger, Enchanteur |

Consulte la page [Métiers](metiers/index.md) pour tous les détails.

---

## 6️⃣ Les Équipements 🛡️

Les équipements améliorent tes statistiques. Il existe **7 emplacements** :
casque, plastron, pantalon, chaussures, arme, amulette, anneau.

On les obtient en combattant dans le **monde**, les **donjons** et les **raids**.
Plus la source est difficile, plus les équipements sont puissants.

Consulte la page [Équipements](equipements/index.md) pour les détails.

---

## 7️⃣ Les Quêtes 📜

Les quêtes donnent de grosses récompenses en XP et Gold.

- **{len(MAIN_QUESTS)} quêtes principales** : à faire dans l'ordre, débloquent du contenu
- **{len(SECONDARY_QUESTS)} quêtes secondaires** : indépendantes, bonus supplémentaires

Consulte la page [Quêtes](quetes.md).

---

## 8️⃣ Les Titres 🎖️

Les titres donnent des **bonus permanents** (XP, Gold, stats de combat, etc.).
Commence par les titres de zone et de niveau — ils sont faciles à débloquer et très utiles.

Consulte la page [Titres](titres.md).

---

## 🎯 Conseils pour débuter

1. **Farm les ennemis** en mode auto pour monter rapidement en niveau
2. **Fais les quêtes principales** dès que tu peux — les récompenses sont énormes
3. **Débloque les titres faciles** (niveaux 10, 25, 50...) pour booster ton XP et ton Gold
4. **Explore les donjons classiques** dès le niveau 5 pour avoir de meilleurs équipements
5. **Rejoins un métier de récolte** pour collecter des matériaux et en vendre à l'HDV
"""
    write("debutant.md", content)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES : classes/index.md + classes/{slug}.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_classes() -> None:
    # ── Vue d'ensemble ──────────────────────────────────────────────────────
    lines = [
        "# ⚔️ Classes\n",
        f"Il existe **{len(CLASSES_STANDARD)} classes standard** (gratuites) et "
        f"**{len(CLASSES_PREMIUM)} classes premium** (rôle Premium requis).\n",
        "\n!!! warning \"Choix définitif\"\n    "
        "La classe choisie est **permanente**. Prends le temps de comparer !\n",
        "\n## 📊 Comparatif rapide\n",
        "| Classe | Rôle | Difficulté | Stats phares |",
        "|--------|------|-----------|--------------|",
    ]
    for cls in ALL_CLASSES:
        emoji = CLASS_EMOJI.get(cls, "")
        slug  = CLASS_SLUG[cls]
        diff  = CLASS_DIFFICULTY[cls]
        role  = CLASS_ROLE[cls]
        prem  = " 💎" if cls in CLASSES_PREMIUM else ""
        s1000 = compute_class_stats(cls, 1000, 0)
        # Best stat highlight
        best = []
        if s1000.get("hp", 0) > 28000:
            best.append(f"❤️ {_fmt_num(s1000['hp'])} HP")
        if s1000.get("p_atk", 0) > 2000:
            best.append(f"⚔️ {_fmt_num(s1000['p_atk'])}")
        if s1000.get("m_atk", 0) > 1500:
            best.append(f"🔮 {_fmt_num(s1000['m_atk'])}")
        if s1000.get("speed", 0) > 400:
            best.append(f"⚡ {_fmt_num(s1000['speed'])}")
        if s1000.get("crit_chance", 0) > 25:
            best.append(f"🎯 {s1000['crit_chance']:.0f}%")
        highlight = " · ".join(best[:2]) if best else "—"
        lines.append(f"| {emoji} **[{cls}]({slug}.md)**{prem} | {role} | {_stars(diff)} | {highlight} |")

    lines.append("\n💎 = Classe Premium\n")

    # ── Stats niveau 1 ──────────────────────────────────────────────────────
    stat_keys   = ["hp", "p_atk", "m_atk", "p_def", "m_def", "speed", "crit_chance"]
    stat_labels = ["❤️ HP", "⚔️ P.Atk", "🔮 M.Atk", "🛡️ P.Déf", "🔷 M.Déf", "⚡ Vit.", "🎯 Crit%"]
    lines.append("\n---\n\n## 📈 Stats au niveau 1 (sans équipement)\n")
    lines.append("| Classe | " + " | ".join(stat_labels) + " |")
    lines.append("|--------|" + "|".join(["------:"] * len(stat_keys)) + "|")
    for cls in ALL_CLASSES:
        emoji = CLASS_EMOJI.get(cls, "")
        base  = BASE_STATS.get(cls, {})
        vals  = []
        for k in stat_keys:
            v = base.get(k, 0)
            if k == "crit_chance":
                vals.append(f"{v:.0f}%")
            else:
                vals.append(_fmt_num(v) if v else "—")
        prem = " 💎" if cls in CLASSES_PREMIUM else ""
        lines.append(f"| {emoji} **{cls}**{prem} | " + " | ".join(vals) + " |")

    # ── Stats niveau 1000 ───────────────────────────────────────────────────
    lines.append("\n---\n\n## 🏆 Stats au niveau 1000 (sans équipement ni prestige)\n")
    lines.append("| Classe | " + " | ".join(stat_labels) + " |")
    lines.append("|--------|" + "|".join(["------:"] * len(stat_keys)) + "|")
    for cls in ALL_CLASSES:
        emoji = CLASS_EMOJI.get(cls, "")
        s     = compute_class_stats(cls, 1000, 0)
        vals  = []
        for k in stat_keys:
            v = s.get(k, 0)
            if k == "crit_chance":
                vals.append(f"{v:.0f}%")
            else:
                vals.append(_fmt_num(v) if v else "—")
        prem = " 💎" if cls in CLASSES_PREMIUM else ""
        lines.append(f"| {emoji} **{cls}**{prem} | " + " | ".join(vals) + " |")

    write("classes/index.md", "\n".join(lines))

    # ── Pages individuelles ─────────────────────────────────────────────────
    for cls in ALL_CLASSES:
        _gen_class_page(cls)


def _gen_class_page(cls: str) -> None:
    slug     = CLASS_SLUG[cls]
    emoji    = CLASS_EMOJI.get(cls, "")
    desc     = CLASS_DESCRIPTION.get(cls, "")
    diff     = CLASS_DIFFICULTY[cls]
    role     = CLASS_ROLE[cls]
    prem     = cls in CLASSES_PREMIUM
    sk       = CLASS_SPELL_KEY[cls]
    spells   = CLASS_SPELLS.get(sk, {})
    resource = spells.get("resource", "")

    lines = [f"# {emoji} {cls}\n"]

    if prem:
        lines.append("!!! note \"Classe Premium\"\n    Cette classe nécessite le rôle Premium pour être sélectionnée.\n")

    lines.append(f"**Rôle :** {role}\n")
    lines.append(f"**Difficulté :** {_stars(diff)} ({diff}/5)\n")
    lines.append(f"\n---\n\n## 📖 Description\n")

    # Parse description — separate passive from rest
    for line in desc.split("\n"):
        if line.strip():
            lines.append(line.strip() + "\n")

    # Resource
    if resource:
        r_max   = spells.get("resource_max", 0)
        r_turn  = spells.get("resource_per_turn", 0)
        r_hit   = spells.get("resource_on_hit", 0)
        r_label = _resource_label(resource)
        r_desc  = f"{r_label} — maximum {r_max}"
        if r_turn:
            r_desc += f", +{r_turn} par tour"
        if r_hit:
            r_desc += f", +{r_hit} par coup reçu"
        lines.append(f"\n**Ressource :** {r_desc}\n")

    # Stats table
    lines.append("\n---\n\n## 📊 Progression des statistiques\n")
    lines.append("| Niveau | ❤️ HP | ⚔️ Atk Phy | 🔮 Atk Mag | 🛡️ Déf Phy | 🔷 Déf Mag | ⚡ Vit. | 🎯 Crit% |")
    lines.append("|-------:|------:|----------:|----------:|----------:|----------:|-------:|--------:|")
    for lvl in [1, 100, 200, 500, 1000]:
        lines.append(_stats_row(cls, lvl))

    # Spells
    if spells:
        lines.append("\n---\n\n## ✨ Sorts\n")
        for skey, s_label in [("s1", "Sort 1"), ("s2", "Sort 2"), ("ultimate", "Ultime")]:
            s = spells.get(skey)
            if not s:
                continue
            ult_tag = " 🌟 **ULTIME**" if s.get("is_ultimate") else ""
            cost    = s.get("cost", 0)
            cd      = s.get("cooldown", 0)
            r_lbl   = _resource_label(resource)
            cd_str  = f" · Temps de recharge : **{cd} tours**" if cd else ""

            lines.append(f"### {s['emoji']} {s['name']}{ult_tag}\n")
            lines.append(f"{s['description']}\n")
            lines.append(f"- **Coût :** {cost} {r_lbl}{cd_str}\n")
            lines.append("")

    # Tips based on passive
    lines.append("\n---\n\n## 💡 Conseils de jeu\n")
    if cls == "Guerrier":
        lines.append("- Plus tu perds de HP, plus tu fais de dégâts — ne fuis pas les combats difficiles !\n")
        lines.append("- Utilise **Châtiment Sanglant** quand tu as peu de vie pour maximiser les dégâts.\n")
        lines.append("- **Immortalité** (ultime) te permet de survivre aux boss les plus dangereux.\n")
    elif cls == "Assassin":
        lines.append("- Accumule des Combos avant d'utiliser tes sorts.\n")
        lines.append("- **Exécution** (ultime) est idéal quand l'ennemi est presque mort.\n")
        lines.append("- Ton passif d'esquive réduit beaucoup les dégâts reçus dans la durée.\n")
    elif cls == "Mage":
        lines.append("- Plus tu as de HP, plus tes dégâts magiques sont élevés — reste en pleine santé.\n")
        lines.append("- **Nova Primordiale** ignore toute la défense magique — garde-la pour les boss.\n")
        lines.append("- **Soif Arcane** te permet de régénérer du Mana tout en attaquant.\n")
    elif cls == "Tireur":
        lines.append("- Ton passif double tes dégâts 25% du temps — très efficace sur les longs combats.\n")
        lines.append("- Utilise **Tir Marqué** puis **Tir Fatal** pour un burst dévastateur.\n")
        lines.append("- Ta vitesse élevée te permet souvent d'attaquer en premier.\n")
    elif cls == "Support":
        lines.append("- Très résistant — parfait pour les combats de longue durée.\n")
        lines.append("- **Renvoi Sacré** (ultime) combine réduction et renvoi de dégâts pour 3 tours.\n")
        lines.append("- Utilise **Frappe d'Affaiblissement** pour affaiblir les ennemis puissants.\n")
    elif cls == "Vampire":
        lines.append("- Vol de vie passif + sorts = régénération en combat quasi permanente.\n")
        lines.append("- Applique **Marque de Sang** puis déclenche l'ultime pour un burst maximal.\n")
        lines.append("- Sacrifier des HP avec **Marque de Sang** est rentable car tu te soignes beaucoup.\n")
    elif cls == "Gardien du Temps":
        lines.append("- Accumule 5 Combos grâce aux coups reçus pour des sorts plus fréquents.\n")
        lines.append("- **Arrêt du Temps** (ultime) paralyse l'ennemi 2 tours — décisif contre les boss.\n")
        lines.append("- Utilise **Fissure du Temps** pour réduire les défenses ennemies avant d'attaquer.\n")
    elif cls == "Ombre Venin":
        lines.append("- Accumule un maximum de stacks de poison avant de déclencher **Nécrose**.\n")
        lines.append("- Ton passif applique du poison 30% du temps — très efficace sur les longues fights.\n")
        lines.append("- **Brume Toxique** réduit aussi la Déf. Mag. ennemie pour encore plus de dégâts.\n")
    elif cls == "Pyromancien":
        lines.append("- Accumule au moins 5 stacks de brûlure avant d'utiliser **Inferno** pour le bonus.\n")
        lines.append("- Ton passif d'embrasement (35%) applique des stacks très rapidement.\n")
        lines.append("- Chaque stack de brûlure augmente tes dégâts — farm les brûlures au maximum.\n")
    elif cls == "Paladin":
        lines.append("- Classe la plus défensive du jeu — idéale pour les contenus de fin de jeu.\n")
        lines.append("- **Pénitence** booste tes stats offensives pendant 2 tours — combo avec l'ultime.\n")
        lines.append("- **Châtiment Divin** (ultime) inflige des dégâts basés sur TOUTES tes stats — dévastateur en fin de combat.\n")

    write(f"classes/{slug}.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : combat/mecanique.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_combat_mecanique() -> None:
    content = """# ⚔️ Mécanique de Combat

## 🔄 Déroulement d'un combat

Un combat se déroule en **tours**. À chaque tour :

1. Le joueur et l'ennemi jouent chacun leur tour (basé sur la **vitesse**)
2. Le joueur peut utiliser un **sort** s'il a assez de ressource
3. Les effets de statut (poison, brûlure) sont appliqués
4. La ressource du joueur se régénère automatiquement

---

## ⚡ Vitesse et ordre d'attaque

- Si ta **vitesse > vitesse ennemie** → tu attaques en premier
- Si ta vitesse est **3× supérieure** à celle de l'ennemi → tu attaques **2 fois** par tour
- La vitesse peut être boostée par des sorts ou des équipements

---

## 🗡️ Calcul des dégâts

Les dégâts physiques sont calculés comme suit :

> **Dégâts** = Attaque Physique − Défense Physique de l'ennemi + Pénétration Physique

La **Pénétration** ignore une partie de la défense ennemie.
Les **Critiques** multiplient les dégâts (multiplicateur de base : 150%).

---

## 🛡️ Types de défense

| Stat | Protège contre |
|------|----------------|
| 🛡️ Défense Physique | Attaques physiques (p_atk) |
| 🔷 Défense Magique | Attaques magiques (m_atk) |
| 🗡️ Pénétration Physique | Réduit la défense physique ennemie |
| 💫 Pénétration Magique | Réduit la défense magique ennemie |

---

## 💉 Effets de statut

| Effet | Description |
|-------|-------------|
| 🔥 Brûlure | Dégâts magiques par tour (15% ATK Mag/stack) |
| ☠️ Poison | Dégâts par tour (3% HP max/stack) |
| 😵 Étourdissement | L'ennemi ne peut pas agir pendant N tours |
| 🩸 Marque | L'ennemi subit des bonus de dégâts |

---

## ✨ Les Sorts

Chaque classe possède **3 sorts** :

- **Sort 1** (S1) : sort de base, coût faible, souvent sans temps de recharge
- **Sort 2** (S2) : sort intermédiaire, coût modéré, temps de recharge
- **⭐ Ultime** : sort puissant, coût élevé, long temps de recharge

Les sorts se déclenchent **automatiquement** quand :
- Tu as assez de ressource
- Le temps de recharge est écoulé
- C'est le bon moment selon l'IA du personnage

---

## ❤️ Régénération HP

Entre les combats, tu récupères automatiquement :
- **+3% de tes HP max** toutes les 10 minutes (passif)
- Des potions de soin peuvent être utilisées en combat

---

## 🎯 Critiques

- La **chance de critique** détermine la probabilité d'un coup critique
- Les **dégâts critiques** multiplient les dégâts du coup critique
- Base : 150% (×1.5 dégâts normaux)
- Certaines classes ont des modificateurs critiques élevés (Assassin 175%, Mage 175%)
"""
    write("combat/mecanique.md", content)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : combat/ennemis.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_combat_ennemis() -> None:
    content = """# 🔍 Simulateur d'Ennemis

Utilise le simulateur interactif ci-dessous pour connaître les statistiques exactes
de n'importe quel ennemi selon la zone, le type de boss, ou le niveau de donjon/raid.

---

<div class="enemy-simulator-tabs" id="simulator-root">
  <p><em>Chargement du simulateur...</em></p>
</div>

<script>
// Le simulateur est chargé depuis javascripts/enemy_calc.js
document.addEventListener('DOMContentLoaded', function() {
  if (typeof initEnemyCalc === 'function') {
    initEnemyCalc('simulator-root');
  }
});
</script>

---

!!! tip "Navigation par mode"
    Chaque page de mode de jeu contient aussi un lien vers le simulateur pré-configuré pour ce mode :

    - [🌍 Simulateur Monde](../modes/monde.md)
    - [🏰 Simulateur Donjons](../modes/donjons.md)
    - [👥 Simulateur Raids](../modes/raids.md)
    - [🐉 Simulateur World Boss](../modes/world_boss.md)
"""
    write("combat/ennemis.md", content)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : equipements/index.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_equipements() -> None:
    content = """# 🛡️ Équipements & Panoplies

Les équipements améliorent tes statistiques de combat. Chaque pièce est liée à ta **classe**
et possède un **niveau**, une **rareté** et un **niveau d'amélioration**.

---

## 🎒 Les 7 emplacements

| Slot | Emoji | Stat principale |
|------|-------|----------------|
| Casque | ⛑️ | Défense physique |
| Plastron | 🦺 | HP |
| Pantalon | 👖 | Vitesse |
| Chaussures | 👟 | Vitesse |
| Arme | ⚔️ | Attaque |
| Amulette | 📿 | Attaque magique |
| Anneau | 💍 | Chance de critique |

---

## 💎 Raretés

Les raretés déterminent la puissance des équipements. Plus la rareté est élevée, plus les stats sont importantes.

| Rareté | Emoji | Multiplicateur |
|--------|-------|---------------:|
| Commun | ⬜ | ×1.0 |
| Peu commun | 🟩 | ×1.2 |
| Rare | 🟦 | ×1.4 |
| Épique | 🟪 | ×1.6 |
| Légendaire | 🟧 | ×1.8 |
| Mythique | 🟥 | ×2.0 |
| Artefact | 🔶 | ×2.2 |
| Divin | 🟡 | ×2.4 |
| Transcendant | 🩵 | ×2.6 |
| Prismatique | 🌈 | ×3.0 |

---

## 🌟 Sources d'équipement

Chaque source a un **multiplicateur de puissance** différent.
Les sources plus difficiles donnent des équipements plus puissants.

| Source | Comment l'obtenir | Puissance relative |
|--------|-------------------|--------------------|
| Monde | Combat dans le monde ouvert | ⭐ |
| Donjon Classique | Donjons niveau 1-100 (classique) | ⭐⭐ |
| Craft | Artisanat (métier forgeron/charpentier) | ⭐⭐⭐ |
| Donjon Élite | Donjons niveau 1-100 (élite) | ⭐⭐⭐ |
| Donjon Abyssal | Donjons niveau 1-100 (abyssal) | ⭐⭐⭐⭐ |
| Raid | Raids niveau 1-10 | ⭐⭐⭐⭐⭐ |

---

## 🔥 Améliorations

Les équipements peuvent être améliorés (Enhancement +1 à +10) pour augmenter leurs statistiques.
Plus le niveau d'amélioration est élevé, plus les stats sont importantes.

---

## 🏆 Panoplies (Bonus de set)

Posséder plusieurs pièces du même **thème** (même source + même classe) donne un bonus de panoplie.
Le bonus est proportionnel au nombre de pièces équipées du même set.

---

!!! info "Restriction de classe"
    Chaque équipement est lié à une classe spécifique.
    Tu ne peux équiper que les items correspondant à **ta propre classe**.
    De plus, un équipement ne peut être porté que si son **niveau ≤ ton niveau**.
"""
    write("equipements/index.md", content)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : metiers/index.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_metiers() -> None:
    # Group conception recipes by profession
    by_prof_recipes: dict[str, list] = {}
    for rid, rec in CONCEPTION_RECIPES.items():
        prof = rec.get("profession", "?")
        by_prof_recipes.setdefault(prof, []).append((rid, rec))

    content = """# 🔨 Métiers

Les métiers te permettent de **récolter des matériaux**, **fabriquer des équipements**
et **créer des consommables** puissants.

Tu peux exercer jusqu'à **3 métiers** simultanément (un de chaque branche).
Chaque métier a son propre niveau, qui monte de **1 à 100**.

---

## Les 3 branches de métiers

| Branche | Description | Métiers disponibles |
|---------|-------------|---------------------|
| 🌾 **Récolte** | Collecter des matériaux dans le monde | Mineur, Bûcheron, Herboriste, Chasseur, Fermier |
| 🔨 **Artisanat** | Fabriquer des équipements à partir de matériaux | Forgeron, Charpentier |
| ⚗️ **Conception** | Créer des consommables (potions, nourriture, runes) | Alchimiste, Boulanger, Enchanteur |

---

## 🌾 Récolte

La récolte s'effectue dans le canal **#métiers**.
Chaque coup de récolte donne des matériaux selon ta profession et ton niveau.

| Profession | Matériaux récoltés | Tier max |
|------------|-------------------|----------|
| ⛏️ Mineur | Minerais, pierres, cristaux | 10 tiers |
| 🪓 Bûcheron | Bois de différentes essences | 10 tiers |
| 🌿 Herboriste | Herbes, fleurs, champignons | 10 tiers |
| 🏹 Chasseur | Cuirs, griffes, crocs, os | 10 tiers |
| 🌾 Fermier | Blé, orge, épices, fruits rares | 10 tiers |

Chaque tier correspond à **10 niveaux de métier** (tier 1 = niv 1-10, tier 10 = niv 91-100).
Un **niveau de récolte plus élevé** augmente les chances de drop de matériaux rares.

Consulte la page [Matériaux](../objets/materiaux.md) pour la liste complète.

---

## 🔨 Artisanat

L'artisanat permet de **fabriquer des équipements** à partir de matériaux récoltés.

| Niveau d'artisanat | Raretés accessibles |
|--------------------|---------------------|
| 1-10 | Commun, Peu commun, Rare |
| 11-30 | + Épique |
| 31-60 | + Légendaire, Mythique |
| 61-100 | + Artefact, Divin, Transcendant, Prismatique |

Les équipements craftés appartiennent à la **source craft** — très puissants.

---

## ⚗️ Conception

La conception produit des **consommables** utilisables en combat.
Consulte les pages correspondantes pour les recettes :

| Profession | Produits | Page |
|------------|---------|------|
| ⚗️ Alchimiste | Potions de soin, d'attaque, de défense... | [Potions](../objets/potions.md) |
| 🍞 Boulanger | Nourriture qui restaure et booste l'énergie | [Nourriture](../objets/nourriture.md) |
| ✨ Enchanteur | Runes qui boostent les stats en combat | [Runes](../objets/runes.md) |

---

"""
    # Recettes par profession
    prof_labels = {
        "alchimiste": ("⚗️", "Alchimiste", "../objets/potions.md"),
        "boulanger":  ("🍞", "Boulanger",  "../objets/nourriture.md"),
        "enchanteur": ("✨", "Enchanteur",  "../objets/runes.md"),
    }

    content += "## 📋 Recettes de conception\n\n"
    for prof_key in ["alchimiste", "boulanger", "enchanteur"]:
        recipes = by_prof_recipes.get(prof_key, [])
        if not recipes:
            continue
        emoji, pname, page = prof_labels.get(prof_key, ("", prof_key, ""))
        recipes_sorted = sorted(recipes, key=lambda x: x[1].get("level_req", 0))
        content += f"### {emoji} {pname} — {len(recipes)} recettes\n\n"
        content += "| Niv. requis | Résultat | Qté | Ingrédients |\n"
        content += "|------------:|----------|----:|-------------|\n"
        for rid, rec in recipes_sorted:
            result_id   = rec.get("result", "?")
            result_item = CONSUMABLES.get(result_id, {})
            result_name = result_item.get("name", result_id)
            result_emoji= result_item.get("emoji", "")
            qty         = rec.get("qty", 1)
            lvl         = rec.get("level_req", 1)
            ingrs       = rec.get("ingredients", {})
            # Format ingredient names nicely
            ingr_parts  = []
            for k, v in ingrs.items():
                mat = MATERIALS.get(k, {})
                mat_name = mat.get("name", k.replace("mat_", "").replace("_", " ").title())
                mat_emoji= mat.get("emoji", "")
                ingr_parts.append(f"{v}× {mat_emoji} {mat_name}")
            ingr_str = ", ".join(ingr_parts)
            content += f"| {lvl} | {result_emoji} {result_name} | ×{qty} | {ingr_str} |\n"
        content += "\n"

    write("metiers/index.md", content)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : modes/index.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_modes_index() -> None:
    content = f"""# 🗺️ Modes de Jeu

Bot Suprême propose **5 modes de jeu** différents, chacun avec ses propres ennemis, récompenses et mécaniques.

---

## Résumé des coûts en énergie

| Mode | Coût ⚡ | Récompenses |
|------|--------:|-------------|
| 🌍 Ennemi monde | {ENERGY_COST.get('ennemi', 1)} | XP, Gold |
| 🌍 Boss classique | {ENERGY_COST.get('boss_classique', 2)} | XP, Gold, Équipement |
| 🌍 Boss runique | {ENERGY_COST.get('boss_runique', 3)} | XP, Gold, Équipement |
| 🌍 Boss emblématique | {ENERGY_COST.get('boss_emblematique', 5)} | XP, Gold, Équipement+ |
| 🌍 Boss antique | {ENERGY_COST.get('boss_antique', 10)} | XP, Gold, Équipement++ |
| 🏰 Donjon classique | {ENERGY_COST.get('donjon_classique', 3)} | Équipement (craft) |
| 🏰 Donjon élite | {ENERGY_COST.get('donjon_elite', 5)} | Équipement (élite) |
| 🏰 Donjon abyssal | {ENERGY_COST.get('donjon_abyssal', 10)} | Équipement (abyssal) |
| 👥 Raid | {ENERGY_COST.get('raid', 100)} | Équipement (raid) |
| 🐉 World Boss | {ENERGY_COST.get('world_boss', 100)} | Reliques, Gold |
| 🥊 PvP | {ENERGY_COST.get('pvp', 5)} | Élo, Gloire |

---

## 🌍 [Monde](monde.md)

Le mode principal. Progresse de zone en zone (1 → 10 000) en battant des ennemis et des boss.
Disponible en **mode automatique** pour farmer en continu.

## 🏰 [Donjons](donjons.md)

7 types de boss, 3 difficultés (Classique / Élite / Abyssal). Les meilleures sources d'équipements.

## 👥 [Raids](raids.md)

10 boss légendaires conçus pour **5 joueurs**. Les équipements les plus puissants du jeu.

## 🐉 [World Boss](world_boss.md)

Un boss partagé par tous les joueurs, réinitialisé chaque semaine. Récompenses basées sur les dégâts infligés.

## 🥊 [Taverne — PvP](pvp.md)

Affronte d'autres joueurs. Système Élo pour le mode classé.
"""
    write("modes/index.md", content)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : modes/monde.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_monde() -> None:
    lines = [
        "# 🌍 Mode Monde\n",
        "Le **Monde** est le mode de jeu principal. Tu progresses zone par zone, "
        "en affrontant des ennemis de plus en plus puissants jusqu'à la zone **10 000**.\n",
        "\n---\n",
        "\n## ⚡ Coûts en énergie\n",
        "| Type d'action | Coût ⚡ |",
        "|---------------|--------:|",
        f"| Ennemi normal | {ENERGY_COST.get('ennemi', 1)} |",
        f"| Boss classique | {ENERGY_COST.get('boss_classique', 2)} |",
        f"| Boss runique | {ENERGY_COST.get('boss_runique', 3)} |",
        f"| Boss emblématique | {ENERGY_COST.get('boss_emblematique', 5)} |",
        f"| Boss antique | {ENERGY_COST.get('boss_antique', 10)} |",
        "",
        "\n---\n",
        "\n## 🗺️ Structure d'une zone\n",
        "Chaque zone contient :\n",
        "- **4 stages d'ennemis** (classes différentes selon le stage)\n",
        "- **1 boss classique** pour passer à la zone suivante\n",
        "- Tous les **10 zones** : un **Boss Runique** plus puissant 🔮\n",
        "- Tous les **100 zones** : un **Boss Emblématique** légendaire 🌟\n",
        "- Tous les **1000 zones** : un **Boss Antique**, le plus redoutable ⚠️\n",
        "",
        "\n---\n",
        "\n## 🌿 Thèmes des zones\n",
        "Les zones sont regroupées en **thèmes** qui changent tous les 1 000 zones.\n",
        "",
        "| Zones | Thème | Ambiance |",
        "|-------|-------|---------|",
    ]

    for i, (theme_name, theme_emoji) in enumerate(ZONE_THEMES):
        zone_start = i * 1000 + 1
        zone_end   = (i + 1) * 1000
        diff = _stars(min(i + 1, 5))
        lines.append(f"| {zone_start}–{zone_end} | {theme_emoji} {theme_name} | {diff} |")

    lines.append("\n---\n")
    lines.append("\n## 👹 Ennemis par classe\n")
    lines.append("Les ennemis tournent cycliquement entre les **10 classes** selon le stage :\n")
    lines.append("")
    lines.append("| Classe | Noms possibles |")
    lines.append("|--------|---------------|")
    for cls, names in ENEMY_NAMES_BY_CLASS.items():
        emoji = CLASS_EMOJI.get(cls, "")
        lines.append(f"| {emoji} {cls} | {', '.join(names)} |")

    lines.append("\n---\n")
    lines.append("\n## 🏆 Types de boss\n")
    lines.append("\n### ⚔️ Boss Classique — toutes les zones\n")
    lines.append("Le boss de chaque zone. Il a **+20% HP** par rapport aux ennemis normaux.\n")
    lines.append("Vaincre le boss permet de **passer à la zone suivante**.\n")
    lines.append(f"- Énergie : **{ENERGY_COST.get('boss_classique', 2)} ⚡**\n")

    lines.append("\n### 🔮 Boss Runique — toutes les 10 zones\n")
    lines.append("Un boss plus puissant avec un **passif spécial** selon sa classe.\n")
    lines.append("Il a **+50% HP** et utilise le **Sort 1** de sa classe.\n")
    lines.append(f"- Énergie : **{ENERGY_COST.get('boss_runique', 3)} ⚡**\n")
    lines.append("")
    lines.append("| Classe | Passif Runique |")
    lines.append("|--------|---------------|")
    for cls, passif in RUNIC_PASSIFS.items():
        emoji = CLASS_EMOJI.get(cls, "")
        lines.append(f"| {emoji} {cls} | **{passif['name']}** : {passif['text']} |")

    lines.append("\n### 🌟 Boss Emblématique — toutes les 100 zones\n")
    lines.append("Un boss légendaire avec un **nom propre**, **+100% HP** et un passif encore plus dangereux.\n")
    lines.append("Il utilise les **Sorts 1 et 2** de sa classe.\n")
    lines.append(f"- Énergie : **{ENERGY_COST.get('boss_emblematique', 5)} ⚡**\n")
    lines.append("")
    lines.append("Noms emblématiques (rotation) : " + ", ".join(EMBLEMATIC_NAMES[:10]) + "...\n")
    lines.append("")
    lines.append("| Classe | Passif Emblématique |")
    lines.append("|--------|---------------------|")
    for cls, passif in EMBLEMATIC_PASSIFS.items():
        emoji = CLASS_EMOJI.get(cls, "")
        lines.append(f"| {emoji} {cls} | **{passif['name']}** : {passif['text']} |")

    lines.append("\n### ⚠️ Boss Antique — toutes les 1000 zones\n")
    lines.append("Le boss ultime de chaque millénaire. **+200% HP**, passif destructeur, "
                 "utilise **Sorts 1, 2 et Ultime**.\n")
    lines.append(f"- Énergie : **{ENERGY_COST.get('boss_antique', 10)} ⚡**\n")
    lines.append("")
    lines.append("Noms antiques : " + ", ".join(ANTIQUE_NAMES) + "\n")
    lines.append("")
    lines.append("| Classe | Passif Antique |")
    lines.append("|--------|---------------|")
    for cls, passif in ANTIQUE_PASSIFS.items():
        emoji = CLASS_EMOJI.get(cls, "")
        lines.append(f"| {emoji} {cls} | **{passif['name']}** : {passif['text']} |")

    lines.append("\n---\n")
    lines.append("\n## 📈 Progression des stats ennemies\n")
    lines.append("Les ennemis deviennent de plus en plus puissants. Voici leurs statistiques à des zones clés :\n")
    lines.append("")
    lines.append("| Zone | ❤️ HP | ⚔️ Atk Phy | 🛡️ Déf Phy | ⚡ Vit. | Difficulté |")
    lines.append("|-----:|------:|----------:|----------:|-------:|-----------|")
    sample_zones = [1, 100, 500, 1000, 2500, 5000, 7500, 10000]
    for z in sample_zones:
        s = compute_enemy_stats(z, "Guerrier")
        diff = _stars(min(1 + (z - 1) // 2000, 5))
        lines.append(f"| {z:,} | {_fmt_num(s['hp'])} | {_fmt_num(s['p_atk'])} | {_fmt_num(s['p_def'])} | {_fmt_num(s['speed'])} | {diff} |")

    lines.append("\n---\n")
    lines.append("\n!!! tip \"Simulateur d'ennemis\"\n    "
                 "Utilise le [Simulateur d'Ennemis](../combat/ennemis.md) pour connaître "
                 "les stats exactes de n'importe quel ennemi dans n'importe quelle zone.\n")

    write("modes/monde.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : modes/donjons.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_donjons() -> None:
    lines = [
        "# 🏰 Donjons\n",
        "Les donjons te permettent d'obtenir des **équipements puissants** en battant des boss spécialisés.\n",
        "Il existe **7 boss de donjon**, chacun lié à un **slot d'équipement** spécifique.\n",
        "\n---\n",
        "\n## ⚡ Niveaux de difficulté\n",
        "",
        "| Difficulté | Énergie ⚡ | Niveaux | Équipement | Difficulté |",
        "|------------|----------:|---------|-----------|-----------|",
        f"| ⚔️ Classique | {ENERGY_COST.get('donjon_classique', 3)} | 1 – 100 | Source Classique ⭐⭐ | {_stars(2)} |",
        f"| 🔥 Élite | {ENERGY_COST.get('donjon_elite', 5)} | 1 – 100 | Source Élite ⭐⭐⭐ | {_stars(3)} |",
        f"| 💀 Abyssal | {ENERGY_COST.get('donjon_abyssal', 10)} | 1 – 100 | Source Abyssale ⭐⭐⭐⭐ | {_stars(4)} |",
        "",
        "\n**Sorts disponibles par difficulté :**\n",
        "- **Classique** : le boss utilise uniquement son Sort 1\n",
        "- **Élite** : le boss utilise Sort 1 et Sort 2\n",
        "- **Abyssal** : le boss utilise Sort 1, Sort 2 et son **Ultime**\n",
        "",
        "\n---\n",
        "\n## 🐲 Les 7 Boss de Donjon\n",
        "Chaque boss est spécialisé dans un slot d'équipement et possède un **passif unique**.\n",
        "",
    ]

    for boss in DUNGEON_BOSSES:
        emoji = boss.get("emoji", "")
        slot  = boss.get("slot", "?").capitalize()
        name  = boss.get("name", "?")
        stat  = boss.get("stat_boost", "?")
        passif = boss.get("passif", "")
        stat_labels = {
            "p_def": "Défense Physique",
            "hp":    "HP",
            "speed": "Vitesse",
            "p_atk": "Attaque Physique",
            "m_atk": "Attaque Magique",
            "crit_chance": "Chance Critique",
        }
        stat_name = stat_labels.get(stat, stat)

        lines.append(f"### {emoji} {name} — Slot : {slot}\n")
        lines.append(f"**Stat boostée :** +50% {stat_name}\n")
        lines.append(f"**Passif :** {passif}\n")
        lines.append("")

    lines.append("\n---\n")
    lines.append("\n## 📈 Stats des boss selon le niveau\n")
    lines.append("Les stats du boss augmentent avec le niveau de donjon (1 à 100).\n")
    lines.append("")
    lines.append("| Niv. Donjon | Zone équiv. | ❤️ HP (Classique) | ❤️ HP (Élite) | ❤️ HP (Abyssal) | Niveau joueur recommandé |")
    lines.append("|------------:|------------:|------------------:|-------------:|----------------:|------------------------:|")
    for lvl in [1, 10, 25, 50, 75, 100]:
        # Use d_casque as example boss (p_def focused)
        zone_c = lvl * 33
        zone_e = 3333 + lvl * 33
        zone_a = 6666 + lvl * 33
        s_c = compute_enemy_stats(zone_c, "Guerrier")
        s_e = compute_enemy_stats(zone_e, "Guerrier")
        s_a = compute_enemy_stats(zone_a, "Guerrier")
        hp_c = int(s_c["hp"] * 1.2 * 1.0)  # classique mult
        hp_e = int(s_e["hp"] * 1.2 * 1.5)  # elite mult
        hp_a = int(s_a["hp"] * 1.2 * 2.0)  # abyssal mult
        rec_lvl = zone_c // 10
        lines.append(f"| {lvl} | {zone_c:,} | {_fmt_num(hp_c)} | {_fmt_num(hp_e)} | {_fmt_num(hp_a)} | {rec_lvl} |")

    lines.append("\n---\n")
    lines.append("\n!!! tip \"Simulateur d'ennemis\"\n    "
                 "Utilise le [Simulateur d'Ennemis](../combat/ennemis.md) pour calculer "
                 "les stats exactes d'un boss de donjon.\n")

    write("modes/donjons.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : modes/raids.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_raids() -> None:
    lines = [
        "# 👥 Raids\n",
        "Les raids sont des combats **épiques** contre des boss légendaires conçus pour **5 joueurs**.\n",
        "Ils donnent les équipements les plus puissants du jeu.\n",
        "\n---\n",
        "\n## 📋 Informations générales\n",
        f"- **Coût :** {ENERGY_COST.get('raid', 100)} ⚡ par raid\n",
        "- **Joueurs :** jusqu'à 5 joueurs en simultané\n",
        "- **Niveaux :** Raid 1 → Raid 10 (difficulté croissante)\n",
        "- **Équipement :** source Raid, la plus puissante du jeu\n",
        "",
        "\n---\n",
        "\n## 🐉 Les 10 Boss de Raid\n",
        "",
    ]

    for boss in RAID_BOSSES:
        rl      = boss.get("raid_level", 1)
        name    = boss.get("name", "?")
        emoji   = boss.get("emoji", "")
        cls     = boss.get("class", "?")
        cls_e   = CLASS_EMOJI.get(cls, "")
        lvl_req = boss.get("level_req", 100)
        spells  = boss.get("spells", {})
        zone_eq = rl * 1000

        # Stats
        s = compute_enemy_stats(zone_eq, cls)
        hp = int(s["hp"] * 2.5 * 4)

        lines.append(f"### {emoji} Raid {rl} — {name}\n")
        lines.append(f"**Classe :** {cls_e} {cls}  |  **Niveau requis :** {lvl_req}  |  **Zone équivalente :** {zone_eq:,}\n")
        lines.append(f"**HP :** environ {_fmt_num(hp)} (pour un groupe de 5 joueurs)\n")

        if spells:
            lines.append("\n**Sorts :**\n")
            for skey in ["s1", "ultimate"]:
                sp = spells.get(skey)
                if not sp:
                    continue
                sp_name  = sp.get("name", skey)
                sp_emoji = sp.get("emoji", "")
                effects  = sp.get("effects", {})
                # Describe effects in plain French
                eff_parts = []
                if effects.get("dmg_mult"):
                    eff_parts.append(f"×{effects['dmg_mult']} dégâts")
                if effects.get("magic"):
                    eff_parts.append("magiques")
                if effects.get("stat_debuff"):
                    for stat, val in effects["stat_debuff"].items():
                        stat_labels = {"speed": "Vitesse", "m_def": "Déf. Mag.", "p_def": "Déf. Phy."}
                        eff_parts.append(f"−{val} {stat_labels.get(stat, stat)} ennemie")
                if effects.get("lifesteal_pct"):
                    eff_parts.append(f"vol de vie {int(effects['lifesteal_pct']*100)}%")
                if effects.get("dot_player_poison"):
                    eff_parts.append(f"+{effects['dot_player_poison']} stacks poison")
                if effects.get("dot_player_burn"):
                    eff_parts.append(f"+{effects['dot_player_burn']} stacks brûlure")
                if effects.get("drain_pct"):
                    eff_parts.append(f"drains {int(effects['drain_pct']*100)}% HP")
                if effects.get("cancel_player_buffs"):
                    eff_parts.append("annule tous tes buffs")
                if effects.get("self_dmg_buff"):
                    eff_parts.append(f"+{int(effects['self_dmg_buff']*100)}% dégâts pendant {effects.get('self_dmg_buff_turns', 1)} tours")
                if effects.get("heal_pct"):
                    eff_parts.append(f"se soigne {int(effects['heal_pct']*100)}% HP max")
                if effects.get("resurrection_25"):
                    eff_parts.append("se résurrecte à 25% HP si tué")
                if effects.get("purge_self"):
                    eff_parts.append("se purifie de tous les debuffs")
                if effects.get("mark_player"):
                    eff_parts.append(f"te marque (+{effects['mark_player']}% dégâts reçus)")

                eff_str = " · ".join(eff_parts) if eff_parts else "Effet spécial"
                tag = " 🌟 *(Ultime)*" if skey == "ultimate" else ""
                lines.append(f"- **{sp_emoji} {sp_name}**{tag} — {eff_str}\n")

        diff = _stars(min(rl // 2 + 1, 5))
        lines.append(f"\n**Difficulté :** {diff}\n")
        lines.append("")

    lines.append("\n---\n")
    lines.append("\n## 📊 Comparatif des raids\n")
    lines.append("")
    lines.append("| Raid | Boss | Niv. requis | Zone équiv. | HP estimés | Difficulté |")
    lines.append("|-----:|------|------------:|------------:|----------:|-----------|")
    for boss in RAID_BOSSES:
        rl  = boss.get("raid_level", 1)
        n   = boss.get("name", "?")
        e   = boss.get("emoji", "")
        lr  = boss.get("level_req", 100)
        ze  = rl * 1000
        cls = boss.get("class", "Guerrier")
        s   = compute_enemy_stats(ze, cls)
        hp  = int(s["hp"] * 2.5 * 4)
        diff = _stars(min(rl // 2 + 1, 5))
        lines.append(f"| {rl} | {e} {n} | {lr} | {ze:,} | {_fmt_num(hp)} | {diff} |")

    lines.append("\n---\n")
    lines.append("\n!!! tip \"Simulateur d'ennemis\"\n    "
                 "Utilise le [Simulateur d'Ennemis](../combat/ennemis.md) pour voir "
                 "les stats exactes des boss de raid.\n")

    write("modes/raids.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : modes/world_boss.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_world_boss() -> None:
    lines = [
        "# 🐉 World Boss\n",
        "Le **World Boss** est un boss colossal partagé par **tous les joueurs** du serveur.\n",
        "Il est réinitialisé chaque **lundi à minuit** et les récompenses sont distribuées selon les dégâts infligés.\n",
        "\n---\n",
        "\n## 📋 Informations générales\n",
        f"- **Coût :** {ENERGY_COST.get('world_boss', 100)} ⚡ par attaque\n",
        "- **Partage :** tous les joueurs attaquent le même boss\n",
        "- **Réinitialisation :** chaque lundi à minuit (UTC)\n",
        "- **Classement :** basé sur les **dégâts totaux** infligés dans la semaine\n",
        "",
        "\n---\n",
        "\n## 🎁 Récompenses hebdomadaires\n",
        "Les récompenses sont distribuées le lundi selon ton classement.\n",
        "",
        "| Rang | Relique | Gold |",
        "|-----:|---------|------:|",
    ]

    rarity_names = {
        "prismatique":  "Prismatique 🌈",
        "transcendant": "Transcendant 🩵",
        "divin":        "Divin 🟡",
        "artefact":     "Artefact 🔶",
        "mythique":     "Mythique 🟥",
        "legendaire":   "Légendaire 🟧",
        "epique":       "Épique 🟪",
        "rare":         "Rare 🟦",
        "peu_commun":   "Peu commun 🟩",
        "commun":       "Commun ⬜",
    }
    rank_emojis = {1: "🥇", 2: "🥈", 3: "🥉"}
    for rank, reward in WB_RANK_REWARDS.items():
        if rank == "default":
            continue
        r_id   = reward.get("relic", "")
        gold   = reward.get("gold", 0)
        # Extract rarity from relic_id (e.g. relic_bot_supreme_prismatique)
        rarity = r_id.replace("relic_bot_supreme_", "")
        r_name = rarity_names.get(rarity, rarity)
        re     = rank_emojis.get(rank, f"#{rank}")
        lines.append(f"| {re} {rank} | {r_name} | {_fmt_num(gold)} |")

    default_r = WB_RANK_REWARDS.get("default", {})
    lines.append(f"| #11+ | Commun ⬜ | {_fmt_num(default_r.get('gold', 200))} |")

    lines.append("\n---\n")
    lines.append("\n## 🗡️ Reliques du World Boss\n")
    lines.append("Les reliques sont équipables et donnent des **bonus permanents en combat**.\n")
    lines.append("Il existe une relique par rareté — plus la rareté est élevée, plus les bonus sont puissants.\n")
    lines.append("")
    lines.append("| Rareté | Vol de vie | Réd. dégâts | Bonus dégâts | Reflet | Double frappe | Regen HP/tour |")
    lines.append("|--------|----------:|------------:|-------------:|-------:|-------------:|--------------:|")
    for rid, rdata in RELICS.items():
        rar   = rdata.get("rarity", "?")
        rem   = rdata.get("emoji", "")
        effs  = rdata.get("effects", {})
        vv    = effs.get("vol_vie", 0)
        rd    = effs.get("reduction_dmg", 0)
        bd    = effs.get("bonus_dmg", 0)
        ref   = effs.get("reflet", 0)
        df    = effs.get("double_frappe", 0)
        rh    = effs.get("regen_hp", 0)
        lines.append(f"| {rem} {rar.capitalize()} | {vv:.0%} | {rd:.0%} | {bd:.0%} | {ref:.0%} | {df:.0%} | {rh:.0%} |")

    lines.append("")
    lines.append("\n!!! info \"Diminishing returns\"\n    "
                 "Posséder plusieurs reliques de même rareté donne des rendements décroissants "
                 "(-5% d'efficacité par copie supplémentaire). Des plafonds empêchent les abus.\n")

    lines.append("\n---\n")
    lines.append("\n## 📈 Stats du World Boss par tour\n")
    lines.append("Le World Boss devient de plus en plus puissant à chaque tour d'attaque personnel. "
                 "Les stats sont calculées à partir d'une zone équivalente qui augmente de ×1.3 par tour.\n")
    lines.append("")
    lines.append("| Tour | Zone équiv. | ❤️ HP | ⚔️ Atk Phy | 🔮 Atk Mag | 🛡️ Déf Phy | ⚡ Vit. |")
    lines.append("|-----:|------------:|------:|----------:|----------:|----------:|-------:|")
    for turn in [0, 1, 2, 3, 5, 7, 10, 15, 20]:
        wb = generate_world_boss(turn)
        ze = wb.get("zone", 0)
        lines.append(f"| {turn} | {_fmt_num(ze)} | {_fmt_num(wb['hp'])} | {_fmt_num(wb['p_atk'])} | {_fmt_num(wb['m_atk'])} | {_fmt_num(wb['p_def'])} | {_fmt_num(wb['speed'])} |")

    write("modes/world_boss.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : modes/pvp.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_pvp() -> None:
    content = f"""# 🥊 Taverne — PvP

La **Taverne** est l'endroit où les joueurs s'affrontent en duel.
Mesure-toi aux autres joueurs et grimpe dans le classement Élo !

---

## 📋 Informations générales

- **Coût :** {ENERGY_COST.get('pvp', 5)} ⚡ par combat
- **Sélection :** tu choisis toi-même ton adversaire
- **Déroulement :** combat tour par tour, identique aux autres modes

---

## 🏆 Deux modes de jeu

### ⚔️ Mode Classique
- Pas d'Élo — résultats sans conséquence sur le classement
- Idéal pour s'entraîner ou tester de nouvelles stratégies

### 🌟 Mode Classé
- Système Élo (coefficient K=32)
- Victoire → tu gagnes des points Élo
- Défaite → tu perds des points Élo
- **Élo de départ :** 1 000 points

---

## 🎖️ Rangs Élo

| Rang | Emoji | Points Élo |
|------|-------|-----------|
| Fer | 🔩 | < 1 000 |
| Bronze | 🥉 | 1 000 – 1 199 |
| Argent | 🥈 | 1 200 – 1 399 |
| Or | 🥇 | 1 400 – 1 599 |
| Platine | 🪙 | 1 600 – 1 799 |
| Diamant | 💎 | 1 800 – 1 999 |
| Maître | ⚜️ | 2 000 – 2 399 |
| Maître Absolu | 👑 | ≥ 2 400 |

---

## 🧠 Conseils PvP

1. **Connais les classes adverses** — chaque classe a des forces et faiblesses spécifiques
2. **Le timing des sorts est crucial** — utilise l'Ultime au bon moment
3. **Les stats d'équipement comptent** — les joueurs bien équipés ont un avantage
4. **Le Gardien du Temps** peut paralyser avec son Ultime — méfie-toi !
5. **Les classes à DoT** (Ombre Venin, Pyromancien) sont efficaces sur les longs combats

---

## 📊 Classement PvP

Le classement PvP est visible dans le canal **#classement**.
Le top 1 hebdomadaire PvP reçoit un titre spécial.
"""
    write("modes/pvp.md", content)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES objets/
# ═══════════════════════════════════════════════════════════════════════════════

def _consumables_by_prof_effect(prof_key: str, effects_filter: list[str] | None = None) -> list[tuple]:
    """Return consumables for a profession, optionally filtered by effect list."""
    result = []
    for iid, item in CONSUMABLES.items():
        if item.get("profession") != prof_key:
            continue
        if effects_filter and item.get("effect") not in effects_filter:
            continue
        result.append((iid, item))
    return result


def _consumable_table(items: list[tuple], show_level: bool = True) -> str:
    lines = []
    if show_level:
        lines.append("| Nom | Effet | Niv. requis |")
        lines.append("|-----|-------|------------:|")
    else:
        lines.append("| Nom | Effet |")
        lines.append("|-----|-------|")

    for iid, item in sorted(items, key=lambda x: x[1].get("level_req", 0)):
        name    = item.get("name", iid)
        emoji   = item.get("emoji", "")
        effect  = item.get("effect", "?")
        value   = item.get("value", 0)
        lvl_req = item.get("level_req", 1)

        # Build effect description
        eff_desc = _effect_desc(effect, item)

        if show_level:
            lines.append(f"| {emoji} **{name}** | {eff_desc} | {lvl_req} |")
        else:
            lines.append(f"| {emoji} **{name}** | {eff_desc} |")

    return "\n".join(lines)


def _effect_desc(effect: str, item: dict) -> str:
    value = item.get("value", 0)
    if effect == "heal_pct":
        return f"Soigne **+{value}%** HP max en combat"
    elif effect == "energy":
        return f"Restaure **+{value} ⚡** énergie"
    elif effect == "energy_regen":
        return f"**+{value}%** régénération d'énergie passive"
    elif effect == "energy_on_win":
        return f"**+{value} ⚡** par victoire de combat"
    elif effect == "energy_def_pct":
        bonus = item.get("combat_bonus", 0)
        return f"+{value} ⚡ · **+{bonus}%** Défense en combat"
    elif effect == "energy_speed_pct":
        bonus = item.get("combat_bonus", 0)
        return f"+{value} ⚡ · **+{bonus}%** Vitesse en combat"
    elif effect == "energy_patk_pct":
        bonus = item.get("combat_bonus", 0)
        return f"+{value} ⚡ · **+{bonus}%** Atk Physique en combat"
    elif effect == "energy_matk_pct":
        bonus = item.get("combat_bonus", 0)
        return f"+{value} ⚡ · **+{bonus}%** Atk Magique en combat"
    elif effect == "energy_all":
        regen = item.get("regen_bonus", 0)
        win   = item.get("win_bonus", 0)
        return f"+{value} ⚡ · +{regen}% regen · +{win} ⚡/victoire"
    elif effect == "p_atk_pct":
        return f"**+{value}%** Attaque Physique (1 combat)"
    elif effect == "m_atk_pct":
        return f"**+{value}%** Attaque Magique (1 combat)"
    elif effect == "def_pct":
        return f"**+{value}%** Défense Phy+Mag (1 combat)"
    elif effect == "speed_pct":
        return f"**+{value}%** Vitesse (1 combat)"
    elif effect == "crit_pct":
        return f"**+{value}%** Chance Critique (1 combat)"
    elif effect == "all_pct":
        return f"**+{value}%** toutes les stats (1 combat)"
    elif effect == "p_atk":
        return f"**+{value}** Attaque Physique (permanent combat)"
    elif effect == "m_atk":
        return f"**+{value}** Attaque Magique (permanent combat)"
    elif effect == "p_def":
        return f"**+{value}** Défense Physique (permanent combat)"
    elif effect == "m_def":
        return f"**+{value}** Défense Magique (permanent combat)"
    elif effect == "speed":
        return f"**+{value}** Vitesse (permanent combat)"
    elif effect == "crit_chance":
        return f"**+{value}%** Chance Critique (permanent combat)"
    elif effect == "p_pen":
        return f"**+{value}** Pénétration Physique (permanent combat)"
    elif effect == "m_pen":
        return f"**+{value}** Pénétration Magique (permanent combat)"
    elif effect == "hp":
        return f"**+{value}** HP (permanent combat)"
    elif effect == "all_stats":
        return f"**+{value}** toutes les stats (permanent combat)"
    elif effect in ("potion_revival", "resurrection"):
        return "Survit une fois à la mort (reste à 1 HP)"
    elif effect == "potion_no_passive":
        return "Désactive le passif de l'ennemi pour ce combat"
    elif effect == "potion_reflect":
        return "Renvoie les dégâts reçus à l'ennemi (ce combat)"
    else:
        return f"Effet : {effect}"


def gen_objets_potions() -> None:
    alch_items = _consumables_by_prof_effect("alchimiste")
    lines = [
        "# ⚗️ Potions & Élixirs\n",
        "Les potions sont créées par le métier **Alchimiste**.\n",
        "Elles se divisent en plusieurs catégories selon leur effet.\n",
        "\n---\n",
    ]

    # Group by effect type
    effect_groups = {
        "💚 Potions de Soin": ["heal_pct"],
        "⚔️ Élixirs d'Attaque": ["p_atk_pct", "m_atk_pct"],
        "🛡️ Élixirs de Défense": ["def_pct"],
        "⚡ Élixirs de Vitesse": ["speed_pct"],
        "🎯 Élixirs de Critique": ["crit_pct"],
        "✨ Élixirs Complets": ["all_pct"],
        "💊 Potions Spéciales": ["potion_revival", "potion_no_passive", "potion_reflect"],
    }

    for group_name, effects in effect_groups.items():
        group_items = [(iid, item) for iid, item in alch_items if item.get("effect") in effects]
        if not group_items:
            continue
        lines.append(f"\n## {group_name}\n")
        lines.append(_consumable_table(group_items))
        lines.append("")

    write("objets/potions.md", "\n".join(lines))


def gen_objets_nourriture() -> None:
    food_items = _consumables_by_prof_effect("boulanger")
    lines = [
        "# 🍞 Nourriture\n",
        "La nourriture est créée par le métier **Boulanger**.\n",
        "Elle restaure de l'**énergie** et peut aussi booster tes stats de combat.\n",
        "\n---\n",
    ]

    effect_groups = {
        "⚡ Pains — Énergie directe": ["energy"],
        "🔄 Infusions — Regen d'énergie": ["energy_regen"],
        "🏆 Rations de Victoire": ["energy_on_win"],
        "🍲 Soupes Fortifiantes (+Énergie +Défense)": ["energy_def_pct"],
        "🥐 Pâtisseries Légères (+Énergie +Vitesse)": ["energy_speed_pct"],
        "🥩 Repas du Guerrier (+Énergie +Atk Phys)": ["energy_patk_pct"],
        "🍰 Délices Mystiques (+Énergie +Atk Mag)": ["energy_matk_pct"],
        "🎊 Festins Légendaires (Énergie + Tout)": ["energy_all"],
    }

    for group_name, effects in effect_groups.items():
        group_items = [(iid, item) for iid, item in food_items if item.get("effect") in effects]
        if not group_items:
            continue
        lines.append(f"\n## {group_name}\n")
        lines.append(_consumable_table(group_items))
        lines.append("")

    write("objets/nourriture.md", "\n".join(lines))


def gen_objets_runes() -> None:
    rune_items = _consumables_by_prof_effect("enchanteur")
    lines = [
        "# ✨ Runes\n",
        "Les runes sont créées par le métier **Enchanteur**.\n",
        "Elles améliorent **définitivement** une stat de combat pour la durée du combat.\n",
        "\n---\n",
        "\n!!! info \"Durée\"\n    "
        "Les runes s'appliquent au début du combat et durent pour toute sa durée.\n",
        "",
    ]

    effect_groups = {
        "⚔️ Runes de Force (Atk Physique)": ["p_atk"],
        "🔮 Runes de Magie (Atk Magique)": ["m_atk"],
        "🛡️ Runes de Défense Physique": ["p_def"],
        "🔷 Runes de Défense Magique": ["m_def"],
        "⚡ Runes de Vitesse": ["speed"],
        "🎯 Runes de Critique": ["crit_chance"],
        "🗡️ Runes de Pénétration Physique": ["p_pen"],
        "💫 Runes de Pénétration Magique": ["m_pen"],
        "❤️ Runes de Vie (HP)": ["hp"],
        "🌟 Rune Divine (Toutes les stats)": ["all_stats"],
    }

    for group_name, effects in effect_groups.items():
        group_items = [(iid, item) for iid, item in rune_items if item.get("effect") in effects]
        if not group_items:
            continue
        lines.append(f"\n## {group_name}\n")
        lines.append(_consumable_table(group_items))
        lines.append("")

    write("objets/runes.md", "\n".join(lines))


def gen_objets_reliques() -> None:
    lines = [
        "# 💎 Reliques\n",
        "Les reliques du **World Boss** donnent des bonus permanents en combat.\n",
        "Plus la rareté est élevée, plus les bonus sont puissants.\n",
        "\n---\n",
        "\n## Comment obtenir des reliques\n",
        "Les reliques s'obtiennent uniquement via le **[World Boss](../modes/world_boss.md)**.\n",
        "Chaque semaine, les meilleurs joueurs reçoivent une relique de leur rang.\n",
        "",
        "\n## Effets des reliques\n",
        "Chaque relique possède les mêmes effets, mais avec des valeurs plus élevées selon la rareté.\n",
        "",
        "| Rareté | Vol de vie | Réd. dégâts | Bonus dégâts | Reflet dégâts | Double frappe | Regen HP/tour |",
        "|--------|----------:|------------:|-------------:|-------------:|-------------:|--------------:|",
    ]

    for rid, rdata in RELICS.items():
        rar  = rdata.get("rarity", "?")
        rem  = rdata.get("emoji", "")
        effs = rdata.get("effects", {})
        vv   = effs.get("vol_vie", 0)
        rd   = effs.get("reduction_dmg", 0)
        bd   = effs.get("bonus_dmg", 0)
        ref  = effs.get("reflet", 0)
        df   = effs.get("double_frappe", 0)
        rh   = effs.get("regen_hp", 0)
        lines.append(f"| {rem} {rar.capitalize()} | {vv:.0%} | {rd:.0%} | {bd:.0%} | {ref:.0%} | {df:.0%} | {rh:.0%} |")

    lines.append("")
    lines.append("\n## Plafonds des effets\n")
    lines.append("Pour éviter les abus, les effets de reliques ont des **plafonds maximaux**,\n"
                 "même si tu possèdes plusieurs reliques.\n\n")
    cap_labels = {
        "vol_vie":       "Vol de vie",
        "reduction_dmg": "Réduction dégâts",
        "bonus_dmg":     "Bonus dégâts",
        "reflet":        "Reflet",
        "double_frappe": "Double frappe",
        "regen_hp":      "Regen HP/tour",
    }
    lines.append("| Effet | Valeur maximale |")
    lines.append("|-------|----------------:|")
    for k, cap in RELIC_CAPS.items():
        lbl = cap_labels.get(k, k)
        lines.append(f"| {lbl} | {cap:.0%} |")

    lines.append("")
    lines.append("\n!!! note \"Diminishing returns\"\n    "
                 "Posséder plusieurs reliques de la même rareté donne des rendements décroissants : "
                 "−5% d'efficacité par copie supplémentaire (2ème = 95%, 3ème = 90%, etc.).\n")

    write("objets/reliques.md", "\n".join(lines))


def gen_objets_materiaux() -> None:
    lines = [
        "# 🌿 Matériaux\n",
        "Les matériaux sont récoltés par les métiers de **récolte** et utilisés "
        "pour fabriquer des équipements et des consommables.\n",
        "\n---\n",
    ]

    prof_labels = {
        "mineur":     ("⛏️", "Mineur",     "Minerais et cristaux"),
        "bucheron":   ("🪓", "Bûcheron",   "Bois de différentes essences"),
        "herboriste": ("🌿", "Herboriste", "Herbes, fleurs et champignons"),
        "chasseur":   ("🏹", "Chasseur",   "Cuirs, griffes, crocs et os"),
        "fermier":    ("🌾", "Fermier",    "Blé, épices, lait et fruits"),
    }

    for prof_key, (pe, pname, pdesc) in prof_labels.items():
        mat_ids = PROFESSION_MATERIALS.get(prof_key, [])
        if not mat_ids:
            continue

        lines.append(f"\n## {pe} {pname}\n")
        lines.append(f"*{pdesc}*\n")
        lines.append(f"Niveaux de récolte requis : 1 → 100 (un tier tous les 10 niveaux)\n")
        lines.append("")
        lines.append("| Tier | Matériau | Emoji | Niv. récolte |")
        lines.append("|-----:|----------|-------|-------------:|")
        for mid in mat_ids:
            mat  = MATERIALS.get(mid, {})
            name = mat.get("name", mid)
            em   = mat.get("emoji", "")
            tier = mat.get("tier", 1)
            niv  = (tier - 1) * 10 + 1
            lines.append(f"| {tier} | {name} | {em} | {niv} |")

    write("objets/materiaux.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : titres.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_titres() -> None:
    lines = [
        "# 🎖️ Titres\n",
        f"Il y a **{len(TITLES)} titres** répartis en **{len(TITLE_CATEGORIES)} catégories**.\n",
        "Les titres avec un bonus actif appliquent leur effet en **permanence** une fois débloqués.\n",
        "\n---\n",
    ]

    def bonus_label(bt: str | None, bv: float) -> str:
        if not bt:
            return "✨ *Cosmétique*"
        labels = {
            "xp_pct":             f"**+{bv}% XP**",
            "gold_pct":           f"**+{bv}% Gold**",
            "prestige_pct":       f"**+{bv}% Prestige**",
            "monde_loot_pct":     f"**+{bv}% loot monde**",
            "djc_stats_pct":      f"**+{bv}% stats donjon classique**",
            "dje_stats_pct":      f"**+{bv}% stats donjon élite**",
            "dja_stats_pct":      f"**+{bv}% stats donjon abyssal**",
            "raid_stats_pct":     f"**+{bv}% stats raid**",
            "wb_stats_pct":       f"**+{bv}% stats World Boss**",
            "harvest_xp_pct":     f"**+{bv}% XP récolte**",
            "craft_xp_pct":       f"**+{bv}% XP artisanat**",
            "conception_xp_pct":  f"**+{bv}% XP conception**",
            "hdv_discount_pct":   f"**−{bv}% commission HDV**",
        }
        return labels.get(bt, f"+{bv} ({bt})")

    for cat_key, cat_label in TITLE_CATEGORIES.items():
        cat_titles = [(tid, t) for tid, t in TITLES.items() if t.get("cat") == cat_key]
        if not cat_titles:
            continue

        lines.append(f"\n## {cat_label}\n")
        lines.append("| Titre | Condition | Bonus | Gold |")
        lines.append("|-------|-----------|-------|------:|")

        for tid, t in cat_titles:
            name  = t.get("name", tid)
            req   = t.get("req", 0)
            rt    = t.get("req_type", "?")
            bt    = t.get("bonus_type")
            bv    = t.get("bonus_value", 0)
            gold  = t.get("reward_gold", 0)
            lines.append(f"| **{name}** | {_req_type_label(rt)} : {_fmt_req(req)} | {bonus_label(bt, bv)} | {_fmt_num(gold)} |")

    write("titres.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : quetes.md
# ═══════════════════════════════════════════════════════════════════════════════
def gen_quetes() -> None:
    lines = [
        "# 📜 Quêtes\n",
        f"Il y a **{len(MAIN_QUESTS)} quêtes principales** et **{len(SECONDARY_QUESTS)} quêtes secondaires**.\n",
        "Les quêtes donnent de grosses récompenses en **XP** et **Gold**.\n",
        "\n---\n",
        "\n## 📖 Quêtes Principales\n",
        "Progression linéaire — chaque quête doit être complétée avant la suivante.\n\n",
        "| # | Quête | Objectif | XP | Gold |",
        "|--:|-------|----------|---:|------:|",
    ]

    for i, q in enumerate(MAIN_QUESTS, 1):
        name  = q.get("name", "?")
        emoji = q.get("emoji", "")
        desc  = q.get("desc", q.get("description", "")).replace("**", "")
        xp    = q.get("xp", q.get("xp_reward", 0))
        gold  = q.get("gold", q.get("gold_reward", 0))
        lines.append(f"| {i} | {emoji} **{name}** | {desc} | {_fmt_num(xp)} | {_fmt_num(gold)} |")

    lines.append("\n\n---\n")
    lines.append("\n## 📋 Quêtes Secondaires\n")
    lines.append("Indépendantes — peuvent être faites dans n'importe quel ordre.\n\n")
    lines.append("| # | Quête | Objectif | XP | Gold |")
    lines.append("|--:|-------|----------|---:|------:|")

    for i, q in enumerate(SECONDARY_QUESTS, 1):
        name  = q.get("name", "?")
        emoji = q.get("emoji", "")
        desc  = q.get("desc", q.get("description", "")).replace("**", "")
        xp    = q.get("xp", q.get("xp_reward", 0))
        gold  = q.get("gold", q.get("gold_reward", 0))
        lines.append(f"| {i} | {emoji} **{name}** | {desc} | {_fmt_num(xp)} | {_fmt_num(gold)} |")

    write("quetes.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating wiki pages...")

    gen_index()
    gen_debutant()

    print("  Classes...")
    gen_classes()

    print("  Combat...")
    gen_combat_mecanique()
    gen_combat_ennemis()

    print("  Equipements...")
    gen_equipements()

    print("  Metiers...")
    gen_metiers()

    print("  Modes de jeu...")
    gen_modes_index()
    gen_monde()
    gen_donjons()
    gen_raids()
    gen_world_boss()
    gen_pvp()

    print("  Objets...")
    gen_objets_potions()
    gen_objets_nourriture()
    gen_objets_runes()
    gen_objets_reliques()
    gen_objets_materiaux()

    print("  Titres & Quetes...")
    gen_titres()
    gen_quetes()

    # Count all generated files
    total = len(list(DOCS.rglob("*.md")))
    print(f"\nDone! {total} pages total in {DOCS}")
