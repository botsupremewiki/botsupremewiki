"""
Moteur de combat du RPG.
Gère les calculs de dégâts, les tours, les passifs de classes et les effets de statut.
"""
from __future__ import annotations
import logging
import math
import random
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

from bot.cogs.rpg.models import compute_total_stats, compute_max_hp, compute_relic_effects, CLASS_SPELLS, STAT_FR


def _parse_food_buffs(raw: str | None) -> dict:
    """Parse le JSON food_buffs depuis la DB. Retourne {} si invalide."""
    if not raw:
        return {}
    try:
        import json
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"food_buffs JSON invalide: {e!r} — valeur: {raw!r:.100}")
        return {}


# ─── Structures de données ─────────────────────────────────────────────────

@dataclass
class CombatStats:
    hp:          int   = 1
    max_hp:      int   = 1
    p_atk:       int   = 0
    m_atk:       int   = 0
    p_pen:       int   = 0
    m_pen:       int   = 0
    p_def:       int   = 0
    m_def:       int   = 0
    speed:       int   = 1
    crit_chance: float = 5.0
    crit_damage: float = 150.0
    shield:      int   = 0  # bouclier absorbant des dégâts

    @classmethod
    def from_dict(cls, d: dict) -> "CombatStats":
        return cls(
            hp          = int(d.get("hp", 1)),
            max_hp      = int(d.get("hp", 1)),
            p_atk       = int(d.get("p_atk", 0)),
            m_atk       = int(d.get("m_atk", 0)),
            p_pen       = int(d.get("p_pen", 0)),
            m_pen       = int(d.get("m_pen", 0)),
            p_def       = int(d.get("p_def", 0)),
            m_def       = int(d.get("m_def", 0)),
            speed       = max(1, int(d.get("speed", 1))),
            crit_chance = float(d.get("crit_chance", 5.0)),
            crit_damage = float(d.get("crit_damage", 150.0)),
            shield      = 0,
        )

    def set_current_hp(self, hp: int):
        self.hp = max(0, min(hp, self.max_hp))


@dataclass
class CombatState:
    """État complet d'un combat."""
    player_stats:   CombatStats
    enemy_stats:    CombatStats
    player_class:   str
    enemy_data:     dict  # données brutes de l'ennemi
    turn:           int   = 0
    log:            list  = field(default_factory=list)

    # Effets de statut joueur
    player_elixir:    dict  = field(default_factory=dict)   # {stat: bonus%}
    player_shield_hp: int   = 0
    player_burns:     int   = 0  # stacks de brûlure sur l'ennemi
    player_poison:    bool  = False
    player_bleed:     bool  = False

    # Effets de statut ennemi
    enemy_debuffs:    dict  = field(default_factory=dict)   # {stat: factor}  <1 = reduction
    enemy_burns:      int   = 0  # stacks de brûlure
    enemy_stun:       int   = 0  # tours restants de stun

    # Buffs Paladin (ramp)
    paladin_ramp_dmg_red: float = 0.0   # 0.0 → 0.30
    paladin_ramp_dmg_amp: float = 0.0   # 0.0 → 0.30
    paladin_initial_stats: dict = field(default_factory=dict)  # stats de référence (début combat, cap +20%)

    # Relics effects
    relic_effects:    dict  = field(default_factory=dict)

    # ── Spell system ─────────────────────────────────────────────────────────
    player_resource:      int   = 0
    spell_cooldowns:      dict  = field(default_factory=dict)   # {spell_key: turns_left}
    spell_active_buffs:   list  = field(default_factory=list)   # [{type, turns, ...}]
    spell_active_debuffs: list  = field(default_factory=list)   # [{type, turns, ...}]

    spell_dodge_next:         bool  = False  # esquive la prochaine attaque ennemie
    spell_damage_amp:         float = 1.0    # multiplicateur dégâts sortants (Marquage)
    spell_damage_reduction:   float = 0.0    # réduction dégâts reçus (Barrière, Aura)
    spell_dot_amp:            float = 1.0    # multiplicateur DoT (Agonie)
    spell_resurrection:       bool  = False  # survie à mort avec 1 HP
    spell_no_heal_turns:      int   = 0      # aucun soin pendant N tours (Transformation)
    ignore_enemy_passive:     bool  = False  # potion_protection_ultime
    resurrection_hp_pct:      float = 0.0    # si >0, ressuscite à ce % de HP max (potion)

    # Passifs boss
    boss_passif_effects:    dict  = field(default_factory=dict)
    boss_spell_turn_counter: int  = 0
    boss_spell_turn_mod:    int   = 0
    boss_pure_dmg_counter:  int   = 0   # counter for periodic pure damage

    last_enemy_damage:    int   = 0      # derniers dégâts reçus (Rembobinage)
    enemy_poison_stacks:  int   = 0      # stacks de poison par sort

    # Nouveaux champs (refonte sorts 2026-03-20)
    undying_turns:            int   = 0      # Guerrier ult: coup fatal → 1 PV
    extra_lifesteal:          float = 0.0    # Vampire: lifesteal buff extra
    extra_lifesteal_turns:    int   = 0
    enemy_marked:             bool  = False  # Tireur S2: ennemi marqué
    enemy_marked_pct:         int   = 0      # % dégâts bonus sur ennemi marqué
    enemy_marked_turns:       int   = 0
    contre_attaque_turns:     int   = 0      # Guerrier S2: riposte automatique
    blood_mark_turns:         int   = 0      # Vampire S2: marque de sang active
    blood_mark_heal_pct:      float = 0.0    # % vol de vie via marque de sang
    spell_reflect_pct:        float = 0.0    # Support ult: renvoi % dégâts
    spell_reflect_turns:      int   = 0
    spell_double_dodge_next:  bool  = False  # Assassin S1: prochaine esquive ×2

    # Passifs boss emblématiques / antiques
    boss_passif_init_done: bool  = False  # init one-time appliqué
    boss_eternity_active:  bool  = False  # Éternité : HP ennemi plancher 50% avant tour 10
    boss_dmg_ramp_stacks:  int   = 0      # Anneau donjon : stacks de ramp dégâts (+3%/tour)
    boss_curse_healing:    bool  = False  # Maudit : soins joueur réduits de 50%
    boss_no_player_crit:   bool  = False  # Malédiction Antique : crits sans bonus
    boss_neant_active:     bool  = False  # Néant : passifs classe désactivés tours 1-3

    # Boss de raid
    raid_boss_resurrected: bool  = False  # Ignareth : résurrection à 25% HP déjà utilisée
    player_burn_stacks:    int   = 0      # stacks de brûlure reçus par le joueur (boss raid)

    @property
    def is_over(self) -> bool:
        return self.player_stats.hp <= 0 or self.enemy_stats.hp <= 0

    @property
    def player_won(self) -> bool:
        return self.enemy_stats.hp <= 0 and self.player_stats.hp > 0


# ─── Calculs de dégâts ─────────────────────────────────────────────────────

def calc_physical_damage(attacker: CombatStats, defender: CombatStats, mult: float = 1.0) -> int:
    effective_def = max(0, defender.p_def - attacker.p_pen)
    raw = attacker.p_atk * mult - effective_def
    return max(1, int(raw))


def calc_magical_damage(attacker: CombatStats, defender: CombatStats, mult: float = 1.0) -> int:
    effective_def = max(0, defender.m_def - attacker.m_pen)
    raw = attacker.m_atk * mult - effective_def
    return max(1, int(raw))


def apply_crit(damage: int, crit_chance: float, crit_damage: float) -> tuple[int, bool]:
    # Excédent de crit_chance au-delà de 100% → bonus crit_damage (1% excédent = +1% crit dmg)
    if crit_chance > 100.0:
        crit_damage += (crit_chance - 100.0)
        crit_chance = 100.0
    is_crit = random.random() < (crit_chance / 100.0)
    if is_crit:
        damage = int(damage * (crit_damage / 100.0))
    return damage, is_crit


def apply_shield(target: CombatStats, damage: int) -> tuple[int, int]:
    """Absorbe les dégâts avec le bouclier. Retourne (dégâts restants, bouclier restant)."""
    if target.shield <= 0:
        return damage, 0
    absorbed = min(target.shield, damage)
    target.shield -= absorbed
    return max(0, damage - absorbed), target.shield


def apply_damage_to_target(target: CombatStats, damage: int) -> int:
    """Applique les dégâts en passant d'abord par le bouclier."""
    remaining, _ = apply_shield(target, damage)
    target.hp = max(0, target.hp - remaining)
    return damage


# ─── Passifs de classe ─────────────────────────────────────────────────────

def apply_player_passive(state: CombatState, base_phys: int, base_magic: int) -> tuple[int, int, list[str]]:
    """
    Applique le passif du joueur et retourne (phys_dmg, magic_dmg, log_extras).
    """
    cls = state.player_class
    ps  = state.player_stats
    es  = state.enemy_stats
    logs = []

    hp_pct_missing = max(0, (ps.max_hp - ps.hp) / max(ps.max_hp, 1))
    hp_pct_current = max(0, ps.hp / max(ps.max_hp, 1))

    if cls == "Guerrier":
        bonus = min(hp_pct_missing * 0.5, 0.30)
        base_phys  = int(base_phys  * (1 + bonus))
        base_magic = int(base_magic * (1 + bonus))
        if bonus > 0:
            logs.append(f"⚔️ Passif Guerrier : +{bonus*100:.1f}% dégâts")

    elif cls == "Assassin":
        # L'esquive est gérée côté défense (voir apply_enemy_attack)
        pass

    elif cls == "Mage":
        bonus = min(hp_pct_current * 0.5, 0.50)
        base_magic = int(base_magic * (1 + bonus))
        if bonus > 0:
            logs.append(f"🔮 Passif Mage : +{bonus*100:.1f}% dégâts magiques")

    elif cls == "Tireur":
        if random.random() < 0.25:
            base_phys  *= 2
            base_magic *= 2
            logs.append("🏹 Passif Tireur : **Double Coup !**")

    elif cls == "Support":
        if random.random() < 0.45:
            shield_val = int(ps.max_hp * 0.10)
            ps.shield += shield_val
            logs.append(f"🛡️ Passif Support : Bouclier +{shield_val:,} HP")

    elif cls == "Vampire":
        # Vol de vie appliqué après les dégâts (voir plus bas)
        pass

    elif cls == "Gardien du Temps":
        if random.random() < 0.55:
            all_stats = ["p_atk", "m_atk", "p_def", "m_def", "speed", "p_pen", "m_pen"]
            # Retirage forcé : on exclut les stats déjà capées à -20%
            uncapped = [s for s in all_stats if state.enemy_debuffs.get(s, 1.0) > 0.80]
            if uncapped:
                stat = random.choice(uncapped)
                current = state.enemy_debuffs.get(stat, 1.0)
                new_val = max(0.80, current - 0.05)
                state.enemy_debuffs[stat] = new_val
                logs.append(f"⏳ Passif Gardien du Temps : {STAT_FR.get(stat, stat)} ennemi −5% → {new_val*100:.0f}%")
                _apply_debuffs_to_enemy(state)

    elif cls == "Ombre Venin":
        if random.random() < 0.40 and state.enemy_poison_stacks < 10:
            state.enemy_poison_stacks += 1
            logs.append(f"☠️ Passif Ombre Venin : +1 stack poison ({state.enemy_poison_stacks} total)")

    elif cls == "Pyromancien":
        if random.random() < 0.45 and state.enemy_burns < 5:
            state.enemy_burns += 1
            logs.append(f"🔥 Passif Pyromancien : +1 stack brûlure ({state.enemy_burns} total)")

    elif cls == "Paladin":
        if random.random() < 0.50:
            stat_choices = ["p_atk", "m_atk", "p_def", "m_def", "p_pen", "m_pen", "speed"]
            # Mémorise les stats initiales au premier proc (référence fixe pour +5% et cap +20%)
            if not state.paladin_initial_stats:
                state.paladin_initial_stats = {s: getattr(ps, s, 0) for s in stat_choices}
            # Retirage forcé : on exclut les stats déjà capées à +20%
            uncapped = [s for s in stat_choices
                        if getattr(ps, s, 0) < state.paladin_initial_stats[s] * 1.2]
            if uncapped:
                stat = random.choice(uncapped)
                increase = max(1, int(state.paladin_initial_stats[stat] * 0.05))
                current = getattr(ps, stat, 0)
                setattr(ps, stat, current + increase)
                logs.append(f"✝️ Passif Paladin : {STAT_FR.get(stat, stat)} +{increase:,} → {current + increase:,}")

    return base_phys, base_magic, logs


