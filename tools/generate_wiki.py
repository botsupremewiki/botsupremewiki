"""
Wiki Generator — Bot Ultime RPG
Reads directly from game data and generates MkDocs markdown pages under docs/.

Usage (from project root):
    python tools/generate_wiki.py
"""
from __future__ import annotations
import sys
import types
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
_models = _load_file("bot.cogs.rpg.models", RPG / "models.py")
_items  = _load_file("bot.cogs.rpg.items",  RPG / "items.py")
_quests = _load_file("bot.cogs.rpg.quests", RPG / "quests.py")

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
WB_RANK_REWARDS        = _models.WB_RANK_REWARDS
RARITIES               = _models.RARITIES
CLASS_SPELLS           = _models.CLASS_SPELLS
compute_class_stats    = _models.compute_class_stats

CONSUMABLES            = _items.CONSUMABLES
CONCEPTION_RECIPES     = _items.CONCEPTION_RECIPES

MAIN_QUESTS            = _quests.MAIN_QUESTS
SECONDARY_QUESTS       = _quests.SECONDARY_QUESTS


# ─── Helpers ────────────────────────────────────────────────────────────────
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
        "level":          "Niveau joueur",
        "prestige":       "Niveau de prestige",
        "zone":           "Zone atteinte",
        "dungeon_clears": "Donjons classiques",
        "elite_clears":   "Donjons élites",
        "abyssal_clears": "Donjons abyssaux",
        "raid_clears":    "Raids complétés",
        "wb_total_damage":"Dégâts WB totaux",
        "wb_attacks":     "Attaques WB",
        "wb_rank1":       "Top 1 WB hebdo",
        "harvest_level":  "Niveau récolte",
        "craft_level":    "Niveau artisanat",
        "conception_level":"Niveau conception",
        "market_sales":   "Ventes HDV",
        "pvp_wins":       "Victoires PvP",
        "pvp_elo":        "Élo PvP",
        "total_gold":     "Gold accumulé",
        "global_rank1":   "Top 1 classement général hebdo",
        "pvp_rank1":      "Top 1 PvP hebdo",
    }
    return labels.get(rt, rt)


