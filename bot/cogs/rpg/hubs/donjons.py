"""
Hub Donjons — Classiques, Élite, Abyssaux.
Canal : 1468959474151587871
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    compute_total_stats, compute_max_hp, get_set_bonus,
    level_up, ENERGY_COST, STAT_FR, STAT_EMOJI, item_tier_label,
)
from bot.cogs.rpg.enemies import DUNGEON_BOSSES, generate_dungeon_boss, format_enemy_stats
from bot.cogs.rpg.items import get_equipment_drops, format_item_name, MATERIALS, get_material_drop_table
from bot.cogs.rpg.combat import build_combat_state, run_one_turn, hp_bar, CombatState, get_spell_buttons_data, format_status_effects
from bot.cogs.rpg.core import increment_and_check_title

_active_dungeon_combats: dict[int, tuple[CombatState, dict]] = {}  # user_id → (state, enemy)
_dungeon_combat_started_at: dict[int, float] = {}   # user_id → timestamp de début (pour cleanup)

DIFFICULTIES = {
    "classique": {"name": "Classique", "emoji": "🟩", "color": 0x4CAF50, "factor": 0.33},
    "elite":     {"name": "Élite",     "emoji": "🟦", "color": 0x2196F3, "factor": 0.66},
    "abyssal":   {"name": "Abyssal",   "emoji": "🟥", "color": 0xFF4444, "factor": 0.99},
}

def _dungeon_min_level(difficulty: str) -> int:
    """Niveau minimum recommandé = zone_equiv(donjon_level=1) // 10."""
    zone_offsets = {"classique": 0, "elite": 3333, "abyssal": 6666}
    zone_equiv_min = zone_offsets.get(difficulty, 0) + 1 * 33
    return max(1, zone_equiv_min // 10)


def _zone_equiv(difficulty: str, level: int) -> int:
    zone_offsets = {"classique": 0, "elite": 3333, "abyssal": 6666}
    return zone_offsets.get(difficulty, 0) + level * 33


class DonjonsHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Donjons Classiques", style=discord.ButtonStyle.success, emoji="🟩", custom_id="rpg:donjons:classique", row=0)
    async def classique(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _show_dungeon_list(interaction, "classique")

    @discord.ui.button(label="Donjons Élite", style=discord.ButtonStyle.primary, emoji="🟦", custom_id="rpg:donjons:elite", row=0)
    async def elite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _show_dungeon_list(interaction, "elite")

    @discord.ui.button(label="Donjons Abyssaux", style=discord.ButtonStyle.danger, emoji="🟥", custom_id="rpg:donjons:abyssal", row=0)
    async def abyssal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _show_dungeon_list(interaction, "abyssal")


async def _show_dungeon_list(interaction: discord.Interaction, difficulty: str):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    if not player.get("class"):
        await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
        return

    diff_data = DIFFICULTIES[difficulty]
    min_level = _dungeon_min_level(difficulty)
    if player.get("level", 1) < min_level:
        await interaction.response.send_message(
            f"🔒 Les donjons **{diff_data['name']}** sont accessibles à partir du **niveau {min_level}**.\n"
            f"Ton niveau actuel : **{player.get('level', 1)}** — Continue à progresser dans le monde !",
            ephemeral=True,
        )
        return

    energy_key = f"donjon_{difficulty}"
    energy_cost = ENERGY_COST.get(energy_key, 3)
    dungeon_level = max(1, min(100, player.get("zone", 1) // 10))
    zone_equiv = _zone_equiv(difficulty, dungeon_level)
    title_bonuses = await db.get_title_bonuses(interaction.user.id)
    xp_pct   = title_bonuses.get("xp_pct",   0)
    gold_pct = title_bonuses.get("gold_pct", 0)
    xp_estim   = round(zone_equiv * 10 * (1 + xp_pct   / 100))
    gold_estim = round(zone_equiv * 3  * (1 + gold_pct / 100))
    xp_suffix   = f" *(+{xp_pct:.0f}% titre)*"   if xp_pct   else ""
    gold_suffix = f" *(+{gold_pct:.0f}% titre)*" if gold_pct else ""

    embed = discord.Embed(
        title=f"{diff_data['emoji']} Donjons {diff_data['name']}",
        description=(
            f"Il y a **{len(DUNGEON_BOSSES)} boss** de donjons, chacun associé à un **slot d'équipement** avec un **passif unique**.\n"
            f"Coût : **{energy_cost} énergies** par combat\n"
            f"⚡ Énergie actuelle : **{player.get('energy', 0)}/{player.get('max_energy', 2000)}**\n"
            f"📊 Niveau du donjon : **{dungeon_level}** (zone equiv. **{zone_equiv}**)\n"
            f"🎁 Récompenses : **~{xp_estim:,} XP**{xp_suffix} | **~{gold_estim:,} golds**{gold_suffix} | **1 item niveau {zone_equiv // 10}**"
        ),
        color=diff_data["color"],
    )

    for boss in DUNGEON_BOSSES:
        stat_boost_fr = STAT_FR.get(boss['stat_boost'], boss['stat_boost'])
        embed.add_field(
            name=f"{boss['emoji']} {boss['name']}",
            value=f"Stat décuplée : **{stat_boost_fr}**\nPassif : *{boss['passif']}*",
            inline=True,
        )

    view = DungeonListView(interaction.user.id, player, difficulty)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class DungeonListView(discord.ui.View):
    def __init__(self, user_id: int, player: dict, difficulty: str):
        super().__init__(timeout=120)
        self.user_id    = user_id
        self.player     = player
        self.difficulty = difficulty

        for boss in DUNGEON_BOSSES:
            btn = discord.ui.Button(
                label=boss["name"][:80],
                emoji=boss["emoji"],
                style=discord.ButtonStyle.primary,
                custom_id=f"rpg:donjons:select:{difficulty}:{boss['id']}",
            )
            btn.callback = self._make_cb(boss["id"])
            self.add_item(btn)

    def _make_cb(self, boss_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
                return
            player = await db.get_player(self.user_id)
            # Niveau du donjon = zone / 10 (entre 1 et 100)
            zone  = player.get("zone", 1)
            level = max(1, min(100, zone // 10))
            enemy = generate_dungeon_boss(boss_id, self.difficulty, level)

            equipment = await db.get_equipment(self.user_id)
            equipped  = [e for e in equipment if e.get("slot_equipped")]
            set_bonus = get_set_bonus(equipped)
            total_stats = compute_total_stats(player["class"], player["level"], player.get("prestige_level", 0), equipped, set_bonus["stats"])
            max_hp    = compute_max_hp(total_stats)
            current_hp= player.get("current_hp") or max_hp

            diff_data  = DIFFICULTIES[self.difficulty]
            energy_key = f"donjon_{self.difficulty}"
            energy_cost = ENERGY_COST.get(energy_key, 3)

            embed = discord.Embed(
                title=f"{enemy.get('theme_emoji', '🏰')} {enemy['name']}",
                description=f"Donjon {diff_data['name']} — Niveau {level}\nPassif : *{enemy.get('passif', '')}*",
                color=diff_data["color"],
            )
            embed.add_field(
                name="👤 Tes Stats",
                value=(
                    f"❤️ {hp_bar(current_hp, max_hp, 12)} {current_hp:,}/{max_hp:,}\n"
                    f"⚔️ **Attaque Physique** : {total_stats.get('p_atk', 0):,}   🔮 **Attaque Magique** : {total_stats.get('m_atk', 0):,}\n"
                    f"🛡️ **Défense Physique** : {total_stats.get('p_def', 0):,}   🔷 **Défense Magique** : {total_stats.get('m_def', 0):,}"
                ),
                inline=True,
            )
            embed.add_field(
                name=f"💀 {enemy['name']}",
                value=format_enemy_stats(enemy),
                inline=True,
            )
            zone_equiv = _zone_equiv(self.difficulty, level)
            title_bonuses = await db.get_title_bonuses(self.user_id)
            _xp_pct   = title_bonuses.get("xp_pct",   0)
            _gold_pct = title_bonuses.get("gold_pct", 0)
            _xp_estim   = round(zone_equiv * 10 * (1 + _xp_pct   / 100))
            _gold_estim = round(zone_equiv * 3  * (1 + _gold_pct / 100))
            _xp_suffix   = f" *(+{_xp_pct:.0f}% titre)*"   if _xp_pct   else ""
            _gold_suffix = f" *(+{_gold_pct:.0f}% titre)*" if _gold_pct else ""
            embed.add_field(
                name="🎁 Récompenses estimées",
                value=(
                    f"✨ XP : **~{_xp_estim:,}**{_xp_suffix} | 💰 Gold : **~{_gold_estim:,}**{_gold_suffix}\n"
                    f"⚔️ Item niveau **{zone_equiv // 10}** garanti\n"
                    f"⚡ Énergie : **-{energy_cost}** (actuel : **{player.get('energy', 0)}**)"
                ),
                inline=False,
            )

            view = DungeonCombatView(self.user_id, enemy, self.difficulty, level)
            await interaction.response.edit_message(embed=embed, view=view)
        return callback


class DungeonCombatView(discord.ui.View):
    def __init__(self, user_id: int, enemy: dict, difficulty: str, level: int, player_class: str = ""):
        super().__init__(timeout=300)
        self.user_id      = user_id
        self.enemy        = enemy
        self.difficulty   = difficulty
        self.level        = level
        self.player_class = player_class
        self._build_buttons(state=None)

    def _build_buttons(self, state: CombatState | None):
        """Reconstruit tous les boutons (attaque de base + sorts)."""
        self.clear_items()

        # Ligne 0 : attaque de base + infos loot
        atk_btn = discord.ui.Button(label="Attaquer", style=discord.ButtonStyle.danger, emoji="⚔️", row=0)
        atk_btn.callback = self._make_action_cb(None)
        self.add_item(atk_btn)

        loot_btn = discord.ui.Button(label="Infos Loot", style=discord.ButtonStyle.secondary, emoji="📦", row=0)
        loot_btn.callback = self._loot_info
        self.add_item(loot_btn)

        # Ligne 1 : sorts (si classe connue et état actif)
        if state and self.player_class:
            for bdata in get_spell_buttons_data(self.player_class, state):
                style = discord.ButtonStyle.red if bdata["is_ultimate"] else discord.ButtonStyle.blurple
                btn = discord.ui.Button(
                    label=bdata["label"],
                    emoji=bdata["emoji"],
                    style=style,
                    disabled=bdata["disabled"],
                    row=1,
                )
                btn.callback = self._make_action_cb(bdata["key"])
                self.add_item(btn)

    def _make_action_cb(self, spell_key: str | None):
        async def callback(interaction: discord.Interaction):
            await self._do_action(interaction, spell_key)
        return callback

    async def _do_action(self, interaction: discord.Interaction, spell_key: str | None):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton combat !", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        if not player:
            await interaction.response.send_message("❌ Profil introuvable.", ephemeral=True)
            return
        # Vérifier si un combat est déjà en cours
        if self.user_id in _active_dungeon_combats:
            state, _ = _active_dungeon_combats[self.user_id]
        else:
            # Vérifier et déduire l'énergie seulement au premier tour
            energy_key  = f"donjon_{self.difficulty}"
            energy_cost = ENERGY_COST.get(energy_key, 3)
            if player.get("energy", 0) < energy_cost:
                await interaction.response.send_message(f"❌ Pas assez d'énergie ! (besoin : {energy_cost})", ephemeral=True)
                return
            if not await db.try_start_combat(self.user_id):
                await interaction.response.send_message("⚔️ Tu es déjà en combat ! Termine ton combat actuel avant d'en lancer un nouveau.", ephemeral=True)
                return
            await db.update_player(self.user_id, energy=max(0, player["energy"] - energy_cost))
            equipment = await db.get_equipment(self.user_id)
            relics    = await db.get_relics(self.user_id)
            djmap = {"classique": "djc_stats_pct", "elite": "dje_stats_pct", "abyssal": "dja_stats_pct"}
            stats_bonus_pct = await db.get_stats_bonus_pct(
                self.user_id, player, djmap.get(self.difficulty, "djc_stats_pct")
            )
            state = build_combat_state(player, self.enemy, equipment, relics, player.get("current_hp"),
                                       stats_bonus_pct=stats_bonus_pct)
            import time as _time
            self.player_class = player["class"]
            _active_dungeon_combats[self.user_id] = (state, self.enemy)
            _dungeon_combat_started_at[self.user_id] = _time.monotonic()

        result = run_one_turn(state, spell_key)
        player = await db.get_player(self.user_id)

        if result["is_over"]:
            del _active_dungeon_combats[self.user_id]
            _dungeon_combat_started_at.pop(self.user_id, None)
            # Nettoyer les flags de potion après usage
            if player.get("potion_revival_active") or player.get("potion_no_passive"):
                await db.update_player(self.user_id, potion_revival_active=0, potion_no_passive=0)
            # Décrémente les buffs alimentaires de combat
            await _consume_combat_food_buffs(self.user_id)
            await db.update_player(self.user_id, current_hp=max(1, result["player_hp"]), in_combat=0)
            if result["player_won"]:
                rewards = await _dungeon_rewards(self.user_id, player, self.enemy, self.difficulty, self.level, result)
                desc  = f"✅ **Victoire** en **{result['turn']}** tours !\n\n**Récompenses :**\n{rewards}"
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
                desc  = f"❌ **Défaite** ! Tu te réveilles avec 1 HP.\n💸 -{gold_lost:,} gold | ⚡ -{energy_lost} énergie | 😴 Regen bloquée 1h"
                color = 0xFF4444
            embed = discord.Embed(title=f"🏰 Donjon — {self.enemy['name']}", description=desc, color=color)
            log_txt = "\n".join(result["log"][-8:])[:1000]
            if log_txt:
                embed.add_field(name="📜 Dernier tour", value=log_txt, inline=False)
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            self._build_buttons(state)
            diff_data = DIFFICULTIES[self.difficulty]
            # Affichage ressource du joueur
            spell_btns = get_spell_buttons_data(self.player_class, state)
            res_info = f"\n{spell_btns[0]['resource_label']}" if spell_btns else ""
            embed = discord.Embed(
                title=f"{diff_data['emoji']} {self.enemy['name']} — Tour {result['turn']}",
                color=diff_data["color"],
            )
            embed.add_field(
                name="👤 Toi",
                value=f"❤️ {hp_bar(result['player_hp'], result['player_max_hp'], 15)}\n{result['player_hp']:,}/{result['player_max_hp']:,}{res_info}",
                inline=True,
            )
            embed.add_field(
                name=f"💀 {self.enemy['name']}",
                value=f"❤️ {hp_bar(result['enemy_hp'], result['enemy_max_hp'], 15)}\n{result['enemy_hp']:,}/{result['enemy_max_hp']:,}",
                inline=True,
            )
            status_txt = format_status_effects(state)
            if status_txt:
                embed.add_field(name="⚡ Effets actifs", value=status_txt[:512], inline=False)
            log_txt = "\n".join(result["log"][-6:])[:800]
            if log_txt:
                embed.add_field(name="📜 Dernier tour", value=log_txt, inline=False)
            await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        if self.user_id in _active_dungeon_combats:
            del _active_dungeon_combats[self.user_id]
        _dungeon_combat_started_at.pop(self.user_id, None)
        await db.update_player(self.user_id, in_combat=0)

    async def _loot_info(self, interaction: discord.Interaction):
        zone_equiv = _zone_equiv(self.difficulty, self.level)

        prof = await db.get_professions(interaction.user.id)
        harvest_type  = prof.get("harvest_type") if prof else None
        harvest_level = prof.get("harvest_level", 0) if prof else 0
        tier_cap = min(10, harvest_level // 10 + 1)
        diff_mat_mult = {"classique": 1.2, "elite": 1.4, "abyssal": 1.6}.get(self.difficulty, 1.0)
        drop_table = get_material_drop_table(zone_equiv, harvest_type, harvest_level, tier_cap=tier_cap)
        drop_table = [{"item_id": d["item_id"], "chance": round(d["chance"] * diff_mat_mult, 2)} for d in drop_table]
        drop_table.sort(key=lambda x: x["chance"], reverse=True)

        lines = ["⚔️ **Équipement** — 1 item garanti (80% ta classe, 20% autre)\n"]
        for drop in drop_table[:20]:
            mat_data = MATERIALS.get(drop["item_id"], {})
            chance = drop["chance"]
            if chance >= 100:
                guaranteed = int(chance / 100)
                extra = chance % 100
                chance_str = f"×{guaranteed} +{extra:.0f}%"
            else:
                chance_str = f"{chance:.1f}%"
            lines.append(f"{mat_data.get('emoji', '?')} **{mat_data.get('name', drop['item_id'])}** — {chance_str}")

        embed = discord.Embed(
            title=f"📦 Loots — {self.enemy['name']}",
            description="\n".join(lines),
            color=0xFF9800,
        )
        embed.set_footer(text="×N +X% = N garantis + X% de chance d'un (N+1)ème | Loots indépendants.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def _consume_combat_food_buffs(user_id: int):
    """Décrémente les buffs alimentaires de combat (délégué à database.consume_food_buffs)."""
    await db.consume_food_buffs(user_id)


async def _dungeon_rewards(user_id: int, player: dict, enemy: dict, difficulty: str, level: int, result: dict) -> str:
    zone_equiv = _zone_equiv(difficulty, level)
    xp_gain   = zone_equiv * 10
    gold_gain  = zone_equiv * 3

    # Bonus titres : XP et gold globaux
    title_bonuses = await db.get_title_bonuses(user_id)
    xp_gain   = int(xp_gain   * (1 + title_bonuses.get("xp_pct",   0) / 100))
    gold_gain = int(gold_gain  * (1 + title_bonuses.get("gold_pct", 0) / 100))

    player_latest = await db.get_player(user_id)
    new_gold = player_latest["gold"] + gold_gain
    new_xp   = player_latest["xp"]   + xp_gain
    new_level, new_xp = level_up(player_latest["level"], new_xp)
    await db.update_player(user_id, gold=new_gold, xp=new_xp, level=new_level)

    rewards_lines = [f"✨ +{xp_gain:,} XP | 💰 +{gold_gain:,} golds"]
    if new_level > player_latest["level"]:
        rewards_lines.append(f"🎉 Niveau {new_level} atteint !")

    # Équipement — 1 item garanti par donjon (80% même classe, 20% autre)
    source_map = {"classique": "donjon_classique", "elite": "donjon_elite", "abyssal": "donjon_abyssal"}
    drop_source = source_map.get(difficulty, "donjon_classique")
    for eq_drop in get_equipment_drops(zone_equiv, player_latest["class"], "dungeon",
                                       drop_source=drop_source):
        await db.add_equipment(user_id, eq_drop["item_id"], eq_drop["rarity"],
                               eq_drop["enhancement"], eq_drop.get("level", 1))
        eq_name = format_item_name(eq_drop["item_id"], eq_drop["rarity"])
        rewards_lines.append(f"⚔️ Équipement : **{eq_name}** *(nv. {eq_drop.get('level', 1)})*!")

    # Loots matériaux
    import random as _random
    prof = await db.get_professions(user_id)
    harvest_type  = prof.get("harvest_type") if prof else None
    harvest_level = prof.get("harvest_level", 0) if prof else 0
    tier_cap = min(10, harvest_level // 10 + 1)
    diff_mat_mult = {"classique": 1.2, "elite": 1.4, "abyssal": 1.6}.get(difficulty, 1.0)
    drop_table = get_material_drop_table(zone_equiv, harvest_type, harvest_level, tier_cap=tier_cap)
    drop_table = [{"item_id": d["item_id"], "chance": round(d["chance"] * diff_mat_mult, 2)} for d in drop_table]
    looted_mats = []
    for drop in drop_table:
        chance = drop["chance"]
        guaranteed = int(chance / 100)
        extra = chance % 100
        qty = guaranteed + (1 if _random.random() * 100 < extra else 0)
        if qty > 0:
            await db.add_material(user_id, drop["item_id"], qty)
            mat_name = MATERIALS.get(drop["item_id"], {}).get("name", drop["item_id"])
            looted_mats.append(f"{mat_name} ×{qty}" if qty > 1 else mat_name)
    if looted_mats:
        rewards_lines.append(f"📦 Matériaux : {', '.join(looted_mats[:5])}" + (" ..." if len(looted_mats) > 5 else ""))
        if harvest_type:
            harvest_xp_gain = max(1, len(looted_mats) * (zone_equiv // 100))
            harvest_xp_gain = int(harvest_xp_gain * (1 + title_bonuses.get("harvest_xp_pct", 0) / 100))
            await db.add_profession_xp(user_id, "harvest", harvest_xp_gain)

    # Progression quêtes — meilleur niveau de donjon complété
    await db.update_dungeon_best(user_id, difficulty, level)

    # Passif quête 1 : chance de gagner +1 énergie après combat gagné
    player_post = await db.get_player(user_id)
    energy_on_win = player_post.get("energy_on_win_chance", 0.0)
    if energy_on_win > 0 and _random.random() < energy_on_win:
        cur_e = player_post.get("energy", 0)
        max_e = player_post.get("max_energy", 2000)
        if cur_e < max_e:
            await db.update_player(user_id, energy=min(cur_e + 1, max_e))
            rewards_lines.append("⚡ +1 énergie (passif)")

    # Bonus énergie par victoire (food buff energy_on_win)
    await db.apply_energy_on_win(user_id, player_post, rewards_lines)

    # Titres donjons — basés sur le niveau maximum atteint (gérés par check_all_titles)

    return "\n".join(rewards_lines)


# ─── Build hub ─────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🏰 Hub Donjons",
        description=(
            "Les donjons proposent **10 boss** aux statistiques uniques et décuplées.\n\n"
            "**Niveaux de difficulté :**\n"
            "🟩 **Classique** — 3 énergies — Loots normaux\n"
            "🟦 **Élite** — 5 énergies — Loots améliorés\n"
            "🟥 **Abyssal** — 10 énergies — Meilleurs loots\n\n"
            "**Le niveau du donjon** correspond à votre zone divisée par 10 (max 100).\n"
            "Le Donjon Niv.100 Abyssal est comparable à la **Zone 10 000** !\n\n"
            "**Combat au tour par tour** (un clic = un tour) — Gérez bien vos HP entre les combats !"
        ),
        color=0x9C27B0,
    )
    view = DonjonsHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