def apply_player_post_attack(state: CombatState, total_dmg: int) -> list[str]:
    """Post-attaque : vol de vie, reliques, etc."""
    logs = []
    cls = state.player_class
    ps  = state.player_stats

    heal_reduce = next((d["value"] for d in state.spell_active_debuffs if d.get("type") == "heal_reduce"), 0)
    heal_mult = 1.0
    if state.boss_curse_healing and not state.ignore_enemy_passive:
        heal_mult *= 0.50
    if heal_reduce > 0:
        heal_mult *= (1 - heal_reduce)

    if cls == "Vampire" and state.spell_no_heal_turns <= 0:
        # Passif : 25% de chance de vol de vie (30%)
        if random.random() < 0.25:
            lifesteal = 0.30 + state.extra_lifesteal
            lifesteal += state.relic_effects.get("vol_vie", 0) / 100
            healed = int(total_dmg * lifesteal * heal_mult)
            healed = min(healed, int(ps.max_hp * 0.10))
            ps.hp = min(ps.max_hp, ps.hp + healed)
            logs.append(f"🧛 Passif Vol de Vie : +{healed:,} HP")
        elif state.extra_lifesteal > 0:
            healed = int(total_dmg * state.extra_lifesteal * heal_mult)
            if healed > 0:
                ps.hp = min(ps.max_hp, ps.hp + healed)
                logs.append(f"🧛 Vol de Vie (sort) : +{healed:,} HP")

    # Marque de Sang — vol de vie sur tous les dégâts si marque active
    if state.blood_mark_turns > 0 and total_dmg > 0 and state.spell_no_heal_turns <= 0:
        healed_bm = int(total_dmg * state.blood_mark_heal_pct * heal_mult)
        if healed_bm > 0:
            ps.hp = min(ps.max_hp, ps.hp + healed_bm)
            logs.append(f"🩸 Marque de Sang : +{healed_bm:,} HP")

    # Relique vol de vie générique
    if cls != "Vampire" and "vol_vie" in state.relic_effects and state.spell_no_heal_turns <= 0:
        lifesteal = state.relic_effects["vol_vie"] / 100
        healed = int(total_dmg * lifesteal * heal_mult)
        ps.hp = min(ps.max_hp, ps.hp + healed)
        if healed > 0:
            logs.append(f"💧 Relique Vol de Vie : +{healed:,} HP")

    return logs


def _apply_debuffs_to_enemy(state: CombatState):
    """Applique les debuffs du Gardien du Temps aux stats de l'ennemi."""
    for stat, factor in state.enemy_debuffs.items():
        base_val = state.enemy_data.get(stat, 0)
        if stat == "hp":
            continue  # On ne réduit pas le max_hp via debuff
        new_val = int(base_val * factor)
        setattr(state.enemy_stats, stat, max(1, new_val))


def _apply_boss_passif_init(state: CombatState) -> list[str]:
    """Applique les effets one-shot des passifs boss au début du combat (tour 1)."""
    passif = state.enemy_data.get("passif", "")
    if not passif or state.ignore_enemy_passive:
        state.boss_passif_init_done = True
        return []

    logs = []
    ps = state.player_stats
    es = state.enemy_stats

    # ── EMBLÉMATIQUES ──────────────────────────────────────────────────────
    if "Réduit toutes tes stats de 10%" in passif:
        for attr in ("p_atk", "m_atk", "p_def", "m_def", "p_pen", "m_pen", "speed"):
            setattr(ps, attr, max(1, int(getattr(ps, attr) * 0.90)))
        logs.append("🌑 Passif boss : Toutes tes stats sont réduites de **10%** !")

    elif "Maudit" in passif and "soins" in passif:
        state.boss_curse_healing = True
        logs.append("🩸 Passif boss : **Malédiction** — tes soins sont réduits de 50% !")

    elif "Aura glaciale" in passif:
        ps.speed = max(1, int(ps.speed * 0.80))
        logs.append("❄️ Passif boss : **Aura Glaciale** — ta vitesse est réduite de 20% !")

    # ── ANTIQUES ───────────────────────────────────────────────────────────
    elif "Fléau Primordial" in passif:
        for attr in ("p_atk", "m_atk", "p_def", "m_def", "p_pen", "m_pen", "speed"):
            setattr(ps, attr, max(1, int(getattr(ps, attr) * 0.85)))
        logs.append("☠️ Passif boss : **Fléau Primordial** — toutes tes stats sont réduites de 15% !")

    elif "Éternité" in passif:
        state.boss_eternity_active = True
        logs.append("⏳ Passif boss : **Éternité** — les HP du boss ne peuvent pas tomber sous 50% avant le tour 10 !")

    elif "Malédiction Antique" in passif:
        state.boss_no_player_crit = True
        logs.append("🔮 Passif boss : **Malédiction Antique** — tes critiques ne font pas de dégâts supplémentaires !")

    elif "Terreur Abyssale" in passif:
        ps.p_def = max(0, int(ps.p_def * 0.70))
        ps.m_def = max(0, int(ps.m_def * 0.70))
        logs.append("👁️ Passif boss : **Terreur Abyssale** — ta Défense Physique et Magique sont réduites de 30% !")

    elif "Néant" in passif and "passifs" in passif:
        state.boss_neant_active = True
        logs.append("🌀 Passif boss : **Néant** — tes passifs de classe sont désactivés pour les 3 premiers tours !")

    elif "Convergence" in passif:
        for attr in ("p_atk", "m_atk", "p_def", "m_def", "p_pen", "m_pen"):
            setattr(es, attr, int(getattr(es, attr) * 1.25))
        es.max_hp = int(es.max_hp * 1.25)
        es.hp     = es.max_hp
        logs.append("🌐 Passif boss : **Convergence** — le boss a absorbé les stats de ses ennemis (+25% à tout) !")

    state.boss_passif_init_done = True
    return logs


# ─── Tour du joueur ────────────────────────────────────────────────────────

