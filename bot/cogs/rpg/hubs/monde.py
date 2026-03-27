"""
Hub Monde — combat par zones 1-10000.
Canal : 1465432915612799109
"""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    compute_total_stats, compute_max_hp, get_set_bonus,
    combat_xp_reward, combat_gold_reward, level_up, ENERGY_COST,
    STAT_FR, STAT_EMOJI, item_tier_label,
)
from bot.cogs.rpg.enemies import get_enemy_for_zone, format_enemy_stats
from bot.cogs.rpg.items import (
    get_material_drop_table, get_equipment_drops, format_item_name,
    MATERIALS, EQUIPMENT_CATALOG,
)
from bot.cogs.rpg.combat import (
    build_combat_state, run_full_combat, run_one_turn, hp_bar, format_combat_stats, CombatState,
    get_spell_buttons_data,
)
from bot.cogs.rpg.core import check_all_titles, increment_and_check_title

# Stock des états de combat actifs (non automatiques)
_active_combats: dict[int, CombatState] = {}
_combat_started_at: dict[int, float] = {}   # user_id → timestamp de début (pour cleanup)

# ─── Constantes Farm ───────────────────────────────────────────────────────
FARM_XP_MULT   = 0.10   # 10% XP
FARM_GOLD_MULT = 0.10   # 10% gold
FARM_LOOT_DIV  = 2      # loots ÷ 2


class MondeHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Afficher le Combat", style=discord.ButtonStyle.primary, emoji="⚔️", custom_id="rpg:monde:afficher", row=0)
    async def afficher_combat(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        zone  = player.get("zone", 1)
        stage = player.get("stage", 1)
        await _send_combat_info(interaction, player, zone, stage, ephemeral=True)


async def _build_combat_info(user_id: int, player: dict, zone: int, stage) -> tuple[discord.Embed, "CombatView"]:
    """Construit l'embed + vue de combat pour la zone/stage courante."""
    is_boss = str(stage) == "boss"
    stage_val = "boss" if is_boss else (int(stage) if str(stage).isdigit() else 1)

    enemy = get_enemy_for_zone(zone, stage_val)
    equipment = await db.get_equipment(user_id)
    equipped  = [e for e in equipment if e.get("slot_equipped")]
    set_bonus = get_set_bonus(equipped)
    total_stats = compute_total_stats(player["class"], player["level"], player.get("prestige_level", 0), equipped, set_bonus["stats"])
    max_hp    = compute_max_hp(total_stats)
    current_hp = player.get("current_hp") or max_hp

    from bot.cogs.rpg.models import CLASS_EMOJI
    enemy_type_str = {
        "ennemi": "Ennemi Classique",
        "boss_classique": "Boss de Zone",
        "boss_runique": "Boss Runique 🔮",
        "boss_emblematique": "Boss Emblématique 🌟",
        "boss_antique": "Boss Antique ⚠️",
    }.get(enemy.get("type", "ennemi"), enemy.get("type", "?"))

    embed = discord.Embed(
        title=f"{enemy.get('theme_emoji', '⚔️')} {enemy['name']}",
        description=f"Zone **{zone}-{stage}** | {enemy_type_str}\nClasse : {CLASS_EMOJI.get(enemy['class'], '')} {enemy['class']}",
        color=0xFF4444 if "boss" in enemy.get("type", "") else 0x5865F2,
    )
    embed.add_field(
        name="👤 Tes Stats",
        value=(
            f"❤️ HP : {hp_bar(current_hp, max_hp, 15)} {current_hp:,}/{max_hp:,}\n"
            f"⚔️ **Attaque Physique** : {total_stats.get('p_atk', 0):,}   🔮 **Attaque Magique** : {total_stats.get('m_atk', 0):,}\n"
            f"🛡️ **Défense Physique** : {total_stats.get('p_def', 0):,}   🔷 **Défense Magique** : {total_stats.get('m_def', 0):,}\n"
            f"⚡ **Vitesse** : {total_stats.get('speed', 0):,}   🎯 **Chance Critique** : {total_stats.get('crit_chance', 0):.1f}%"
        ),
        inline=True,
    )
    embed.add_field(
        name=f"💀 Stats de {enemy['name']}",
        value=format_enemy_stats(enemy),
        inline=True,
    )

    _etype = enemy.get("type", "")
    _boss_type = ("boss_antique"      if _etype == "boss_antique"      else
                  "boss_emblematique" if _etype == "boss_emblematique" else
                  "boss_classique"    if "boss" in _etype              else "monster")
    _title_bonuses = await db.get_title_bonuses(user_id)
    _xp_pct   = _title_bonuses.get("xp_pct",   0)
    _gold_pct = _title_bonuses.get("gold_pct", 0)
    xp_reward  = round(combat_xp_reward(zone, _boss_type)   * (1 + _xp_pct   / 100))
    gold_reward = round(combat_gold_reward(zone, _boss_type) * (1 + _gold_pct / 100))
    _xp_sfx   = f" *(+{_xp_pct:.0f}% titre)*"   if _xp_pct   else ""
    _gold_sfx = f" *(+{_gold_pct:.0f}% titre)*" if _gold_pct else ""
    energy_type  = {
        "boss_antique":      "boss_antique",
        "boss_emblematique": "boss_emblematique",
        "boss_runique":      "boss_runique",
        "boss_classique":    "boss_classique",
    }.get(_etype, "ennemi")
    energy_cost = ENERGY_COST.get(energy_type, 1)

    embed.add_field(
        name="🎁 Récompenses",
        value=f"✨ XP : **{xp_reward:,}**{_xp_sfx} | 💰 Gold : **{gold_reward:,}**{_gold_sfx} | ⚡ Énergie : **-{energy_cost}**",
        inline=False,
    )
    embed.add_field(name="⚡ Énergie actuelle", value=f"**{player.get('energy', 0)}/{player.get('max_energy', 2000)}**", inline=True)

    is_manual = enemy.get("type") in ("boss_runique", "boss_emblematique", "boss_antique")
    view = CombatView(user_id, player, enemy, is_manual=is_manual)
    return embed, view


async def _send_combat_info(interaction: discord.Interaction, player: dict, zone: int, stage, ephemeral: bool = True):
    """Affiche les infos de combat pour la zone/stage courante."""
    embed, view = await _build_combat_info(interaction.user.id, player, zone, stage)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=ephemeral)


