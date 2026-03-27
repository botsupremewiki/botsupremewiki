"""
Quêtes du RPG — Mode Histoire Linéaire.

Deux chaînes indépendantes, une quête active à la fois dans chaque chaîne :
  - MAIN_QUESTS       : progression solo (zones, niveaux, donjons, prestige)
  - SECONDARY_QUESTS  : activités variées (métiers, commerce, raids, PvP)

Chaque quête :  id, name, emoji, desc, progress_key, threshold
  + optionnel : special {"type": ..., "value": ...}  pour les récompenses passives

Déblocages cohérents :
  - Donjon classique : level ≥ 4
  - Donjon élite     : level ≥ 337
  - Donjon abyssal   : level ≥ 667
  - Raid n           : level ≥ n × 100
  - prestige_level   : niveau auquel le joueur a effectué son prestige (max atteint avant reset)
"""
from __future__ import annotations

# ─── Quêtes Principales (100) ────────────────────────────────────────────────

MAIN_QUESTS: list[dict] = [
    # ── Phase 1 — Découverte (q01-q20) ───────────────────────────────────────
    # Zones 5-750 · Niveaux 5-100 · Classiques 1-30
    {
        "id": "q01", "name": "L'Aventure Commence", "emoji": "🌱",
        "desc": "Atteins la **zone 5** dans le monde.",
        "progress_key": "zone", "threshold": 5,
    },
    {
        "id": "q02", "name": "Premiers Pas", "emoji": "👣",
        "desc": "Atteins la **zone 20**.",
        "progress_key": "zone", "threshold": 20,
    },
    {
        "id": "q03", "name": "Baptême du Feu", "emoji": "🔥",
        "desc": "Atteins le **niveau 5**.",
        "progress_key": "level", "threshold": 5,
    },
    {
        "id": "q04", "name": "Exploration Initiale", "emoji": "🗺️",
        "desc": "Atteins la **zone 50**.",
        "progress_key": "zone", "threshold": 50,
    },
    {
        "id": "q05", "name": "Premier Palier", "emoji": "📈",
        "desc": "Atteins le **niveau 10**.",
        "progress_key": "level", "threshold": 10,
    },
    {
        "id": "q06", "name": "Centième Zone", "emoji": "💯",
        "desc": "Atteins la **zone 100**.",
        "progress_key": "zone", "threshold": 100,
    },
    {
        "id": "q07", "name": "Premier Donjon", "emoji": "🏰",
        "desc": "Complète un **donjon classique** (niveau 1 minimum).",
        "progress_key": "dungeon_best_classique", "threshold": 1,
    },
    {
        "id": "q08", "name": "Guerrier Confirmé", "emoji": "🗡️",
        "desc": "Atteins le **niveau 20**.",
        "progress_key": "level", "threshold": 20,
    },
    {
        "id": "q09", "name": "Horizons Lointains", "emoji": "🌅",
        "desc": "Atteins la **zone 200**.",
        "progress_key": "zone", "threshold": 200,
    },
    {
        "id": "q10", "name": "Explorateur des Donjons", "emoji": "🕯️",
        "desc": "Complète un **donjon classique niveau 5**.",
        "progress_key": "dungeon_best_classique", "threshold": 5,
    },
    {
        "id": "q11", "name": "Cap des Trente", "emoji": "🏅",
        "desc": "Atteins le **niveau 30**.",
        "progress_key": "level", "threshold": 30,
    },
    {
        "id": "q12", "name": "Terres Reculées", "emoji": "🏔️",
        "desc": "Atteins la **zone 300**.",
        "progress_key": "zone", "threshold": 300,
    },
    {
        "id": "q13", "name": "Habitué des Couloirs", "emoji": "🔑",
        "desc": "Complète un **donjon classique niveau 10**.",
        "progress_key": "dungeon_best_classique", "threshold": 10,
    },
    {
        "id": "q14", "name": "Demi-Centenaire", "emoji": "5️⃣0️⃣",
        "desc": "Atteins le **niveau 50**.",
        "progress_key": "level", "threshold": 50,
    },
    {
        "id": "q15", "name": "Grande Traversée", "emoji": "🏕️",
        "desc": "Atteins la **zone 500**.",
        "progress_key": "zone", "threshold": 500,
    },
    {
        "id": "q16", "name": "Chasseur de Donjons", "emoji": "🎯",
        "desc": "Complète un **donjon classique niveau 20**.",
        "progress_key": "dungeon_best_classique", "threshold": 20,
    },
    {
        "id": "q17", "name": "Trois Quarts du Centenaire", "emoji": "🔱",
        "desc": "Atteins le **niveau 75**.",
        "progress_key": "level", "threshold": 75,
    },
    {
        "id": "q18", "name": "Terres du Milieu", "emoji": "🌐",
        "desc": "Atteins la **zone 750**.",
        "progress_key": "zone", "threshold": 750,
    },
    {
        "id": "q19", "name": "Maître Classique", "emoji": "🏆",
        "desc": "Complète un **donjon classique niveau 30**.",
        "progress_key": "dungeon_best_classique", "threshold": 30,
    },
    {
        "id": "q20", "name": "Centurion", "emoji": "🛡️",
        "desc": "Atteins le **niveau 100**.",
        "progress_key": "level", "threshold": 100,
    },

    # ── Phase 2 — Montée en Puissance (q21-q40) ───────────────────────────────
    # Zones 1 000-3 000 · Niveaux 125-300 · Classiques 40-90
    # (pas d'élites : débloqués seulement à level 337)
    {
        "id": "q21", "name": "Porte du Grand Monde", "emoji": "🌋",
        "desc": "Atteins la **zone 1 000**.",
        "progress_key": "zone", "threshold": 1_000,
    },
    {
        "id": "q22", "name": "Au-delà du Centenaire", "emoji": "📊",
        "desc": "Atteins le **niveau 125**.",
        "progress_key": "level", "threshold": 125,
    },
    {
        "id": "q23", "name": "Terres Nouvelles", "emoji": "🗺️",
        "desc": "Atteins la **zone 1 200**.",
        "progress_key": "zone", "threshold": 1_200,
    },
    {
        "id": "q24", "name": "Conquérant des Profondeurs", "emoji": "🗡️",
        "desc": "Complète un **donjon classique niveau 40**.",
        "progress_key": "dungeon_best_classique", "threshold": 40,
    },
    {
        "id": "q25", "name": "Ascension", "emoji": "🚀",
        "desc": "Atteins le **niveau 150**.",
        "progress_key": "level", "threshold": 150,
    },
    {
        "id": "q26", "name": "Terres des Anciens", "emoji": "🗿",
        "desc": "Atteins la **zone 1 500**.",
        "progress_key": "zone", "threshold": 1_500,
    },
    {
        "id": "q27", "name": "Conquérant Classique", "emoji": "👑",
        "desc": "Complète un **donjon classique niveau 50**.",
        "progress_key": "dungeon_best_classique", "threshold": 50,
    },
    {
        "id": "q28", "name": "Cap des Cent Soixante-Quinze", "emoji": "📈",
        "desc": "Atteins le **niveau 175**.",
        "progress_key": "level", "threshold": 175,
    },
    {
        "id": "q29", "name": "Au-delà des Frontières", "emoji": "🌌",
        "desc": "Atteins la **zone 1 750**.",
        "progress_key": "zone", "threshold": 1_750,
    },
    {
        "id": "q30", "name": "Maître de Guerre", "emoji": "⚔️",
        "desc": "Atteins le **niveau 200**.",
        "progress_key": "level", "threshold": 200,
    },
    {
        "id": "q31", "name": "Monde Profond", "emoji": "🌊",
        "desc": "Atteins la **zone 2 000**.",
        "progress_key": "zone", "threshold": 2_000,
    },
    {
        "id": "q32", "name": "Maître Ultime Classique", "emoji": "💎",
        "desc": "Complète un **donjon classique niveau 60**.",
        "progress_key": "dungeon_best_classique", "threshold": 60,
    },
    {
        "id": "q33", "name": "Quart de Millénaire", "emoji": "🔢",
        "desc": "Atteins le **niveau 250**.",
        "progress_key": "level", "threshold": 250,
    },
    {
        "id": "q34", "name": "Abysses du Monde", "emoji": "🕳️",
        "desc": "Atteins la **zone 2 500**.",
        "progress_key": "zone", "threshold": 2_500,
    },
    {
        "id": "q35", "name": "Champion des Donjons", "emoji": "🥇",
        "desc": "Complète un **donjon classique niveau 70**.",
        "progress_key": "dungeon_best_classique", "threshold": 70,
    },
    {
        "id": "q36", "name": "Seigneur de Guerre", "emoji": "🔴",
        "desc": "Atteins le **niveau 300**.",
        "progress_key": "level", "threshold": 300,
    },
    {
        "id": "q37", "name": "Terres du Lointain", "emoji": "🌠",
        "desc": "Atteins la **zone 2 750**.",
        "progress_key": "zone", "threshold": 2_750,
    },
    {
        "id": "q38", "name": "Légende des Profondeurs", "emoji": "🌟",
        "desc": "Complète un **donjon classique niveau 80**.",
        "progress_key": "dungeon_best_classique", "threshold": 80,
    },
    {
        "id": "q39", "name": "Au-delà du Possible", "emoji": "🌌",
        "desc": "Atteins la **zone 3 000**.",
        "progress_key": "zone", "threshold": 3_000,
    },
    {
        "id": "q40", "name": "Presque Élite", "emoji": "🔱",
        "desc": "Complète un **donjon classique niveau 90**.",
        "progress_key": "dungeon_best_classique", "threshold": 90,
    },

    # ── Phase 3 — Élite (q41-q60) ─────────────────────────────────────────────
    # Zones 3 300-5 000 · Niveaux 330-500 · Élites 1-50 · Classique 100
    # (élites débloqués à level 337 ✓)
    {
        "id": "q41", "name": "Aux Portes de l'Élite", "emoji": "🟦",
        "desc": "Atteins le **niveau 330**.",
        "progress_key": "level", "threshold": 330,
    },
    {
        "id": "q42", "name": "Confins du Monde", "emoji": "🏔️",
        "desc": "Atteins la **zone 3 300**.",
        "progress_key": "zone", "threshold": 3_300,
    },
    {
        "id": "q43", "name": "Conquérant Absolu", "emoji": "💀",
        "desc": "Complète un **donjon classique niveau 100**.",
        "progress_key": "dungeon_best_classique", "threshold": 100,
    },
    {
        "id": "q44", "name": "Premier Défi Élite", "emoji": "🔵",
        "desc": "Complète un **donjon élite** (niveau 1 minimum, requiert level 337).",
        "progress_key": "dungeon_best_elite", "threshold": 1,
    },
    {
        "id": "q45", "name": "Guerrier d'Élite", "emoji": "💠",
        "desc": "Atteins le **niveau 350**.",
        "progress_key": "level", "threshold": 350,
    },
    {
        "id": "q46", "name": "Terres Élites", "emoji": "🌐",
        "desc": "Atteins la **zone 3 500**.",
        "progress_key": "zone", "threshold": 3_500,
    },
    {
        "id": "q47", "name": "Habitué des Élites", "emoji": "🔷",
        "desc": "Complète un **donjon élite niveau 10**.",
        "progress_key": "dungeon_best_elite", "threshold": 10,
    },
    {
        "id": "q48", "name": "Terres Mythiques", "emoji": "✨",
        "desc": "Atteins la **zone 3 750**.",
        "progress_key": "zone", "threshold": 3_750,
    },
    {
        "id": "q49", "name": "Cap des Quatre Cents", "emoji": "🔢",
        "desc": "Atteins le **niveau 400**.",
        "progress_key": "level", "threshold": 400,
    },
    {
        "id": "q50", "name": "Cœur du Monde", "emoji": "🌍",
        "desc": "Atteins la **zone 4 000**.",
        "progress_key": "zone", "threshold": 4_000,
    },
    {
        "id": "q51", "name": "Expert Élite", "emoji": "⭐",
        "desc": "Complète un **donjon élite niveau 20**.",
        "progress_key": "dungeon_best_elite", "threshold": 20,
    },
    {
        "id": "q52", "name": "Quasi-Mythique", "emoji": "💫",
        "desc": "Atteins le **niveau 450**.",
        "progress_key": "level", "threshold": 450,
    },
    {
        "id": "q53", "name": "Confins Mythiques", "emoji": "🌌",
        "desc": "Atteins la **zone 4 500**.",
        "progress_key": "zone", "threshold": 4_500,
    },
    {
        "id": "q54", "name": "Vétéran Élite", "emoji": "🏅",
        "desc": "Complète un **donjon élite niveau 30**.",
        "progress_key": "dungeon_best_elite", "threshold": 30,
    },
    {
        "id": "q55", "name": "Demi-Dieu", "emoji": "🌟",
        "desc": "Atteins le **niveau 475**.",
        "progress_key": "level", "threshold": 475,
    },
    {
        "id": "q56", "name": "Terres du Crépuscule", "emoji": "🌇",
        "desc": "Atteins la **zone 4 750**.",
        "progress_key": "zone", "threshold": 4_750,
    },
    {
        "id": "q57", "name": "Cinq Cents", "emoji": "5️⃣",
        "desc": "Atteins le **niveau 500**.",
        "progress_key": "level", "threshold": 500,
    },
    {
        "id": "q58", "name": "Mi-Légende", "emoji": "🌠",
        "desc": "Atteins la **zone 5 000**.",
        "progress_key": "zone", "threshold": 5_000,
    },
    {
        "id": "q59", "name": "Maître des Élites", "emoji": "🔰",
        "desc": "Complète un **donjon élite niveau 40**.",
        "progress_key": "dungeon_best_elite", "threshold": 40,
    },
    {
        "id": "q60", "name": "Champion Élite", "emoji": "🥇",
        "desc": "Complète un **donjon élite niveau 50**.",
        "progress_key": "dungeon_best_elite", "threshold": 50,
    },

    # ── Phase 4 — Abyssal (q61-q80) ───────────────────────────────────────────
    # Zones 5 500-8 000 · Niveaux 550-800 · Élites 60-90 · Abyssaux 1-30
    # (abyssaux débloqués à level 667 ✓)
    {
        "id": "q61", "name": "Seigneur Légendaire", "emoji": "👑",
        "desc": "Atteins le **niveau 550**.",
        "progress_key": "level", "threshold": 550,
    },
    {
        "id": "q62", "name": "Terres des Légendes", "emoji": "🏔️",
        "desc": "Atteins la **zone 5 500**.",
        "progress_key": "zone", "threshold": 5_500,
    },
    {
        "id": "q63", "name": "Conquérant Élite", "emoji": "💠",
        "desc": "Complète un **donjon élite niveau 60**.",
        "progress_key": "dungeon_best_elite", "threshold": 60,
    },
    {
        "id": "q64", "name": "Six Cents", "emoji": "🔢",
        "desc": "Atteins le **niveau 600**.",
        "progress_key": "level", "threshold": 600,
    },
    {
        "id": "q65", "name": "Profondeurs Légendaires", "emoji": "🌊",
        "desc": "Atteins la **zone 6 000**.",
        "progress_key": "zone", "threshold": 6_000,
    },
    {
        "id": "q66", "name": "Champion des Élites", "emoji": "💎",
        "desc": "Complète un **donjon élite niveau 70**.",
        "progress_key": "dungeon_best_elite", "threshold": 70,
    },
    {
        "id": "q67", "name": "Aux Portes de l'Abîme", "emoji": "🌑",
        "desc": "Atteins le **niveau 650**.",
        "progress_key": "level", "threshold": 650,
    },
    {
        "id": "q68", "name": "Terres Abyssales", "emoji": "🕳️",
        "desc": "Atteins la **zone 6 500**.",
        "progress_key": "zone", "threshold": 6_500,
    },
    {
        "id": "q69", "name": "Plongeon dans l'Abîme", "emoji": "🟥",
        "desc": "Complète un **donjon abyssal** (niveau 1 minimum, requiert level 667).",
        "progress_key": "dungeon_best_abyssal", "threshold": 1,
    },
    {
        "id": "q70", "name": "Sept Cents", "emoji": "⚡",
        "desc": "Atteins le **niveau 700**.",
        "progress_key": "level", "threshold": 700,
    },
    {
        "id": "q71", "name": "Légende Élite", "emoji": "🔱",
        "desc": "Complète un **donjon élite niveau 80**.",
        "progress_key": "dungeon_best_elite", "threshold": 80,
    },
    {
        "id": "q72", "name": "Territoires Mythiques", "emoji": "🗺️",
        "desc": "Atteins la **zone 7 000**.",
        "progress_key": "zone", "threshold": 7_000,
    },
    {
        "id": "q73", "name": "Habitué de l'Abîme", "emoji": "🌀",
        "desc": "Complète un **donjon abyssal niveau 10**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 10,
    },
    {
        "id": "q74", "name": "Quasi-Divin", "emoji": "💡",
        "desc": "Atteins le **niveau 750**.",
        "progress_key": "level", "threshold": 750,
    },
    {
        "id": "q75", "name": "Terres Primordiales", "emoji": "🌋",
        "desc": "Atteins la **zone 7 500**.",
        "progress_key": "zone", "threshold": 7_500,
    },
    {
        "id": "q76", "name": "Presque au Sommet Élite", "emoji": "🔝",
        "desc": "Complète un **donjon élite niveau 90**.",
        "progress_key": "dungeon_best_elite", "threshold": 90,
    },
    {
        "id": "q77", "name": "Chasseur des Abysses", "emoji": "🕷️",
        "desc": "Complète un **donjon abyssal niveau 20**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 20,
    },
    {
        "id": "q78", "name": "Guerrier Divin", "emoji": "⚔️",
        "desc": "Atteins le **niveau 800**.",
        "progress_key": "level", "threshold": 800,
    },
    {
        "id": "q79", "name": "Terres du Divin", "emoji": "🌠",
        "desc": "Atteins la **zone 8 000**.",
        "progress_key": "zone", "threshold": 8_000,
    },
    {
        "id": "q80", "name": "Dompteur des Abysses", "emoji": "🐉",
        "desc": "Complète un **donjon abyssal niveau 30**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 30,
    },

    # ── Phase 5 — Légende (q81-q100) ─────────────────────────────────────────
    # Zones 8 500-10 000 · Niveaux 850-1 000 · Élites 100 · Abyssaux 40-100
    # prestige_level 100/500/1 000
    {
        "id": "q81", "name": "Seigneur des Élites", "emoji": "👑",
        "desc": "Complète un **donjon élite niveau 100**.",
        "progress_key": "dungeon_best_elite", "threshold": 100,
    },
    {
        "id": "q82", "name": "Abyssal Confirmé", "emoji": "🌀",
        "desc": "Complète un **donjon abyssal niveau 40**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 40,
    },
    {
        "id": "q83", "name": "Cap des Huit Cent Cinquante", "emoji": "📈",
        "desc": "Atteins le **niveau 850**.",
        "progress_key": "level", "threshold": 850,
    },
    {
        "id": "q84", "name": "Au-delà du Divin", "emoji": "✨",
        "desc": "Atteins la **zone 8 500**.",
        "progress_key": "zone", "threshold": 8_500,
    },
    {
        "id": "q85", "name": "Renaissance", "emoji": "🔄",
        "desc": "Effectue un **prestige** avec au moins le **niveau 100** (prestige_level ≥ 100).",
        "progress_key": "prestige_level", "threshold": 100,
    },
    {
        "id": "q86", "name": "Conquérant des Abysses", "emoji": "🌋",
        "desc": "Complète un **donjon abyssal niveau 50**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 50,
    },
    {
        "id": "q87", "name": "Neuf Cents", "emoji": "🔢",
        "desc": "Atteins le **niveau 900**.",
        "progress_key": "level", "threshold": 900,
    },
    {
        "id": "q88", "name": "Terres Légendaires", "emoji": "🌐",
        "desc": "Atteins la **zone 9 000**.",
        "progress_key": "zone", "threshold": 9_000,
    },
    {
        "id": "q89", "name": "Maître de l'Abîme", "emoji": "👁️",
        "desc": "Complète un **donjon abyssal niveau 70**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 70,
    },
    {
        "id": "q90", "name": "Presque Dieu", "emoji": "💫",
        "desc": "Atteins le **niveau 950**.",
        "progress_key": "level", "threshold": 950,
    },
    {
        "id": "q91", "name": "Terres de l'Absolu", "emoji": "🌑",
        "desc": "Atteins la **zone 9 250**.",
        "progress_key": "zone", "threshold": 9_250,
    },
    {
        "id": "q92", "name": "Transcendance", "emoji": "♻️",
        "desc": "Effectue un **prestige** avec au moins le **niveau 500** (prestige_level ≥ 500).",
        "progress_key": "prestige_level", "threshold": 500,
    },
    {
        "id": "q93", "name": "Presque l'Abîme Total", "emoji": "🕳️",
        "desc": "Complète un **donjon abyssal niveau 90**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 90,
    },
    {
        "id": "q94", "name": "Dieu Vivant", "emoji": "🌟",
        "desc": "Atteins le **niveau 1 000**.",
        "progress_key": "level", "threshold": 1_000,
    },
    {
        "id": "q95", "name": "Confins du Monde", "emoji": "🏔️",
        "desc": "Atteins la **zone 9 500**.",
        "progress_key": "zone", "threshold": 9_500,
    },
    {
        "id": "q96", "name": "Seigneur de l'Abîme", "emoji": "🌀",
        "desc": "Complète un **donjon abyssal niveau 100**.",
        "progress_key": "dungeon_best_abyssal", "threshold": 100,
    },
    {
        "id": "q97", "name": "Fin du Monde Connue", "emoji": "🌍",
        "desc": "Atteins la **zone 9 750**.",
        "progress_key": "zone", "threshold": 9_750,
    },
    {
        "id": "q98", "name": "La Fin du Monde", "emoji": "🌋",
        "desc": "Atteins la **zone 10 000**.",
        "progress_key": "zone", "threshold": 10_000,
    },
    {
        "id": "q99", "name": "Toucher la Divinité", "emoji": "✨",
        "desc": "Effectue un **prestige** avec au moins le **niveau 1 000** (prestige_level ≥ 1 000).",
        "progress_key": "prestige_level", "threshold": 1_000,
    },
    {
        "id": "q100", "name": "L'Éternel", "emoji": "✝️",
        "desc": "Atteins à nouveau le **niveau 1 000** après un prestige.",
        "progress_key": "level", "threshold": 1_000,
    },
]