def player_turn(state: CombatState) -> list[str]:
    """Effectue le tour du joueur et retourne le log."""
    logs = []
    ps = state.player_stats
    es = state.enemy_stats

    # Init passif boss (une seule fois au tour 1)
    if not state.boss_passif_init_done:
        logs.extend(_apply_boss_passif_init(state))

    passif = state.enemy_data.get("passif", "")
    ignore = state.ignore_enemy_passive

    # Emprise Temporelle : joueur saute son attaque tous les 5 tours
    if not ignore and "Emprise Temporelle" in passif and state.turn % 5 == 0:
        logs.append("⏳ Passif boss : **Emprise Temporelle** — ton tour est bloqué !")
        return logs

    # Régénération HP relique (début du tour)
    regen_hp_pct = state.relic_effects.get("regen_hp", 0)
    if regen_hp_pct > 0 and ps.hp > 0:
        regen_amt = int(ps.max_hp * regen_hp_pct / 100)
        if regen_amt > 0:
            ps.hp = min(ps.max_hp, ps.hp + regen_amt)
            logs.append(f"💚 Régénération Relique : +{regen_amt:,} HP")

    # Dévoration : le boss vole 3% de tes stats offensives à chaque tour
    if not ignore and "Dévoration" in passif:
        steal_atk  = max(0, int(ps.p_atk * 0.03))
        steal_matk = max(0, int(ps.m_atk * 0.03))
        ps.p_atk = max(1, ps.p_atk - steal_atk)
        ps.m_atk = max(1, ps.m_atk - steal_matk)
        es.p_atk += steal_atk
        es.m_atk += steal_matk
        if steal_atk > 0 or steal_matk > 0:
            logs.append(f"🕷️ Passif boss : **Dévoration** — -{steal_atk:,} ATK Phy / -{steal_matk:,} ATK Mag volés !")

    # Appliquer élixirs
    eff_p_atk = ps.p_atk
    eff_m_atk = ps.m_atk

    # Nombre d'attaques selon la vitesse
    ref = min(ps.speed, es.speed)
    attacks = math.floor(state.turn * ps.speed / max(ref, 1)) - math.floor((state.turn - 1) * ps.speed / max(ref, 1))
    attacks = max(1, attacks)

    total_damage = 0
    for _ in range(attacks):
        if es.hp <= 0:
            break
        phys  = calc_physical_damage(ps, es)
        magic = calc_magical_damage(ps, es)

        # Néant : passifs de classe désactivés les 3 premiers tours
        if not ignore and state.boss_neant_active and state.turn <= 3:
            passive_logs = []
        else:
            phys, magic, passive_logs = apply_player_passive(state, phys, magic)
        logs.extend(passive_logs)

        # Bonus relique dégâts
        if "bonus_dmg" in state.relic_effects:
            mult_r = 1 + state.relic_effects["bonus_dmg"] / 100
            phys  = int(phys  * mult_r)
            magic = int(magic * mult_r)

        # Bonus sort (Marquage Tireur, etc.)
        if state.spell_damage_amp != 1.0:
            phys  = int(phys  * state.spell_damage_amp)
            magic = int(magic * state.spell_damage_amp)

        # Critique (Malédiction Antique : crits sans bonus de dégâts)
        combined = phys + magic
        if not ignore and state.boss_no_player_crit:
            is_crit = False  # crit_chance toujours 0 effet
        else:
            combined, is_crit = apply_crit(combined, ps.crit_chance, ps.crit_damage)

        # Immunité aux critiques ennemi (5 premiers tours, emblématique)
        if not ignore and "Immunité aux critiques" in passif and state.turn <= 5:
            is_crit = False
            combined = phys + magic  # annule le bonus critique déjà appliqué

        # Casque donjon : réduit les dégâts critiques reçus de crit_dmg_reduction_pct
        crit_red = state.boss_passif_effects.get("crit_dmg_reduction_pct", 0)
        if is_crit and crit_red > 0:
            pre_crit = phys + magic
            crit_bonus = combined - pre_crit
            combined = pre_crit + int(crit_bonus * (1 - crit_red))

        # Bonus ennemi marqué (Tireur S3)
        if state.enemy_marked and state.enemy_marked_pct > 0:
            mark_bonus = 1 + state.enemy_marked_pct / 100
            combined = int(combined * mark_bonus)

        # Stacks de poison (Ombre Venin) : +35% m_atk par stack (dégâts purs, ignore def)
        if state.player_class == "Ombre Venin" and state.enemy_poison_stacks > 0:
            poison_bonus = int(ps.m_atk * 0.35 * state.enemy_poison_stacks)
            combined += poison_bonus

        # Bouclier Ancien (antique) : absorbe 30% des 5 premiers tours
        if not ignore and "Bouclier Ancien" in passif and state.turn <= 5:
            combined = int(combined * 0.70)

        # Esquive boss (Assassin passif)
        dodge = state.boss_passif_effects.get("dodge_pct", 0)
        if dodge > 0 and random.random() < dodge:
            logs.append("💨 L'ennemi esquive l'attaque !")
            continue  # skip this attack

        # Amulette donjon : renvoie dmg_reflect_pct des dégâts reçus en dégâts purs
        reflect_pct = state.boss_passif_effects.get("dmg_reflect_pct", 0)
        if reflect_pct > 0:
            reflect_pure = int(combined * reflect_pct)
            apply_damage_to_target(ps, reflect_pure)
            if reflect_pure > 0:
                logs.append(f"📿 Renvoi Mystique : **{reflect_pure:,}** dégâts purs en retour → {ps.hp:,} HP")

        dmg_done = apply_damage_to_target(es, combined)
        total_damage += dmg_done

        # Résurrection Ignareth (boss raid) : si boss tombe à 0, ressuscite à 25% une fois
        if es.hp <= 0 and state.raid_boss_resurrected:
            state.raid_boss_resurrected = False  # consume the resurrection
            es.hp = max(1, int(es.max_hp * 0.25))
            logs.append(f"🔥 **Résurrection du Phénix !** Ignareth ressuscite à **{es.hp:,}** HP !")

        # Éternité : HP ennemi plancher 50% avant tour 10
        if not ignore and state.boss_eternity_active and state.turn < 10:
            floor_hp = int(es.max_hp * 0.50)
            if es.hp < floor_hp:
                es.hp = floor_hp

        # Absorption (emblématique) : 20% des dégâts reçus → bouclier ennemi
        if not ignore and "Absorption" in passif and dmg_done > 0:
            es.shield = min(es.max_hp, es.shield + int(dmg_done * 0.20))

        # Riposte (emblématique) : 30% des dégâts physiques renvoyés au joueur
        if not ignore and "Riposte" in passif and phys > 0:
            riposte_dmg = int(phys * 0.30)
            apply_damage_to_target(ps, riposte_dmg)
            logs.append(f"🔄 Passif boss : **Riposte** — {riposte_dmg:,} dégâts renvoyés → {ps.hp:,} HP")

        crit_txt = " ✨CRITIQUE!" if is_crit else ""
        logs.append(f"🗡️ Tu attaques pour **{combined:,}** dégâts{crit_txt}")

    # Double frappe relique (chance de répéter une attaque normale)
    double_frappe_pct = state.relic_effects.get("double_frappe", 0)
    if double_frappe_pct > 0 and es.hp > 0 and random.random() < double_frappe_pct / 100:
        phys  = calc_physical_damage(ps, es)
        magic = calc_magical_damage(ps, es)
        phys, magic, _ = apply_player_passive(state, phys, magic)
        if state.player_class == "Paladin":
            phys  = int(phys  * (1 + state.paladin_ramp_dmg_amp))
            magic = int(magic * (1 + state.paladin_ramp_dmg_amp))
        if "bonus_dmg" in state.relic_effects:
            mult_r = 1 + state.relic_effects["bonus_dmg"] / 100
            phys  = int(phys  * mult_r)
            magic = int(magic * mult_r)
        if state.spell_damage_amp != 1.0:
            phys  = int(phys  * state.spell_damage_amp)
            magic = int(magic * state.spell_damage_amp)
        combined_df = phys + magic
        combined_df, is_crit_df = apply_crit(combined_df, ps.crit_chance, ps.crit_damage)
        dmg_df = apply_damage_to_target(es, combined_df)
        total_damage += dmg_df
        crit_txt_df = " ✨CRITIQUE!" if is_crit_df else ""
        logs.append(f"⚡ Double Frappe (relique) : **{combined_df:,}** dégâts{crit_txt_df}")

    # Post-attaque
    logs.extend(apply_player_post_attack(state, total_damage))

    # DoTs sur l'ennemi
    if state.enemy_burns > 0:
        burn_dmg = int(ps.m_atk * 0.15 * state.enemy_burns * state.spell_dot_amp)
        es.hp = max(0, es.hp - burn_dmg)
        logs.append(f"🔥 Brûlure ({state.enemy_burns} stacks) : **-{burn_dmg:,}** HP ennemi")

    # Saignée (Assassin set Voile de Sang)
    if state.player_bleed:
        bleed_dmg = int(es.max_hp * 0.02)
        es.hp = max(0, es.hp - bleed_dmg)
        state.player_bleed = False
        logs.append(f"🩸 Saignée : **-{bleed_dmg:,}** HP ennemi")

    return logs


# ─── Sort de boss ──────────────────────────────────────────────────────────