class CombatView(discord.ui.View):
    def __init__(self, user_id: int, player: dict, enemy: dict, is_manual: bool = False):
        super().__init__(timeout=300)
        self.user_id   = user_id
        self.player    = player
        self.enemy     = enemy
        self.is_manual = is_manual
        self.auto_running = False

        enemy_type = enemy.get("type", "ennemi")
        energy_cost_key = {
            "ennemi":           "ennemi",
            "boss_classique":   "boss_classique",
            "boss_emblematique": "boss_emblematique",
            "boss_antique":      "boss_antique",
        }.get(enemy_type, "ennemi")

        atk_btn = discord.ui.Button(
            label="Attaquer",
            style=discord.ButtonStyle.danger,
            emoji="⚔️",
            custom_id="rpg:monde:attaquer",
        )
        atk_btn.callback = self._attaquer
        self.add_item(atk_btn)

        if not is_manual:
            auto_btn = discord.ui.Button(
                label="Attaquer en Boucle",
                style=discord.ButtonStyle.secondary,
                emoji="🔄",
                custom_id="rpg:monde:auto",
            )
            auto_btn.callback = self._auto_attaquer
            self.add_item(auto_btn)

        # Bouton Farm — uniquement sur les boss (classique, emblématique, antique)
        if "boss" in enemy.get("type", ""):
            farm_btn = discord.ui.Button(
                label="Farm",
                style=discord.ButtonStyle.secondary,
                emoji="🌾",
                custom_id="rpg:monde:open_farm",
            )
            farm_btn.callback = self._open_farm
            self.add_item(farm_btn)

        loot_btn = discord.ui.Button(
            label="Infos Loot",
            style=discord.ButtonStyle.primary,
            emoji="📦",
            custom_id="rpg:monde:loot_info",
        )
        loot_btn.callback = self._loot_info
        self.add_item(loot_btn)

    async def _attaquer(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        if not player:
            await interaction.response.send_message("❌ Profil introuvable.", ephemeral=True)
            return

        energy_type = {
            "ennemi": "ennemi", "boss_classique": "boss_classique",
            "boss_runique": "boss_runique",
            "boss_emblematique": "boss_emblematique", "boss_antique": "boss_antique",
        }.get(self.enemy.get("type", "ennemi"), "ennemi")
        cost = ENERGY_COST.get(energy_type, 1)
        if player.get("energy", 0) < cost:
            await interaction.response.send_message(f"❌ Pas assez d'énergie ! (besoin : **{cost}**, actuel : **{player.get('energy', 0)}**)", ephemeral=True)
            return

        if not await db.try_start_combat(self.user_id):
            await interaction.response.send_message("⚔️ Tu es déjà en combat ! Termine ou fuis ton combat actuel avant d'en lancer un nouveau.", ephemeral=True)
            return
        await db.update_player(self.user_id, energy=max(0, player.get("energy", 0) - cost))

        try:
            if self.is_manual:
                # Combat manuel tour par tour
                await _start_manual_combat(interaction, player, self.enemy)
            else:
                # Combat automatique (classique/boss classique) — édite le message éphémère
                await _run_auto_combat(interaction, player, self.enemy)
        except Exception:
            await db.update_player(self.user_id, in_combat=0)
            raise

    async def _auto_attaquer(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return

        player = await db.get_player(self.user_id)
        if not player:
            await interaction.response.send_message("❌ Profil introuvable.", ephemeral=True)
            return

        zone  = player.get("zone", 1)
        stage = player.get("stage", 1)
        enemy = get_enemy_for_zone(zone, stage)

        if enemy.get("type") in ("boss_emblematique", "boss_antique"):
            await interaction.response.send_message(
                f"❌ **{enemy['name']}** est un Boss Spécial — utilise le combat manuel !",
                ephemeral=True,
            )
            return

        energy_type = "boss_classique" if str(stage) == "boss" else "ennemi"
        cost = ENERGY_COST.get(energy_type, 1)
        if player.get("energy", 0) < cost:
            await interaction.response.send_message(
                f"❌ Pas assez d'énergie ! (besoin : **{cost}**)", ephemeral=True
            )
            return

        if not await db.try_start_combat(self.user_id):
            await interaction.response.send_message("⚔️ Tu es déjà en combat ! Termine ou fuis ton combat actuel avant d'en lancer un nouveau.", ephemeral=True)
            return
        loop_view = AutoLoopView(self.user_id)
        embed = discord.Embed(
            title="🔄 Combat en Boucle",
            description="Lancement du combat automatique...\n\n*Appuie sur Stop pour arrêter à tout moment.*",
            color=0x607D8B,
        )
        await interaction.response.edit_message(embed=embed, view=loop_view)
        task = asyncio.create_task(_run_auto_loop(interaction, loop_view))
        task.add_done_callback(lambda t: t.exception() if not t.cancelled() and t.exception() else None)

    async def _open_farm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        zone = self.enemy.get("zone", player.get("zone", 1))
        embed, view = await _build_farm_info(self.user_id, player, zone)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _loot_info(self, interaction: discord.Interaction):
        zone = self.enemy.get("zone", 1)
        prof = await db.get_professions(self.user_id)
        harvest_type  = prof.get("harvest_type") if prof else None
        harvest_level = prof.get("harvest_level", 0) if prof else 0
        tier_cap = min(10, harvest_level // 10 + 1)
        drop_table = get_material_drop_table(zone, harvest_type, harvest_level, tier_cap=tier_cap)

        title_bonuses = await db.get_title_bonuses(self.user_id)
        loot_pct = title_bonuses.get("monde_loot_pct", 0)
        loot_mult = 1 + loot_pct / 100

        drop_table.sort(key=lambda x: x["chance"], reverse=True)
        lines = []
        for drop in drop_table[:20]:
            mat_data = MATERIALS.get(drop["item_id"], {})
            chance = drop["chance"] * loot_mult
            if chance >= 100:
                guaranteed = int(chance / 100)
                extra = chance % 100
                chance_str = f"×{guaranteed} +{extra:.0f}%"
            else:
                chance_str = f"{chance:.1f}%"
            lines.append(f"{mat_data.get('emoji', '?')} **{mat_data.get('name', drop['item_id'])}** — {chance_str}")

        _etype = self.enemy.get("type", "")
        _eq_chances = {
            "boss_antique":      "3 items garantis (classe) + 1 autre",
            "boss_emblematique": "100% (classe) + 50% (autre)",
            "boss_classique":    "50% (classe) + 10% (autre)",
        }
        eq_chance_str = _eq_chances.get(_etype, "10% (classe) + 1% (autre)" if "boss" not in _etype else "50% (classe) + 10% (autre)")
        lines.append(f"\n⚔️ **Équipement** — {eq_chance_str}")

        embed = discord.Embed(
            title=f"📦 Loots de {self.enemy['name']}",
            description="\n".join(lines),
            color=0xFF9800,
        )
        footer = "×N +X% = N garantis + X% de chance d'un (N+1)ème | Loots indépendants."
        if loot_pct:
            footer += f" | Bonus loot titre : +{loot_pct:.0f}% appliqué."
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── Mode boucle ───────────────────────────────────────────────────────────


class AutoLoopView(discord.ui.View):
    """Vue pendant le combat en boucle — uniquement le bouton Stop."""

    def __init__(self, user_id: int):
        super().__init__(timeout=600)
        self.user_id      = user_id
        self.running      = True
        self.combats_won  = 0
        self.stop_reason  = ""

        stop_btn = discord.ui.Button(label="Stop", style=discord.ButtonStyle.danger, emoji="🛑")
        stop_btn.callback = self._stop
        self.add_item(stop_btn)

    async def _stop(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        self.running     = False
        self.stop_reason = "Manuel"
        await interaction.response.defer()


async def _run_auto_loop(orig_interaction: discord.Interaction, view: AutoLoopView):
    """Boucle de combat automatique — édite le message toutes les 3 s."""
    user_id = view.user_id

    try:
        while view.running:
            player = await db.get_player(user_id)
            if not player:
                view.running     = False
                view.stop_reason = "Profil introuvable"
                break

            zone  = player.get("zone", 1)
            stage = player.get("stage", 1)
            enemy = get_enemy_for_zone(zone, stage)

            # Stopper sur boss spéciaux
            if enemy.get("type") in ("boss_emblematique", "boss_antique"):
                view.running     = False
                view.stop_reason = f"Boss Spécial : **{enemy['name']}** !"
                break

            # Vérifier l'énergie
            energy_type = "boss_classique" if str(stage) == "boss" else "ennemi"
            cost = ENERGY_COST.get(energy_type, 1)
            if player.get("energy", 0) < cost:
                view.running     = False
                view.stop_reason = "Plus d'énergie"
                break

            # Déduire l'énergie et lancer le combat
            await db.update_player(user_id, energy=max(0, player["energy"] - cost))
            equipment = await db.get_equipment(user_id)
            relics    = await db.get_relics(user_id)
            result    = run_full_combat(player, enemy, equipment, relics, player.get("current_hp"))

            # Nettoyer les flags de potion après usage
            if player.get("potion_revival_active") or player.get("potion_no_passive"):
                await db.update_player(user_id, potion_revival_active=0, potion_no_passive=0)
            # Décrémente les buffs alimentaires de combat
            await _consume_combat_food_buffs(user_id)

            zone_label = f"Zone **{zone}-{stage}**"

            if result["won"]:
                view.combats_won += 1
                rewards_str = await _apply_combat_rewards(user_id, player, enemy, result)
                await db.update_player(user_id, current_hp=max(1, result["player_hp_remaining"]))

                embed = discord.Embed(
                    title="🔄 Combat en Boucle",
                    description=(
                        f"📍 {zone_label} — {enemy['name']}\n"
                        f"**Combat #{view.combats_won}** — ✅ Victoire en **{result['turns']}** tours !\n\n"
                        f"{rewards_str}\n\n"
                        f"*Prochain combat dans 3 secondes... (Stop pour arrêter)*"
                    ),
                    color=0x00FF88,
                )
                if not view.running:
                    # Stop pressé pendant le combat
                    break
                try:
                    await orig_interaction.edit_original_response(embed=embed, view=view)
                except discord.HTTPException:
                    pass
            else:
                gold_lost   = int(player.get("gold", 0) * 0.10)
                energy_lost = min(10, player.get("energy", 0))
                blocked_until = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
                await db.update_player(
                    user_id, current_hp=1,
                    gold=max(0, player.get("gold", 0) - gold_lost),
                    energy=max(0, player.get("energy", 0) - energy_lost),
                    regen_blocked_until=blocked_until,
                    death_gold_lost=gold_lost,
                    death_energy_lost=energy_lost,
                )
                view.running     = False
                view.stop_reason = "Mort au combat"
                embed = discord.Embed(
                    title="🔄 Combat en Boucle",
                    description=(
                        f"📍 {zone_label} — {enemy['name']}\n"
                        f"**Combat #{view.combats_won + 1}** — ❌ Défaite !\n"
                        f"💸 -{gold_lost:,} gold | ⚡ -{energy_lost} énergie | 😴 Regen bloquée 1h"
                    ),
                    color=0xFF4444,
                )
                try:
                    await orig_interaction.edit_original_response(embed=embed, view=view)
                except discord.HTTPException:
                    pass
                break

            await asyncio.sleep(3)
    finally:
        await db.update_player(user_id, in_combat=0)

    await _show_auto_summary(orig_interaction, view)


async def _show_auto_summary(orig_interaction: discord.Interaction, view: AutoLoopView):
    """Affiche le résumé final de la boucle automatique."""
    reason_map = {
        "Manuel":             "⏹️ Arrêté manuellement",
        "Plus d'énergie":     "⚡ Plus d'énergie",
        "Mort au combat":     "💀 Mort au combat",
        "Profil introuvable": "❌ Profil introuvable",
    }
    stop_txt = reason_map.get(view.stop_reason, view.stop_reason or "⏹️ Arrêté")

    embed = discord.Embed(
        title="🛑 Boucle de Combat — Résumé",
        description=(
            f"{stop_txt}\n\n"
            f"**Combats gagnés :** {view.combats_won}\n\n"
            f"*Clique sur Combat Suivant pour continuer !*"
        ),
        color=0x607D8B,
    )
    result_view = CombatResultView(view.user_id)
    try:
        await orig_interaction.edit_original_response(embed=embed, view=result_view)
    except Exception:
        pass


# ─── Combat auto ───────────────────────────────────────────────────────────

async def _run_auto_combat(interaction: discord.Interaction, player: dict, enemy: dict):
    """Lance un combat entier en automatique et édite le message éphémère avec le résultat."""
    equipment = await db.get_equipment(interaction.user.id)
    relics    = await db.get_relics(interaction.user.id)

    result = run_full_combat(player, enemy, equipment, relics, player.get("current_hp"))

    # Nettoyer les flags de potion après usage
    if player.get("potion_revival_active") or player.get("potion_no_passive"):
        await db.update_player(interaction.user.id, potion_revival_active=0, potion_no_passive=0)
    # Décrémente les buffs alimentaires de combat
    await _consume_combat_food_buffs(interaction.user.id)

    # Sauvegarder HP restants
    await db.update_player(interaction.user.id, current_hp=max(1, result["player_hp_remaining"]))

    if result["won"]:
        rewards = await _apply_combat_rewards(interaction.user.id, player, enemy, result)
        desc = (
            f"✅ **Victoire** en **{result['turns']}** tours !\n"
            f"❤️ HP restants : {result['player_hp_remaining']:,}/{result['player_max_hp']:,}\n\n"
            f"**Récompenses :**\n{rewards}"
        )
        log_preview = "\n".join(result["log"][-10:]) if result["log"] else ""
        color = 0x00FF88
    else:
        await db.update_player(interaction.user.id, current_hp=1)
        desc = f"❌ **Défaite** après **{result['turns']}** tours... Tu te réveilles avec 1 HP."
        log_preview = "\n".join(result["log"][-10:]) if result["log"] else ""
        color = 0xFF4444

    embed = discord.Embed(title=f"⚔️ Combat — {enemy['name']}", description=desc, color=color)
    if log_preview:
        embed.add_field(name="📜 Derniers tours", value=log_preview[:1000], inline=False)

    await db.update_player(interaction.user.id, in_combat=0)
    result_view = CombatResultView(interaction.user.id)
    await interaction.response.edit_message(embed=embed, view=result_view)


class CombatResultView(discord.ui.View):
    """Vue affichée après un combat auto : Combat Suivant uniquement."""

    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id

        next_btn = discord.ui.Button(
            label="Combat Suivant",
            style=discord.ButtonStyle.success,
            emoji="⚔️",
            custom_id="rpg:monde:combat_suivant",
        )
        next_btn.callback = self._combat_suivant
        self.add_item(next_btn)

    async def _combat_suivant(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return

        player = await db.get_player(self.user_id)
        if not player:
            await interaction.response.edit_message(
                embed=discord.Embed(title="❌ Erreur", description="Profil introuvable.", color=0xFF4444),
                view=None,
            )
            return

        zone  = player.get("zone", 1)
        stage = player.get("stage", 1)
        embed, view = await _build_combat_info(self.user_id, player, zone, stage)
        await interaction.response.edit_message(embed=embed, view=view)

# ─── Combat manuel ─────────────────────────────────────────────────────────

async def _start_manual_combat(interaction: discord.Interaction, player: dict, enemy: dict):
    """Démarre un combat manuel (boss emblématiques, boss antiques)."""
    user_id   = interaction.user.id
    equipment = await db.get_equipment(user_id)
    relics    = await db.get_relics(user_id)
    state = build_combat_state(player, enemy, equipment, relics, player.get("current_hp"))
    import time as _time
    _active_combats[user_id] = state
    _combat_started_at[user_id] = _time.monotonic()

    player_class = player.get("class", "")
    embed = _build_manual_combat_embed(player, enemy, state, log_lines=[])
    view  = ManualCombatView(user_id, enemy, player_class=player_class, state=state)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def _build_manual_combat_embed(player: dict, enemy: dict, state: CombatState, log_lines: list[str], resource_label: str = "") -> discord.Embed:
    embed = discord.Embed(
        title=f"⚔️ Combat Manuel — {enemy['name']}",
        color=0xFF9800,
    )
    player_val = f"❤️ {hp_bar(state.player_stats.hp, state.player_stats.max_hp, 15)}\n{state.player_stats.hp:,}/{state.player_stats.max_hp:,}"
    if resource_label:
        player_val += f"\n{resource_label}"
    embed.add_field(name="👤 Toi", value=player_val, inline=True)
    embed.add_field(
        name=f"💀 {enemy['name']}",
        value=f"❤️ {hp_bar(state.enemy_stats.hp, state.enemy_stats.max_hp, 15)}\n{state.enemy_stats.hp:,}/{state.enemy_stats.max_hp:,}",
        inline=True,
    )
    if log_lines:
        embed.add_field(name="📜 Dernier tour", value="\n".join(log_lines[-8:])[:1000], inline=False)
    if enemy.get("passif"):
        embed.set_footer(text=f"Passif ennemi : {enemy['passif']}")
    return embed


class ManualCombatView(discord.ui.View):
    def __init__(self, user_id: int, enemy: dict, *, player_class: str = "", state: CombatState | None = None):
        super().__init__(timeout=300)
        self.user_id      = user_id
        self.enemy        = enemy
        self.player_class = player_class
        self._build_buttons(state)

    def _build_buttons(self, state: CombatState | None):
        self.clear_items()
        atk_btn = discord.ui.Button(label="Attaquer", style=discord.ButtonStyle.danger, emoji="⚔️", row=0)
        atk_btn.callback = self._make_action_cb(None)
        self.add_item(atk_btn)

        flee_btn = discord.ui.Button(label="Fuir", style=discord.ButtonStyle.secondary, emoji="🏃", row=0)
        flee_btn.callback = self._flee
        self.add_item(flee_btn)

        if self.player_class and state is not None:
            for bdata in get_spell_buttons_data(self.player_class, state):
                btn = discord.ui.Button(
                    label=bdata["label"],
                    emoji=bdata["emoji"],
                    style=discord.ButtonStyle.primary if not bdata["is_ultimate"] else discord.ButtonStyle.danger,
                    disabled=bdata["disabled"],
                    row=1,
                )
                btn.callback = self._make_action_cb(bdata["spell_key"])
                self.add_item(btn)

    def _make_action_cb(self, spell_key: str | None):
        async def callback(interaction: discord.Interaction):
            await self._do_action(interaction, spell_key)
        return callback

    async def _do_action(self, interaction: discord.Interaction, spell_key: str | None):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        state = _active_combats.get(self.user_id)
        if not state:
            await interaction.response.send_message("❌ Aucun combat actif trouvé.", ephemeral=True)
            return
        result = run_one_turn(state, spell_key=spell_key)
        player = await db.get_player(self.user_id)

        if result["is_over"]:
            del _active_combats[self.user_id]
            _combat_started_at.pop(self.user_id, None)
            # Nettoyer les flags de potion après usage
            if player.get("potion_revival_active") or player.get("potion_no_passive"):
                await db.update_player(self.user_id, potion_revival_active=0, potion_no_passive=0)
            # Décrémente les buffs alimentaires de combat
            await _consume_combat_food_buffs(self.user_id)
            await db.update_player(self.user_id, current_hp=max(1, result["player_hp"]), in_combat=0)
            if result["player_won"]:
                rewards = await _apply_combat_rewards(self.user_id, player, self.enemy, result)
                desc = f"✅ **Victoire** en **{result['turn']}** tours !\n\n**Récompenses :**\n{rewards}"
                color = 0x00FF88
            else:
                gold_lost   = int(player.get("gold", 0) * 0.10)
                energy_lost = min(10, player.get("energy", 0))
                blocked_until = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
                await db.update_player(
                    self.user_id, current_hp=1,
                    gold=max(0, player.get("gold", 0) - gold_lost),
                    energy=max(0, player.get("energy", 0) - energy_lost),
                    regen_blocked_until=blocked_until,
                    death_gold_lost=gold_lost,
                    death_energy_lost=energy_lost,
                )
                desc = f"❌ **Défaite** ! Tu te réveilles avec 1 HP.\n💸 -{gold_lost:,} gold | ⚡ -{energy_lost} énergie | 😴 Regen bloquée 1h"
                color = 0xFF4444
            embed = discord.Embed(title=f"⚔️ Combat terminé — {self.enemy['name']}", description=desc, color=color)
            log_preview = "\n".join(result["log"][-8:])[:1000]
            if log_preview:
                embed.add_field(name="📜 Dernier tour", value=log_preview, inline=False)
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            spell_btns = get_spell_buttons_data(self.player_class, state)
            resource_label = spell_btns[0]["resource_label"] if spell_btns else ""
            self._build_buttons(state)
            embed = _build_manual_combat_embed(player, self.enemy, state, result["log"], resource_label)
            await interaction.response.edit_message(embed=embed, view=self)

    async def _flee(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        if self.user_id in _active_combats:
            del _active_combats[self.user_id]
        _combat_started_at.pop(self.user_id, None)
        await db.update_player(self.user_id, in_combat=0)
        await interaction.response.edit_message(
            embed=discord.Embed(title="🏃 Tu as fui !", description="Tes HP actuels sont conservés.", color=0xFF9800),
            view=None,
        )

    async def on_timeout(self):
        if self.user_id in _active_combats:
            del _active_combats[self.user_id]
        _combat_started_at.pop(self.user_id, None)
        await db.update_player(self.user_id, in_combat=0)


# ─── Récompenses ────────────────────────────────────────────────────────────

async def _apply_combat_rewards(user_id: int, player: dict, enemy: dict, result: dict) -> str:
    """Distribue les récompenses après un combat gagné. Retourne une string de résumé."""
    zone  = enemy.get("zone", 1)
    etype = enemy.get("type", "")
    boss_type = ("boss_antique" if etype == "boss_antique" else
                 "boss_emblematique" if etype == "boss_emblematique" else
                 "boss_classique" if "boss" in etype else "monster")

    xp_gain   = combat_xp_reward(zone, boss_type)
    gold_gain  = combat_gold_reward(zone, boss_type)

    # Bonus reliques sur XP et gold
    # Bonus titres sur XP et gold globaux
    title_bonuses = await db.get_title_bonuses(user_id)
    xp_gain   = int(xp_gain   * (1 + title_bonuses.get("xp_pct",   0) / 100))
    gold_gain = int(gold_gain  * (1 + title_bonuses.get("gold_pct", 0) / 100))

    player = await db.get_player(user_id)
    new_gold = player["gold"] + gold_gain
    new_xp   = player["xp"]   + xp_gain
    new_level, new_xp = level_up(player["level"], new_xp)
    await db.update_player(user_id, gold=new_gold, xp=new_xp, level=new_level)

    rewards_lines = [f"✨ +{xp_gain:,} XP | 💰 +{gold_gain:,} golds"]
    if new_level > player["level"]:
        rewards_lines.append(f"🎉 Niveau {new_level} atteint !")

    # Loots matériaux
    prof = await db.get_professions(user_id)
    harvest_type  = prof.get("harvest_type") if prof else None
    harvest_level = prof.get("harvest_level", 0) if prof else 0
    tier_cap = min(10, harvest_level // 10 + 1)
    drop_table = get_material_drop_table(zone, harvest_type, harvest_level, tier_cap=tier_cap)

    import random
    loot_mult = 1 + title_bonuses.get("monde_loot_pct", 0) / 100
    looted_mats = []
    for drop in drop_table:
        chance = drop["chance"] * loot_mult
        guaranteed = int(chance / 100)
        extra = chance % 100
        qty = guaranteed + (1 if random.random() * 100 < extra else 0)
        if qty > 0:
            await db.add_material(user_id, drop["item_id"], qty)
            mat_name = MATERIALS.get(drop["item_id"], {}).get("name", drop["item_id"])
            looted_mats.append(f"{mat_name} ×{qty}" if qty > 1 else mat_name)

    if looted_mats:
        rewards_lines.append(f"📦 Matériaux : {', '.join(looted_mats[:5])}" + (" ..." if len(looted_mats) > 5 else ""))
        if harvest_type:
            harvest_xp_gain = max(1, len(looted_mats) * (zone // 100))
            harvest_xp_gain = int(harvest_xp_gain * (1 + title_bonuses.get("harvest_xp_pct", 0) / 100))
            await db.add_profession_xp(user_id, "harvest", harvest_xp_gain)

    # Drop équipement
    for eq_drop in get_equipment_drops(zone, player["class"], boss_type, drop_source="monde"):
        await db.add_equipment(user_id, eq_drop["item_id"], eq_drop["rarity"],
                               eq_drop["enhancement"], eq_drop.get("level", 1))
        eq_name = format_item_name(eq_drop["item_id"], eq_drop["rarity"])
        rewards_lines.append(f"⚔️ Équipement : **{eq_name}** *(nv. {eq_drop.get('level', 1)})*!")

    # Avancer dans les zones
    player_updated = await db.get_player(user_id)
    zone  = player_updated.get("zone", 1)
    stage = player_updated.get("stage", 1)
    new_zone, new_stage = _advance_zone(zone, stage)
    await db.update_player(user_id, zone=new_zone, stage=new_stage)

    # Passif quête 1 : chance de gagner +1 énergie après combat gagné
    import random as _random
    energy_on_win = player_updated.get("energy_on_win_chance", 0.0)
    if energy_on_win > 0 and _random.random() < energy_on_win:
        cur_e = player_updated.get("energy", 0)
        max_e = player_updated.get("max_energy", 2000)
        if cur_e < max_e:
            await db.update_player(user_id, energy=min(cur_e + 1, max_e))
            rewards_lines.append("⚡ +1 énergie (passif)")

    # Bonus énergie par victoire (food buff energy_on_win)
    await db.apply_energy_on_win(user_id, player_updated, rewards_lines)

    # Titres
    is_boss = boss_type != "monster"
    await increment_and_check_title(user_id, "t_boss_1k" if is_boss else "t_explorateur")
    if boss_type == "boss_emblematique":
        await increment_and_check_title(user_id, "t_boss_embl")
    player_final = await db.get_player(user_id)
    await check_all_titles(user_id, player_final)

    return "\n".join(rewards_lines)


async def _consume_combat_food_buffs(user_id: int):
    """Décrémente les buffs alimentaires de combat (délégué à database.consume_food_buffs)."""
    await db.consume_food_buffs(user_id)


def _advance_zone(zone: int, stage: int | str) -> tuple[int, int | str]:
    """Avance d'un stage ou d'une zone.
    Enchaînement : ennemis 1-10 → boss → boss_runique (×10) → boss_emblematique (×100) → boss_antique (×1000) → zone+1.
    """
    if isinstance(stage, int) or (isinstance(stage, str) and stage.isdigit()):
        s = int(stage)
        if s >= 10:
            return zone, "boss"
        return zone, s + 1

    if stage == "boss":
        if zone % 10 == 0:
            return zone, "boss_runique"
        return zone + 1, 1

    if stage == "boss_runique":
        if zone % 100 == 0:
            return zone, "boss_emblematique"
        return zone + 1, 1

    if stage == "boss_emblematique":
        if zone % 1000 == 0:
            return zone, "boss_antique"
        return zone + 1, 1

    if stage == "boss_antique":
        return zone + 1, 1

    return zone + 1, 1


# ─── Mode Farm ─────────────────────────────────────────────────────────────

async def _build_farm_info(user_id: int, player: dict, zone: int) -> tuple[discord.Embed, "FarmView"]:
    """Construit l'embed + vue farm pour une zone donnée."""
    import random as _r
    farm_stage = _r.randint(1, 10)
    enemy = get_enemy_for_zone(zone, farm_stage)

    equipment = await db.get_equipment(user_id)
    equipped  = [e for e in equipment if e.get("slot_equipped")]
    set_bonus = get_set_bonus(equipped)
    total_stats = compute_total_stats(player["class"], player["level"], player.get("prestige_level", 0), equipped, set_bonus["stats"])
    max_hp    = compute_max_hp(total_stats)
    current_hp = player.get("current_hp") or max_hp

    from bot.cogs.rpg.models import CLASS_EMOJI
    xp_reward   = max(1, int(combat_xp_reward(zone, "monster") * FARM_XP_MULT))
    gold_reward = max(1, int(combat_gold_reward(zone, "monster") * FARM_GOLD_MULT))

    embed = discord.Embed(
        title=f"{enemy.get('theme_emoji', '🌾')} {enemy['name']}",
        description=f"Zone **{zone}-Farm** | Ennemi de Farm\nClasse : {CLASS_EMOJI.get(enemy['class'], '')} {enemy['class']}",
        color=0x607D8B,
    )
    embed.add_field(
        name="👤 Tes Stats",
        value=(
            f"❤️ HP : {hp_bar(current_hp, max_hp, 15)} {current_hp:,}/{max_hp:,}\n"
            f"⚔️ **Attaque Physique** : {total_stats.get('p_atk', 0):,}   🔮 **Attaque Magique** : {total_stats.get('m_atk', 0):,}\n"
            f"🛡️ **Défense Physique** : {total_stats.get('p_def', 0):,}   🔷 **Défense Magique** : {total_stats.get('m_def', 0):,}\n"
            f"⚡ **Vitesse** : {total_stats.get('speed', 0):,}   🎯 **Chance Critique** : {total_stats.get('crit_chance', 0):.1f}%"
        ),
        inline=True,
    )
    embed.add_field(
        name=f"💀 Stats de {enemy['name']}",
        value=format_enemy_stats(enemy),
        inline=True,
    )
    embed.add_field(
        name="🎁 Récompenses Farm",
        value=(
            f"✨ XP : **{xp_reward:,}** | 💰 Gold : **{gold_reward:,}** | ⚡ Énergie : **-1**\n"
            f"⚠️ Loots ÷{FARM_LOOT_DIV} | Pas d'avancement de zone"
        ),
        inline=False,
    )
    embed.add_field(name="⚡ Énergie actuelle", value=f"**{player.get('energy', 0)}/{player.get('max_energy', 2000)}**", inline=True)

    view = FarmView(user_id, player, enemy, zone)
    return embed, view


class FarmView(discord.ui.View):
    def __init__(self, user_id: int, player: dict, enemy: dict, zone: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.player  = player
        self.enemy   = enemy
        self.zone    = zone

        farm_btn = discord.ui.Button(label="Farm", style=discord.ButtonStyle.danger, emoji="🌾", custom_id="rpg:monde:farm_do")
        farm_btn.callback = self._farm
        self.add_item(farm_btn)

        farm_loop_btn = discord.ui.Button(label="Farm en Boucle", style=discord.ButtonStyle.secondary, emoji="🔄", custom_id="rpg:monde:farm_loop")
        farm_loop_btn.callback = self._farm_loop
        self.add_item(farm_loop_btn)

        show_boss_btn = discord.ui.Button(label="Afficher le Combat", style=discord.ButtonStyle.primary, emoji="⚔️", custom_id="rpg:monde:farm_show_boss")
        show_boss_btn.callback = self._show_boss_combat
        self.add_item(show_boss_btn)

        loot_btn = discord.ui.Button(label="Infos Loot", style=discord.ButtonStyle.primary, emoji="📦", custom_id="rpg:monde:farm_loot_info")
        loot_btn.callback = self._loot_info
        self.add_item(loot_btn)

    async def _farm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        cost = ENERGY_COST.get("ennemi", 1)
        if player.get("energy", 0) < cost:
            await interaction.response.send_message(f"❌ Pas assez d'énergie ! (besoin : **{cost}**)", ephemeral=True)
            return
        await db.update_player(self.user_id, energy=max(0, player["energy"] - cost))
        await _run_farm_combat(interaction, player, self.enemy, self.zone)

    async def _farm_loop(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        cost = ENERGY_COST.get("ennemi", 1)
        if player.get("energy", 0) < cost:
            await interaction.response.send_message(f"❌ Pas assez d'énergie ! (besoin : **{cost}**)", ephemeral=True)
            return
        loop_view = FarmAutoLoopView(self.user_id, self.zone)
        embed = discord.Embed(
            title="🌾 Farm en Boucle",
            description=f"Zone **{self.zone}-Farm** — Lancement du farm automatique...\n\n*Appuie sur Stop pour arrêter.*",
            color=0x607D8B,
        )
        await interaction.response.edit_message(embed=embed, view=loop_view)
        asyncio.create_task(_run_farm_auto_loop(interaction, loop_view, self.zone))

    async def _show_boss_combat(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        embed, view = await _build_combat_info(self.user_id, player, self.zone, "boss")
        await interaction.response.edit_message(embed=embed, view=view)

    async def _loot_info(self, interaction: discord.Interaction):
        prof = await db.get_professions(self.user_id)
        harvest_type  = prof.get("harvest_type") if prof else None
        harvest_level = prof.get("harvest_level", 0) if prof else 0
        tier_cap = min(10, harvest_level // 10 + 1)
        drop_table = get_material_drop_table(self.zone, harvest_type, harvest_level, tier_cap=tier_cap)

        title_bonuses = await db.get_title_bonuses(self.user_id)
        loot_pct = title_bonuses.get("monde_loot_pct", 0)
        farm_loot_mult = (1 + loot_pct / 100) / FARM_LOOT_DIV

        drop_table.sort(key=lambda x: x["chance"], reverse=True)
        lines = []
        for drop in drop_table[:20]:
            mat_data = MATERIALS.get(drop["item_id"], {})
            chance = drop["chance"] * farm_loot_mult
            if chance >= 100:
                guaranteed = int(chance / 100)
                extra = chance % 100
                chance_str = f"×{guaranteed} +{extra:.0f}%"
            else:
                chance_str = f"{chance:.1f}%"
            lines.append(f"{mat_data.get('emoji', '?')} **{mat_data.get('name', drop['item_id'])}** — {chance_str}")

        lines.append(f"\n⚔️ **Équipement** — 10% (classe) + 1% (autre)")
        lines.append(f"⚠️ *Loots ÷{FARM_LOOT_DIV} en mode Farm*")

        embed = discord.Embed(
            title=f"📦 Loots Farm — Zone {self.zone}",
            description="\n".join(lines),
            color=0xFF9800,
        )
        footer = "×N +X% = N garantis + X% chance (N+1)ème | Indépendants."
        if loot_pct:
            footer += f" | Bonus loot titre : +{loot_pct:.0f}% appliqué."
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def _run_farm_combat(interaction: discord.Interaction, player: dict, enemy: dict, zone: int):
    """Lance un combat farm et affiche le résultat."""
    equipment = await db.get_equipment(interaction.user.id)
    relics    = await db.get_relics(interaction.user.id)
    result    = run_full_combat(player, enemy, equipment, relics, player.get("current_hp"))

    await db.update_player(interaction.user.id, current_hp=max(1, result["player_hp_remaining"]))

    if result["won"]:
        rewards = await _apply_farm_rewards(interaction.user.id, player, enemy, zone, result)
        desc = (
            f"✅ **Victoire** en **{result['turns']}** tours !\n"
            f"❤️ HP restants : {result['player_hp_remaining']:,}/{result['player_max_hp']:,}\n\n"
            f"**Récompenses (Farm) :**\n{rewards}"
        )
        color = 0x00FF88
    else:
        await db.update_player(interaction.user.id, current_hp=1)
        desc = f"❌ **Défaite** après **{result['turns']}** tours... Tu te réveilles avec 1 HP."
        color = 0xFF4444

    log_preview = "\n".join(result["log"][-10:]) if result["log"] else ""
    embed = discord.Embed(title=f"🌾 Farm — {enemy['name']}", description=desc, color=color)
    if log_preview:
        embed.add_field(name="📜 Derniers tours", value=log_preview[:1000], inline=False)

    result_view = FarmResultView(interaction.user.id, zone)
    await interaction.response.edit_message(embed=embed, view=result_view)


class FarmResultView(discord.ui.View):
    """Vue après un combat farm : Farm Suivant ou retour au Boss."""

    def __init__(self, user_id: int, zone: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.zone    = zone

        farm_next_btn = discord.ui.Button(label="Farm Suivant", style=discord.ButtonStyle.success, emoji="🌾", custom_id="rpg:monde:farm_next")
        farm_next_btn.callback = self._farm_next
        self.add_item(farm_next_btn)

        boss_btn = discord.ui.Button(label="Afficher le Combat", style=discord.ButtonStyle.primary, emoji="⚔️", custom_id="rpg:monde:farm_to_boss")
        boss_btn.callback = self._to_boss
        self.add_item(boss_btn)

    async def _farm_next(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        embed, view = await _build_farm_info(self.user_id, player, self.zone)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _to_boss(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        embed, view = await _build_combat_info(self.user_id, player, self.zone, "boss")
        await interaction.response.edit_message(embed=embed, view=view)


async def _apply_farm_rewards(user_id: int, player: dict, enemy: dict, zone: int, result: dict) -> str:
    """Distribue les récompenses farm : 10% XP/gold, loots ÷2, pas d'avancement de zone."""
    xp_gain   = max(1, int(combat_xp_reward(zone, "monster") * FARM_XP_MULT))
    gold_gain = max(1, int(combat_gold_reward(zone, "monster") * FARM_GOLD_MULT))

    # Bonus titres (appliqués après le ×10% farm)
    title_bonuses = await db.get_title_bonuses(user_id)
    xp_gain   = int(xp_gain   * (1 + title_bonuses.get("xp_pct",   0) / 100))
    gold_gain = int(gold_gain  * (1 + title_bonuses.get("gold_pct", 0) / 100))

    player = await db.get_player(user_id)
    new_gold = player["gold"] + gold_gain
    new_xp   = player["xp"]  + xp_gain
    new_level, new_xp = level_up(player["level"], new_xp)
    await db.update_player(user_id, gold=new_gold, xp=new_xp, level=new_level)

    rewards_lines = [f"✨ +{xp_gain:,} XP | 💰 +{gold_gain:,} golds *(×10%)*"]
    if new_level > player["level"]:
        rewards_lines.append(f"🎉 Niveau {new_level} atteint !")

    # Loots matériaux ÷ FARM_LOOT_DIV
    import random as _r
    prof = await db.get_professions(user_id)
    harvest_type  = prof.get("harvest_type") if prof else None
    harvest_level = prof.get("harvest_level", 0) if prof else 0
    tier_cap = min(10, harvest_level // 10 + 1)
    drop_table = get_material_drop_table(zone, harvest_type, harvest_level, tier_cap=tier_cap)

    farm_loot_mult = (1 + title_bonuses.get("monde_loot_pct", 0) / 100) / FARM_LOOT_DIV
    looted_mats = []
    for drop in drop_table:
        chance    = drop["chance"] * farm_loot_mult
        guaranteed = int(chance / 100)
        extra      = chance % 100
        qty = guaranteed + (1 if _r.random() * 100 < extra else 0)
        if qty > 0:
            await db.add_material(user_id, drop["item_id"], qty)
            mat_name = MATERIALS.get(drop["item_id"], {}).get("name", drop["item_id"])
            looted_mats.append(f"{mat_name} ×{qty}" if qty > 1 else mat_name)

    if looted_mats:
        rewards_lines.append(f"📦 Matériaux : {', '.join(looted_mats[:5])}" + (" ..." if len(looted_mats) > 5 else ""))
        if harvest_type:
            harvest_xp_gain = max(1, len(looted_mats) * (zone // 100))
            harvest_xp_gain = int(harvest_xp_gain * (1 + title_bonuses.get("harvest_xp_pct", 0) / 100))
            await db.add_profession_xp(user_id, "harvest", harvest_xp_gain)

    # Drop équipement ÷ FARM_LOOT_DIV (filtre supplémentaire à 50%)
    for eq_drop in get_equipment_drops(zone, player["class"], "monster", drop_source="monde"):
        if _r.random() < (1 / FARM_LOOT_DIV):
            await db.add_equipment(user_id, eq_drop["item_id"], eq_drop["rarity"],
                                   eq_drop["enhancement"], eq_drop.get("level", 1))
            eq_name = format_item_name(eq_drop["item_id"], eq_drop["rarity"])
            rewards_lines.append(f"⚔️ Équipement : **{eq_name}** *(nv. {eq_drop.get('level', 1)})*!")

    rewards_lines.append("📍 Zone conservée (mode Farm)")
    return "\n".join(rewards_lines)


class FarmAutoLoopView(discord.ui.View):
    """Vue pendant le farm en boucle — uniquement le bouton Stop."""

    def __init__(self, user_id: int, zone: int):
        super().__init__(timeout=600)
        self.user_id     = user_id
        self.zone        = zone
        self.running     = True
        self.combats_won = 0
        self.stop_reason = ""

        stop_btn = discord.ui.Button(label="Stop", style=discord.ButtonStyle.danger, emoji="🛑")
        stop_btn.callback = self._stop
        self.add_item(stop_btn)

    async def _stop(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        self.running     = False
        self.stop_reason = "Manuel"
        await interaction.response.defer()


async def _run_farm_auto_loop(orig_interaction: discord.Interaction, view: FarmAutoLoopView, zone: int):
    """Boucle de farm automatique — édite le message toutes les 3 s."""
    import random as _r
    user_id = view.user_id

    while view.running:
        player = await db.get_player(user_id)
        if not player:
            view.running     = False
            view.stop_reason = "Profil introuvable"
            break

        cost = ENERGY_COST.get("ennemi", 1)
        if player.get("energy", 0) < cost:
            view.running     = False
            view.stop_reason = "Plus d'énergie"
            break

        farm_stage = _r.randint(1, 10)
        enemy = get_enemy_for_zone(zone, farm_stage)

        await db.update_player(user_id, energy=max(0, player["energy"] - cost))
        equipment = await db.get_equipment(user_id)
        relics    = await db.get_relics(user_id)
        result    = run_full_combat(player, enemy, equipment, relics, player.get("current_hp"))

        if result["won"]:
            view.combats_won += 1
            rewards_str = await _apply_farm_rewards(user_id, player, enemy, zone, result)
            await db.update_player(user_id, current_hp=max(1, result["player_hp_remaining"]))

            embed = discord.Embed(
                title="🌾 Farm en Boucle",
                description=(
                    f"📍 Zone **{zone}-Farm** — {enemy['name']}\n"
                    f"**Farm #{view.combats_won}** — ✅ Victoire en **{result['turns']}** tours !\n\n"
                    f"{rewards_str}\n\n"
                    f"*Prochain farm dans 3 secondes... (Stop pour arrêter)*"
                ),
                color=0x00FF88,
            )
            if not view.running:
                break
            try:
                await orig_interaction.edit_original_response(embed=embed, view=view)
            except Exception:
                pass
        else:
            gold_lost   = int(player.get("gold", 0) * 0.10)
            energy_lost = min(10, player.get("energy", 0))
            blocked_until = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            await db.update_player(
                user_id, current_hp=1,
                gold=max(0, player.get("gold", 0) - gold_lost),
                energy=max(0, player.get("energy", 0) - energy_lost),
                regen_blocked_until=blocked_until,
                death_gold_lost=gold_lost,
                death_energy_lost=energy_lost,
            )
            view.running     = False
            view.stop_reason = "Mort au combat"
            embed = discord.Embed(
                title="🌾 Farm en Boucle",
                description=(
                    f"📍 Zone **{zone}-Farm** — {enemy['name']}\n"
                    f"**Farm #{view.combats_won + 1}** — ❌ Défaite !\n"
                    f"💸 -{gold_lost:,} gold | ⚡ -{energy_lost} énergie | 😴 Regen bloquée 1h"
                ),
                color=0xFF4444,
            )
            try:
                await orig_interaction.edit_original_response(embed=embed, view=view)
            except Exception:
                pass
            break

        await asyncio.sleep(3)

    await _show_farm_summary(orig_interaction, view, zone)


async def _show_farm_summary(orig_interaction: discord.Interaction, view: FarmAutoLoopView, zone: int):
    """Résumé final de la boucle de farm."""
    reason_map = {
        "Manuel":             "⏹️ Arrêté manuellement",
        "Plus d'énergie":     "⚡ Plus d'énergie",
        "Mort au combat":     "💀 Mort au combat",
        "Profil introuvable": "❌ Profil introuvable",
    }
    stop_txt = reason_map.get(view.stop_reason, view.stop_reason or "⏹️ Arrêté")

    embed = discord.Embed(
        title="🛑 Farm en Boucle — Résumé",
        description=(
            f"{stop_txt}\n\n"
            f"**Farms gagnés :** {view.combats_won}\n\n"
            f"*Farm Suivant pour continuer, ou Afficher le Combat pour revenir au boss !*"
        ),
        color=0x607D8B,
    )
    result_view = FarmResultView(view.user_id, zone)
    try:
        await orig_interaction.edit_original_response(embed=embed, view=result_view)
    except Exception:
        pass


# ─── Build hub ─────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🗺️ Hub Monde",
        description=(
            "Explorez le monde et combattez des ennemis toujours plus puissants !\n\n"
            "**Structure des zones :**\n"
            "• Zones **X-1** à **X-10** : Ennemis classiques (1 énergie)\n"
            "• Zone **X-Boss** : Boss de zone (2 énergies)\n"
            "• Toutes les **100 zones** : Boss Emblématique 🌟 (5 énergies) — Combat Manuel\n"
            "• Tous les **1000 zones** : Boss Antique ⚠️ (10 énergies) — Combat Manuel\n"
            "• Zone **10000** : Boss Final 🌈 — Chromastrix !\n\n"
            "**Système :**\n"
            "• ⚡ Chaque combat coûte de l'énergie\n"
            "• ❤️ Tes HP sont conservés entre les combats\n"
            "• 📦 Chaque victoire peut dropper des matériaux et équipements\n"
            "• 🔄 Mode automatique disponible pour les ennemis classiques et boss de zone\n"
        ),
        color=0x2196F3,
    )
    embed.set_footer(text="Cliquez sur Afficher le Combat pour commencer !")
    view = MondeHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
