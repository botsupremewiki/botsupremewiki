"""
Hub World Boss & Reliques.
Canal : 1465433246727799038
"""
from __future__ import annotations
import discord
from discord.ext import commands

import random
from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    compute_total_stats, compute_max_hp, get_set_bonus,
    RELICS, RELIC_CAPS, compute_relic_effects, WB_RANK_REWARDS, ENERGY_COST,
    STAT_FR, STAT_EMOJI,
)
from bot.cogs.rpg.items import MATERIALS
from bot.cogs.rpg.enemies import generate_world_boss, format_enemy_stats
from bot.cogs.rpg.combat import build_combat_state, run_one_turn, hp_bar, CombatState, _class_to_spell_key
from bot.cogs.rpg.models import CLASS_SPELLS
from bot.cogs.rpg.core import increment_and_check_title

_WB_MAX_ATTACKS_PER_WEEK = 10

# ── Constante de calibrage HP (ajustable après la 1ère semaine de données) ──
# Formule : boss_hp = num_joueurs × 10 attaques × 0.8 participation × K × avg_level^1.5
# K=30 → 10 joueurs niv.100 = ~2.4M HP | 30 joueurs niv.80 = ~4.3M HP
# Augmente K si le boss meurt trop facilement, baisse si trop dur.
_WB_DAMAGE_K = 30


def compute_wb_weekly_hp(num_players: int, avg_level: float, avg_prestige: float = 0) -> int:
    """HP dynamiques du Boss Suprême cette semaine, calibrés sur le serveur."""
    if num_players <= 0:
        return 5_000_000
    prestige_mult = 1.0 + avg_prestige * 0.05  # chaque niveau de prestige = +5%
    avg_dmg_estimate = _WB_DAMAGE_K * (max(1, avg_level) ** 1.5) * prestige_mult
    target_attacks = num_players * _WB_MAX_ATTACKS_PER_WEEK * 0.80
    return max(1_000_000, int(target_attacks * avg_dmg_estimate))


class WorldBossHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Afficher le Bot Suprême", style=discord.ButtonStyle.danger,
                       emoji="🤖", custom_id="rpg:wb:show", row=0)
    async def show_wb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_wb_show(interaction)

    @discord.ui.button(label="Mes Reliques", style=discord.ButtonStyle.primary,
                       emoji="💎", custom_id="rpg:wb:relics", row=0)
    async def relics(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_relics(interaction)

    @discord.ui.button(label="Classement", style=discord.ButtonStyle.secondary,
                       emoji="🏆", custom_id="rpg:wb:leaderboard", row=0)
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_wb_leaderboard(interaction)


async def _handle_wb_show(interaction: discord.Interaction):
    """Affiche les stats du WB vs le joueur + passif, avec un bouton Attaquer."""
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    if not player.get("class"):
        await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
        return
    if player.get("zone", 1) < 1000:
        await interaction.response.send_message(
            f"🔒 Le World Boss est accessible à partir de la **zone 1 000**.\n"
            f"Ta zone actuelle : **{player.get('zone', 1)}** — Continue à progresser dans le monde !",
            ephemeral=True,
        )
        return

    personal_turn = player.get("wb_personal_turn", 0)
    scaled_enemy = generate_world_boss(personal_turn)

    # Stats du joueur
    from bot.cogs.rpg.combat import hp_bar
    from bot.cogs.rpg.models import compute_total_stats, compute_max_hp, get_set_bonus
    equipment = await db.get_equipment(interaction.user.id)
    equipped  = [e for e in equipment if e.get("slot_equipped")]
    set_bonus = get_set_bonus(equipped)
    total_stats = compute_total_stats(player["class"], player["level"], player.get("prestige_level", 0), equipped, set_bonus["stats"])
    max_hp    = compute_max_hp(total_stats)
    current_hp = max_hp

    weekly_attacks = await db.get_wb_weekly_attacks(interaction.user.id)
    attacks_left   = _WB_MAX_ATTACKS_PER_WEEK - weekly_attacks
    energy_cost    = ENERGY_COST.get("world_boss", 50)

    # Formule réelle : 10 + 2 × (personal_turn + survie/mort)
    _pt = weekly_attacks  # personal_turn pour la prochaine attaque
    next_mat_min = 10 + 2 * _pt        # si le joueur meurt
    next_mat_max = 10 + 2 * (_pt + 1)  # si le joueur survit
    zone_equiv = round(1000 * (1.25 ** personal_turn))

    # ── HP collectifs du serveur ──
    from bot.cogs.rpg.database import current_week_start
    week = current_week_start()
    server_stats   = await db.get_wb_server_stats()
    raw_boss_hp    = compute_wb_weekly_hp(
        server_stats["num_players"], server_stats["avg_level"], server_stats["avg_prestige"]
    )
    boss_weekly_hp = await db.get_or_create_wb_weekly_hp(week, raw_boss_hp)
    total_dmg      = await db.get_wb_total_weekly_damage(week)
    pct_done       = min(1.0, total_dmg / boss_weekly_hp)
    bar_len        = 14
    filled         = int(pct_done * bar_len)
    boss_bar       = "█" * filled + "░" * (bar_len - filled)
    boss_killed    = total_dmg >= boss_weekly_hp

    embed = discord.Embed(
        title=f"🤖 {scaled_enemy['name']}",
        description=(
            f"**Tour personnel #{personal_turn + 1}** | Zone équivalente : **{zone_equiv:,}**\n\n"
            f"🗡️ Attaques restantes : **{attacks_left}/{_WB_MAX_ATTACKS_PER_WEEK}** cette semaine\n"
            f"⚡ Coût par attaque : **{energy_cost}** énergies (tu as : **{player.get('energy', 0)}**)\n\n"
            + (
                f"💀 **Boss Suprême VAINCU cette semaine !** Les récompenses ont été distribuées."
                if boss_killed else
                f"❤️‍🔥 **HP Collectifs** : `{boss_bar}` **{total_dmg:,}/{boss_weekly_hp:,}** ({pct_done*100:.1f}%)\n"
                f"*{server_stats['num_players']} joueurs · Niv. moyen {server_stats['avg_level']:.0f}*"
            )
        ),
        color=0x00FF00 if boss_killed else 0xFF4444,
    )
    embed.add_field(
        name="👤 Tes Stats",
        value=(
            f"❤️ HP : {hp_bar(current_hp, max_hp, 12)} {current_hp:,}/{max_hp:,}\n"
            f"⚔️ **Attaque Physique** : {total_stats.get('p_atk', 0):,}   🔮 **Attaque Magique** : {total_stats.get('m_atk', 0):,}\n"
            f"🛡️ **Défense Physique** : {total_stats.get('p_def', 0):,}   🔷 **Défense Magique** : {total_stats.get('m_def', 0):,}\n"
            f"⚡ **Vitesse** : {total_stats.get('speed', 0):,}   🎯 **Chance Critique** : {total_stats.get('crit_chance', 0):.1f}%"
        ),
        inline=True,
    )
    embed.add_field(
        name=f"🤖 Stats du {scaled_enemy['name']}",
        value=format_enemy_stats(scaled_enemy),
        inline=True,
    )
    if scaled_enemy.get("passif"):
        embed.add_field(name="🔮 Passif", value=scaled_enemy["passif"], inline=False)

    embed.add_field(
        name="🎒 Récompense de ta prochaine attaque",
        value=(
            f"**{next_mat_min}–{next_mat_max} matériaux aléatoires** (survie : {next_mat_max}, mort : {next_mat_min})\n"
            f"*Tous types et tiers confondus — 100% aléatoire*"
        ),
        inline=False,
    )

    embed.set_footer(text="Le classement est réinitialisé chaque lundi à minuit UTC.")

    view = WBAttackView(interaction.user.id, player_class=player.get("class", ""))
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class WBAttackView(discord.ui.View):
    """Vue éphémère avec le bouton Attaquer le World Boss (+ sorts de classe)."""

    def __init__(self, user_id: int, player_class: str = ""):
        super().__init__(timeout=300)
        self.user_id      = user_id
        self.player_class = player_class
        self._build_buttons()

    def _build_buttons(self):
        self.clear_items()

        # Ligne 0 : attaque de base
        atk_btn = discord.ui.Button(label="Attaquer", style=discord.ButtonStyle.danger, emoji="⚔️", row=0)
        atk_btn.callback = self._make_action_cb(None)
        self.add_item(atk_btn)

        # Ligne 1 : sorts (ressources initialisées au max pour le WB, pas de cooldown persistent)
        cls_key = _class_to_spell_key(self.player_class) if self.player_class else ""
        if cls_key:
            spell_data = CLASS_SPELLS.get(cls_key, {})
            for spell_key in ("s1", "s2", "s3", "ultimate"):
                spell = spell_data.get(spell_key)
                if not spell:
                    continue
                style = discord.ButtonStyle.red if spell["is_ultimate"] else discord.ButtonStyle.blurple
                btn = discord.ui.Button(
                    label=spell["name"],
                    emoji=spell["emoji"],
                    style=style,
                    row=1,
                )
                btn.callback = self._make_action_cb(spell_key)
                self.add_item(btn)

    def _make_action_cb(self, spell_key: str | None):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
                return
            await _do_wb_attack(interaction, spell_key)
        return callback


async def _do_wb_attack(interaction: discord.Interaction, spell_key: str | None = None):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)

    energy_cost = ENERGY_COST.get("world_boss", 50)
    if player.get("energy", 0) < energy_cost:
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="❌ Pas assez d'énergie",
                description=f"Il te faut **{energy_cost}** énergies, tu n'en as que **{player.get('energy', 0)}**.",
                color=0xFF4444,
            ),
            view=None,
        )
        return

    weekly_attacks = await db.get_wb_weekly_attacks(interaction.user.id)
    if weekly_attacks >= _WB_MAX_ATTACKS_PER_WEEK:
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="❌ Limite hebdomadaire atteinte",
                description=(
                    f"Tu as déjà utilisé tes **{_WB_MAX_ATTACKS_PER_WEEK} attaques** cette semaine.\n"
                    "Le classement est réinitialisé chaque **lundi à minuit UTC**."
                ),
                color=0xFF4444,
            ),
            view=None,
        )
        return

    if not await db.try_start_combat(interaction.user.id):
        await interaction.response.edit_message(
            embed=discord.Embed(title="⚔️ Déjà en combat", description="Tu es déjà en combat ! Termine ton combat actuel avant d'attaquer le World Boss.", color=0xFF4444),
            view=None,
        )
        return

    # Déduire l'énergie
    await db.update_player(interaction.user.id, energy=max(0, player["energy"] - energy_cost))

    personal_turn = player.get("wb_personal_turn", 0)
    scaled_enemy = generate_world_boss(personal_turn)

    equipment   = await db.get_equipment(interaction.user.id)
    relics_data = await db.get_relics(interaction.user.id)
    stats_bonus_pct = await db.get_stats_bonus_pct(interaction.user.id, player, "wb_stats_pct")
    state = build_combat_state(player, scaled_enemy, equipment, relics_data, None,
                               stats_bonus_pct=stats_bonus_pct, ignore_food_buffs=True)
    # WB : ressources initialisées au maximum (pas de persistance de cooldown entre attaques)
    cls_key = _class_to_spell_key(player.get("class", ""))
    if cls_key:
        state.player_resource = CLASS_SPELLS.get(cls_key, {}).get("resource_max", 100)

    # Combat 40 tours : 20 tours joueur + 20 tours WB (joueur en premier)
    # La vitesse ne détermine PAS l'ordre, mais les doubles attaques via sorts/passifs comptent
    state.player_stats.speed = 1
    state.enemy_stats.speed = 1
    _WB_LARGE_HP = 10_000_000_000
    state.enemy_stats.hp = _WB_LARGE_HP
    state.enemy_stats.max_hp = _WB_LARGE_HP

    all_logs: list[str] = []
    result = {}
    player_survived = True
    for _round in range(20):
        result = run_one_turn(state, spell_key)
        all_logs.extend(result["log"])
        if state.is_over:
            if not state.player_won:
                player_survived = False
            break

    # Dégâts réels = HP infligés au boss sur les 20 tours
    real_damage = max(1, _WB_LARGE_HP - (result.get("enemy_hp", _WB_LARGE_HP)))
    await db.add_wb_damage(interaction.user.id, interaction.user.display_name, real_damage)

    # Mise à jour personal_turn: +1 si survie, reset à 0 si mort
    if not player_survived:
        # Joueur mort → reset
        await db.update_player(interaction.user.id, wb_personal_turn=0)
        new_personal_turn = 0
        death_msg = "\n💀 **Défaite !** Le Bot Suprême repasse à Zone 1000 pour toi."
    else:
        new_personal_turn = min(personal_turn + 1, 19)  # cap Tour 20 (index 19)
        await db.update_player(interaction.user.id, wb_personal_turn=new_personal_turn)
        death_msg = ""

    # Zone suivante pour affichage
    next_zone = round(1000 * (1.25 ** new_personal_turn))

    # Vérification titres WB (attaques + dégâts cumulés)
    from bot.cogs.rpg.models import TITLES as _TITLES
    for tid, t in _TITLES.items():
        if t["req_type"] == "wb_attacks":
            await increment_and_check_title(interaction.user.id, tid)
        elif t["req_type"] == "wb_total_damage":
            await increment_and_check_title(interaction.user.id, tid, real_damage)
    await db.increment_quest_stat(interaction.user.id, "world_boss_count")

    # Récompense immédiate : 10 mats de base + 2 par attaque du WB survivée
    # Survie = +1 tour tenu (personal_turn+1), mort = tours tenus = personal_turn
    # Tour 1 survie=12, Tour 1 mort=10 | Tour 20 survie=50, Tour 20 mort=48
    wb_mat_count = 10 + 2 * (personal_turn + (1 if player_survived else 0))
    all_mat_ids = list(MATERIALS.keys())
    mat_drops: dict[str, int] = {}
    for _ in range(wb_mat_count):
        mid = random.choice(all_mat_ids)
        mat_drops[mid] = mat_drops.get(mid, 0) + 1
    for mid, qty in mat_drops.items():
        await db.add_material(interaction.user.id, mid, qty)

    attacks_left = _WB_MAX_ATTACKS_PER_WEEK - weekly_attacks - 1

    # Classement mis à jour
    leaderboard = await db.get_wb_leaderboard()
    player_row = next((r for r in leaderboard if r["user_id"] == interaction.user.id), None)
    current_rank = leaderboard.index(player_row) + 1 if player_row else None
    weekly_total_dmg = player_row["damage"] if player_row else real_damage
    weekly_total_atk = player_row["attacks"] if player_row else 1

    turns_played = result.get("turn", 20)
    embed = discord.Embed(
        title="🤖 Bot Suprême — Attaque !",
        description=(
            f"Tu attaques **{scaled_enemy['name']}** (Tour WB #{personal_turn + 1} — Zone {scaled_enemy['zone']:,}) !\n\n"
            f"💥 Dégâts infligés : **{real_damage:,}** ({turns_played} tours de combat)\n"
            f"⚡ Énergie restante : **{max(0, player['energy'] - energy_cost)}**\n"
            f"🗡️ Attaques restantes cette semaine : **{attacks_left}/{_WB_MAX_ATTACKS_PER_WEEK}**"
            f"{death_msg}"
        ),
        color=0xFF4444,
    )

    # Champ classement & récompense projetée
    if current_rank is not None:
        medals = ["🥇", "🥈", "🥉"] + ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        medal = medals[current_rank - 1] if current_rank <= len(medals) else f"#{current_rank}"
        reward = WB_RANK_REWARDS.get(current_rank, WB_RANK_REWARDS["default"])
        relic_info = RELICS.get(reward["relic"])
        if relic_info:
            reward_txt = f"{relic_info['emoji']} **{relic_info['rarity'].capitalize()}** +{reward['gold']:,}g"
        else:
            reward_txt = f"+{reward['gold']:,}g"
        # Joueur juste devant pour montrer la cible
        if current_rank > 1:
            rival = leaderboard[current_rank - 2]
            gap = rival["damage"] - weekly_total_dmg
            rival_txt = f"\n📈 Prochain rang : **{rival['display_name']}** (+{gap:,} dégâts)"
        else:
            rival_txt = "\n🏆 Tu es en tête du classement !"
        embed.add_field(
            name=f"{medal} Classement — #{current_rank} / {len(leaderboard)}",
            value=f"🎁 Récompense projetée : {reward_txt}{rival_txt}",
            inline=False,
        )

    # Champ matériaux reçus
    mat_lines = " | ".join(
        f"{MATERIALS[mid]['emoji']} {MATERIALS[mid]['name']} ×{qty}"
        for mid, qty in sorted(mat_drops.items(), key=lambda x: -x[1])
    )
    embed.add_field(
        name=f"🎒 Matériaux obtenus ({wb_mat_count})",
        value=mat_lines[:1024],
        inline=False,
    )

    # Champ progression personnelle
    embed.add_field(
        name="📊 Ta progression",
        value=(
            f"🗺️ Prochaine zone : **{next_zone:,}**\n"
            f"💥 Dégâts totaux cette semaine : **{weekly_total_dmg:,}**\n"
            f"🗡️ Attaques effectuées : **{weekly_total_atk}/{_WB_MAX_ATTACKS_PER_WEEK}**"
        ),
        inline=False,
    )

    # Progression collective après cette attaque
    from bot.cogs.rpg.database import current_week_start
    week           = current_week_start()
    server_stats   = await db.get_wb_server_stats()
    raw_boss_hp    = compute_wb_weekly_hp(
        server_stats["num_players"], server_stats["avg_level"], server_stats["avg_prestige"]
    )
    boss_weekly_hp = await db.get_or_create_wb_weekly_hp(week, raw_boss_hp)
    total_dmg      = await db.get_wb_total_weekly_damage(week)
    pct_done       = min(1.0, total_dmg / boss_weekly_hp)
    bar_len        = 12
    filled         = int(pct_done * bar_len)
    boss_bar       = "█" * filled + "░" * (bar_len - filled)
    boss_killed    = total_dmg >= boss_weekly_hp
    if boss_killed:
        await db.mark_wb_killed(week)
    collective_txt = (
        "💀 **Boss Suprême VAINCU cette semaine !** 🎉"
        if boss_killed else
        f"`{boss_bar}` {total_dmg:,}/{boss_weekly_hp:,} ({pct_done*100:.1f}%)"
    )
    embed.add_field(name="❤️‍🔥 Vie collective du Boss", value=collective_txt, inline=False)

    log_txt = "\n".join(all_logs[-8:])[:800]
    if log_txt:
        embed.add_field(name="📜 Combat", value=log_txt, inline=False)
    embed.set_footer(text="Le classement est réinitialisé chaque lundi à minuit UTC.")

    await db.update_player(interaction.user.id, in_combat=0)
    # Si il reste des attaques, on peut réattaquer
    if attacks_left > 0:
        view = WBAttackView(interaction.user.id, player_class=player.get("class", ""))
        await interaction.response.edit_message(embed=embed, view=view)
    else:
        await interaction.response.edit_message(embed=embed, view=None)