# ─── Quêtes Secondaires (100) ─────────────────────────────────────────────────
# Ordre par zone équivalente (profession lv×100), puis PvP à la fin.
# Récompense par quête : +0,5% de chance de gagner +1 énergie après combat gagné (energy_on_win_chance).

SECONDARY_QUESTS: list[dict] = [
    # ── z0 — Choisir ses métiers (s01-s03) ────────────────────────────────────
    {
        "id": "s01", "name": "Premier Métier", "emoji": "🌾",
        "desc": "Choisis une **profession de récolte**.",
        "progress_key": "has_harvest", "threshold": 1,
    },
    # ── z0 — Choisir ses métiers (s02-s03) ──────────────────────────────────────
    {
        "id": "s02", "name": "L'Artisan", "emoji": "🔨",
        "desc": "Choisis un **métier d'artisanat**.",
        "progress_key": "has_craft", "threshold": 1,
    },
    {
        "id": "s03", "name": "Le Concepteur", "emoji": "📐",
        "desc": "Choisis un **métier de conception**.",
        "progress_key": "has_conception", "threshold": 1,
    },
    # ── z500 — Niveaux 5, premières transactions (s04-s09) ───────────────────────
    {
        "id": "s04", "name": "Premiers Fruits", "emoji": "🌱",
        "desc": "Atteins le **niveau 5** en récolte.",
        "progress_key": "harvest_level", "threshold": 5,
    },
    {
        "id": "s05", "name": "Premier Coup de Marteau", "emoji": "🔩",
        "desc": "Atteins le **niveau 5** en artisanat.",
        "progress_key": "craft_level", "threshold": 5,
    },
    {
        "id": "s06", "name": "Premiers Schémas", "emoji": "✏️",
        "desc": "Atteins le **niveau 5** en conception.",
        "progress_key": "conception_level", "threshold": 5,
    },
    {
        "id": "s07", "name": "Marchand Débutant", "emoji": "🏪",
        "desc": "Réalise ta **1ère vente** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 1,
    },
    {
        "id": "s08", "name": "Acheteur Avisé", "emoji": "🛍️",
        "desc": "Réalise ton **1er achat** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 1,
    },
    {
        "id": "s09", "name": "Premier Échange", "emoji": "🤝",
        "desc": "Réalise ton **1er échange** avec un autre joueur.",
        "progress_key": "trade_count", "threshold": 1,
    },
    # ── z1000 — Niveaux 10, raid 1, combo (s10-s14) ───────────────────────
    {
        "id": "s10", "name": "Mains dans la Terre", "emoji": "🌿",
        "desc": "Atteins le **niveau 10** en récolte.",
        "progress_key": "harvest_level", "threshold": 10,
    },
    {
        "id": "s11", "name": "Façonneur", "emoji": "⚒️",
        "desc": "Atteins le **niveau 10** en artisanat.",
        "progress_key": "craft_level", "threshold": 10,
    },
    {
        "id": "s12", "name": "L'Inventeur", "emoji": "💡",
        "desc": "Atteins le **niveau 10** en conception.",
        "progress_key": "conception_level", "threshold": 10,
    },
    {
        "id": "s13", "name": "Raid Découverte", "emoji": "👥",
        "desc": "Complète ton **premier raid**.",
        "progress_key": "raid_max_completed", "threshold": 1,
    },
    {
        "id": "s14", "name": "Polyvalent", "emoji": "🔄",
        "desc": "Atteins le **niveau 10** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 10,
    },
    # ── z1500 — 5 ventes / achats / échanges (s15-s17) ──────────────────────
    {
        "id": "s15", "name": "Vendeur Régulier", "emoji": "🛒",
        "desc": "Réalise **5 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 5,
    },
    {
        "id": "s16", "name": "Acheteur Régulier", "emoji": "📦",
        "desc": "Réalise **5 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 5,
    },
    {
        "id": "s17", "name": "Échangeur Débutant", "emoji": "🔗",
        "desc": "Réalise **5 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 5,
    },
    # ── z2000 — Niveaux 20, raid 2, combo (s18-s22) ───────────────────────
    {
        "id": "s18", "name": "Cueilleur Confirmé", "emoji": "🍃",
        "desc": "Atteins le **niveau 20** en récolte.",
        "progress_key": "harvest_level", "threshold": 20,
    },
    {
        "id": "s19", "name": "Forgeron Débutant", "emoji": "🔧",
        "desc": "Atteins le **niveau 20** en artisanat.",
        "progress_key": "craft_level", "threshold": 20,
    },
    {
        "id": "s20", "name": "Concepteur Débutant", "emoji": "📏",
        "desc": "Atteins le **niveau 20** en conception.",
        "progress_key": "conception_level", "threshold": 20,
    },
    {
        "id": "s21", "name": "Raid Confirmé", "emoji": "🔥",
        "desc": "Complète un **raid niveau 2**.",
        "progress_key": "raid_max_completed", "threshold": 2,
    },
    {
        "id": "s22", "name": "Trimaître Débutant", "emoji": "⚒️",
        "desc": "Atteins le **niveau 20** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 20,
    },
    # ── z2500 — 10 ventes / achats / échanges (s23-s25) ──────────────────────
    {
        "id": "s23", "name": "La Bonne Affaire", "emoji": "💰",
        "desc": "Réalise **10 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 10,
    },
    {
        "id": "s24", "name": "Collectionneur", "emoji": "📦",
        "desc": "Réalise **10 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 10,
    },
    {
        "id": "s25", "name": "Réseau de Marchands", "emoji": "🌐",
        "desc": "Réalise **10 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 10,
    },
    # ── z3000 — Niveaux 30, raid 3, combo (s26-s30) ───────────────────────
    {
        "id": "s26", "name": "Récolteur Aguerri", "emoji": "🌻",
        "desc": "Atteins le **niveau 30** en récolte.",
        "progress_key": "harvest_level", "threshold": 30,
    },
    {
        "id": "s27", "name": "Artisan Aguerri", "emoji": "⚙️",
        "desc": "Atteins le **niveau 30** en artisanat.",
        "progress_key": "craft_level", "threshold": 30,
    },
    {
        "id": "s28", "name": "Architecte Amateur", "emoji": "📐",
        "desc": "Atteins le **niveau 30** en conception.",
        "progress_key": "conception_level", "threshold": 30,
    },
    {
        "id": "s29", "name": "Raid Avancé", "emoji": "💪",
        "desc": "Complète un **raid niveau 3**.",
        "progress_key": "raid_max_completed", "threshold": 3,
    },
    {
        "id": "s30", "name": "Trimaître Intermédiaire", "emoji": "🛠️",
        "desc": "Atteins le **niveau 30** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 30,
    },
    # ── z3500 — 25 ventes / achats / échanges (s31-s33) ──────────────────────
    {
        "id": "s31", "name": "Marchand Actif", "emoji": "📊",
        "desc": "Réalise **25 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 25,
    },
    {
        "id": "s32", "name": "Acheteur Assidu", "emoji": "🔍",
        "desc": "Réalise **25 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 25,
    },
    {
        "id": "s33", "name": "Partenaire Commercial", "emoji": "🤜",
        "desc": "Réalise **25 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 25,
    },
    # ── z4000 — Niveaux 40, raid 4, combo (s34-s38) ───────────────────────
    {
        "id": "s34", "name": "Maître des Champs", "emoji": "🌲",
        "desc": "Atteins le **niveau 40** en récolte.",
        "progress_key": "harvest_level", "threshold": 40,
    },
    {
        "id": "s35", "name": "Artisan Intermédiaire", "emoji": "🔨",
        "desc": "Atteins le **niveau 40** en artisanat.",
        "progress_key": "craft_level", "threshold": 40,
    },
    {
        "id": "s36", "name": "Concepteur Intermédiaire", "emoji": "📋",
        "desc": "Atteins le **niveau 40** en conception.",
        "progress_key": "conception_level", "threshold": 40,
    },
    {
        "id": "s37", "name": "Chasseur de Raids", "emoji": "⚔️",
        "desc": "Complète un **raid niveau 4**.",
        "progress_key": "raid_max_completed", "threshold": 4,
    },
    {
        "id": "s38", "name": "Trimaître Aguerri", "emoji": "🎯",
        "desc": "Atteins le **niveau 40** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 40,
    },
    # ── z4500 — 50 ventes / achats / échanges (s39-s41) ──────────────────────
    {
        "id": "s39", "name": "Marchand Prospère", "emoji": "💹",
        "desc": "Réalise **50 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 50,
    },
    {
        "id": "s40", "name": "Chasseur de Bonnes Affaires", "emoji": "🎯",
        "desc": "Réalise **50 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 50,
    },
    {
        "id": "s41", "name": "Commerçant Aguerri", "emoji": "💼",
        "desc": "Réalise **50 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 50,
    },
    # ── z5000 — Niveaux 50, raid 5, combo (s42-s46) ───────────────────────
    {
        "id": "s42", "name": "Récolteur Chevronné", "emoji": "🌾",
        "desc": "Atteins le **niveau 50** en récolte.",
        "progress_key": "harvest_level", "threshold": 50,
    },
    {
        "id": "s43", "name": "Forgeron Confirmé", "emoji": "⚗️",
        "desc": "Atteins le **niveau 50** en artisanat.",
        "progress_key": "craft_level", "threshold": 50,
    },
    {
        "id": "s44", "name": "Ingénieur Confirmé", "emoji": "🔬",
        "desc": "Atteins le **niveau 50** en conception.",
        "progress_key": "conception_level", "threshold": 50,
    },
    {
        "id": "s45", "name": "Raid Élite", "emoji": "🌟",
        "desc": "Complète un **raid niveau 5**.",
        "progress_key": "raid_max_completed", "threshold": 5,
    },
    {
        "id": "s46", "name": "Trimaître Chevronné", "emoji": "🏅",
        "desc": "Atteins le **niveau 50** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 50,
    },
    # ── z5500 — 100 ventes / achats / échanges (s47-s49) ──────────────────────
    {
        "id": "s47", "name": "Négociant Confirmé", "emoji": "🤑",
        "desc": "Réalise **100 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 100,
    },
    {
        "id": "s48", "name": "Accumulateur", "emoji": "📊",
        "desc": "Réalise **100 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 100,
    },
    {
        "id": "s49", "name": "Baron du Commerce", "emoji": "🏅",
        "desc": "Réalise **100 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 100,
    },
    # ── z6000 — Niveaux 60, raid 6, combo (s50-s54) ───────────────────────
    {
        "id": "s50", "name": "Expert Récolteur", "emoji": "🌳",
        "desc": "Atteins le **niveau 60** en récolte.",
        "progress_key": "harvest_level", "threshold": 60,
    },
    {
        "id": "s51", "name": "Artisan Chevronné", "emoji": "🔨",
        "desc": "Atteins le **niveau 60** en artisanat.",
        "progress_key": "craft_level", "threshold": 60,
    },
    {
        "id": "s52", "name": "Concepteur Chevronné", "emoji": "📊",
        "desc": "Atteins le **niveau 60** en conception.",
        "progress_key": "conception_level", "threshold": 60,
    },
    {
        "id": "s53", "name": "Vétéran des Raids", "emoji": "🔱",
        "desc": "Complète un **raid niveau 6**.",
        "progress_key": "raid_max_completed", "threshold": 6,
    },
    {
        "id": "s54", "name": "Trimaître Expert", "emoji": "💎",
        "desc": "Atteins le **niveau 60** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 60,
    },
    # ── z6500 — 250 ventes / achats / échanges (s55-s57) ──────────────────────
    {
        "id": "s55", "name": "Grand Marchand", "emoji": "🏦",
        "desc": "Réalise **250 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 250,
    },
    {
        "id": "s56", "name": "Grand Acheteur", "emoji": "💎",
        "desc": "Réalise **250 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 250,
    },
    {
        "id": "s57", "name": "Magnat du Commerce", "emoji": "👑",
        "desc": "Réalise **250 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 250,
    },
    # ── z7000 — Niveaux 70, raid 7, combo (s58-s62) ───────────────────────
    {
        "id": "s58", "name": "Grand Récolteur", "emoji": "🌴",
        "desc": "Atteins le **niveau 70** en récolte.",
        "progress_key": "harvest_level", "threshold": 70,
    },
    {
        "id": "s59", "name": "Grand Forgeron", "emoji": "⛏️",
        "desc": "Atteins le **niveau 70** en artisanat.",
        "progress_key": "craft_level", "threshold": 70,
    },
    {
        "id": "s60", "name": "Grand Architecte", "emoji": "🏛️",
        "desc": "Atteins le **niveau 70** en conception.",
        "progress_key": "conception_level", "threshold": 70,
    },
    {
        "id": "s61", "name": "Raid Légendaire", "emoji": "💎",
        "desc": "Complète un **raid niveau 7**.",
        "progress_key": "raid_max_completed", "threshold": 7,
    },
    {
        "id": "s62", "name": "Trimaître Maître", "emoji": "🌟",
        "desc": "Atteins le **niveau 70** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 70,
    },
    # ── z7500 — 500 ventes / achats / échanges (s63-s65) ──────────────────────
    {
        "id": "s63", "name": "Roi des Ventes", "emoji": "👑",
        "desc": "Réalise **500 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 500,
    },
    {
        "id": "s64", "name": "Roi des Achats", "emoji": "🏆",
        "desc": "Réalise **500 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 500,
    },
    {
        "id": "s65", "name": "Réseau Élite", "emoji": "🌐",
        "desc": "Réalise **500 échanges** avec d'autres joueurs.",
        "progress_key": "trade_count", "threshold": 500,
    },
    # ── z8000 — Niveaux 80, raid 8, combo (s66-s70) ───────────────────────
    {
        "id": "s66", "name": "Récolteur Élite", "emoji": "🌺",
        "desc": "Atteins le **niveau 80** en récolte.",
        "progress_key": "harvest_level", "threshold": 80,
    },
    {
        "id": "s67", "name": "Artisan Élite", "emoji": "🏗️",
        "desc": "Atteins le **niveau 80** en artisanat.",
        "progress_key": "craft_level", "threshold": 80,
    },
    {
        "id": "s68", "name": "Concepteur Élite", "emoji": "🔭",
        "desc": "Atteins le **niveau 80** en conception.",
        "progress_key": "conception_level", "threshold": 80,
    },
    {
        "id": "s69", "name": "Conquérant des Raids", "emoji": "🏅",
        "desc": "Complète un **raid niveau 8**.",
        "progress_key": "raid_max_completed", "threshold": 8,
    },
    {
        "id": "s70", "name": "Trimaître Élite", "emoji": "🎖️",
        "desc": "Atteins le **niveau 80** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 80,
    },
    # ── z8500 — 1000 ventes / achats (s71-s72) ─────────────────────────────
    {
        "id": "s71", "name": "Légende du Commerce", "emoji": "🌟",
        "desc": "Réalise **1 000 ventes** à l'hôtel des ventes.",
        "progress_key": "market_sells", "threshold": 1000,
    },
    {
        "id": "s72", "name": "Trésorier Légendaire", "emoji": "💰",
        "desc": "Réalise **1 000 achats** à l'hôtel des ventes.",
        "progress_key": "market_buys", "threshold": 1000,
    },
    # ── z9000 — Niveaux 90, raid 9, combo (s73-s77) ───────────────────────
    {
        "id": "s73", "name": "Maître Récolteur", "emoji": "🌴",
        "desc": "Atteins le **niveau 90** en récolte.",
        "progress_key": "harvest_level", "threshold": 90,
    },
    {
        "id": "s74", "name": "Maître Forgeron", "emoji": "🔱",
        "desc": "Atteins le **niveau 90** en artisanat.",
        "progress_key": "craft_level", "threshold": 90,
    },
    {
        "id": "s75", "name": "Maître Concepteur", "emoji": "🎓",
        "desc": "Atteins le **niveau 90** en conception.",
        "progress_key": "conception_level", "threshold": 90,
    },
    {
        "id": "s76", "name": "Maître des Raids", "emoji": "👑",
        "desc": "Complète un **raid niveau 9**.",
        "progress_key": "raid_max_completed", "threshold": 9,
    },
    {
        "id": "s77", "name": "Trimaître Légendaire", "emoji": "🌠",
        "desc": "Atteins le **niveau 90** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 90,
    },
    # ── z10000 — Niveaux 100, raid 10, combo (s78-s82) ──────────────────────
    {
        "id": "s78", "name": "Seigneur des Ressources", "emoji": "🌟",
        "desc": "Atteins le **niveau 100** en récolte.",
        "progress_key": "harvest_level", "threshold": 100,
    },
    {
        "id": "s79", "name": "Seigneur de la Forge", "emoji": "⚒️",
        "desc": "Atteins le **niveau 100** en artisanat.",
        "progress_key": "craft_level", "threshold": 100,
    },
    {
        "id": "s80", "name": "Seigneur des Créations", "emoji": "✨",
        "desc": "Atteins le **niveau 100** en conception.",
        "progress_key": "conception_level", "threshold": 100,
    },
    {
        "id": "s81", "name": "Légende du Raid", "emoji": "🌠",
        "desc": "Complète un **raid niveau 10**.",
        "progress_key": "raid_max_completed", "threshold": 10,
    },
    {
        "id": "s82", "name": "La Perfection", "emoji": "✨",
        "desc": "Atteins le **niveau 100** dans les **3 métiers**.",
        "progress_key": "all_prof", "threshold": 100,
    },
    # ── PvP Classique — Combats (s83-s91) ───────────────────────────────────────
    {
        "id": "s83", "name": "Dans l'Arène", "emoji": "⚔️",
        "desc": "Réalise ton **1er combat PvP**.",
        "progress_key": "pvp_fights", "threshold": 1,
    },
    {
        "id": "s84", "name": "Duelliste", "emoji": "🗡️",
        "desc": "Réalise **5 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 5,
    },
    {
        "id": "s85", "name": "Gladiateur", "emoji": "🏟️",
        "desc": "Réalise **10 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 10,
    },
    {
        "id": "s86", "name": "Combattant Acharné", "emoji": "💥",
        "desc": "Réalise **25 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 25,
    },
    {
        "id": "s87", "name": "Guerrier de l'Arène", "emoji": "🔴",
        "desc": "Réalise **50 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 50,
    },
    {
        "id": "s88", "name": "Arène Vétéran", "emoji": "🏆",
        "desc": "Réalise **100 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 100,
    },
    {
        "id": "s89", "name": "Légionnaire", "emoji": "⚡",
        "desc": "Réalise **250 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 250,
    },
    {
        "id": "s90", "name": "Arène Légendaire", "emoji": "🌟",
        "desc": "Réalise **500 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 500,
    },
    {
        "id": "s91", "name": "Immortel de l'Arène", "emoji": "💀",
        "desc": "Réalise **1 000 combats PvP**.",
        "progress_key": "pvp_fights", "threshold": 1000,
    },
    # ── PvP Classé — Victoires (s92-s100) ───────────────────────────────────────
    {
        "id": "s92", "name": "Première Victoire", "emoji": "🥊",
        "desc": "Remporte ton **1er combat PvP**.",
        "progress_key": "pvp_wins", "threshold": 1,
    },
    {
        "id": "s93", "name": "Vainqueur Régulier", "emoji": "🎯",
        "desc": "Remporte **5 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 5,
    },
    {
        "id": "s94", "name": "Champion Débutant", "emoji": "🥉",
        "desc": "Remporte **10 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 10,
    },
    {
        "id": "s95", "name": "Vainqueur Confirmé", "emoji": "🥈",
        "desc": "Remporte **25 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 25,
    },
    {
        "id": "s96", "name": "Champion", "emoji": "🥇",
        "desc": "Remporte **50 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 50,
    },
    {
        "id": "s97", "name": "Maître de l'Arène", "emoji": "🏆",
        "desc": "Remporte **100 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 100,
    },
    {
        "id": "s98", "name": "Grand Champion", "emoji": "👑",
        "desc": "Remporte **250 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 250,
    },
    {
        "id": "s99", "name": "Invincible", "emoji": "⚡",
        "desc": "Remporte **500 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 500,
    },
    {
        "id": "s100", "name": "Légende de l'Arène", "emoji": "💫",
        "desc": "Remporte **1 000 victoires PvP**.",
        "progress_key": "pvp_wins", "threshold": 1000,
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
    if key == "prestige_level":
        return player.get("prestige_level", 0)
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
    if key in ("all_prof", "all_prof_100"):
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