def write(filename: str, content: str) -> None:
    path = DOCS / filename
    path.write_text(content, encoding="utf-8")
    print(f"  OK {filename}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : index.md
# ═══════════════════════════════════════════════════════════════════════════
def gen_index() -> None:
    n_classes = len(ALL_CLASSES)
    n_titles  = len(TITLES)
    n_items   = len(CONSUMABLES)
    n_recipes = len(CONCEPTION_RECIPES)
    n_quests  = len(MAIN_QUESTS) + len(SECONDARY_QUESTS)

    content = f"""# Bienvenue sur le Wiki RPG

> **Bot Ultime RPG** est un jeu de rôle complet jouable directement sur Discord.
> Progresse à travers des zones, affronte des boss, explore des donjons et défie d'autres joueurs !

---

## 📊 Chiffres clés

| Catégorie       | Total |
|-----------------|------:|
| Classes         | {n_classes} |
| Titres          | {n_titles} |
| Consommables    | {n_items} |
| Recettes        | {n_recipes} |
| Quêtes          | {n_quests} |
| Raretés         | {len(RARITIES)} |
| Zones max       | 10 000 |
| Niveau max      | 1 000 |

---

## 🗺️ Navigation rapide

- **[Guide Débutant](guide_debutant.md)** — Par où commencer
- **[Classes](classes.md)** — Les {n_classes} classes disponibles et leurs sorts
- **[Modes de Jeu](modes_de_jeu.md)** — Monde, Donjons, Raids, PvP, World Boss
- **[Objets](objets.md)** — Potions, Élixirs, Pains, Runes
- **[Métiers](metiers.md)** — Récolte, Artisanat, Conception
- **[Quêtes](quetes.md)** — Toutes les quêtes principales et secondaires
- **[Titres](titres.md)** — Titres disponibles et leurs bonus

---

!!! info "Wiki généré automatiquement"
    Ce wiki est généré directement depuis le code du jeu et reste toujours à jour.
"""
    write("index.md", content)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : guide_debutant.md
# ═══════════════════════════════════════════════════════════════════════════
def gen_guide_debutant() -> None:
    cost_monde = ENERGY_COST.get("ennemi", 1)
    cost_boss  = ENERGY_COST.get("boss_classique", 2)
    cost_djc   = ENERGY_COST.get("donjon_classique", 3)
    regen_int  = PASSIVE_REGEN_INTERVAL // 60

    content = f"""# Guide Débutant

## 1. Choisir sa classe

Rends-toi dans le canal **#classe** et sélectionne ta classe.
Il existe {len(CLASSES_STANDARD)} classes standard (gratuites) et {len(CLASSES_PREMIUM)} classes premium.
⚠️ Ce choix est **définitif** — réfléchis bien !

Consulte la page [Classes](classes.md) pour comparer les statistiques et les sorts.

---

## 2. L'Énergie ⚡

L'énergie est la ressource principale du jeu. Chaque action en consomme.

| Type d'action        | Coût |
|----------------------|-----:|
| Combattre un ennemi  | {cost_monde} |
| Boss classique       | {cost_boss} |
| Donjon classique     | {cost_djc} |
| Voir les autres coûts | [Modes de Jeu](modes_de_jeu.md) |

- **Maximum :** {_fmt_num(MAX_ENERGY)} énergie
- **Régénération passive :** +{PASSIVE_REGEN_ENERGY} énergie toutes les {regen_int} minutes
- **Régénération HP passive :** +{PASSIVE_REGEN_HP_PCT}% HP max toutes les {regen_int} minutes

---

## 3. Progresser dans le Monde

Dans le canal **#monde**, tu peux :

- **Attaquer** un ennemi de ta zone actuelle
- **Avancer** si tu bats le boss de la zone
- Utiliser le **mode auto** pour farmer automatiquement

Les zones vont jusqu'à **10 000**. Ton niveau détermine les zones accessibles
*(règle approximative : zone ≈ niveau × 9)*.

---

## 4. L'XP et les Niveaux

- L'XP nécessaire par niveau = **1 000 × niveau actuel**
  (ex : passer du niveau 5 au 6 demande 5 000 XP)
- Niveau maximum : **1 000**
- Après le niveau 1 000 : accès au **Prestige**

---

## 5. Les Métiers

Rejoins jusqu'à **3 métiers** (1 récolte, 1 artisanat, 1 conception).
Voir la page [Métiers](metiers.md) pour tous les détails.

---

## 6. Les Quêtes

Les quêtes donnent de grosses récompenses (XP + Gold).
Il y a {len(MAIN_QUESTS)} quêtes principales et {len(SECONDARY_QUESTS)} quêtes secondaires.
Voir la page [Quêtes](quetes.md).

---

## 7. Les Titres

Les titres donnent des bonus permanents (XP, Gold, Stats, etc.).
Commence par les titres de **zone** et de **niveau** pour booster ta progression.
Voir la page [Titres](titres.md).
"""
    write("guide_debutant.md", content)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : classes.md
# ═══════════════════════════════════════════════════════════════════════════
def gen_classes() -> None:
    lines = ["# Classes\n"]
    lines.append(f"> Il existe **{len(CLASSES_STANDARD)} classes standard** et **{len(CLASSES_PREMIUM)} classes premium**.\n")
    lines.append("Le choix de classe est **définitif**.\n")

    # Stats columns
    stat_keys = ["hp", "p_atk", "m_atk", "p_def", "m_def", "speed", "crit_chance", "crit_damage"]
    stat_labels = {
        "hp": "HP", "p_atk": "P.Atk", "m_atk": "M.Atk",
        "p_def": "P.Déf", "m_def": "M.Déf", "speed": "Vit.",
        "crit_chance": "Crit%", "crit_damage": "CritDmg%",
    }

    # Table niveau 1
    lines.append("\n## Stats de base (Niveau 1, Prestige 0)\n")
    header = "| Classe | " + " | ".join(stat_labels[k] for k in stat_keys) + " |"
    sep    = "|--------|" + "|".join(["------:"] * len(stat_keys)) + "|"
    lines.append(header)
    lines.append(sep)
    for cls in ALL_CLASSES:
        emoji = CLASS_EMOJI.get(cls, "")
        base  = BASE_STATS.get(cls, {})
        vals  = []
        for k in stat_keys:
            v = base.get(k, 0)
            if k in ("crit_chance", "crit_damage"):
                vals.append(f"{v:.0f}%")
            else:
                vals.append(str(int(v)) if v else "—")
        premium_tag = " *(P)*" if cls in CLASSES_PREMIUM else ""
        lines.append(f"| {emoji} **{cls}**{premium_tag} | " + " | ".join(vals) + " |")

    lines.append("\n*(P) = Classe Premium*\n")

    # Stats niveau 1000
    lines.append("\n## Stats cibles (Niveau 1000, Prestige 0, sans équipement)\n")
    lines.append(header)
    lines.append(sep)
    for cls in ALL_CLASSES:
        emoji = CLASS_EMOJI.get(cls, "")
        stats = compute_class_stats(cls, 1000, 0)
        vals  = []
        for k in stat_keys:
            v = stats.get(k, 0)
            if k in ("crit_chance", "crit_damage"):
                vals.append(f"{v:.0f}%")
            else:
                vals.append(_fmt_num(v) if v else "—")
        premium_tag = " *(P)*" if cls in CLASSES_PREMIUM else ""
        lines.append(f"| {emoji} **{cls}**{premium_tag} | " + " | ".join(vals) + " |")

    # Descriptions + Sorts
    lines.append("\n---\n\n## Détail des classes\n")
    for cls in ALL_CLASSES:
        emoji = CLASS_EMOJI.get(cls, "")
        desc  = CLASS_DESCRIPTION.get(cls, "")
        cls_key = cls.lower().replace(" ", "_").replace("é", "e").replace("è", "e")
        # Normalize key for CLASS_SPELLS
        spell_key = {
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
        }.get(cls, cls.lower())

        lines.append(f"### {emoji} {cls}\n")
        lines.append(desc.replace("\\n", "\n") + "\n")

        spells_data = CLASS_SPELLS.get(spell_key, {})
        if spells_data:
            resource = spells_data.get("resource", "?").capitalize()
            r_max    = spells_data.get("resource_max", 0)
            r_turn   = spells_data.get("resource_per_turn", 0)
            r_hit    = spells_data.get("resource_on_hit", 0)
            lines.append(f"\n**Ressource :** {resource} (max {r_max}")
            if r_turn:
                lines.append(f", +{r_turn}/tour")
            if r_hit:
                lines.append(f", +{r_hit} par coup reçu")
            lines.append(")\n")

            lines.append("\n**Sorts :**\n\n")
            for skey in ("s1", "s2", "ultimate"):
                s = spells_data.get(skey)
                if not s:
                    continue
                tag = " *(Ultimate)*" if s.get("is_ultimate") else ""
                cost_label = f"Coût : {s['cost']} {resource}"
                cd = s.get("cooldown", 0)
                cd_label = f" · CD : {cd} tours" if cd else ""
                lines.append(f"- **{s['emoji']} {s['name']}**{tag} — {s['description']}  \n")
                lines.append(f"  *{cost_label}{cd_label}*\n\n")

        lines.append("\n---\n")

    write("classes.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : modes_de_jeu.md
# ═══════════════════════════════════════════════════════════════════════════
def gen_modes_de_jeu() -> None:
    content = f"""# Modes de Jeu

## Coûts en Énergie

| Mode de jeu             | Coût ⚡ |
|-------------------------|--------:|
| Ennemi normal           | {ENERGY_COST.get('ennemi', '?')} |
| Boss classique          | {ENERGY_COST.get('boss_classique', '?')} |
| Boss runique            | {ENERGY_COST.get('boss_runique', '?')} |
| Boss emblématique       | {ENERGY_COST.get('boss_emblematique', '?')} |
| Boss antique            | {ENERGY_COST.get('boss_antique', '?')} |
| Donjon classique        | {ENERGY_COST.get('donjon_classique', '?')} |
| Donjon élite            | {ENERGY_COST.get('donjon_elite', '?')} |
| Donjon abyssal          | {ENERGY_COST.get('donjon_abyssal', '?')} |
| Raid                    | {ENERGY_COST.get('raid', '?')} |
| World Boss              | {ENERGY_COST.get('world_boss', '?')} |
| PvP                     | {ENERGY_COST.get('pvp', '?')} |

**Maximum d'énergie :** {_fmt_num(MAX_ENERGY)} ⚡
**Régénération passive :** +{PASSIVE_REGEN_ENERGY} toutes les {PASSIVE_REGEN_INTERVAL // 60} min

---

## ⚔️ Monde

Le mode principal. Tu progresses de zone en zone en battant des ennemis et des boss.

- **Ennemis** : 1⚡ par combat
- **Stages par zone** : 1-2-3-4-Boss
- **Avancement** : battre le boss pour passer à la zone suivante
- **Mode auto** : boucle automatique de 3 secondes
- **Zones** : 1 → 10 000

**Types de boss :**

| Type | Multiplicateur XP/Gold |
|------|----------------------:|
| Boss classique | ×3 |
| Boss emblématique | ×10 |
| Boss antique | ×30 |

---

## 🏰 Donjons

Les donjons sont des défis à difficulté croissante avec de meilleures récompenses d'équipement.

| Type | Énergie | Source mult équipements |
|------|--------:|------------------------|
| Classique | {ENERGY_COST.get('donjon_classique', '?')}⚡ | ×1.2 |
| Élite | {ENERGY_COST.get('donjon_elite', '?')}⚡ | ×1.4 |
| Abyssal | {ENERGY_COST.get('donjon_abyssal', '?')}⚡ | ×1.6 |

Les niveaux de donjon augmentent la puissance des équipements obtenus.

---

## 👥 Raids

Les raids donnent les équipements les plus puissants du jeu (×1.8 mult).

- **Coût :** {ENERGY_COST.get('raid', '?')}⚡ par raid
- **Niveaux :** 1 → 10
- **Équipement :** Source "raid" (multiplicateur ×1.8)

---

## 🐉 World Boss

Un boss partagé par tous les joueurs, réinitialisé chaque semaine.

- **Coût :** {ENERGY_COST.get('world_boss', '?')}⚡ par attaque
- **Classement :** par dégâts totaux infligés dans la semaine
- **Récompenses** (distribuées le lundi à minuit UTC) :

| Rang | Relique | Gold |
|-----:|---------|------:|
| 🥇 #1 | Prismatique 🌈 | {_fmt_num(50_000)} |
| 🥈 #2 | Transcendant 🩵 | {_fmt_num(30_000)} |
| 🥉 #3 | Divin 🟡 | {_fmt_num(20_000)} |
| #4 | Artefact 🔶 | {_fmt_num(12_000)} |
| #5 | Mythique 🟥 | {_fmt_num(8_000)} |
| #6 | Légendaire 🟧 | {_fmt_num(5_000)} |
| #7 | Épique 🟪 | {_fmt_num(3_000)} |
| #8 | Rare 🟦 | {_fmt_num(2_000)} |
| #9-10 | Peu commun 🟩 | {_fmt_num(1_000)} / {_fmt_num(500)} |
| #11+ | Commun ⬜ | {_fmt_num(200)} |

---

## 🥊 PvP

Affronte d'autres joueurs en duel.

- **Coût :** {ENERGY_COST.get('pvp', '?')}⚡ par combat
- **Mode classique :** pas d'Élo, pour pratiquer
- **Mode classé :** système Élo (K=32), rang visible dans le classement
- **Élo de départ :** 1 000

| Rang Élo | Fourchette |
|----------|-----------|
| Fer 🔩 | < 1 000 |
| Bronze 🥉 | 1 000 – 1 199 |
| Argent 🥈 | 1 200 – 1 399 |
| Or 🥇 | 1 400 – 1 599 |
| Platine 🪙 | 1 600 – 1 799 |
| Diamant 💎 | 1 800 – 1 999 |
| Maître ⚜️ | 2 000 – 2 399 |
| Maître Absolu 👑 | ≥ 2 400 |

---

## 🌟 Prestige

Disponible au niveau 1 000. Le prestige réinitialise le niveau en échange d'un bonus permanent de **+0,1% aux stats** par niveau de prestige.

- Niveau de prestige maximum : **1 000**
- Bonus max (prestige 1000) : **+100% aux stats de classe**

---

## 📦 Équipements

Les équipements ont 7 emplacements :

| Slot | Emoji |
|------|-------|
| Casque | ⛑️ |
| Plastron | 🦺 |
| Pantalon | 👖 |
| Chaussures | 👟 |
| Arme | ⚔️ |
| Amulette | 📿 |
| Anneau | 💍 |

**Raretés** (du plus faible au plus puissant) :

| Rareté | Multiplicateur |
|--------|---------------:|
| Commun ⬜ | ×1.0 |
| Peu commun 🟩 | ×1.2 |
| Rare 🟦 | ×1.4 |
| Épique 🟪 | ×1.6 |
| Légendaire 🟧 | ×1.8 |
| Mythique 🟥 | ×2.0 |
| Artefact 🔶 | ×2.2 |
| Divin 🟡 | ×2.4 |
| Transcendant 🩵 | ×2.6 |
| Prismatique 🌈 | ×3.0 |
"""
    write("modes_de_jeu.md", content)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : objets.md
# ═══════════════════════════════════════════════════════════════════════════
def gen_objets() -> None:
    lines = ["# Objets Consommables\n"]
    lines.append("Tous les consommables sont fabriqués par les métiers de **conception**.\n")

    # Group by profession then by effect/type
    by_prof: dict[str, list] = {}
    for iid, item in CONSUMABLES.items():
        prof = item.get("profession", "?")
        by_prof.setdefault(prof, []).append((iid, item))

    prof_labels = {
        "alchimiste": "⚗️ Alchimiste",
        "boulanger":  "🍞 Boulanger",
        "enchanteur": "✨ Enchanteur",
    }

    effect_label = {
        "heal_pct":          ("💚 Potion de Soin",    "Soigne % HP max en combat"),
        "energy":            ("⚡ Énergie",            "Restaure de l'énergie"),
        "p_atk_pct":         ("⚔️ Force",              "+% Attaque Physique (1 combat)"),
        "m_atk_pct":         ("🔮 Magie",              "+% Attaque Magique (1 combat)"),
        "def_pct":           ("🛡️ Défense",            "+% Défense Phy+Mag (1 combat)"),
        "speed_pct":         ("⚡ Vitesse",            "+% Vitesse (1 combat)"),
        "crit_pct":          ("🎯 Critique",           "+% Chance Critique (1 combat)"),
        "all_pct":           ("✨ Tout",               "+% Toutes les stats (1 combat)"),
        "p_atk":             ("⚔️ Attaque Phys.",     "+Attaque Physique flat"),
        "m_atk":             ("🔮 Attaque Mag.",      "+Attaque Magique flat"),
        "p_def":             ("🛡️ Déf. Phys.",        "+Défense Physique flat"),
        "m_def":             ("🔷 Déf. Mag.",         "+Défense Magique flat"),
        "speed":             ("⚡ Vitesse",            "+Vitesse flat"),
        "crit_chance":       ("🎯 Critique",           "+Chance Critique flat"),
        "p_pen":             ("🗡️ Pén. Phys.",        "+Pénétration Physique"),
        "m_pen":             ("💫 Pén. Mag.",          "+Pénétration Magique"),
        "hp":                ("❤️ HP",                "+HP flat"),
        "all_stats":         ("✨ Toutes stats",       "+Toutes les stats flat"),
        "energy_regen":      ("🔄 Regen Énergie",     "+% Regen énergie passive"),
        "energy_on_win":     ("🏆 Énergie/Victoire",  "+Énergie par victoire"),
        "energy_def_pct":    ("🍲 Soupe Fortifiante", "+Énergie + Défense%"),
        "energy_speed_pct":  ("🥐 Pâtisserie",        "+Énergie + Vitesse%"),
        "energy_patk_pct":   ("🥩 Repas Guerrier",    "+Énergie + Atk Phys%"),
        "energy_matk_pct":   ("🍰 Délice Mystique",   "+Énergie + Atk Mag%"),
        "energy_all":        ("🎊 Festin",             "+Énergie + Regen + Victoire"),
        "potion_revival":    ("💊 Résurrection",       "Survit 1 fois à la mort (1 HP)"),
        "potion_no_passive": ("🚫 Suppression Passif","Désactive le passif ennemi"),
        "potion_reflect":    ("🪞 Réflexion",          "Renvoie les dégâts"),
    }

    for prof_key in ["alchimiste", "boulanger", "enchanteur"]:
        items = by_prof.get(prof_key, [])
        if not items:
            continue
        label = prof_labels.get(prof_key, prof_key)
        lines.append(f"\n## {label}\n")

        # Group by effect type
        by_effect: dict[str, list] = {}
        for iid, item in items:
            eff = item.get("effect", "?")
            by_effect.setdefault(eff, []).append((iid, item))

        for eff, eff_items in by_effect.items():
            eff_name, eff_desc = effect_label.get(eff, (eff, ""))
            lines.append(f"\n### {eff_name}\n")
            if eff_desc:
                lines.append(f"*{eff_desc}*\n\n")

            lines.append("| Nom | Valeur | Emoji |")
            lines.append("|-----|-------:|-------|")
            for iid, item in eff_items:
                name  = item.get("name", iid)
                val   = item.get("value", "")
                emoji = item.get("emoji", "")
                unit  = "%" if eff.endswith("_pct") or eff in ("heal_pct", "crit_chance") else ""
                if eff == "energy_all":
                    regen = item.get("regen_bonus", 0)
                    win   = item.get("win_bonus", 0)
                    val_str = f"+{val} ⚡ · +{regen}% regen · +{win}/victoire"
                elif eff in ("energy_def_pct", "energy_speed_pct", "energy_patk_pct", "energy_matk_pct"):
                    bonus = item.get("combat_bonus", 0)
                    val_str = f"+{val} ⚡ · +{bonus}%"
                elif isinstance(val, (int, float)) and val:
                    val_str = f"+{val}{unit}"
                else:
                    val_str = str(val)
                lines.append(f"| {emoji} {name} | {val_str} | {emoji} |")

    # Special potions section
    special_items = [(iid, item) for iid, item in CONSUMABLES.items()
                     if item.get("type") in ("special_potion", "potion_speciale")
                     or item.get("effect") in ("potion_revival", "potion_no_passive", "potion_reflect")]
    if special_items:
        lines.append("\n## 💊 Potions Spéciales\n")
        lines.append("| Nom | Effet | Emoji |")
        lines.append("|-----|-------|-------|")
        for iid, item in special_items:
            name  = item.get("name", iid)
            eff   = item.get("effect", "?")
            emoji = item.get("emoji", "")
            _, desc = effect_label.get(eff, (eff, eff))
            lines.append(f"| {emoji} {name} | {desc} | {emoji} |")

    write("objets.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : metiers.md
# ═══════════════════════════════════════════════════════════════════════════
def gen_metiers() -> None:
    # Group recipes by profession
    by_prof: dict[str, list] = {}
    for rid, rec in CONCEPTION_RECIPES.items():
        prof = rec.get("profession", "?")
        by_prof.setdefault(prof, []).append((rid, rec))

    prof_labels = {
        "alchimiste": ("⚗️", "Alchimiste"),
        "boulanger":  ("🍞", "Boulanger"),
        "enchanteur": ("✨", "Enchanteur"),
    }

    content = """# Métiers

Le système de métiers se divise en **3 branches** indépendantes :

| Branche | Description |
|---------|-------------|
| 🌾 Récolte | Collecter des matériaux dans le monde |
| 🔨 Artisanat | Fabriquer des équipements |
| ⚗️ Conception | Créer des consommables (potions, runes, nourriture) |

Chaque branche possède son propre niveau (1 → 100).

---

## 🌾 Récolte

La récolte s'effectue dans le canal **#métiers**. Chaque classe de métier de récolte
débloque des matériaux spécifiques selon son niveau.

**Professions de récolte :**

| Profession | Matériaux principaux |
|------------|---------------------|
| 🌿 Herboriste | Herbes, fleurs, plantes |
| ⛏️ Mineur | Minerais, cristaux, pierres |
| 🏹 Chasseur | Cuirs, griffes, crocs, os |
| 🌾 Fermier | Blé, orge, maïs, épices |

---

## 🔨 Artisanat

L'artisanat permet de fabriquer des **équipements** (panoplies) à partir de matériaux récoltés.

- La rareté des items craftés dépend du **niveau d'artisanat**
- Meilleur niveau = accès aux raretés supérieures
- Multiplicateur de puissance : ×1.0 → ×2.0 selon le niveau

---

## ⚗️ Conception

La conception produit des **consommables** (potions, runes, nourriture).
Voir aussi la page [Objets](objets.md) pour les effets.

"""
    for prof_key in ["alchimiste", "boulanger", "enchanteur"]:
        recipes = by_prof.get(prof_key, [])
        if not recipes:
            continue
        emoji, pname = prof_labels.get(prof_key, ("", prof_key))
        content += f"### {emoji} {pname}\n\n"
        content += f"**{len(recipes)} recettes** disponibles.\n\n"

        # Sort by level_req
        recipes_sorted = sorted(recipes, key=lambda x: x[1].get("level_req", 0))

        content += "| Niveau | Résultat | Qté | Ingrédients |\n"
        content += "|-------:|----------|----:|-------------|\n"
        for rid, rec in recipes_sorted:
            result_id = rec.get("result", "?")
            result_item = CONSUMABLES.get(result_id, {})
            result_name = result_item.get("name", result_id)
            result_emoji = result_item.get("emoji", "")
            qty     = rec.get("qty", 1)
            lvl     = rec.get("level_req", 1)
            ingrs   = rec.get("ingredients", {})
            ingr_str = ", ".join(f"{v}× {k.replace('mat_', '').replace('_', ' ')}" for k, v in ingrs.items())
            content += f"| {lvl} | {result_emoji} {result_name} | ×{qty} | {ingr_str} |\n"
        content += "\n"

    write("metiers.md", content)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : quetes.md
# ═══════════════════════════════════════════════════════════════════════════
def gen_quetes() -> None:
    lines = ["# Quêtes\n"]
    lines.append(f"Il y a **{len(MAIN_QUESTS)} quêtes principales** et **{len(SECONDARY_QUESTS)} quêtes secondaires**.\n")

    lines.append("\n## 📜 Quêtes Principales\n")
    lines.append("Progression linéaire obligatoire.\n\n")
    lines.append("| # | Quête | Objectif | XP | Gold |")
    lines.append("|--:|-------|----------|---:|------:|")
    for i, q in enumerate(MAIN_QUESTS, 1):
        name  = q.get("name", "?")
        emoji = q.get("emoji", "")
        desc  = q.get("desc", q.get("description", ""))
        xp    = q.get("xp", q.get("xp_reward", 0))
        gold  = q.get("gold", q.get("gold_reward", 0))
        # Strip markdown bold from desc for table readability
        desc  = desc.replace("**", "")
        lines.append(f"| {i} | {emoji} **{name}** | {desc} | {_fmt_num(xp)} | {_fmt_num(gold)} |")

    lines.append("\n\n## 📋 Quêtes Secondaires\n")
    lines.append("Indépendantes, peuvent être faites dans n'importe quel ordre.\n\n")
    lines.append("| # | Quête | Objectif | XP | Gold |")
    lines.append("|--:|-------|----------|---:|------:|")
    for i, q in enumerate(SECONDARY_QUESTS, 1):
        name  = q.get("name", "?")
        emoji = q.get("emoji", "")
        desc  = q.get("desc", q.get("description", ""))
        xp    = q.get("xp", q.get("xp_reward", 0))
        gold  = q.get("gold", q.get("gold_reward", 0))
        desc  = desc.replace("**", "")
        lines.append(f"| {i} | {emoji} **{name}** | {desc} | {_fmt_num(xp)} | {_fmt_num(gold)} |")

    write("quetes.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : titres.md
# ═══════════════════════════════════════════════════════════════════════════
def gen_titres() -> None:
    lines = ["# Titres\n"]
    lines.append(f"Il y a **{len(TITLES)} titres** au total, regroupés en {len(TITLE_CATEGORIES)} catégories.\n")
    lines.append("Les titres avec un bonus actif appliquent leur effet en permanence une fois débloqués.\n")

    def bonus_label(bt: str | None, bv: float) -> str:
        if not bt:
            return "*(cosmétique)*"
        labels = {
            "xp_pct":              f"+{bv}% XP",
            "gold_pct":            f"+{bv}% Gold",
            "prestige_pct":        f"+{bv}% Prestige",
            "monde_loot_pct":      f"+{bv}% loot monde",
            "djc_stats_pct":       f"+{bv}% stats donjon classique",
            "dje_stats_pct":       f"+{bv}% stats donjon élite",
            "dja_stats_pct":       f"+{bv}% stats donjon abyssal",
            "raid_stats_pct":      f"+{bv}% stats raid",
            "wb_stats_pct":        f"+{bv}% stats WB",
            "harvest_xp_pct":      f"+{bv}% XP récolte",
            "craft_xp_pct":        f"+{bv}% XP artisanat",
            "conception_xp_pct":   f"+{bv}% XP conception",
            "hdv_discount_pct":    f"-{bv}% commission HDV",
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
            req_label = _req_type_label(rt)
            req_str   = _fmt_req(req)
            bonus_str = bonus_label(bt, bv)
            lines.append(f"| **{name}** | {req_label} : {req_str} | {bonus_str} | {_fmt_num(gold)} |")

    write("titres.md", "\n".join(lines))


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating wiki pages...")
    gen_index()
    gen_guide_debutant()
    gen_classes()
    gen_modes_de_jeu()
    gen_objets()
    gen_metiers()
    gen_quetes()
    gen_titres()
    print(f"\nDone! {len(list(DOCS.glob('*.md')))} pages in {DOCS}")