_RELIC_EFFECT_LABELS = {
    "vol_vie":       ("💧 Vol de Vie",       "%"),
    "reduction_dmg": ("🪨 Réduction Dégâts", "%"),
    "bonus_dmg":     ("💪 Amplification",    "%"),
    "reflet":        ("🪞 Renvoi",           "%"),
    "double_frappe": ("⚡ Double Frappe",    "% chance"),
    "regen_hp":      ("💚 Régénération HP",  "% HP/tour"),
}

async def _handle_relics(interaction: discord.Interaction):
    relics_data = await db.get_relics(interaction.user.id)

    # Compter par relic_id (= par rareté)
    relic_counts: dict[str, int] = {}
    for r in relics_data:
        relic_counts[r["relic_id"]] = relic_counts.get(r["relic_id"], 0) + 1

    # Calculer les effets combinés (avec caps)
    effects = compute_relic_effects(relics_data)

    embed = discord.Embed(
        title="💎 Mes Reliques du Bot Suprême",
        description=(
            f"Tu possèdes **{len(relics_data)}** relique(s) au total.\n"
            "Toute participation au World Boss te rapporte au moins une relique **commune**.\n"
            "Les rangs supérieurs donnent des raretés plus élevées.\n"
            "Chaque relique donne **6 effets** simultanément, -5% d'efficacité par copie de même rareté."
        ),
        color=0x9C27B0,
    )

    # Afficher les 10 raretés
    for relic_id, relic_info in RELICS.items():
        owned = relic_counts.get(relic_id, 0)
        if owned == 0:
            continue
        eff_pct = f" (eff. : {max(0.0, 1.0 - 0.05 * (owned - 1)) * 100:.0f}% sur la dernière)"
        # Calculer les effets de cette rareté spécifique
        eff_lines = []
        for eff_key, (label, unit) in _RELIC_EFFECT_LABELS.items():
            val = relic_info["effects"].get(eff_key, 0)
            eff_lines.append(f"{label} +{val:.1f}{unit}")
        embed.add_field(
            name=f"{relic_info['emoji']} {relic_info['rarity'].capitalize()} ×{owned}{eff_pct}",
            value="\n".join(eff_lines),
            inline=True,
        )

    # Afficher les effets combinés actifs
    if effects:
        effect_lines = []
        for eff_key, (label, unit) in _RELIC_EFFECT_LABELS.items():
            val = effects.get(eff_key, 0)
            if val > 0:
                cap = RELIC_CAPS.get(eff_key, 100)
                cap_txt = " *(cap atteint)*" if val >= cap else ""
                effect_lines.append(f"{label} : **+{val:.1f}{unit}**{cap_txt}")
        if effect_lines:
            embed.add_field(
                name="✨ Effets Totaux Actifs",
                value="\n".join(effect_lines),
                inline=False,
            )
    elif not relics_data:
        embed.add_field(
            name="🔒 Aucune relique",
            value="Participe au World Boss pour obtenir ta première relique !",
            inline=False,
        )

    caps_txt = " · ".join(
        f"{label} {RELIC_CAPS[key]:.0f}%"
        for key, (label, _) in _RELIC_EFFECT_LABELS.items()
        if key in RELIC_CAPS
    )
    embed.set_footer(text=f"Plafonds : {caps_txt}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def _handle_wb_leaderboard(interaction: discord.Interaction):
    rows = await db.get_wb_leaderboard()

    from bot.cogs.rpg.database import current_week_start
    week          = current_week_start()
    server_stats  = await db.get_wb_server_stats()
    raw_boss_hp   = compute_wb_weekly_hp(
        server_stats["num_players"], server_stats["avg_level"], server_stats["avg_prestige"]
    )
    boss_weekly_hp = await db.get_or_create_wb_weekly_hp(week, raw_boss_hp)
    total_dmg      = await db.get_wb_total_weekly_damage(week)
    pct_done       = min(1.0, total_dmg / boss_weekly_hp)
    bar_len        = 14
    filled         = int(pct_done * bar_len)
    boss_bar       = "█" * filled + "░" * (bar_len - filled)
    boss_killed    = total_dmg >= boss_weekly_hp

    embed = discord.Embed(
        title="🏆 Classement Bot Suprême — Semaine en cours",
        description=(
            "**Tous les participants** reçoivent une relique chaque lundi à minuit UTC.\n"
            "Plus tu es haut dans le classement, plus la rareté est élevée !\n\n"
            + (
                "💀 **Boss Suprême VAINCU cette semaine !** 🎉"
                if boss_killed else
                f"❤️‍🔥 **HP Collectifs** : `{boss_bar}` **{total_dmg:,}/{boss_weekly_hp:,}** ({pct_done*100:.1f}%)"
            )
        ),
        color=0x00FF00 if boss_killed else 0xFFD700,
    )

    if not rows:
        embed.description += "\n\n*Aucun dégât enregistré cette semaine.*"
    else:
        medals = ["🥇", "🥈", "🥉"] + ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        default_reward = WB_RANK_REWARDS["default"]
        lines = []
        for i, row in enumerate(rows[:10]):
            medal = medals[i] if i < len(medals) else f"#{i+1}"
            reward = WB_RANK_REWARDS.get(i + 1, default_reward)
            relic_info = RELICS.get(reward["relic"])
            relic_txt = f"{relic_info['emoji']} {relic_info['rarity'].capitalize()}" if relic_info else ""
            lines.append(
                f"{medal} **{row['display_name']}** — {row['damage']:,} dégâts"
                + (f"  →  {relic_txt} +{reward['gold']:,}g" if relic_txt else "")
            )
        if len(rows) > 10:
            relic_info_def = RELICS.get(default_reward["relic"])
            def_emoji = relic_info_def["emoji"] if relic_info_def else "⬜"
            lines.append(f"*... +{len(rows)-10} autres participants → {def_emoji} Commune +{default_reward['gold']:,}g*")
        embed.add_field(name="Classement", value="\n".join(lines), inline=False)

    # Montrer la position du joueur
    player_row = next((r for r in rows if r["user_id"] == interaction.user.id), None)
    if player_row:
        rank = rows.index(player_row) + 1
        reward = WB_RANK_REWARDS.get(rank, WB_RANK_REWARDS["default"])
        relic_info = RELICS.get(reward["relic"])
        relic_txt = f"{relic_info['emoji']} {relic_info['rarity'].capitalize()}" if relic_info else "Commune"
        embed.set_footer(text=f"Ta position : #{rank} — Récompense prévue : {relic_txt} +{reward['gold']:,} gold")
    else:
        embed.set_footer(text="Tu n'es pas encore dans le classement — attaque le boss pour obtenir une relique !")

    await interaction.response.send_message(embed=embed, ephemeral=True)


def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🤖 Hub Bot Suprême & Reliques",
        description=(
            "Le **Bot Suprême** est un ennemi légendaire que tous les joueurs affrontent **ensemble**.\n"
            "Ses HP sont **dynamiques** chaque semaine selon le niveau moyen du serveur.\n\n"
            "**Règles :**\n"
            f"⚡ Coût : **{ENERGY_COST.get('world_boss', 50)} énergies** par attaque\n"
            f"🗡️ Maximum : **{_WB_MAX_ATTACKS_PER_WEEK} attaques** par semaine\n"
            "🔄 Le classement est réinitialisé **chaque lundi à minuit UTC**\n\n"
            "**HP Collectifs :**\n"
            "❤️‍🔥 Les dégâts de **tous les joueurs** s'accumulent contre un boss commun.\n"
            "Si le boss atteint 0 HP, il est vaincu et des récompenses bonus sont distribuées !\n\n"
            "**Récompenses hebdomadaires :**\n"
            "🌈 #1 : Prismatique · 🩵 #2 : Transcendant · 🟡 #3 : Divin\n"
            "🔶 #4 : Artefact · 🟥 #5 : Mythique · 🟧 #6 : Légendaire\n"
            "🟪 #7 : Épique · 🟦 #8 : Rare · 🟩 #9-10 : Peu Commun\n"
            "⬜ Tous les participants : Commune (minimum garanti)\n\n"
            "**Récompense par attaque :**\n"
            "🎒 **10–12 mats** au tour 1, **28–30 mats** au tour 10 — formule : `10 + 2 × tour (+2 si survie)`\n\n"
            "**Reliques :**\n"
            "💎 Les reliques donnent des bonus permanents à tes stats.\n"
            "Chaque copie supplémentaire d'une même relique est 5% moins efficace."
        ),
        color=0xFF4444,
    )
    view = WorldBossHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