def _apply_boss_spell(state: CombatState) -> list[str]:
    """Déclenche un sort de boss selon le compteur de tours."""
    logs = []
    boss_spells = state.enemy_data.get("boss_spells", [])
    spell_mod   = state.boss_spell_turn_mod
    if not boss_spells or spell_mod <= 0:
        return logs

    state.boss_spell_turn_counter += 1
    if state.boss_spell_turn_counter % spell_mod != 0:
        return logs

    spell_idx = (state.boss_spell_turn_counter // spell_mod - 1) % len(boss_spells)
    spell_key  = boss_spells[spell_idx]

    # Sorts custom (boss de raid) prioritaires sur CLASS_SPELLS
    custom_spells = state.enemy_data.get("boss_custom_spells", {})
    if custom_spells:
        spell_data = custom_spells.get(spell_key)
    else:
        cls_key    = state.enemy_data.get("boss_spell_cls_key", "")
        spell_data = CLASS_SPELLS.get(cls_key, {}).get(spell_key) if cls_key else None

    if not spell_data:
        return logs

    ps      = state.player_stats
    es      = state.enemy_stats
    effects = spell_data.get("effects", {})
    logs.append(f"{spell_data['emoji']} **{spell_data['name']}** *(sort ennemi)* !")

    # ── Purge de tous les debuffs sur le boss (ultime)
    if effects.get("purge_self"):
        state.enemy_burns         = 0
        state.enemy_poison_stacks = 0
        state.enemy_marked        = False
        state.enemy_marked_turns  = 0
        state.spell_active_debuffs = []
        state.enemy_debuffs       = {}
        state.enemy_stun          = 0
        logs.append("🌀 **Purge** — tous les effets négatifs sont dissipés !")

    # ── Buff offensif temporaire (Vorgath Rage Ancienne)
    if effects.get("self_dmg_buff", 0) > 0:
        buff_pct   = effects["self_dmg_buff"]
        buff_turns = effects.get("self_dmg_buff_turns", 3)
        state.spell_active_buffs.append({"type": "enemy_dmg_amp", "value": buff_pct, "turns": buff_turns})
        logs.append(f"💢 Buff offensif : +{int(buff_pct*100)}% dégâts pendant {buff_turns} tours !")

    # ── Dégâts AoE
    dmg_mult = effects.get("dmg_mult", 0)
    if dmg_mult > 0:
        active_amp = sum(b["value"] for b in state.spell_active_buffs if b.get("type") == "enemy_dmg_amp")
        if active_amp > 0:
            dmg_mult = dmg_mult * (1 + active_amp)

        if effects.get("magic"):
            raw = max(1, int(es.m_atk * dmg_mult - ps.m_def))
        else:
            raw = max(1, int(es.p_atk * dmg_mult - ps.p_def))

        # Bonus si joueur marqué (Karek Salve Finale)
        if effects.get("dmg_mult_if_marked") and state.enemy_marked:
            raw = int(raw * effects["dmg_mult_if_marked"])
            logs.append("🎯 Cible marquée — dégâts amplifiés !")

        raw, is_crit = apply_crit(raw, es.crit_chance, es.crit_damage)

        ls = effects.get("lifesteal_pct", 0) or state.boss_passif_effects.get("lifesteal_pct", 0)
        if ls > 0:
            heal = int(raw * ls)
            es.hp = min(es.max_hp, es.hp + heal)
            if heal > 0:
                logs.append(f"🩸 Vol de vie : +{heal:,} HP ennemi")

        apply_damage_to_target(ps, raw)
        crit_txt = " ✨CRITIQUE!" if is_crit else ""
        logs.append(f"💥 Dégâts sort : **{raw:,}**{crit_txt}")

    # ── Soin boss
    if effects.get("heal_pct", 0) > 0:
        heal = int(es.max_hp * effects["heal_pct"])
        es.hp = min(es.max_hp, es.hp + heal)
        logs.append(f"💚 Soin (sort) : **+{heal:,}** HP ennemi")

    # ── Drain joueur (Serath)
    if effects.get("drain_pct", 0) > 0:
        drain = int(ps.max_hp * effects["drain_pct"])
        apply_damage_to_target(ps, drain)
        es.hp = min(es.max_hp, es.hp + drain)
        if drain > 0:
            logs.append(f"⬛ Drain : **-{drain:,}** HP joueur, +{drain:,} HP ennemi")

    # ── Réduction soins joueur (Serath)
    if effects.get("heal_reduce", 0) > 0:
        state.spell_active_debuffs.append({"type": "heal_reduce", "value": effects["heal_reduce"], "turns": 3})
        logs.append(f"🩸 Malédiction : soins réduits de {int(effects['heal_reduce']*100)}% pendant 3 tours")

    # ── Marquage du joueur (Karek)
    if effects.get("mark_player", 0) > 0:
        state.enemy_marked       = True
        state.enemy_marked_pct   = effects["mark_player"]
        state.enemy_marked_turns = 2
        logs.append(f"🎯 Joueur marqué : +{effects['mark_player']}% dégâts reçus pendant 2 tours")

    # ── Annulation des buffs joueur (Chronovex)
    if effects.get("cancel_player_buffs"):
        state.spell_active_buffs = []
        logs.append("♾️ Tous tes buffs actifs sont annulés !")

    # ── DoT brûlure sur joueur (Ignareth)
    if effects.get("dot_player_burn", 0) > 0:
        state.player_burn_stacks = min(10, state.player_burn_stacks + effects["dot_player_burn"])
        logs.append(f"🔥 {effects['dot_player_burn']} stacks de brûlure appliqués !")

    # ── Résurrection unique boss (Ignareth)
    if effects.get("resurrection_25") and not state.raid_boss_resurrected:
        state.raid_boss_resurrected = True
        logs.append("🔥 **Résurrection du Phénix** — Ignareth ressuscitera à 25% HP !")

    # ── Debuffs stats joueur
    if "stat_debuff" in effects:
        for stat, pct in effects["stat_debuff"].items():
            cur = getattr(ps, stat, 0)
            if cur > 0:
                setattr(ps, stat, max(0, int(cur * (1 - pct / 100))))
        logs.append("📉 Stat(s) joueur réduites par le sort ennemi")

    return logs


# ─── Tour de l'ennemi ──────────────────────────────────────────────────────

def enemy_turn(state: CombatState) -> list[str]:
    """Effectue le tour de l'ennemi et retourne le log."""
    logs = []
    ps = state.player_stats
    es = state.enemy_stats

    pe = state.boss_passif_effects

    # Regen boss (Support passif)
    if pe.get("heal_per_turn_pct", 0) > 0:
        heal = int(es.max_hp * pe["heal_per_turn_pct"])
        es.hp = min(es.max_hp, es.hp + heal)
        logs.append(f"💚 Régénération boss : +{heal:,} HP")

    # Drain joueur (Vampire antique)
    if pe.get("drain_player_pct", 0) > 0:
        drain = int(ps.max_hp * pe["drain_player_pct"])
        apply_damage_to_target(ps, drain)
        es.hp = min(es.max_hp, es.hp + drain)
        if drain > 0:
            logs.append(f"🧛 Drain Vampirique : -{drain:,} HP joueur, +{drain:,} HP ennemi")

    # Dégâts purs périodiques (Mage / Paladin antique)
    if pe.get("pure_dmg_interval", 0) > 0:
        state.boss_pure_dmg_counter += 1
        if state.boss_pure_dmg_counter % pe["pure_dmg_interval"] == 0:
            pure = int(es.max_hp * pe["pure_dmg_pct"])
            apply_damage_to_target(ps, pure)
            logs.append(f"⚡ Dégâts Purs (passif) : **{pure:,}**")

    if state.is_over:
        return logs

    if state.enemy_stun > 0:
        if pe.get("stun_immune", False):
            state.enemy_stun = 0
            logs.append("🛡️ L'ennemi est immunisé aux étourdissements !")
        else:
            state.enemy_stun -= 1
            logs.append("💫 L'ennemi est étourdi et ne peut pas agir !")
            return logs

    ref = min(ps.speed, es.speed)
    attacks = math.floor(state.turn * es.speed / max(ref, 1)) - math.floor((state.turn - 1) * es.speed / max(ref, 1))
    attacks = max(1, attacks)

    # Chaussures donjon : 20% de chance d'attaquer deux fois
    if pe.get("double_attack_chance", 0) > 0 and random.random() < pe["double_attack_chance"]:
        attacks += 1
        logs.append("⚡ Foulée Redoublée : l'ennemi attaque **deux fois** !")

    # Anneau donjon : +3% dégâts par tour (max 10 stacks)
    ramp_per = pe.get("dmg_ramp_per_turn", 0)
    if ramp_per > 0:
        max_stacks = int(pe.get("dmg_ramp_max_stacks", 10))
        state.boss_dmg_ramp_stacks = min(max_stacks, state.boss_dmg_ramp_stacks + 1)
        if state.boss_dmg_ramp_stacks > 0:
            logs.append(f"💍 Empowerment Runique : stack {state.boss_dmg_ramp_stacks}/{max_stacks} (+{int(state.boss_dmg_ramp_stacks*ramp_per*100)}% dégâts)")
    ramp_mult = 1.0 + state.boss_dmg_ramp_stacks * ramp_per

    for _ in range(attacks):
        if ps.hp <= 0:
            break

        # Esquive sort (Disparaître)
        if state.spell_dodge_next:
            state.spell_dodge_next = False
            logs.append("🌫️ L'ennemi attaque… **Esquivé (sort) !**")
            continue

        # Esquive Assassin passif (double si double_dodge_next actif)
        if state.player_class == "Assassin":
            dodge_chance = 0.40 if state.spell_double_dodge_next else 0.20
            if random.random() < dodge_chance:
                state.spell_double_dodge_next = False
                logs.append("🗡️ L'ennemi attaque… **Esquivé !**")
                continue
            state.spell_double_dodge_next = False

        phys  = calc_physical_damage(es, ps)
        magic = calc_magical_damage(es, ps)
        combined = phys + magic

        # Passif ennemi spéciaux
        passif = state.enemy_data.get("passif", "")

        if not state.ignore_enemy_passive and passif:
            # Regen — emblématique 2% / Résilience Ancienne 5%
            if "Régénère" in passif and "HP max" in passif:
                heal = int(es.max_hp * 0.02)
                es.hp = min(es.max_hp, es.hp + heal)
                logs.append(f"💚 Passif boss : **Régénération** +{heal:,} HP ennemi")
            elif "Résilience Ancienne" in passif:
                heal = int(es.max_hp * 0.05)
                es.hp = min(es.max_hp, es.hp + heal)
                logs.append(f"💚 Passif boss : **Résilience Ancienne** +{heal:,} HP ennemi")

            # Dégâts purs (emblématique 3 — 5% HP max)
            if "dégâts purs" in passif and "HP max" in passif:
                pure_dmg = int(ps.max_hp * 0.05)
                apply_damage_to_target(ps, pure_dmg)
                logs.append(f"💀 Passif boss : **Dégâts Purs** — {pure_dmg:,} dégâts ignorant toute défense → {ps.hp:,} HP")

            # Les 3 premiers tours, dégâts doublés
            if "premiers tours, dégâts doublés" in passif and state.turn <= 3:
                combined = int(combined * 1.5)
                logs.append(f"💢 Passif boss : **Frénésie** — dégâts ×1.5 ! (tour {state.turn}/3)")

            # Enragé : +10% dégâts par 20% HP perdus
            if "Enragé" in passif:
                hp_lost_pct = (es.max_hp - es.hp) / max(es.max_hp, 1)
                stages = int(hp_lost_pct / 0.20)
                if stages > 0:
                    combined = int(combined * (1 + 0.10 * stages))
                    logs.append(f"😡 Passif boss : **Enragé** ×{stages} (+{stages*10}% dégâts)")

        # Critique ennemi
        combined, is_crit = apply_crit(combined, es.crit_chance, es.crit_damage)

        # Passif enrage (Guerrier)
        enrage_per = pe.get("enrage_per_25pct", 0)
        if enrage_per > 0:
            hp_lost_pct = 1.0 - es.hp / max(es.max_hp, 1)
            enrage_stacks = int(hp_lost_pct / 0.25)
            enrage_bonus = min(pe.get("enrage_max", 0), enrage_stacks * enrage_per)
            if enrage_bonus > 0:
                combined = int(combined * (1 + enrage_bonus))

        # Passif ignore_mdef — bonus dégâts basé sur la def mag ignorée (Mage ou arme donjon)
        ignore_mdef = pe.get("ignore_mdef_pct", 0)
        if ignore_mdef > 0:
            combined += int(ps.m_def * ignore_mdef)

        # Passif ignore_pdef — bonus dégâts basé sur la def phys ignorée (arme donjon)
        ignore_pdef = pe.get("ignore_pdef_pct", 0)
        if ignore_pdef > 0:
            combined += int(ps.p_def * ignore_pdef)

        # Anneau donjon : ramp dégâts cumulé par tour
        if ramp_mult > 1.0:
            combined = int(combined * ramp_mult)

        # Renvoi de dégâts (sort Support ult — appliqué avant la réduction)
        if state.spell_reflect_pct > 0 and state.spell_reflect_turns > 0:
            reflect_spell = int(combined * state.spell_reflect_pct)
            es.hp = max(0, es.hp - reflect_spell)
            combined = max(1, combined - reflect_spell)
            if reflect_spell > 0:
                logs.append(f"🪞 Renvoi Sacré : **{reflect_spell:,}** dégâts renvoyés à l'ennemi")

        # Réduction dégâts sort (Barrière, Écran Magique, etc.)
        if state.spell_damage_reduction > 0:
            combined = int(combined * (1 - state.spell_damage_reduction))

        # Réduction dégâts reliques
        if "reduction_dmg" in state.relic_effects:
            combined = int(combined * (1 - state.relic_effects["reduction_dmg"] / 100))

        # Renvoi de dégâts (relique)
        if "reflet" in state.relic_effects:
            reflect_dmg = int(combined * state.relic_effects["reflet"] / 100)
            es.hp = max(0, es.hp - reflect_dmg)
            if reflect_dmg > 0:
                logs.append(f"🪞 Renvoi : **-{reflect_dmg:,}** HP ennemi")

        hp_before = ps.hp
        apply_damage_to_target(ps, combined)
        actual_dmg = hp_before - ps.hp
        state.last_enemy_damage = max(state.last_enemy_damage, actual_dmg)

        # Lifesteal boss (Vampire)
        ls = pe.get("lifesteal_pct", 0)
        if ls > 0 and combined > 0:
            heal_ls = int(combined * ls)
            es.hp = min(es.max_hp, es.hp + heal_ls)

        # Contre-Attaque (Guerrier S2) — riposte après avoir reçu un coup
        if state.contre_attaque_turns > 0 and actual_dmg > 0 and es.hp > 0:
            ca_phys  = calc_physical_damage(ps, es)
            ca_magic = calc_magical_damage(ps, es)
            ca_dmg   = ca_phys + ca_magic
            apply_damage_to_target(es, ca_dmg)
            logs.append(f"🔄 Contre-Attaque : **{ca_dmg:,}** dégâts en retour → ennemi {es.hp:,} HP")

        # Rage gagnée sur coup reçu (Guerrier, Paladin, Vampire)
        cls_key = _class_to_spell_key(state.player_class)
        if cls_key:
            on_hit = CLASS_SPELLS.get(cls_key, {}).get("resource_on_hit", 0)
            if on_hit > 0:
                resource_max = CLASS_SPELLS[cls_key].get("resource_max", 100)
                state.player_resource = min(resource_max, state.player_resource + on_hit)

        # Résurrection (sort Support ou potion)
        if ps.hp <= 0 and state.spell_resurrection:
            if state.resurrection_hp_pct > 0:
                ps.hp = int(ps.max_hp * state.resurrection_hp_pct)
            else:
                ps.hp = 1
            state.spell_resurrection = False
            hp_txt = f"{ps.hp:,} HP" if state.resurrection_hp_pct > 0 else "1 HP"
            logs.append(f"🌟 **Résurrection !** Vous survivez avec {hp_txt} !")

        # Indestructible (Guerrier ult)
        if ps.hp <= 0 and state.undying_turns > 0:
            ps.hp = 1
            state.undying_turns -= 1
            logs.append("💢 Indestructible ! Survie à 1 PV !")

        crit_txt = " ✨CRITIQUE!" if is_crit else ""
        logs.append(f"💢 L'ennemi attaque pour **{combined:,}** dégâts{crit_txt} → **{ps.hp:,}/{ps.max_hp:,}** HP")

    # Sort de boss
    if not state.is_over:
        spell_logs = _apply_boss_spell(state)
        logs.extend(spell_logs)
        if state.is_over:
            return logs

    return logs


# ─── Combat complet ────────────────────────────────────────────────────────

def run_full_combat(
    player_data: dict,
    enemy_data:  dict,
    equipment_list: list[dict],
    relics: list[dict],
    current_hp: int | None = None,
    elixir: dict = None,
) -> dict:
    """
    Lance un combat complet (automatique, pour le mode monde classique).
    Retourne un dict avec :
      - won: bool
      - player_hp_remaining: int
      - turns: int
      - log: list[str]
      - damage_dealt: int (total dégâts sur l'ennemi)
    """
    from bot.cogs.rpg.models import compute_total_stats, compute_max_hp
    from bot.cogs.rpg.models import get_set_bonus

    # Stats totales du joueur
    set_bonus = get_set_bonus(equipment_list)
    total_stats = compute_total_stats(
        player_data["class"], player_data["level"], player_data["prestige_level"],
        equipment_list, set_bonus["stats"]
    )
    if elixir:
        for k, v in elixir.items():
            if k in total_stats:
                total_stats[k] = int(total_stats[k] * (1 + v / 100))

    relic_effects = compute_relic_effects(relics) if relics else {}

    ps = CombatStats.from_dict(total_stats)
    max_hp = compute_max_hp(total_stats)
    ps.max_hp = max_hp
    ps.hp = min(max_hp, current_hp if current_hp is not None else max_hp)

    es = CombatStats.from_dict(enemy_data)
    es.max_hp = es.hp

    state = CombatState(
        player_stats  = ps,
        enemy_stats   = es,
        player_class  = player_data["class"],
        enemy_data    = enemy_data,
        relic_effects = relic_effects,
    )

    full_log = []
    max_turns = 200
    total_damage = 0
    prev_enemy_hp = es.hp

    while not state.is_over and state.turn < max_turns:
        state.turn += 1
        full_log.append(f"— **Tour {state.turn}** —")

        p_logs = player_turn(state)
        full_log.extend(p_logs)
        total_damage += prev_enemy_hp - state.enemy_stats.hp
        prev_enemy_hp = state.enemy_stats.hp

        if not state.is_over:
            e_logs = enemy_turn(state)
            full_log.extend(e_logs)

    if state.turn >= max_turns and not state.is_over:
        full_log.append("⏰ Temps écoulé — combat nul !")

    return {
        "won":                state.player_won,
        "player_hp_remaining":state.player_stats.hp,
        "player_max_hp":      state.player_stats.max_hp,
        "turns":              state.turn,
        "log":                full_log,
        "damage_dealt":       total_damage,
    }


# ─── Système de sorts ──────────────────────────────────────────────────────

_CLASS_KEY_MAP = {
    "Guerrier":        "guerrier",
    "Assassin":        "assassin",
    "Mage":            "mage",
    "Tireur":          "tireur",
    "Support":         "support",
    "Vampire":         "vampire",
    "Gardien du Temps":"gardien_du_temps",
    "Ombre Venin":     "ombre_venin",
    "Pyromancien":     "pyromancien",
    "Paladin":         "paladin",
}


def _class_to_spell_key(player_class: str) -> str:
    return _CLASS_KEY_MAP.get(player_class, "")


def tick_player_side(state: CombatState) -> list[str]:
    """Appelé avant l'action du joueur : regen ressource, cooldowns, expiration buffs joueur."""
    logs = []
    cls_key = _class_to_spell_key(state.player_class)
    spell_data = CLASS_SPELLS.get(cls_key, {}) if cls_key else {}

    # Régénération de ressource
    regen = spell_data.get("resource_per_turn", 0)
    resource_max = spell_data.get("resource_max", 100)
    if regen > 0:
        state.player_resource = min(resource_max, state.player_resource + regen)

    # Décrément des cooldowns
    for sk in list(state.spell_cooldowns):
        if state.spell_cooldowns[sk] > 0:
            state.spell_cooldowns[sk] -= 1

    # Décrément no_heal_turns
    if state.spell_no_heal_turns > 0:
        state.spell_no_heal_turns -= 1

    # Expiration buffs joueur
    new_buffs = []
    for buff in state.spell_active_buffs:
        buff["turns"] -= 1
        if buff["turns"] <= 0:
            btype = buff["type"]
            if btype == "stat":
                setattr(state.player_stats, buff["stat"], buff["original"])
            elif btype == "damage_amp":
                state.spell_damage_amp = 1.0
            elif btype == "damage_reduction":
                state.spell_damage_reduction = 0.0
            elif btype == "dot_amp":
                state.spell_dot_amp = 1.0
            # enemy_dmg_amp expire silencieusement (buff offensif boss raid)
        else:
            new_buffs.append(buff)
    state.spell_active_buffs = new_buffs

    # Décrément extra_lifesteal
    if state.extra_lifesteal_turns > 0:
        state.extra_lifesteal_turns -= 1
        if state.extra_lifesteal_turns == 0:
            state.extra_lifesteal = 0.0

    # Décrément undying_turns (Guerrier ult)
    if state.undying_turns > 0:
        state.undying_turns -= 1

    # Décrément contre_attaque_turns (Guerrier S2)
    if state.contre_attaque_turns > 0:
        state.contre_attaque_turns -= 1

    # Décrément blood_mark_turns (Vampire S2)
    if state.blood_mark_turns > 0:
        state.blood_mark_turns -= 1
        if state.blood_mark_turns == 0:
            state.blood_mark_heal_pct = 0.0

    # Décrément spell_reflect_turns (Support ult)
    if state.spell_reflect_turns > 0:
        state.spell_reflect_turns -= 1
        if state.spell_reflect_turns == 0:
            state.spell_reflect_pct = 0.0

    # DoT brûlure reçus par le joueur (boss raid Ignareth)
    if state.player_burn_stacks > 0:
        burn_dmg = int(state.player_stats.max_hp * 0.02 * state.player_burn_stacks)
        if burn_dmg > 0:
            state.player_stats.hp = max(0, state.player_stats.hp - burn_dmg)
            logs.append(f"🔥 Brûlure ({state.player_burn_stacks} stacks) : **-{burn_dmg:,}** HP")
        # Décrémentation : -1 stack par tour ennemi
        state.player_burn_stacks = max(0, state.player_burn_stacks - 1)

    return logs


def tick_enemy_side(state: CombatState) -> list[str]:
    """Appelé avant le tour de l'ennemi : expiration debuffs ennemis."""
    logs = []

    # Expiration debuffs ennemi
    new_debuffs = []
    for debuff in state.spell_active_debuffs:
        debuff["turns"] -= 1
        if debuff["turns"] <= 0:
            dtype = debuff["type"]
            if dtype == "stat":
                setattr(state.enemy_stats, debuff["stat"], debuff["original"])
            elif dtype == "speed":
                state.enemy_stats.speed = debuff["original_speed"]
        else:
            new_debuffs.append(debuff)
    state.spell_active_debuffs = new_debuffs

    # Décrément enemy_marked (Tireur)
    if state.enemy_marked_turns > 0:
        state.enemy_marked_turns -= 1
        if state.enemy_marked_turns == 0:
            state.enemy_marked = False
            state.enemy_marked_pct = 0

    return logs


# Alias de compatibilité (si des modules externes appellent encore tick_spell_effects)
def tick_spell_effects(state: CombatState) -> list[str]:
    logs = tick_player_side(state)
    logs.extend(tick_enemy_side(state))
    return logs


def format_status_effects(state: "CombatState") -> str:
    """Retourne une chaîne compacte des effets actifs (buffs joueur + debuffs ennemi).
    Renvoie '' si aucun effet actif."""
    parts = []

    # ── Buffs joueur ──
    for b in state.spell_active_buffs:
        label = b.get("label", b["type"])
        parts.append(f"{label} *({b['turns']}t)*")
    if state.undying_turns > 0:
        parts.append(f"🛡️ Indestructible *({state.undying_turns}t)*")
    if state.extra_lifesteal > 0 and state.extra_lifesteal_turns > 0:
        parts.append(f"🩸 Vol de vie +{state.extra_lifesteal * 100:.0f}% *({state.extra_lifesteal_turns}t)*")
    if state.spell_no_heal_turns > 0:
        parts.append(f"🦇 Sans soin *({state.spell_no_heal_turns}t)*")
    if state.spell_dodge_next:
        parts.append("💨 Esquive prête")
    if state.spell_double_dodge_next:
        parts.append("💨💨 Double esquive prête")
    if state.contre_attaque_turns > 0:
        parts.append(f"⚔️ Contre-attaque *({state.contre_attaque_turns}t)*")
    if state.blood_mark_turns > 0:
        parts.append(f"🩸 Marque de sang *({state.blood_mark_turns}t)*")
    if state.spell_reflect_turns > 0:
        parts.append(f"🔰 Renvoi sacré *({state.spell_reflect_turns}t)*")

    # ── Debuffs ennemi ──
    for d in state.spell_active_debuffs:
        label = d.get("label", d["type"])
        parts.append(f"{label} *({d['turns']}t)*")
    if state.enemy_marked:
        parts.append(f"🎯 Ennemi marqué +{state.enemy_marked_pct}% *({state.enemy_marked_turns}t)*")
    if state.enemy_poison_stacks > 0:
        amp_txt = f" → +{int(state.enemy_poison_stacks * 12)}% dégâts" if state.player_class == "Ombre Venin" else ""
        parts.append(f"☠️ Poison {state.enemy_poison_stacks} stacks{amp_txt}")
    if state.enemy_stun > 0:
        parts.append(f"💫 Ennemi étourdi *({state.enemy_stun}t)*")

    return "\n".join(parts)


def apply_spell(state: CombatState, spell_key: str) -> dict:
    """
    Applique un sort du joueur. spell_key : 's1' | 's2' | 'ultimate'
    Retourne {success: bool, log: list[str]}
    """
    cls_key = _class_to_spell_key(state.player_class)
    if not cls_key:
        return {"success": False, "log": ["❌ Classe inconnue pour les sorts"]}

    spell_data = CLASS_SPELLS.get(cls_key, {})
    spell = spell_data.get(spell_key)
    if not spell:
        return {"success": False, "log": ["❌ Sort inconnu"]}

    cost      = spell["cost"]
    cooldown  = spell["cooldown"]
    min_turn  = spell["min_turn"]
    resource_name = spell_data.get("resource", "ressource")
    resource_max  = spell_data.get("resource_max", 100)

    if state.turn < min_turn:
        return {"success": False, "log": [f"❌ Sort utilisable à partir du tour {min_turn}"]}
    if state.spell_cooldowns.get(spell_key, 0) > 0:
        cd = state.spell_cooldowns[spell_key]
        return {"success": False, "log": [f"❌ Sort en recharge ({cd} tour(s))"]};
    if state.player_resource < cost:
        return {"success": False, "log": [f"❌ Pas assez de {resource_name} ({state.player_resource}/{cost})"]}

    # Déduction ressource + cooldown
    state.player_resource -= cost
    if cooldown > 0:
        state.spell_cooldowns[spell_key] = cooldown

    logs = [f"{spell['emoji']} **{spell['name']}** !"]
    effects = spell.get("effects", {})
    ps = state.player_stats
    es = state.enemy_stats

    # ── Sacrifice HP (Guerrier S1, Vampire S2) ─────────────────────────────
    if "self_damage_pct" in effects:
        self_dmg = int(ps.max_hp * effects["self_damage_pct"])
        ps.hp = max(1, ps.hp - self_dmg)
        logs.append(f"💔 Sacrifice : -{self_dmg:,} HP propres ({ps.hp:,}/{ps.max_hp:,} restants)")

    # ── Dégâts Support dual-type (physiques + magiques) ─────────────────────
    if effects.get("dual_type", False) and "dmg_mult" in effects:
        dmg_mult = effects["dmg_mult"]
        eff_pdef = max(0, es.p_def - ps.p_pen)
        eff_mdef = max(0, es.m_def - ps.m_pen)
        phys_part  = max(1, int(ps.p_atk * dmg_mult - eff_pdef))
        magic_part = max(1, int(ps.m_atk * dmg_mult - eff_mdef))
        dual_dmg   = phys_part + magic_part
        dual_dmg, is_crit_dual = apply_crit(dual_dmg, ps.crit_chance, ps.crit_damage)
        if state.enemy_marked and state.enemy_marked_pct > 0:
            dual_dmg = int(dual_dmg * (1 + state.enemy_marked_pct / 100))
        if "bonus_dmg" in state.relic_effects:
            dual_dmg = int(dual_dmg * (1 + state.relic_effects["bonus_dmg"] / 100))
        apply_damage_to_target(es, dual_dmg)
        crit_txt = " ✨CRITIQUE!" if is_crit_dual else ""
        logs.append(f"⚡ Dégâts (Phy+Mag) : **{dual_dmg:,}**{crit_txt}")
        # Marque de Sang après dégâts dual
        if state.blood_mark_turns > 0 and dual_dmg > 0 and state.spell_no_heal_turns <= 0:
            healed_bm = int(dual_dmg * state.blood_mark_heal_pct)
            if healed_bm > 0:
                ps.hp = min(ps.max_hp, ps.hp + healed_bm)
                logs.append(f"🩸 Marque de Sang : +{healed_bm:,} HP")

    # ── Exécution scalante (Assassin ult) ────────────────────────────────────
    elif effects.get("execute_scaling", False):
        enemy_hp_pct = es.hp / max(es.max_hp, 1)
        base_m = effects.get("execute_base_mult", 2.0)
        max_m  = effects.get("execute_max_mult", 5.0)
        exec_mult = base_m + (max_m - base_m) * (1 - enemy_hp_pct)
        eff_def = max(0, es.p_def - ps.p_pen)
        exec_dmg = max(1, int(ps.p_atk * exec_mult - eff_def))
        exec_dmg, is_crit_ex = apply_crit(exec_dmg, ps.crit_chance, ps.crit_damage)
        if state.enemy_marked and state.enemy_marked_pct > 0:
            exec_dmg = int(exec_dmg * (1 + state.enemy_marked_pct / 100))
        if "bonus_dmg" in state.relic_effects:
            exec_dmg = int(exec_dmg * (1 + state.relic_effects["bonus_dmg"] / 100))
        apply_damage_to_target(es, exec_dmg)
        crit_txt = " ✨CRITIQUE!" if is_crit_ex else ""
        logs.append(f"💀 Exécution ×{exec_mult:.1f} (ennemi à {enemy_hp_pct*100:.0f}% PV) : **{exec_dmg:,}**{crit_txt}")

    # ── Festin Sanglant (Vampire ult) ────────────────────────────────────────
    elif effects.get("blood_mark_ultime", False):
        has_mark = state.blood_mark_turns > 0
        v_mult = effects["bonus_mult"] if has_mark else effects["base_mult"]
        if has_mark:
            logs.append("🩸 Marque de Sang active — dégâts amplifiés !")
        else:
            state.blood_mark_turns = 3
            state.blood_mark_heal_pct = 0.50
            logs.append("🩸 Marque de Sang appliquée !")
        eff_def  = max(0, es.p_def - ps.p_pen)
        v_dmg    = max(1, int(ps.p_atk * v_mult - eff_def))
        v_dmg, is_crit_v = apply_crit(v_dmg, ps.crit_chance, ps.crit_damage)
        if "bonus_dmg" in state.relic_effects:
            v_dmg = int(v_dmg * (1 + state.relic_effects["bonus_dmg"] / 100))
        apply_damage_to_target(es, v_dmg)
        crit_txt = " ✨CRITIQUE!" if is_crit_v else ""
        logs.append(f"💀 Festin Sanglant ×{v_mult} : **{v_dmg:,}**{crit_txt}")
        # Stun après
        stun_turns = effects.get("stun_after", 1)
        state.enemy_stun += stun_turns
        logs.append(f"💫 L'ennemi est étourdi pendant {stun_turns} tour(s) !")
        # Marque de Sang — soin
        if state.blood_mark_turns > 0 and v_dmg > 0 and state.spell_no_heal_turns <= 0:
            healed_v = int(v_dmg * state.blood_mark_heal_pct)
            if healed_v > 0:
                ps.hp = min(ps.max_hp, ps.hp + healed_v)
                logs.append(f"🩸 Marque de Sang : +{healed_v:,} HP")

    # ── Châtiment Divin (Paladin ult — dégâts basés sur toutes les stats) ───
    elif effects.get("all_stats_damage", False):
        stat_sum = (ps.p_atk + ps.m_atk + ps.p_pen + ps.m_pen
                    + ps.p_def + ps.m_def + ps.speed)
        base_all = max(1, stat_sum)
        base_all, is_crit_pa = apply_crit(base_all, ps.crit_chance, ps.crit_damage)
        if "bonus_dmg" in state.relic_effects:
            base_all = int(base_all * (1 + state.relic_effects["bonus_dmg"] / 100))
        if state.enemy_marked and state.enemy_marked_pct > 0:
            base_all = int(base_all * (1 + state.enemy_marked_pct / 100))
        apply_damage_to_target(es, base_all)
        crit_txt = " ✨CRITIQUE!" if is_crit_pa else ""
        logs.append(f"⚡ Châtiment Divin (stats: {stat_sum:,}) : **{base_all:,}**{crit_txt}")

    # ── Dégâts ──────────────────────────────────────────────────────────────
    elif "dmg_mult" in effects:
        # Exécution (Assassin ult) : choisir le bon multiplicateur selon HP ennemi
        if "execute_threshold" in effects:
            enemy_hp_pct = state.enemy_stats.hp / max(state.enemy_stats.max_hp, 1)
            if enemy_hp_pct < effects["execute_threshold"]:
                dmg_mult = effects.get("execute_mult", effects["dmg_mult"])
                logs.append(f"💀 Exécution ! (ennemi à {enemy_hp_pct*100:.0f}% PV) — multiplicateur ×{dmg_mult}")
            else:
                dmg_mult = effects["dmg_mult"]
        else:
            dmg_mult  = effects["dmg_mult"]
        is_magic  = effects.get("magic", False)
        hits      = effects.get("hits", 1)
        pen_pct   = effects.get("pen_pct", 0.0)
        total_spell_dmg = 0

        for hit_i in range(hits):
            if es.hp <= 0:
                break

            if is_magic:
                if effects.get("ignore_mdef", False):
                    base_dmg = max(1, int(ps.m_atk * dmg_mult))
                else:
                    effective_mdef = max(0, es.m_def - ps.m_pen)
                    base_dmg = max(1, int(ps.m_atk * dmg_mult - effective_mdef))
            else:
                if pen_pct:
                    reduced_def = int(es.p_def * (1 - pen_pct))
                    effective_def = max(0, reduced_def - ps.p_pen)
                else:
                    effective_def = max(0, es.p_def - ps.p_pen)
                base_dmg = max(1, int(ps.p_atk * dmg_mult - effective_def))

            # Bonus par stack de brûlure (Pyromancien)
            if "bonus_per_burn" in effects and state.enemy_burns > 0:
                burn_bonus = int(ps.m_atk * effects["bonus_per_burn"] * state.enemy_burns)
                # Multiplicateur si stacks >= seuil : s'applique UNIQUEMENT sur le bonus brûlure
                if "burn_threshold" in effects and state.enemy_burns >= effects["burn_threshold"]:
                    mult = effects.get("burn_threshold_mult", 1.0)
                    burn_bonus = int(burn_bonus * mult)
                    logs.append(f"🌋 Inferno — seuil {effects['burn_threshold']} stacks ! (×{mult} sur bonus brûlure)")
                base_dmg += burn_bonus

            # Bonus vs debuffs (Paladin Jugement)
            if "bonus_vs_debuff" in effects:
                has_debuffs = bool(state.spell_active_debuffs) or state.enemy_stun > 0
                if has_debuffs:
                    bonus_mult = effects["bonus_vs_debuff"]
                    eff_mdef = max(0, es.m_def - ps.m_pen)
                    base_dmg = max(1, int(ps.m_atk * bonus_mult - eff_mdef))
                    logs.append("⚖️ Ennemi affaibli — dégâts amplifiés !")

            # Critique
            crit_chance = ps.crit_chance
            if effects.get("double_crit_chance", False):
                crit_chance = min(100.0, crit_chance * 2)
            if effects.get("guaranteed_crit", False):
                crit_chance = 100.0
            base_dmg, is_crit = apply_crit(base_dmg, crit_chance, ps.crit_damage)

            # Bonus combo sur critique (Assassin S1)
            if "bonus_combo_on_crit" in effects and is_crit:
                cls_key_tmp = _class_to_spell_key(state.player_class)
                res_max_tmp = CLASS_SPELLS.get(cls_key_tmp, {}).get("resource_max", 5) if cls_key_tmp else 5
                state.player_resource = min(res_max_tmp, state.player_resource + effects["bonus_combo_on_crit"])
                logs.append(f"🗡️ Critique ! +{effects['bonus_combo_on_crit']} combo bonus")

            # Bonus dégâts sort actif (Marquage)
            if state.spell_damage_amp != 1.0:
                base_dmg = int(base_dmg * state.spell_damage_amp)

            # Relique bonus_dmg
            if "bonus_dmg" in state.relic_effects:
                base_dmg = int(base_dmg * (1 + state.relic_effects["bonus_dmg"] / 100))

            # Bonus ennemi marqué (Tireur S3)
            if state.enemy_marked and state.enemy_marked_pct > 0:
                mark_bonus = 1 + state.enemy_marked_pct / 100
                base_dmg = int(base_dmg * mark_bonus)

            apply_damage_to_target(es, base_dmg)
            total_spell_dmg += base_dmg

            crit_txt = " ✨CRITIQUE!" if is_crit else ""
            hit_txt  = f" (coup {hit_i+1}/{hits})" if hits > 1 else ""
            logs.append(f"⚡ Dégâts : **{base_dmg:,}**{crit_txt}{hit_txt}")

        # Vol de vie (sort) — inclut le buff extra_lifesteal (Vampire S3)
        total_lifesteal = effects.get("lifesteal", 0.0) + state.extra_lifesteal
        if total_lifesteal > 0 and total_spell_dmg > 0 and state.spell_no_heal_turns <= 0:
            ls = total_lifesteal + state.relic_effects.get("vol_vie", 0) / 100
            healed = int(total_spell_dmg * ls)
            ps.hp = min(ps.max_hp, ps.hp + healed)
            logs.append(f"🩸 Vol de vie : +{healed:,} HP")
        elif "vol_vie" in state.relic_effects and effects.get("lifesteal", 0.0) == 0 and state.extra_lifesteal == 0 and state.spell_no_heal_turns <= 0:
            ls = state.relic_effects["vol_vie"] / 100
            healed = int(total_spell_dmg * ls)
            if healed > 0:
                ps.hp = min(ps.max_hp, ps.hp + healed)
                logs.append(f"💧 Relique Vol de Vie : +{healed:,} HP")

        # Multiplier les stacks (Apocalypse Pyromancien)
        if "dot_stacks_mult" in effects and state.enemy_burns > 0:
            mult = effects["dot_stacks_mult"]
            state.enemy_burns = min(20, state.enemy_burns * mult)
            logs.append(f"🔥 Stacks de brûlure ×{mult} → {state.enemy_burns}")

        # Exploser les DoT (Nécrose Ombre Venin)
        if effects.get("explode_dots", False) and state.enemy_poison_stacks > 0:
            explode_mult = effects.get("explode_mult", 1.0)
            per_stack = int(ps.m_atk * 0.12 * explode_mult)
            explode_dmg = per_stack * state.enemy_poison_stacks
            es.hp = max(0, es.hp - explode_dmg)
            logs.append(f"💀 Nécrose : {state.enemy_poison_stacks} stacks × {per_stack:,} = **{explode_dmg:,}** dégâts !")
            state.enemy_poison_stacks = 0

    # ── DoT ─────────────────────────────────────────────────────────────────
    if "dot" in effects:
        stacks = effects.get("dot_stacks", 1)
        # Embrasement (Pyromancien S2) : stacks bonus selon actifs
        if effects.get("dot_stacks_from_active") and effects["dot"] == "burn":
            active_stacks = state.enemy_burns
            bonus = min(active_stacks, effects.get("dot_stacks_bonus_max", 2))
            stacks = stacks + bonus if stacks > 0 else bonus
        if effects["dot"] == "burn":
            state.enemy_burns = min(20, state.enemy_burns + stacks)
            logs.append(f"🔥 Brûlure : +{stacks} stack(s) → {state.enemy_burns} total")
        elif effects["dot"] == "poison":
            state.enemy_poison_stacks += stacks
            logs.append(f"☠️ Poison : +{stacks} stack(s) → {state.enemy_poison_stacks} total")

    # ── Soin ────────────────────────────────────────────────────────────────
    if "heal_pct" in effects and state.spell_no_heal_turns <= 0:
        heal_amt = int(ps.max_hp * effects["heal_pct"])
        ps.hp = min(ps.max_hp, ps.hp + heal_amt)
        logs.append(f"💚 Soin : +{heal_amt:,} HP → {ps.hp:,}/{ps.max_hp:,}")

    if effects.get("heal_last_dmg", False) and state.spell_no_heal_turns <= 0:
        pct = effects.get("heal_last_dmg_pct", 1.0)
        heal_amt = int(state.last_enemy_damage * pct)
        ps.hp = min(ps.max_hp, ps.hp + heal_amt)
        logs.append(f"⏪ Rembobinage : +{heal_amt:,} HP récupérés → {ps.hp:,}/{ps.max_hp:,}")

    # ── Bouclier ─────────────────────────────────────────────────────────────
    if "shield_pct" in effects:
        shield_val = int(ps.max_hp * effects["shield_pct"])
        ps.shield += shield_val
        logs.append(f"🛡️ Bouclier : +{shield_val:,} HP")

    # Bouclier basé sur PV manquants (Guerrier S2)
    if "shield_from_missing_hp_pct" in effects:
        missing_hp = ps.max_hp - ps.hp
        shield_val = int(missing_hp * effects["shield_from_missing_hp_pct"])
        ps.shield += max(0, shield_val)
        logs.append(f"🛡️ Bouclier +{shield_val:,} (PV manquants)")

    # ── Buff joueur (stats) ───────────────────────────────────────────────────
    if "stat_buff" in effects:
        buff_turns = effects.get("buff_turns", 1)
        no_heal = effects.get("no_heal_turns", 0)
        for stat, pct in effects["stat_buff"].items():
            if stat == "dmg_pct":
                state.spell_damage_amp = 1 + pct / 100
                state.spell_active_buffs.append({"type": "damage_amp", "turns": buff_turns, "label": f"⚔️ Dégâts +{pct}%"})
                logs.append(f"🎯 Dégâts +{pct}% pendant {buff_turns} tour(s)")
            else:
                current = getattr(ps, stat, 0)
                factor = 1 + pct / 100
                if stat == "crit_chance":
                    new_val = round(current * factor, 2)
                else:
                    new_val = max(1, int(current * factor))
                setattr(ps, stat, new_val)
                sign = "+" if pct > 0 else ""
                stat_name = STAT_FR.get(stat, stat)
                state.spell_active_buffs.append({"type": "stat", "stat": stat, "original": current, "turns": buff_turns, "label": f"📈 {stat_name} {sign}{pct}%"})
                logs.append(f"📈 {stat_name} {sign}{pct}% pendant {buff_turns} tour(s)")
        if no_heal > 0:
            state.spell_no_heal_turns = no_heal
            logs.append(f"🦇 Transformation : aucun soin pendant {no_heal} tour(s)")

    # ── Debuff ennemi (stats) ────────────────────────────────────────────────
    if "stat_debuff" in effects:
        buff_turns = effects.get("buff_turns", 1)
        for stat, pct in effects["stat_debuff"].items():
            current = getattr(es, stat, 0)
            new_val = max(1, int(current * (1 - pct / 100)))
            setattr(es, stat, new_val)
            stat_name = STAT_FR.get(stat, stat)
            state.spell_active_debuffs.append({"type": "stat", "stat": stat, "original": current, "turns": buff_turns, "label": f"📉 {stat_name} ennemi -{pct}%"})
            logs.append(f"📉 {stat_name} ennemi -{pct}% pendant {buff_turns} tour(s)")

    # ── Ralentissement ennemi ────────────────────────────────────────────────
    if "speed_debuff" in effects:
        turns = effects.get("speed_debuff_turns", 1)
        original_speed = es.speed
        es.speed = max(1, int(es.speed * (1 - effects["speed_debuff"])))
        state.spell_active_debuffs.append({"type": "speed", "original_speed": original_speed, "turns": turns, "label": f"⏳ Vitesse ennemi -{effects['speed_debuff']*100:.0f}%"})
        logs.append(f"⏳ Vitesse ennemi -{effects['speed_debuff']*100:.0f}% pendant {turns} tour(s)")

    # ── Stun ────────────────────────────────────────────────────────────────
    if "stun" in effects:
        state.enemy_stun += effects["stun"]
        logs.append(f"💫 L'ennemi est étourdi pendant {effects['stun']} tour(s) !")

    # ── Réduction de dégâts reçus ────────────────────────────────────────────
    if "damage_reduction" in effects:
        turns = effects.get("dmg_reduction_turns", 1)
        state.spell_damage_reduction = effects["damage_reduction"]
        state.spell_active_buffs.append({"type": "damage_reduction", "turns": turns, "label": f"🛡️ Réduction -{effects['damage_reduction']*100:.0f}%"})
        logs.append(f"🛡️ Réduction des dégâts -{effects['damage_reduction']*100:.0f}% pendant {turns} tour(s)")

    # ── Amplification des DoT ────────────────────────────────────────────────
    if "dot_amp" in effects:
        turns = effects.get("dot_amp_turns", 1)
        state.spell_dot_amp = effects["dot_amp"]
        state.spell_active_buffs.append({"type": "dot_amp", "turns": turns})
        logs.append(f"🤢 Agonie : DoT ×{effects['dot_amp']} pendant {turns} tour(s)")

    # ── Esquive prochaine attaque ────────────────────────────────────────────
    if effects.get("dodge_next", False):
        state.spell_dodge_next = True
        logs.append("🌫️ Disparaître : prochaine attaque ennemie esquivée !")

    # ── Résurrection ─────────────────────────────────────────────────────────
    if effects.get("resurrection", False):
        state.spell_resurrection = True
        logs.append("🌟 Résurrection préparée : vous survivrez à la mort avec 1 HP !")

    # ── Indestructible (Guerrier ult) ─────────────────────────────────────────
    if "undying_turns" in effects:
        state.undying_turns = effects["undying_turns"]
        logs.append(f"💢 Indestructible pendant {effects['undying_turns']} tours !")

    # ── Soif (Vampire S3) — buff lifesteal temporaire ─────────────────────────
    if "lifesteal_buff" in effects:
        state.extra_lifesteal = effects["lifesteal_buff"]
        state.extra_lifesteal_turns = effects.get("buff_turns", 3)
        logs.append(f"🦇 Soif activée : +{int(effects['lifesteal_buff']*100)}% vol de vie pendant {effects.get('buff_turns', 3)} tours")

    # ── Marquage ennemi (Tireur S2) ───────────────────────────────────────────
    if "mark_enemy" in effects:
        state.enemy_marked = True
        state.enemy_marked_pct = effects.get("mark_dmg_bonus_pct", 20)
        state.enemy_marked_turns = effects.get("mark_turns", 3)
        logs.append(f"🔴 Ennemi Marqué ! +{state.enemy_marked_pct}% dégâts reçus pendant {state.enemy_marked_turns} tours")

    # ── Contre-Attaque (Guerrier S2) ─────────────────────────────────────────
    if "contre_attaque_turns" in effects:
        state.contre_attaque_turns = effects["contre_attaque_turns"]
        logs.append(f"🔄 Contre-Attaque active pendant {effects['contre_attaque_turns']} tours !")

    # ── Marque de Sang (Vampire S2) ──────────────────────────────────────────
    if "blood_mark" in effects:
        state.blood_mark_turns = effects.get("blood_mark_turns", 3)
        state.blood_mark_heal_pct = effects.get("blood_mark_heal_pct", 0.50)
        logs.append(f"🩸 Marque de Sang appliquée ({state.blood_mark_turns} tours) !")

    # ── Renvoi Sacré (Support ult) ───────────────────────────────────────────
    if "reflect_pct" in effects:
        state.spell_reflect_pct   = effects["reflect_pct"]
        state.spell_reflect_turns = effects.get("reflect_turns", 3)
        pct_txt = int(effects["reflect_pct"] * 100)
        logs.append(f"🪞 Renvoi Sacré : {pct_txt}% des dégâts renvoyés pendant {state.spell_reflect_turns} tours !")

    # ── Mana bonus (Mage S1) ─────────────────────────────────────────────────
    if "bonus_resource" in effects:
        cls_key_tmp = _class_to_spell_key(state.player_class)
        res_max_tmp = CLASS_SPELLS.get(cls_key_tmp, {}).get("resource_max", 100) if cls_key_tmp else 100
        state.player_resource = min(res_max_tmp, state.player_resource + effects["bonus_resource"])
        res_sym = {"rage": "🔴", "mana": "🔵", "combo": "🟡"}.get(
            CLASS_SPELLS.get(cls_key_tmp, {}).get("resource", "combo"), "⚪")
        logs.append(f"{res_sym} +{effects['bonus_resource']} {CLASS_SPELLS.get(cls_key_tmp, {}).get('resource', 'ressource')} récupéré !")

    # ── Double esquive (Assassin S1) ──────────────────────────────────────────
    if effects.get("double_dodge_next", False):
        state.spell_double_dodge_next = True
        logs.append("👁️ Instinct aiguisé : prochaine esquive à 40% !")

    return {"success": True, "log": logs}


def get_spell_buttons_data(player_class: str, state: CombatState) -> list[dict]:
    """Retourne les données des 4 boutons de sorts pour les Views Discord."""
    cls_key = _class_to_spell_key(player_class)
    if not cls_key:
        return []

    spell_data   = CLASS_SPELLS.get(cls_key, {})
    resource     = spell_data.get("resource", "combo")
    resource_max = spell_data.get("resource_max", 5)
    current_res  = state.player_resource

    # Symbole ressource
    res_sym = {"rage": "🔴", "mana": "🔵", "combo": "🟡"}.get(resource, "⚪")
    resource_label = f"{res_sym} {current_res}/{resource_max}"

    buttons = []
    for spell_key in ("s1", "s2", "ultimate"):
        spell = spell_data.get(spell_key)
        if not spell:
            continue

        cost     = spell["cost"]
        cd       = state.spell_cooldowns.get(spell_key, 0)
        min_turn = spell["min_turn"]

        can_use = (
            state.turn >= min_turn
            and cd == 0
            and current_res >= cost
        )

        if cd > 0:
            label = f"{spell['name']} [{cd}t]"
        elif current_res < cost:
            label = f"{spell['name']} [{cost}{res_sym}]"
        elif state.turn < min_turn:
            label = f"{spell['name']} [T{min_turn}]"
        else:
            label = spell["name"]

        buttons.append({
            "key":          spell_key,
            "label":        label[:80],
            "emoji":        spell["emoji"],
            "disabled":     not can_use,
            "is_ultimate":  spell["is_ultimate"],
            "resource_label": resource_label,
        })

    return buttons


def run_one_turn(state: CombatState, spell_key: str | None = None) -> dict:
    """
    Effectue un seul tour de combat (joueur puis ennemi).
    spell_key : 's1'|'s2'|'ultimate' → remplace l'attaque de base.
    Retourne: {log, is_over, player_won, player_hp, player_max_hp, enemy_hp, enemy_max_hp}
    """
    state.turn += 1
    log = [f"— **Tour {state.turn}** —"]

    # Tick côté joueur (regen ressource, cooldowns, expiration buffs joueur)
    log.extend(tick_player_side(state))

    # Action joueur : sort ou attaque de base
    if spell_key:
        result = apply_spell(state, spell_key)
        log.extend(result["log"])
        if not result["success"]:
            # Sort raté → attaque de base
            p_logs = player_turn(state)
            log.extend(p_logs)
    else:
        p_logs = player_turn(state)
        log.extend(p_logs)

    if not state.is_over:
        # Tick côté ennemi (expiration debuffs ennemis) avant son tour
        log.extend(tick_enemy_side(state))
        e_logs = enemy_turn(state)
        log.extend(e_logs)

    return {
        "log":          log,
        "is_over":      state.is_over,
        "player_won":   state.player_won,
        "player_hp":    state.player_stats.hp,
        "player_max_hp":state.player_stats.max_hp,
        "enemy_hp":     state.enemy_stats.hp,
        "enemy_max_hp": state.enemy_stats.max_hp,
        "turn":         state.turn,
    }


def build_combat_state(
    player_data: dict,
    enemy_data: dict,
    equipment_list: list[dict],
    relics: list[dict],
    current_hp: int | None = None,
    elixir: dict = None,
    stats_bonus_pct: float = 0,
    ignore_food_buffs: bool = False,
) -> CombatState:
    """Construit un état de combat sans le lancer.

    stats_bonus_pct : bonus % de stats passif issu des titres débloqués
                      (cumul du bonus contextuel + bonus prestige titre).
    """
    import json as _json
    from bot.cogs.rpg.models import compute_total_stats, compute_max_hp, get_set_bonus

    set_bonus = get_set_bonus(equipment_list)

    # 1. Stats de base finales = classe + niveau + prestige + équipements (bonus flat panoplie inclus)
    set_bonus_flat = {k: v for k, v in set_bonus["stats"].items() if not k.endswith("_pct")}
    base_stats = compute_total_stats(
        player_data["class"], player_data["level"], player_data["prestige_level"],
        equipment_list, set_bonus_flat or None
    )

    # 2. Accumulation additive de tous les bonus % (panoplie + titres + runes équip + élixir + nourriture)
    pct_pool: dict[str, float] = {}

    def _add_pct(stat: str, value: float) -> None:
        pct_pool[stat] = pct_pool.get(stat, 0.0) + value

    # Bonus panoplie (%)
    for k, v in set_bonus["stats"].items():
        if k.endswith("_pct"):
            _add_pct(k[:-4], v)

    # Bonus titres (%)
    if stats_bonus_pct:
        for k in base_stats:
            _add_pct(k, stats_bonus_pct)

    # Élixir passé en paramètre direct (legacy)
    if elixir:
        for k, v in elixir.items():
            _add_pct(k, v)

    # Runes posées sur les équipements (%)
    for eq in equipment_list:
        rune_data = eq.get("rune_bonuses")
        if rune_data:
            try:
                runes = _json.loads(rune_data) if isinstance(rune_data, str) else rune_data
                for rstat, rval in runes.items():
                    _add_pct(rstat, rval)
            except Exception:
                pass

    # Élixir et buffs nourriture combat (%)
    food_buffs: dict = {}
    if not ignore_food_buffs:
        food_buffs = _parse_food_buffs(player_data.get("food_buffs"))
        _elixir_map = {
            "elixir_patk":  ("p_atk",),
            "elixir_matk":  ("m_atk",),
            "elixir_def":   ("p_def", "m_def"),   # legacy (anciens élixirs def combinés)
            "elixir_def_p": ("p_def",),
            "elixir_def_m": ("m_def",),
            "elixir_speed": ("speed",),
            "elixir_all":   ("p_atk", "m_atk", "p_def", "m_def", "speed"),
        }
        for ekey, estats in _elixir_map.items():
            ebuff = food_buffs.get(ekey)
            if ebuff and ebuff.get("combats", 0) > 0:
                for s in estats:
                    _add_pct(s, ebuff["value"])
        _food_stat_map = {
            "stat_def":   ("p_def", "m_def"),
            "stat_speed": ("speed",),
            "stat_patk":  ("p_atk",),
            "stat_matk":  ("m_atk",),
        }
        for stat_key, targets in _food_stat_map.items():
            buff = food_buffs.get(stat_key)
            if buff and buff.get("combats", 0) > 0:
                for s in targets:
                    _add_pct(s, buff["value"])

    # 3. Application unique — tous les % sont additifs entre eux, appliqués aux stats de base finales
    total_stats: dict = {}
    for k, v in base_stats.items():
        pct = pct_pool.get(k, 0.0)
        if pct:
            if k in ("crit_chance", "crit_damage"):
                total_stats[k] = round(v * (1 + pct / 100), 2)
            else:
                total_stats[k] = int(v * (1 + pct / 100))
        else:
            total_stats[k] = v

    # Élixir critique (bonus flat sur crit_damage, hors pool %)
    if not ignore_food_buffs and food_buffs:
        ecrit = food_buffs.get("elixir_crit")
        if ecrit and ecrit.get("combats", 0) > 0:
            total_stats["crit_damage"] = total_stats.get("crit_damage", 0) + ecrit["value"]

    relic_effects = compute_relic_effects(relics) if relics else {}

    ps = CombatStats.from_dict(total_stats)
    max_hp = compute_max_hp(total_stats)
    ps.max_hp = max_hp
    ps.hp = min(max_hp, current_hp if current_hp is not None else max_hp)

    es = CombatStats.from_dict(enemy_data)
    es.max_hp = es.hp

    # Ressource initiale = 1 tick (pour que les sorts soient accessibles dès le tour 1 ou 2)
    cls_key = _class_to_spell_key(player_data["class"])
    initial_resource = CLASS_SPELLS.get(cls_key, {}).get("resource_per_turn", 0) if cls_key else 0

    state = CombatState(
        player_stats    = ps,
        enemy_stats     = es,
        player_class    = player_data["class"],
        enemy_data      = enemy_data,
        relic_effects   = relic_effects,
        player_resource = initial_resource,
    )
    # Potions pré-combat
    if player_data.get("potion_revival_active"):
        state.spell_resurrection = True
        state.resurrection_hp_pct = 0.5
    if player_data.get("potion_no_passive"):
        state.ignore_enemy_passive = True

    # Passifs boss — effets immédiats sur stats
    enemy_passif = enemy_data.get("passif_effects", {})
    if enemy_passif:
        if "player_speed_debuff_pct" in enemy_passif:
            ps = state.player_stats
            ps.speed = max(1, int(ps.speed * (1 - enemy_passif["player_speed_debuff_pct"])))
        if "player_pdef_debuff_pct" in enemy_passif:
            ps = state.player_stats
            ps.p_def = max(0, int(ps.p_def * (1 - enemy_passif["player_pdef_debuff_pct"])))
        if "enemy_speed_buff_pct" in enemy_passif:
            es = state.enemy_stats
            es.speed = int(es.speed * (1 + enemy_passif["enemy_speed_buff_pct"]))
        if "bonus_crit_chance" in enemy_passif:
            es = state.enemy_stats
            es.crit_chance = min(100.0, es.crit_chance + enemy_passif["bonus_crit_chance"])
        state.boss_passif_effects = enemy_passif
    state.boss_spell_turn_mod = enemy_data.get("boss_spell_turn_mod", 0)

    return state


# ─── PvP ───────────────────────────────────────────────────────────────────

def run_pvp_turn(state: CombatState, attacker: str = "player", spell_key: str | None = None) -> dict:
    """
    Effectue un tour en PvP.
    attacker  : 'player' (le défieur) ou 'enemy' (le défié).
    spell_key : sort à utiliser à la place de l'attaque de base.
    """
    state.turn += 1
    log = [f"— **Tour {state.turn}** —"]

    # Tick effets de sorts du joueur actif
    tick_logs = tick_spell_effects(state)
    log.extend(tick_logs)

    if attacker == "player":
        if spell_key:
            result = apply_spell(state, spell_key)
            log.extend(result["log"])
            if not result["success"]:
                p_logs = player_turn(state)
                log.extend(p_logs)
        else:
            p_logs = player_turn(state)
            log.extend(p_logs)
    else:
        if spell_key:
            result = apply_spell(state, spell_key)
            log.extend(result["log"])
            if not result["success"]:
                e_logs = enemy_turn(state)
                log.extend(e_logs)
        else:
            e_logs = enemy_turn(state)
            log.extend(e_logs)

    return {
        "log":          log,
        "is_over":      state.is_over,
        "player_won":   state.player_won,
        "player_hp":    state.player_stats.hp,
        "player_max_hp":state.player_stats.max_hp,
        "enemy_hp":     state.enemy_stats.hp,
        "enemy_max_hp": state.enemy_stats.max_hp,
        "turn":         state.turn,
    }


# ─── Utilitaires d'affichage ───────────────────────────────────────────────

def hp_bar(current: int, maximum: int, length: int = 20) -> str:
    """Génère une barre de vie visuelle."""
    if maximum <= 0:
        return "█" * length
    ratio = max(0, min(1, current / maximum))
    filled = int(ratio * length)
    empty  = length - filled
    bar = "█" * filled + "░" * empty
    pct = ratio * 100
    return f"`{bar}` {pct:.1f}%"


def format_combat_stats(stats: dict) -> str:
    lines = [
        f"❤️ **Points de Vie** : {stats.get('hp', 0):,}",
        f"⚔️ **Attaque Physique** : {stats.get('p_atk', 0):,}   🔮 **Attaque Magique** : {stats.get('m_atk', 0):,}",
        f"🛡️ **Défense Physique** : {stats.get('p_def', 0):,}   🔷 **Défense Magique** : {stats.get('m_def', 0):,}",
        f"🗡️ **Pénétration Physique** : {stats.get('p_pen', 0):,}   💫 **Pénétration Magique** : {stats.get('m_pen', 0):,}",
        f"⚡ **Vitesse** : {stats.get('speed', 0):,}   🎯 **Chance Critique** : {stats.get('crit_chance', 0):.1f}%   💥 **Dégâts Critiques** : {stats.get('crit_damage', 150):.0f}%",
    ]
    return "\n".join(lines)
