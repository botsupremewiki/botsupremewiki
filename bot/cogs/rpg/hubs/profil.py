"""
Hub Profil — Voir Profil, Inventaire, Sac à dos, Forgeron, Prestige, Récompense quotidienne.
Canal : 1464542599867269252
"""
from __future__ import annotations
import json
import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    CLASS_EMOJI, RARITY_EMOJI, SLOT_EMOJI, SLOTS,
    compute_total_stats, compute_max_hp, get_set_bonus, compute_equipment_stats,
    SET_BONUSES, SOURCE_POWER_MULT, RARITY_MULT, RARITIES,
    compute_class_stats, xp_for_level, level_up, daily_reward, MAX_LEVEL,
    STAT_FR, STAT_EMOJI, item_tier_label, stat_display,
)
from bot.cogs.rpg.items import (
    EQUIPMENT_CATALOG, CONSUMABLES, format_item_name, format_eq_name,
    get_enhancement_cost, item_sell_price, get_consumable_value,
)

ITEMS_PER_PAGE = 15
FORGE_ITEMS_PER_PAGE = 25
MARKET_COMMISSION = 0.05  # 5%

# Coût d'enchantement/déséquipement des runes (or)
_RUNE_COST_WEIGHTS = {
    "p_atk": 200, "m_atk": 200, "p_def": 150, "m_def": 150,
    "speed": 500, "crit_chance": 2000, "p_pen": 250, "m_pen": 250,
    "hp": 20, "all_stats": 500,
}

def _get_rune_equip_cost(rune_data: dict) -> int:
    effect = rune_data.get("effect", "")
    value  = rune_data.get("value", 0)
    weight = _RUNE_COST_WEIGHTS.get(effect, 200)
    return max(1000, value * weight)

def _get_rune_remove_cost(rune_bonuses: dict) -> int:
    """Coût de déséquipement = 50% du coût d'équipement de la rune stockée."""
    total = 0
    for effect, value in rune_bonuses.items():
        weight = _RUNE_COST_WEIGHTS.get(effect, 200)
        total += max(1000, value * weight)
    return total // 2

_eq_display_name = format_eq_name  # alias local


# ─── Hub principal ─────────────────────────────────────────────────────────

class ProfilHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Voir Profil", style=discord.ButtonStyle.primary, emoji="👤", custom_id="rpg:profil:voir", row=0)
    async def voir_profil(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        embed = await build_profil_embed(interaction.user, player)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Inventaire", style=discord.ButtonStyle.secondary, emoji="🎒", custom_id="rpg:profil:inventaire", row=0)
    async def inventaire(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        equipment = await db.get_equipment(interaction.user.id)
        embed, view = build_inventaire_embed(interaction.user, player, equipment, page=0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Sac à dos", style=discord.ButtonStyle.secondary, emoji="🎽", custom_id="rpg:profil:sac", row=0)
    async def sac_a_dos(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        consumables = await db.get_consumables(interaction.user.id)
        embed, view = build_sac_embed(interaction.user, player, consumables)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Forge", style=discord.ButtonStyle.secondary, emoji="⚒️", custom_id="rpg:profil:forgeron", row=0)
    async def forgeron(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        equipment = await db.get_equipment(interaction.user.id)
        consumables = await db.get_consumables(interaction.user.id)
        runes = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") == "rune"]
        embed, view = build_forgeron_embed(interaction.user, player, equipment, runes, eq_page=0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Prestige", style=discord.ButtonStyle.danger, emoji="✨", custom_id="rpg:profil:prestige", row=1)
    async def prestige(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        embed, view = build_prestige_embed(player)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Récompense Quotidienne", style=discord.ButtonStyle.success, emoji="🎁", custom_id="rpg:profil:daily", row=1)
    async def daily_reward_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        await handle_daily_reward(interaction, player)


# ─── Fonctions d'affichage ────────────────────────────────────────────────

async def build_profil_embed(user: discord.User, player: dict) -> discord.Embed:
    from bot.cogs.rpg.models import compute_total_stats, compute_max_hp, get_set_bonus
    equipment = await db.get_equipment(user.id)
    equipped  = [e for e in equipment if e.get("slot_equipped")]
    set_bonus = get_set_bonus(equipped)
    total_stats = compute_total_stats(
        player["class"], player["level"], player.get("prestige_level", 0),
        equipped, set_bonus["stats"]
    )
    max_hp = compute_max_hp(total_stats)
    current_hp = player.get("current_hp") or max_hp

    xp_needed = xp_for_level(player["level"])
    xp_pct    = min(100, player["xp"] * 100 // max(xp_needed, 1))

    embed = discord.Embed(
        title=f"👤 Profil de {user.display_name}",
        color=0x5865F2,
    )
    embed.set_thumbnail(url=user.display_avatar.url)

    embed.add_field(
        name="📊 Informations",
        value=(
            f"**Classe** : {CLASS_EMOJI.get(player['class'], '')} {player['class']}\n"
            f"**Niveau** : {player['level']}/{MAX_LEVEL}\n"
            f"**XP** : {player['xp']:,} / {xp_needed:,} ({xp_pct}%)\n"
            f"**Gold** : {player['gold']:,} 💰\n"
            f"**Zone** : {player['zone']}-{player['stage']}\n"
            f"**Prestige** : {player.get('prestige_level', 0)} (bonus +{player.get('prestige_level', 0) * 0.1:.1f}%)\n"
            f"**Élo PvP** : {player.get('pvp_elo', 1000)}\n"
        ),
        inline=False,
    )

    from bot.cogs.rpg.combat import hp_bar
    embed.add_field(
        name="❤️ Vitalité",
        value=(
            f"HP : {hp_bar(current_hp, max_hp)}\n"
            f"{current_hp:,} / {max_hp:,}\n"
            f"⚡ Énergie : **{player.get('energy', 0)}/{player.get('max_energy', 2000)}**"
        ),
        inline=False,
    )

    embed.add_field(
        name="⚔️ Stats Totales",
        value=(
            f"⚔️ **Attaque Physique** : {total_stats.get('p_atk', 0):,}   🔮 **Attaque Magique** : {total_stats.get('m_atk', 0):,}\n"
            f"🛡️ **Défense Physique** : {total_stats.get('p_def', 0):,}   🔷 **Défense Magique** : {total_stats.get('m_def', 0):,}\n"
            f"🗡️ **Pénétration Physique** : {total_stats.get('p_pen', 0):,}   💫 **Pénétration Magique** : {total_stats.get('m_pen', 0):,}\n"
            f"⚡ **Vitesse** : {total_stats.get('speed', 0):,}   🎯 **Chance Critique** : {total_stats.get('crit_chance', 0):.1f}%   💥 **Dégâts Critiques** : {total_stats.get('crit_damage', 150):.0f}%"
        ),
        inline=False,
    )

    if set_bonus["passives"]:
        embed.add_field(
            name="💎 Bonus de Panoplie",
            value="\n".join(set_bonus["passives"]),
            inline=False,
        )

    return embed


def build_inventaire_embed(user: discord.User, player: dict, equipment: list[dict], page: int = 0) -> tuple:
    equipped    = [e for e in equipment if e.get("slot_equipped")]
    unequipped  = [e for e in equipment if not e.get("slot_equipped")]
    total_pages = max(1, (len(unequipped) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

    embed = discord.Embed(
        title=f"🎒 Inventaire — {user.display_name}",
        color=0x5865F2,
    )

    # Équipements portés (par slot)
    equipped_text = ""
    for slot in SLOTS:
        slot_item = next((e for e in equipped if e["slot_equipped"] == slot), None)
        if slot_item:
            name = _eq_display_name(slot_item)
            equipped_text += f"{SLOT_EMOJI[slot]} **{slot.capitalize()}** : {name}\n"
        else:
            equipped_text += f"{SLOT_EMOJI[slot]} **{slot.capitalize()}** : *vide*\n"
    embed.add_field(name="🧥 Équipement Porté", value=equipped_text or "*Aucun*", inline=False)

    # Stats des équipements
    eq_stats = compute_equipment_stats(equipped)
    if equipped:
        STAT_LABEL = {
            "hp": "❤️ Points de Vie", "p_atk": "⚔️ Attaque Physique", "m_atk": "🔮 Attaque Magique",
            "p_def": "🛡️ Défense Physique", "m_def": "🔷 Défense Magique",
            "p_pen": "🗡️ Pénétration Physique", "m_pen": "💫 Pénétration Magique",
            "speed": "⚡ Vitesse", "crit_chance": "🎯 Chance Critique", "crit_damage": "💥 Dégâts Critiques",
        }
        stat_order = ["hp", "p_atk", "m_atk", "p_def", "m_def", "p_pen", "m_pen", "speed", "crit_chance", "crit_damage"]
        stats_text = "\n".join(
            f"{STAT_LABEL[k]} : **+{eq_stats.get(k, 0):.1f}**" if k in ("crit_chance", "crit_damage")
            else f"{STAT_LABEL[k]} : **+{eq_stats.get(k, 0):,}**"
            for k in stat_order if eq_stats.get(k, 0)
        ) or "*Aucun équipement*"
        embed.add_field(name="📊 Stats des Équipements", value=stats_text, inline=False)

    # Panoplies équipées
    STAT_SHORT = {
        "hp": "PV", "p_atk": "ATK Physique", "m_atk": "ATK Magique",
        "p_def": "DEF Physique", "m_def": "DEF Magique", "p_pen": "PEN Physique",
        "m_pen": "PEN Magique", "speed": "Vitesse", "crit_chance": "Crit%", "crit_damage": "CritDMG%",
    }
    set_counts: dict[str, int] = {}
    min_rarity_per_set: dict[str, str] = {}
    for eq in equipped:
        item_data = EQUIPMENT_CATALOG.get(eq["item_id"])
        if not item_data:
            continue
        set_key = item_data.get("set")
        if not set_key:
            continue
        set_counts[set_key] = set_counts.get(set_key, 0) + 1
        r = eq.get("rarity", "commun")
        if set_key not in min_rarity_per_set:
            min_rarity_per_set[set_key] = r
        elif RARITIES.index(r) < RARITIES.index(min_rarity_per_set[set_key]):
            min_rarity_per_set[set_key] = r

    if set_counts:
        set_lines = []
        for set_key, count in set_counts.items():
            set_data = SET_BONUSES.get(set_key)
            if not set_data:
                continue
            rarity      = min_rarity_per_set.get(set_key, "commun")
            r_emoji     = RARITY_EMOJI.get(rarity, "")
            mult        = RARITY_MULT[rarity] * SOURCE_POWER_MULT.get(set_data.get("source", "monde"), 1.0)
            set_name    = set_data.get("name", set_key)
            set_lines.append(f"**{set_name}** — {count}/7 pcs {r_emoji} *{rarity}*")
            for threshold, label in ((2, "2 pcs"), (3, "3 pcs"), (4, "4 pcs"), (5, "5 pcs"), (6, "6 pcs"), (7, "7 pcs")):
                if count < threshold:
                    continue
                tier = set_data.get(f"{threshold}pcs", {})
                if not tier:
                    continue
                passive = tier.get("passive")
                if passive:
                    txt = passive if len(passive) <= 80 else passive[:77] + "…"
                    set_lines.append(f"  ✅ **{label}** : {txt}")
                else:
                    stats_str = " | ".join(
                        f"{STAT_SHORT.get(k, k)} +{int(v * mult)}" for k, v in tier.items()
                    )
                    set_lines.append(f"  ✅ **{label}** : {stats_str}")
            set_lines.append("")

        set_value = "\n".join(set_lines).rstrip()
        # Discord field value limit = 1024 chars
        if len(set_value) > 1024:
            set_value = set_value[:1021] + "…"
        embed.add_field(name="💎 Panoplies Équipées", value=set_value, inline=False)

    # Bonus de runes (agrégés sur tous les items équipés)
    total_rune_bonuses: dict[str, int] = {}
    for eq in equipped:
        rb = json.loads(eq.get("rune_bonuses") or "{}")
        for k, v in rb.items():
            total_rune_bonuses[k] = total_rune_bonuses.get(k, 0) + v
    if total_rune_bonuses:
        STAT_LABEL_RUNE = {
            "hp": "❤️ PV", "p_atk": "⚔️ ATK Physique", "m_atk": "🔮 ATK Magique",
            "p_def": "🛡️ DEF Physique", "m_def": "🔷 DEF Magique",
            "p_pen": "🗡️ PEN Physique", "m_pen": "💫 PEN Magique",
            "speed": "⚡ Vitesse", "crit_chance": "🎯 Crit%", "crit_damage": "💥 CritDMG%",
        }
        rune_lines = [
            f"{STAT_LABEL_RUNE.get(k, k)} : **+{v}**" for k, v in total_rune_bonuses.items()
        ]
        embed.add_field(name="🔮 Bonus de Runes", value="\n".join(rune_lines), inline=False)

    # Inventaire (paginé)
    page_items = unequipped[page * ITEMS_PER_PAGE:(page + 1) * ITEMS_PER_PAGE]
    if page_items:
        inv_lines = []
        for idx, item in enumerate(page_items):
            name      = _eq_display_name(item)
            item_lvl  = item.get("level", 1)
            item_class = EQUIPMENT_CATALOG.get(item["item_id"], {}).get("class", "")
            suffix = f"  *(nv. {item_lvl}"
            if item_class:
                suffix += f" — {item_class}"
            suffix += ")*"
            inv_lines.append(f"`{idx + 1}.` {name}{suffix}")
        embed.add_field(
            name=f"📦 Inventaire ({len(unequipped)} items) — Page {page + 1}/{total_pages}",
            value="\n".join(inv_lines),
            inline=False,
        )
    else:
        embed.add_field(name="📦 Inventaire", value="*Vide*", inline=False)

    view = InventaireView(user.id, player, equipment, page, total_pages)
    return embed, view


class InventaireView(discord.ui.View):
    def __init__(self, user_id: int, player: dict, equipment: list[dict], page: int, total_pages: int):
        super().__init__(timeout=180)
        self.user_id     = user_id
        self.player      = player
        self.equipment   = equipment
        self.page        = page
        self.total_pages = total_pages
        self.selected_ids: list[int] = []

        equipped   = [e for e in equipment if e.get("slot_equipped")]
        unequipped = [e for e in equipment if not e.get("slot_equipped")]
        page_items = unequipped[page * ITEMS_PER_PAGE:(page + 1) * ITEMS_PER_PAGE]

        # Dropdown sélection
        if page_items:
            options = []
            for idx, item in enumerate(page_items):
                label = _eq_display_name(item)[:100]
                options.append(discord.SelectOption(
                    label=label,
                    value=str(item["id"]),
                    description=f"Slot : {EQUIPMENT_CATALOG.get(item['item_id'], {}).get('slot', '?')}",
                ))
            select = discord.ui.Select(
                placeholder="Sélectionner un équipement...",
                options=options,
                min_values=0,
                max_values=min(len(options), 7),
                custom_id="rpg:inv:select",
                row=0,
            )
            select.callback = self._on_select
            self.add_item(select)

        # Boutons équiper/déséquiper/vendre
        equip_btn = discord.ui.Button(label="Équiper", style=discord.ButtonStyle.success, emoji="✅", custom_id="rpg:inv:equip", row=1)
        equip_btn.callback = self._equip
        self.add_item(equip_btn)

        unequip_btn = discord.ui.Button(label="Déséquiper", style=discord.ButtonStyle.secondary, emoji="❌", custom_id="rpg:inv:unequip", row=1)
        unequip_btn.callback = self._unequip
        self.add_item(unequip_btn)

        sell_btn = discord.ui.Button(label="Vendre", style=discord.ButtonStyle.danger, emoji="💰", custom_id="rpg:inv:sell", row=1)
        sell_btn.callback = self._sell
        self.add_item(sell_btn)

        sell_all_btn = discord.ui.Button(label="Vendre tout (page)", style=discord.ButtonStyle.danger, emoji="🗑️", custom_id="rpg:inv:sell_all", row=2)
        sell_all_btn.callback = self._sell_all
        self.add_item(sell_all_btn)

        # Navigation
        if total_pages > 1:
            prev_btn = discord.ui.Button(label="◀", style=discord.ButtonStyle.secondary, disabled=(page == 0), custom_id="rpg:inv:prev", row=2)
            prev_btn.callback = self._prev_page
            self.add_item(prev_btn)

            next_btn = discord.ui.Button(label="▶", style=discord.ButtonStyle.secondary, disabled=(page >= total_pages - 1), custom_id="rpg:inv:next", row=2)
            next_btn.callback = self._next_page
            self.add_item(next_btn)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_ids = [int(v) for v in interaction.data["values"]]
        await interaction.response.defer()

    async def _equip(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_ids:
            await interaction.response.send_message("❌ Sélectionne d'abord un équipement.", ephemeral=True)
            return

        # Snapshot old max HP before equip changes
        old_equipped = [e for e in self.equipment if e.get("slot_equipped")]
        old_set_bonus = get_set_bonus(old_equipped)
        old_total = compute_total_stats(
            self.player["class"], self.player["level"], self.player.get("prestige_level", 0),
            old_equipped, old_set_bonus["stats"]
        )
        old_max_hp = compute_max_hp(old_total)
        old_pct = (self.player.get("current_hp") or old_max_hp) / old_max_hp

        errors = []
        equipped_count = 0
        for inv_id in self.selected_ids:
            item = next((e for e in self.equipment if e["id"] == inv_id), None)
            if not item:
                continue
            item_data = EQUIPMENT_CATALOG.get(item["item_id"])
            if not item_data:
                continue
            if item_data.get("class") != self.player.get("class"):
                errors.append(f"❌ **{format_item_name(item['item_id'], item.get('rarity'))}** — classe **{item_data['class']}** requise.")
                continue
            item_level = item.get("level", 1)
            if self.player.get("level", 1) < item_level:
                errors.append(f"❌ **{format_item_name(item['item_id'], item.get('rarity'))}** — niveau **{item_level}** requis.")
                continue
            slot = item_data["slot"]
            await db.equip_item(self.user_id, inv_id, slot)
            equipped_count += 1

        equipment = await db.get_equipment(self.user_id)
        player    = await db.get_player(self.user_id)

        # Preserve HP percentage
        if equipped_count:
            new_equipped = [e for e in equipment if e.get("slot_equipped")]
            new_set_bonus = get_set_bonus(new_equipped)
            new_total = compute_total_stats(
                player["class"], player["level"], player.get("prestige_level", 0),
                new_equipped, new_set_bonus["stats"]
            )
            new_max_hp = compute_max_hp(new_total)
            new_hp = max(1, round(new_max_hp * old_pct))
            await db.update_player(self.user_id, current_hp=new_hp)
            player = await db.get_player(self.user_id)

        embed, view = build_inventaire_embed(interaction.user, player, equipment, self.page)
        if equipped_count:
            embed.add_field(name="✅ Équipement", value=f"{equipped_count} item(s) équipé(s).", inline=False)
        if errors:
            embed.add_field(name="⚠️ Erreurs", value="\n".join(errors), inline=False)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _unequip(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_ids:
            # Déséquiper par slot
            await interaction.response.send_message("❌ Sélectionne d'abord un équipement.", ephemeral=True)
            return
        # Snapshot old max HP before unequip changes
        old_equipped = [e for e in self.equipment if e.get("slot_equipped")]
        old_set_bonus = get_set_bonus(old_equipped)
        old_total = compute_total_stats(
            self.player["class"], self.player["level"], self.player.get("prestige_level", 0),
            old_equipped, old_set_bonus["stats"]
        )
        old_max_hp = compute_max_hp(old_total)
        old_pct = (self.player.get("current_hp") or old_max_hp) / old_max_hp

        for inv_id in self.selected_ids:
            await db.unequip_item(self.user_id, inv_id)
        equipment = await db.get_equipment(self.user_id)
        player    = await db.get_player(self.user_id)

        # Preserve HP percentage
        new_equipped = [e for e in equipment if e.get("slot_equipped")]
        new_set_bonus = get_set_bonus(new_equipped)
        new_total = compute_total_stats(
            player["class"], player["level"], player.get("prestige_level", 0),
            new_equipped, new_set_bonus["stats"]
        )
        new_max_hp = compute_max_hp(new_total)
        new_hp = max(1, round(new_max_hp * old_pct))
        await db.update_player(self.user_id, current_hp=new_hp)
        player = await db.get_player(self.user_id)

        embed, view = build_inventaire_embed(interaction.user, player, equipment, self.page)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _sell(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_ids:
            await interaction.response.send_message("❌ Sélectionne d'abord un équipement.", ephemeral=True)
            return
        total_gold = 0
        for inv_id in self.selected_ids:
            item = next((e for e in self.equipment if e["id"] == inv_id), None)
            if item and not item.get("slot_equipped"):
                price = item_sell_price(item["item_id"], item.get("rarity", "commun"), item.get("enhancement", 0))
                total_gold += price
                await db.remove_equipment(self.user_id, inv_id)
        player = await db.get_player(self.user_id)
        await db.update_player(self.user_id, gold=player["gold"] + total_gold)
        equipment = await db.get_equipment(self.user_id)
        player    = await db.get_player(self.user_id)
        embed, view = build_inventaire_embed(interaction.user, player, equipment, max(0, self.page))
        embed.add_field(name="💰 Vente", value=f"Tu as vendu {len(self.selected_ids)} équipement(s) pour **{total_gold:,}** golds.", inline=False)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _sell_all(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        unequipped = [e for e in self.equipment if not e.get("slot_equipped")]
        page_items = unequipped[self.page * ITEMS_PER_PAGE:(self.page + 1) * ITEMS_PER_PAGE]
        total_gold = 0
        for item in page_items:
            price = item_sell_price(item["item_id"], item.get("rarity", "commun"), item.get("enhancement", 0))
            total_gold += price
            await db.remove_equipment(self.user_id, item["id"])
        player = await db.get_player(self.user_id)
        await db.update_player(self.user_id, gold=player["gold"] + total_gold)
        equipment = await db.get_equipment(self.user_id)
        player    = await db.get_player(self.user_id)
        embed, view = build_inventaire_embed(interaction.user, player, equipment, max(0, self.page - 1 if not equipment else self.page))
        embed.add_field(name="💰 Vente de la page", value=f"{len(page_items)} équipement(s) vendu(s) pour **{total_gold:,}** golds.", inline=False)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _prev_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        equipment = await db.get_equipment(self.user_id)
        player    = await db.get_player(self.user_id)
        embed, view = build_inventaire_embed(interaction.user, player, equipment, max(0, self.page - 1))
        await interaction.response.edit_message(embed=embed, view=view)

    async def _next_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        equipment = await db.get_equipment(self.user_id)
        player    = await db.get_player(self.user_id)
        embed, view = build_inventaire_embed(interaction.user, player, equipment, self.page + 1)
        await interaction.response.edit_message(embed=embed, view=view)


# ─── Sac à dos ────────────────────────────────────────────────────────────

def build_sac_embed(user: discord.User, player: dict, consumables: list[dict]) -> tuple:
    runes   = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") == "rune"]
    potions = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") in ("potion", "elixir")]
    foods   = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") == "food"]

    embed = discord.Embed(title=f"🎽 Sac à dos — {user.display_name}", color=0x5865F2)

    def fmt_list(items):
        if not items:
            return "*Vide*"
        return "\n".join(
            f"{CONSUMABLES.get(c['item_id'], {}).get('emoji', '?')} **{CONSUMABLES.get(c['item_id'], {}).get('name', c['item_id'])}** ×{c['quantity']}"
            for c in items
        )

    embed.add_field(name="💊 Potions & Élixirs", value=fmt_list(potions), inline=False)
    embed.add_field(name="🍞 Nourriture", value=fmt_list(foods), inline=False)
    embed.add_field(name="🔮 Runes", value=fmt_list(runes), inline=False)
    embed.set_footer(text="Sélectionne un item dans le menu puis clique sur Consommer.")

    view = SacView(user.id, player, consumables)
    return embed, view


class SacView(discord.ui.View):
    def __init__(self, user_id: int, player: dict, consumables: list[dict]):
        super().__init__(timeout=180)
        self.user_id     = user_id
        self.player      = player
        self.consumables = consumables
        self.selected_id: str | None = None

        # Dropdown — tous les consommables (potions, élixirs, nourriture, runes)
        all_items = consumables[:25]
        if all_items:
            options = []
            for c in all_items:
                data = CONSUMABLES.get(c["item_id"], {})
                item_type = data.get("type", "?")
                val = get_consumable_value(c["item_id"])
                desc = f"Type : {item_type} | Valeur : {val:,} golds/u" if val else f"Type : {item_type}"
                options.append(discord.SelectOption(
                    label=f"{data.get('name', c['item_id'])} ×{c['quantity']}"[:100],
                    value=c["item_id"],
                    emoji=data.get("emoji"),
                    description=desc[:100],
                ))
            select = discord.ui.Select(placeholder="Sélectionner un item...", options=options, custom_id="rpg:sac:select", row=0)
            select.callback = self._on_select
            self.add_item(select)

        consume_btn = discord.ui.Button(label="Consommer", style=discord.ButtonStyle.success, emoji="✅", custom_id="rpg:sac:consume", row=1)
        consume_btn.callback = self._consume
        self.add_item(consume_btn)

        auto_btn = discord.ui.Button(label="Auto HP+Énergie", style=discord.ButtonStyle.primary, emoji="🔋", custom_id="rpg:sac:auto", row=1)
        auto_btn.callback = self._auto_consume
        self.add_item(auto_btn)

        sell_btn = discord.ui.Button(label="Vendre tout", style=discord.ButtonStyle.danger, emoji="💰", custom_id="rpg:sac:sell_all", row=2)
        sell_btn.callback = self._sell_all
        self.add_item(sell_btn)

        sell_qty_btn = discord.ui.Button(label="Vendre (quantité)", style=discord.ButtonStyle.secondary, emoji="✏️", custom_id="rpg:sac:sell_qty", row=2)
        sell_qty_btn.callback = self._sell_qty
        self.add_item(sell_qty_btn)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_id = interaction.data["values"][0]
        await interaction.response.defer()

    async def _auto_consume(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        from bot.cogs.rpg.models import compute_class_stats, compute_max_hp
        cs = compute_class_stats(player["class"], player["level"], player.get("prestige_level", 0))
        max_hp     = compute_max_hp(cs)
        current_hp = player.get("current_hp") or max_hp
        cur_energy = player.get("energy", 0)
        max_energy = player.get("max_energy", 2000)

        consumables = await db.get_consumables(self.user_id)

        heal_pool = sorted(
            [(c, CONSUMABLES.get(c["item_id"], {})) for c in consumables
             if CONSUMABLES.get(c["item_id"], {}).get("effect") == "heal_pct"],
            key=lambda x: x[1].get("value", 0),
        )
        energy_pool = sorted(
            [(c, CONSUMABLES.get(c["item_id"], {})) for c in consumables
             if CONSUMABLES.get(c["item_id"], {}).get("effect") == "energy"],
            key=lambda x: x[1].get("value", 0),
        )

        # Simuler (sans toucher à la DB) pour construire le récap de confirmation
        sim_hp  = current_hp
        sim_en  = cur_energy
        hp_plan:  list[tuple[str, int]] = []   # (item_id, qty)
        en_plan:  list[tuple[str, int]] = []

        for c, data in heal_pool:
            heal_val = int(max_hp * data.get("value", 0) / 100)
            if heal_val <= 0:
                continue
            qty_left = c["quantity"]
            uses = 0
            while sim_hp < max_hp and qty_left > 0:
                sim_hp = min(max_hp, sim_hp + heal_val)
                qty_left -= 1
                uses += 1
            if uses:
                hp_plan.append((data.get("name", c["item_id"]), uses))

        for c, data in energy_pool:
            en_val = data.get("value", 0)
            if en_val <= 0:
                continue
            qty_left = c["quantity"]
            uses = 0
            while sim_en < max_energy and qty_left > 0:
                sim_en = min(max_energy, sim_en + en_val)
                qty_left -= 1
                uses += 1
            if uses:
                en_plan.append((data.get("name", c["item_id"]), uses))

        if not hp_plan and not en_plan:
            msg = "✅ HP et énergie déjà au maximum !" if current_hp >= max_hp and cur_energy >= max_energy \
                  else "❌ Aucune potion ou nourriture utilisable pour HP/énergie."
            await interaction.response.send_message(msg, ephemeral=True)
            return

        # Embed de confirmation
        lines = ["**Voici ce qui sera consommé :**\n"]
        if hp_plan:
            lines.append("❤️ **Potions :**")
            for name, qty in hp_plan:
                lines.append(f"  • {name} ×{qty}")
            lines.append(f"  → HP : **{current_hp:,}** → **{sim_hp:,}/{max_hp:,}**\n")
        if en_plan:
            lines.append("⚡ **Nourriture :**")
            for name, qty in en_plan:
                lines.append(f"  • {name} ×{qty}")
            lines.append(f"  → Énergie : **{cur_energy}** → **{sim_en}/{max_energy}**")

        embed = discord.Embed(
            title="🔋 Auto HP+Énergie — Confirmation",
            description="\n".join(lines),
            color=0x5865F2,
        )
        view = AutoConsumeConfirmView(
            self.user_id, heal_pool, energy_pool, max_hp, max_energy, current_hp, cur_energy
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def _sell_all(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_id:
            await interaction.response.send_message("❌ Sélectionne d'abord un item.", ephemeral=True)
            return
        cons = next((c for c in self.consumables if c["item_id"] == self.selected_id), None)
        if not cons:
            await interaction.response.send_message("❌ Item introuvable.", ephemeral=True)
            return
        await self._do_sell(interaction, self.selected_id, cons["quantity"])

    async def _sell_qty(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_id:
            await interaction.response.send_message("❌ Sélectionne d'abord un item.", ephemeral=True)
            return
        cons = next((c for c in self.consumables if c["item_id"] == self.selected_id), None)
        if not cons:
            await interaction.response.send_message("❌ Item introuvable.", ephemeral=True)
            return
        unit_val = get_consumable_value(self.selected_id)
        await interaction.response.send_modal(
            SellConsumableQtyModal(self.user_id, self.selected_id, cons["quantity"], unit_val)
        )

    async def _do_sell(self, interaction: discord.Interaction, item_id: str, qty: int):
        ok = await db.remove_consumable(self.user_id, item_id, qty)
        if not ok:
            await interaction.response.send_message("❌ Quantité insuffisante.", ephemeral=True)
            return
        unit_val = get_consumable_value(item_id)
        gold_earned = unit_val * qty
        player = await db.get_player(self.user_id)
        await db.update_player(self.user_id, gold=player["gold"] + gold_earned)
        data = CONSUMABLES.get(item_id, {})
        name = data.get("name", item_id)
        emoji = data.get("emoji", "")
        await interaction.response.send_message(
            f"✅ Vendu {emoji} **{name}** ×{qty} pour **{gold_earned:,}** golds 💰",
            ephemeral=True,
        )

    async def _consume(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_id:
            await interaction.response.send_message("❌ Sélectionne d'abord un item.", ephemeral=True)
            return
        item_data = CONSUMABLES.get(self.selected_id)
        if not item_data:
            await interaction.response.send_message("❌ Item inconnu.", ephemeral=True)
            return
        if item_data.get("type") == "rune":
            await interaction.response.send_message("❌ Les runes ne se consomment pas directement — elles s'appliquent pendant un combat.", ephemeral=True)
            return

        # Effets empilables → modal pour choisir la quantité
        effect = item_data.get("effect")
        if effect in ("heal_pct", "energy"):
            cons = next((c for c in self.consumables if c["item_id"] == self.selected_id), None)
            max_qty = cons["quantity"] if cons else 1
            await interaction.response.send_modal(ConsumeQtyModal(self.user_id, self.selected_id, max_qty, item_data))
            return

        removed = await db.remove_consumable(self.user_id, self.selected_id, 1)
        if not removed:
            await interaction.response.send_message("❌ Tu n'as plus cet item.", ephemeral=True)
            return

        player = await db.get_player(self.user_id)
        from bot.cogs.rpg.models import compute_class_stats, compute_max_hp
        cs     = compute_class_stats(player["class"], player["level"], player.get("prestige_level", 0))
        max_hp = compute_max_hp(cs)
        current_hp = player.get("current_hp") or max_hp
        effect  = item_data.get("effect")
        value   = item_data.get("value", 0)
        msg     = ""

        if effect == "heal_pct":
            healed = int(max_hp * value / 100)
            new_hp = min(max_hp, current_hp + healed)
            await db.update_player(self.user_id, current_hp=new_hp)
            msg = f"❤️ Soigné de **{healed:,}** HP ! ({new_hp:,}/{max_hp:,})"
        elif effect == "energy":
            new_energy = min(player.get("max_energy", 100), player.get("energy", 0) + value)
            await db.update_player(self.user_id, energy=new_energy)
            msg = f"⚡ Énergie restaurée de **{value}** ! ({new_energy}/{player.get('max_energy', 2000)})"
        elif effect == "no_death_penalty":
            # Vérifier que la pénalité est encore active
            blocked_until = player.get("regen_blocked_until")
            if not blocked_until:
                await db.add_consumable(self.user_id, self.selected_id, 1)  # rembourser la potion
                await interaction.response.send_message(
                    "❌ Aucune pénalité de mort active — la potion n'a pas été consommée.",
                    ephemeral=True,
                )
                return
            try:
                blocked_dt = datetime.fromisoformat(blocked_until)
                still_active = datetime.now(timezone.utc) < blocked_dt
            except Exception:
                still_active = False
            if not still_active:
                await db.add_consumable(self.user_id, self.selected_id, 1)
                await interaction.response.send_message(
                    "❌ La pénalité de mort a déjà expiré — la potion n'a pas été consommée.",
                    ephemeral=True,
                )
                return
            # Rembourser gold + énergie perdus et lever le blocage
            gold_back   = player.get("death_gold_lost", 0)
            energy_back = player.get("death_energy_lost", 0)
            new_gold   = player.get("gold", 0) + gold_back
            new_energy = min(player.get("max_energy", 2000), player.get("energy", 0) + energy_back)
            await db.update_player(
                self.user_id,
                gold=new_gold,
                energy=new_energy,
                regen_blocked_until=None,
                death_gold_lost=0,
                death_energy_lost=0,
            )
            msg = (
                f"🔰 **Pénalité annulée !**\n"
                f"💰 +{gold_back:,} gold remboursé\n"
                f"⚡ +{energy_back} énergie remboursée\n"
                f"😴 Blocage de regen levé"
            )
        elif effect in ("energy_regen", "energy_on_win", "energy_def_pct",
                        "energy_speed_pct", "energy_patk_pct", "energy_matk_pct", "energy_all"):
            import json
            from datetime import datetime, timezone, timedelta
            food_buffs = {}
            try:
                raw = player.get("food_buffs")
                if raw:
                    food_buffs = json.loads(raw)
            except Exception:
                pass

            expires_24h = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
            energy_gain = item_data.get("value", 0)
            lines = []

            if energy_gain > 0:
                new_energy = min(player.get("max_energy", 2000), player.get("energy", 0) + energy_gain)
                await db.update_player(self.user_id, energy=new_energy)
                lines.append(f"⚡ +{energy_gain} énergie ({new_energy}/{player.get('max_energy', 2000)})")

            if effect == "energy_regen" or effect == "energy_all":
                regen_val = item_data.get("value", 0) if effect == "energy_regen" else item_data.get("regen_bonus", 0)
                food_buffs["energy_regen"] = {"value": regen_val, "expires": expires_24h}
                lines.append(f"😴 Régénération passive +{regen_val}% pendant 24h")

            if effect == "energy_on_win" or effect == "energy_all":
                win_val = item_data.get("value", 0) if effect == "energy_on_win" else item_data.get("win_bonus", 0)
                food_buffs["energy_on_win"] = {"value": win_val, "expires": expires_24h}
                lines.append(f"⚡ +{win_val} énergie par victoire pendant 24h")

            if effect == "energy_def_pct":
                food_buffs["stat_def"] = {"value": item_data.get("combat_value", 0), "combats": 1}
                lines.append(f"🛡️ +{item_data.get('combat_value', 0)}% Défense Physique & Magique pendant ce combat")
            elif effect == "energy_speed_pct":
                food_buffs["stat_speed"] = {"value": item_data.get("combat_value", 0), "combats": 1}
                lines.append(f"⚡ +{item_data.get('combat_value', 0)}% Vitesse pendant ce combat")
            elif effect == "energy_patk_pct":
                food_buffs["stat_patk"] = {"value": item_data.get("combat_value", 0), "combats": 1}
                lines.append(f"⚔️ +{item_data.get('combat_value', 0)}% Attaque Physique pendant ce combat")
            elif effect == "energy_matk_pct":
                food_buffs["stat_matk"] = {"value": item_data.get("combat_value", 0), "combats": 1}
                lines.append(f"🔮 +{item_data.get('combat_value', 0)}% Attaque Magique pendant ce combat")

            await db.update_player(self.user_id, food_buffs=json.dumps(food_buffs))
            msg = f"🍽️ **{item_data['name']}** consommé !\n" + "\n".join(lines)

        elif effect == "revive_half_hp":
            await db.update_player(self.user_id, potion_revival_active=1)
            msg = "❤️‍🔥 **Potion de Résurrection** active ! Tu survivras à la mort avec 50% HP lors du prochain combat."

        elif effect == "ignore_passive":
            await db.update_player(self.user_id, potion_no_passive=1)
            msg = "🛡️ **Potion de Protection Ultime** active ! Les passifs ennemis seront ignorés lors du prochain combat."

        elif effect in ("p_atk_pct", "m_atk_pct", "def_pct", "speed_pct", "crit_pct", "all_pct"):
            # Élixirs — stockés dans food_buffs, actifs pour 1 combat
            # Un seul élixir par type (le nouveau écrase l'ancien du même type)
            # Différents types d'élixirs peuvent coexister
            import json
            food_buffs = {}
            try:
                raw = player.get("food_buffs")
                if raw:
                    food_buffs = json.loads(raw)
            except Exception:
                pass
            _elixir_key = {
                "p_atk_pct": "elixir_patk", "m_atk_pct": "elixir_matk",
                "def_pct":    "elixir_def",  "speed_pct": "elixir_speed",
                "crit_pct":   "elixir_crit", "all_pct":   "elixir_all",
            }[effect]
            food_buffs[_elixir_key] = {"value": value, "combats": 1}
            await db.update_player(self.user_id, food_buffs=json.dumps(food_buffs))
            _effect_label = {
                "p_atk_pct": "Attaque Physique", "m_atk_pct": "Attaque Magique",
                "def_pct":    "Défense Phys & Mag", "speed_pct": "Vitesse",
                "crit_pct":   "Chance Critique",  "all_pct":   "Toutes les Stats",
            }[effect]
            msg = f"⚗️ **{item_data['name']}** actif ! **+{value}% {_effect_label}** lors du prochain combat."

        else:
            msg = f"✅ **{item_data['name']}** consommé ! (effet non reconnu)"

        await interaction.response.send_message(msg, ephemeral=True)


class SellConsumableQtyModal(discord.ui.Modal, title="Quantité à vendre"):
    quantity = discord.ui.TextInput(label="Quantité", placeholder="ex: 5", min_length=1, max_length=6)

    def __init__(self, user_id: int, item_id: str, max_qty: int, unit_val: int):
        super().__init__()
        self.user_id  = user_id
        self.item_id  = item_id
        self.max_qty  = max_qty
        self.unit_val = unit_val
        self.quantity.placeholder = f"1 – {max_qty} (valeur : {unit_val:,} golds/u)"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qty = int(self.quantity.value)
        except ValueError:
            await interaction.response.send_message("❌ Quantité invalide.", ephemeral=True)
            return
        if qty <= 0 or qty > self.max_qty:
            await interaction.response.send_message(f"❌ Quantité invalide (1 – {self.max_qty}).", ephemeral=True)
            return
        ok = await db.remove_consumable(self.user_id, self.item_id, qty)
        if not ok:
            await interaction.response.send_message("❌ Quantité insuffisante.", ephemeral=True)
            return
        gold_earned = self.unit_val * qty
        player = await db.get_player(self.user_id)
        await db.update_player(self.user_id, gold=player["gold"] + gold_earned)
        data = CONSUMABLES.get(self.item_id, {})
        name = data.get("name", self.item_id)
        emoji = data.get("emoji", "")
        await interaction.response.send_message(
            f"✅ Vendu {emoji} **{name}** ×{qty} pour **{gold_earned:,}** golds 💰",
            ephemeral=True,
        )


class ConsumeQtyModal(discord.ui.Modal, title="Consommer"):
    quantity = discord.ui.TextInput(label="Quantité", placeholder="ex: 3", min_length=1, max_length=6)

    def __init__(self, user_id: int, item_id: str, max_qty: int, item_data: dict):
        super().__init__()
        self.user_id   = user_id
        self.item_id   = item_id
        self.max_qty   = max_qty
        self.item_data = item_data
        self.quantity.placeholder = f"1 – {max_qty} ({item_data.get('name', item_id)})"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qty = int(self.quantity.value)
        except ValueError:
            await interaction.response.send_message("❌ Quantité invalide.", ephemeral=True)
            return
        if qty <= 0 or qty > self.max_qty:
            await interaction.response.send_message(f"❌ Quantité invalide (1 – {self.max_qty}).", ephemeral=True)
            return

        player = await db.get_player(self.user_id)
        from bot.cogs.rpg.models import compute_class_stats, compute_max_hp
        cs     = compute_class_stats(player["class"], player["level"], player.get("prestige_level", 0))
        max_hp = compute_max_hp(cs)
        current_hp = player.get("current_hp") or max_hp
        effect = self.item_data.get("effect")
        value  = self.item_data.get("value", 0)
        name   = self.item_data.get("name", self.item_id)

        if effect == "heal_pct":
            heal_per = int(max_hp * value / 100)
            total_healed = 0
            consumed = 0
            for _ in range(qty):
                if current_hp >= max_hp:
                    break
                ok = await db.remove_consumable(self.user_id, self.item_id, 1)
                if not ok:
                    break
                current_hp = min(max_hp, current_hp + heal_per)
                total_healed += heal_per
                consumed += 1
            await db.update_player(self.user_id, current_hp=current_hp)
            msg = f"❤️ {consumed}× **{name}** consommé(s) — +**{total_healed:,}** HP ({current_hp:,}/{max_hp:,})"

        elif effect == "energy":
            cur_en  = player.get("energy", 0)
            max_en  = player.get("max_energy", 2000)
            total   = 0
            consumed = 0
            for _ in range(qty):
                if cur_en >= max_en:
                    break
                ok = await db.remove_consumable(self.user_id, self.item_id, 1)
                if not ok:
                    break
                cur_en = min(max_en, cur_en + value)
                total += value
                consumed += 1
            await db.update_player(self.user_id, energy=cur_en)
            msg = f"⚡ {consumed}× **{name}** consommé(s) — +**{total}** énergie ({cur_en}/{max_en})"

        else:
            msg = f"✅ **{name}** consommé !"

        await interaction.response.send_message(msg, ephemeral=True)


class AutoConsumeConfirmView(discord.ui.View):
    def __init__(self, user_id: int, heal_pool: list, energy_pool: list,
                 max_hp: int, max_energy: int, current_hp: int, cur_energy: int):
        super().__init__(timeout=60)
        self.user_id     = user_id
        self.heal_pool   = heal_pool
        self.energy_pool = energy_pool
        self.max_hp      = max_hp
        self.max_energy  = max_energy
        self.current_hp  = current_hp
        self.cur_energy  = cur_energy

        confirm = discord.ui.Button(label="Confirmer", style=discord.ButtonStyle.success, emoji="✅")
        confirm.callback = self._confirm
        self.add_item(confirm)

        cancel = discord.ui.Button(label="Annuler", style=discord.ButtonStyle.secondary, emoji="❌")
        cancel.callback = self._cancel
        self.add_item(cancel)

    async def _cancel(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        await interaction.response.edit_message(content="❌ Annulé.", embed=None, view=None)

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return

        current_hp = self.current_hp
        cur_energy = self.cur_energy
        from collections import Counter
        hp_used: list[str] = []
        en_used: list[str] = []

        for c, data in self.heal_pool:
            heal_val = int(self.max_hp * data.get("value", 0) / 100)
            if heal_val <= 0:
                continue
            qty_left = c["quantity"]
            while current_hp < self.max_hp and qty_left > 0:
                ok = await db.remove_consumable(self.user_id, c["item_id"], 1)
                if not ok:
                    break
                current_hp = min(self.max_hp, current_hp + heal_val)
                qty_left -= 1
                hp_used.append(data.get("name", c["item_id"]))

        for c, data in self.energy_pool:
            en_val = data.get("value", 0)
            if en_val <= 0:
                continue
            qty_left = c["quantity"]
            while cur_energy < self.max_energy and qty_left > 0:
                ok = await db.remove_consumable(self.user_id, c["item_id"], 1)
                if not ok:
                    break
                cur_energy = min(self.max_energy, cur_energy + en_val)
                qty_left -= 1
                en_used.append(data.get("name", c["item_id"]))

        await db.update_player(self.user_id, current_hp=current_hp, energy=cur_energy)

        lines = []
        if hp_used:
            counts = Counter(hp_used)
            used_str = ", ".join(f"**{n}** ×{q}" for n, q in counts.items())
            lines.append(f"❤️ HP : **{current_hp:,}/{self.max_hp:,}** — {used_str}")
        if en_used:
            counts = Counter(en_used)
            used_str = ", ".join(f"**{n}** ×{q}" for n, q in counts.items())
            lines.append(f"⚡ Énergie : **{cur_energy}/{self.max_energy}** — {used_str}")

        await interaction.response.edit_message(
            content="\n".join(lines) or "✅ Rien à consommer.",
            embed=None, view=None,
        )


# ─── Forgeron ─────────────────────────────────────────────────────────────

def build_forgeron_embed(user: discord.User, player: dict, equipment: list[dict], runes: list[dict], eq_page: int = 0) -> tuple:
    all_eq  = sorted(equipment, key=lambda e: (e.get("slot_equipped") is None, e.get("id", 0)))
    total_pages = max(1, (len(all_eq) + FORGE_ITEMS_PER_PAGE - 1) // FORGE_ITEMS_PER_PAGE)
    page_eq = all_eq[eq_page * FORGE_ITEMS_PER_PAGE:(eq_page + 1) * FORGE_ITEMS_PER_PAGE]

    embed = discord.Embed(title=f"⚒️ Forge — {user.display_name}", color=0xFF9800)
    embed.description = (
        "Améliorez vos équipements jusqu'à **+10** grâce à de l'or.\n"
        "Enchainez des **Runes** à vos équipements pour des bonus supplémentaires."
    )

    if page_eq:
        lines = []
        for item in page_eq:
            name = _eq_display_name(item)
            cost = get_enhancement_cost(item.get("enhancement", 0))
            equipped_mark = "✅ " if item.get("slot_equipped") else ""
            cost_str = f"(Amélio +{item['enhancement']+1} : **{cost:,}** 💰)" if cost >= 0 else "(Max)"
            lines.append(f"{equipped_mark}{name} {cost_str}")
        embed.add_field(
            name=f"⚔️ Équipements (Page {eq_page + 1}/{total_pages})",
            value="\n".join(lines),
            inline=False,
        )
    else:
        embed.add_field(name="⚔️ Équipements", value="*Aucun équipement*", inline=False)

    if runes:
        rune_lines = [
            f"{CONSUMABLES.get(r['item_id'], {}).get('emoji', '?')} **{CONSUMABLES.get(r['item_id'], {}).get('name', r['item_id'])}** ×{r['quantity']}"
            for r in runes[:25]
        ]
        embed.add_field(name="🔮 Runes disponibles", value="\n".join(rune_lines) or "*Aucune*", inline=False)
    else:
        embed.add_field(name="🔮 Runes disponibles", value="*Aucune rune*", inline=False)

    embed.add_field(name="💰 Or disponible", value=f"**{player['gold']:,}**", inline=True)

    view = ForgeronView(user.id, player, all_eq, runes, eq_page, total_pages)
    return embed, view


class ForgeronView(discord.ui.View):
    def __init__(self, user_id: int, player: dict, all_eq: list[dict], runes: list[dict], page: int, total_pages: int):
        super().__init__(timeout=180)
        self.user_id     = user_id
        self.player      = player
        self.all_eq      = all_eq
        self.runes       = runes
        self.page        = page
        self.total_pages = total_pages
        self.selected_eq_id: int | None = None
        self.selected_rune_id: str | None = None

        page_eq = all_eq[page * FORGE_ITEMS_PER_PAGE:(page + 1) * FORGE_ITEMS_PER_PAGE]

        # Dropdown équipements (avec 🔮 si rune présente)
        if page_eq:
            eq_options = []
            for e in page_eq:
                label = format_eq_name(e)[:100]
                eq_options.append(discord.SelectOption(
                    label=label,
                    value=str(e["id"]),
                    description=f"+{e.get('enhancement', 0)} | Amélio : {get_enhancement_cost(e.get('enhancement', 0)):,} 💰",
                ))
            eq_select = discord.ui.Select(placeholder="Choisir un équipement...", options=eq_options, custom_id="rpg:forge:eq_select", row=0)
            eq_select.callback = self._on_eq_select
            self.add_item(eq_select)

        # Dropdown runes
        if runes:
            rune_options = [
                discord.SelectOption(
                    label=f"{CONSUMABLES.get(r['item_id'], {}).get('name', r['item_id'])} ×{r['quantity']}"[:100],
                    value=r["item_id"],
                    emoji=CONSUMABLES.get(r["item_id"], {}).get("emoji"),
                    description=f"Coût enchant : {_get_rune_equip_cost(CONSUMABLES.get(r['item_id'], {})):,} 💰",
                )
                for r in runes[:25]
            ]
            rune_select = discord.ui.Select(placeholder="Choisir une rune...", options=rune_options, custom_id="rpg:forge:rune_select", row=1)
            rune_select.callback = self._on_rune_select
            self.add_item(rune_select)

        forge_btn = discord.ui.Button(label="Forger", style=discord.ButtonStyle.success, emoji="⚒️", custom_id="rpg:forge:forge", row=2)
        forge_btn.callback = self._forge
        self.add_item(forge_btn)

        enchant_btn = discord.ui.Button(label="Enchanter Rune", style=discord.ButtonStyle.primary, emoji="🔮", custom_id="rpg:forge:enchant", row=2)
        enchant_btn.callback = self._enchant
        self.add_item(enchant_btn)

        remove_rune_btn = discord.ui.Button(label="Déséquiper Rune", style=discord.ButtonStyle.danger, emoji="💔", custom_id="rpg:forge:remove_rune", row=2)
        remove_rune_btn.callback = self._remove_rune
        self.add_item(remove_rune_btn)

        if total_pages > 1:
            prev_btn = discord.ui.Button(label="◀", style=discord.ButtonStyle.secondary, disabled=(page == 0), custom_id="rpg:forge:prev", row=3)
            prev_btn.callback = self._prev
            self.add_item(prev_btn)

            next_btn = discord.ui.Button(label="▶", style=discord.ButtonStyle.secondary, disabled=(page >= total_pages - 1), custom_id="rpg:forge:next", row=3)
            next_btn.callback = self._next
            self.add_item(next_btn)

    async def _on_eq_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_eq_id = int(interaction.data["values"][0])
        await interaction.response.defer()

    async def _on_rune_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_rune_id = interaction.data["values"][0]
        await interaction.response.defer()

    async def _forge(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_eq_id:
            await interaction.response.send_message("❌ Sélectionne d'abord un équipement.", ephemeral=True)
            return
        item = next((e for e in self.all_eq if e["id"] == self.selected_eq_id), None)
        if not item:
            await interaction.response.send_message("❌ Item introuvable.", ephemeral=True)
            return
        current_enh = item.get("enhancement", 0)
        cost = get_enhancement_cost(current_enh)
        if cost < 0:
            await interaction.response.send_message("❌ Cet équipement est déjà au maximum (+10).", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        if player["gold"] < cost:
            await interaction.response.send_message(f"❌ Il te manque **{cost - player['gold']:,}** golds.", ephemeral=True)
            return
        new_enh = await db.enhance_equipment(self.user_id, self.selected_eq_id)
        await db.update_player(self.user_id, gold=player["gold"] - cost)
        player    = await db.get_player(self.user_id)
        equipment = await db.get_equipment(self.user_id)
        all_eq    = sorted(equipment, key=lambda e: (e.get("slot_equipped") is None, e.get("id", 0)))
        consumables = await db.get_consumables(self.user_id)
        runes = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") == "rune"]
        embed, view = build_forgeron_embed(interaction.user, player, equipment, runes, self.page)
        name = format_item_name(item["item_id"], item.get("rarity"), new_enh)
        embed.add_field(name="⚒️ Forge réussie !", value=f"{name} → **+{new_enh}** (-{cost:,} 💰)", inline=False)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _enchant(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_eq_id or not self.selected_rune_id:
            await interaction.response.send_message("❌ Sélectionne un équipement ET une rune.", ephemeral=True)
            return
        item = next((e for e in self.all_eq if e["id"] == self.selected_eq_id), None)
        if not item:
            await interaction.response.send_message("❌ Item introuvable.", ephemeral=True)
            return
        # Vérification : 1 rune par item max
        existing_rb = json.loads(item.get("rune_bonuses") or "{}")
        if existing_rb:
            await interaction.response.send_message("❌ Cet équipement possède déjà une rune. Déséquipe-la d'abord.", ephemeral=True)
            return
        rune_data = CONSUMABLES.get(self.selected_rune_id, {})
        effect_key = rune_data.get("effect", "")
        effect_val = rune_data.get("value", 0)
        cost = _get_rune_equip_cost(rune_data)
        player = await db.get_player(self.user_id)
        if player["gold"] < cost:
            await interaction.response.send_message(f"❌ Il te manque **{cost - player['gold']:,}** golds pour enchanter.", ephemeral=True)
            return
        removed = await db.remove_consumable(self.user_id, self.selected_rune_id, 1)
        if not removed:
            await interaction.response.send_message("❌ Tu n'as plus cette rune.", ephemeral=True)
            return
        await db.update_player(self.user_id, gold=player["gold"] - cost)
        await db.add_rune_to_equipment(self.user_id, self.selected_eq_id, effect_key, effect_val)
        effect_name = STAT_FR.get(effect_key, effect_key)
        effect_emoji = STAT_EMOJI.get(effect_key, "")
        base_name = format_item_name(item["item_id"], item.get("rarity"), item.get("enhancement", 0))
        player = await db.get_player(self.user_id)
        equipment = await db.get_equipment(self.user_id)
        consumables = await db.get_consumables(self.user_id)
        runes = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") == "rune"]
        embed, view = build_forgeron_embed(interaction.user, player, equipment, runes, self.page)
        embed.add_field(
            name="🔮 Enchantement appliqué !",
            value=f"{base_name} 🔮 reçoit **+{effect_val}** {effect_emoji} {effect_name} (-{cost:,} 💰)",
            inline=False,
        )
        await interaction.response.edit_message(embed=embed, view=view)

    async def _remove_rune(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_eq_id:
            await interaction.response.send_message("❌ Sélectionne d'abord un équipement.", ephemeral=True)
            return
        item = next((e for e in self.all_eq if e["id"] == self.selected_eq_id), None)
        if not item:
            await interaction.response.send_message("❌ Item introuvable.", ephemeral=True)
            return
        rb = json.loads(item.get("rune_bonuses") or "{}")
        if not rb:
            await interaction.response.send_message("❌ Cet équipement n'a pas de rune.", ephemeral=True)
            return
        cost = _get_rune_remove_cost(rb)
        player = await db.get_player(self.user_id)
        if player["gold"] < cost:
            await interaction.response.send_message(f"❌ Il te manque **{cost - player['gold']:,}** golds pour déséquiper la rune.", ephemeral=True)
            return
        await db.update_player(self.user_id, gold=player["gold"] - cost)
        await db.remove_rune_from_equipment(self.user_id, self.selected_eq_id)
        base_name = format_item_name(item["item_id"], item.get("rarity"), item.get("enhancement", 0))
        rune_str = ", ".join(f"+{v} {STAT_FR.get(k, k)}" for k, v in rb.items())
        player = await db.get_player(self.user_id)
        equipment = await db.get_equipment(self.user_id)
        consumables = await db.get_consumables(self.user_id)
        runes = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") == "rune"]
        embed, view = build_forgeron_embed(interaction.user, player, equipment, runes, self.page)
        embed.add_field(
            name="💔 Rune déséquipée",
            value=f"{base_name} — rune [{rune_str}] retirée (-{cost:,} 💰)",
            inline=False,
        )
        await interaction.response.edit_message(embed=embed, view=view)

    async def _prev(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        equipment = await db.get_equipment(self.user_id)
        consumables = await db.get_consumables(self.user_id)
        runes = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") == "rune"]
        player = await db.get_player(self.user_id)
        embed, view = build_forgeron_embed(interaction.user, player, equipment, runes, max(0, self.page - 1))
        await interaction.response.edit_message(embed=embed, view=view)

    async def _next(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        equipment = await db.get_equipment(self.user_id)
        consumables = await db.get_consumables(self.user_id)
        runes = [c for c in consumables if CONSUMABLES.get(c["item_id"], {}).get("type") == "rune"]
        player = await db.get_player(self.user_id)
        embed, view = build_forgeron_embed(interaction.user, player, equipment, runes, self.page + 1)
        await interaction.response.edit_message(embed=embed, view=view)


# ─── Prestige ─────────────────────────────────────────────────────────────

def build_prestige_embed(player: dict) -> tuple:
    current_prestige  = player.get("prestige_level", 0)
    current_level     = player.get("level", 1)
    new_prestige      = max(current_prestige, current_level)

    embed = discord.Embed(
        title="✨ Prestige",
        description=(
            "Le **Prestige** remet ta partie à zéro en échange d'un puissant bonus permanent.\n\n"
            "**Ce qui est conservé :**\n"
            "• Classements PvP et World Boss\n"
            "• Titres débloqués\n"
            "• Banque (golds, items)\n"
            "• Reliques\n\n"
            "**Ce qui est réinitialisé :**\n"
            "• Classe (à rechoisir)\n"
            "• Niveau, XP, golds (hors banque)\n"
            "• Zone et stage\n"
            "• Inventaire complet (items, matériaux, consommables)\n"
            "• Professions et métiers\n"
            "• HP actuels\n\n"
        ),
        color=0xFF9800,
    )
    embed.add_field(
        name="📊 Détails du Prestige",
        value=(
            f"**Niveau actuel** : {current_level}\n"
            f"**Prestige actuel** : {current_prestige}\n"
            f"**Nouveau prestige** : {new_prestige}\n"
            f"**Bonus de stats** : +{new_prestige * 0.1:.1f}%\n\n"
            f"⚠️ Minimum requis : **Niveau 10**"
        ),
        inline=False,
    )

    can_prestige = current_level >= 10
    view = PrestigeView(player, can_prestige)
    return embed, view


class PrestigeView(discord.ui.View):
    def __init__(self, player: dict, can_prestige: bool):
        super().__init__(timeout=60)
        self.player = player
        btn = discord.ui.Button(
            label="Confirmer le Prestige",
            style=discord.ButtonStyle.danger,
            emoji="✨",
            custom_id="rpg:prestige:confirm",
            disabled=not can_prestige,
        )
        btn.callback = self._confirm
        self.add_item(btn)

    async def _confirm(self, interaction: discord.Interaction):
        player = await db.get_player(interaction.user.id)
        if not player:
            await interaction.response.send_message("❌ Profil introuvable.", ephemeral=True)
            return
        current_level    = player.get("level", 1)
        current_prestige = player.get("prestige_level", 0)
        if current_level < 10:
            await interaction.response.send_message("❌ Niveau minimum 10 requis.", ephemeral=True)
            return
        new_prestige = max(current_prestige, current_level)

        # Reset complet du joueur
        await db.update_player(
            interaction.user.id,
            level          = 1,
            xp             = 0,
            gold           = 0,
            zone           = 1,
            stage          = 1,
            boss_stage     = 0,
            prestige_level = new_prestige,
            current_hp     = None,
            energy         = 500,
        )
        # Réinitialiser la classe séparément (mot-clé réservé)
        import aiosqlite
        async with aiosqlite.connect(db.DB_PATH) as conn:
            await conn.execute("UPDATE players SET class=NULL WHERE user_id=?", (interaction.user.id,))
            await conn.execute("DELETE FROM inventory_equipment WHERE user_id=?", (interaction.user.id,))
            await conn.execute("DELETE FROM inventory_consumables WHERE user_id=?", (interaction.user.id,))
            await conn.execute("DELETE FROM inventory_materials WHERE user_id=?", (interaction.user.id,))
            # Reset professions
            await conn.execute(
                "UPDATE professions SET harvest_type=NULL, harvest_level=0, harvest_xp=0, "
                "craft_type=NULL, craft_level=0, craft_xp=0, "
                "conception_type=NULL, conception_level=0, conception_xp=0 WHERE user_id=?",
                (interaction.user.id,)
            )
            await conn.commit()

        embed = discord.Embed(
            title="✨ Prestige Accompli !",
            description=(
                f"Ton prestige est maintenant **{new_prestige}** !\n"
                f"Bonus de stats de classe : **+{new_prestige * 0.1:.1f}%**\n\n"
                "Tout a été réinitialisé. Choisis une nouvelle classe pour continuer !"
            ),
            color=0x00FF88,
        )
        await interaction.response.edit_message(embed=embed, view=None)


# ─── Récompense quotidienne ────────────────────────────────────────────────

async def handle_daily_reward(interaction: discord.Interaction, player: dict):
    now      = datetime.now(timezone.utc)
    last_str = player.get("last_daily")
    streak   = player.get("daily_streak", 0)

    if last_str:
        last_dt = datetime.fromisoformat(last_str).replace(tzinfo=timezone.utc)
        diff    = now - last_dt
        if diff.total_seconds() < 86400:  # moins de 24h
            remaining = timedelta(seconds=86400) - diff
            hours, rem = divmod(int(remaining.total_seconds()), 3600)
            minutes    = rem // 60
            embed = discord.Embed(
                title="⏰ Récompense non disponible",
                description=f"Reviens dans **{hours}h {minutes}min** !",
                color=0xFF4444,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        elif diff.total_seconds() > 172800:  # plus de 48h → streak reset
            streak = 0
        else:
            streak += 1
    else:
        streak = 1

    player_updated = await db.get_player(interaction.user.id)
    rewards = daily_reward(streak, player_updated["level"])
    new_gold = player_updated["gold"] + rewards["gold"]
    new_xp   = player_updated["xp"]   + rewards["xp"]

    # XP et level up
    from bot.cogs.rpg.models import level_up
    new_level, new_xp = level_up(player_updated["level"], new_xp)

    # Tirage aléatoire pondéré des items
    from bot.cogs.rpg.items import (
        DAILY_POTION_POOL, DAILY_FOOD_POOL, DAILY_RUNE_POOL,
        pick_daily_item, CONSUMABLES,
    )
    from collections import Counter
    n = rewards["item_count"]
    potion_ids = [pick_daily_item(DAILY_POTION_POOL) for _ in range(n)]
    food_ids   = [pick_daily_item(DAILY_FOOD_POOL)   for _ in range(n)]
    rune_ids   = [pick_daily_item(DAILY_RUNE_POOL)   for _ in range(n)]

    for item_id, qty in Counter(potion_ids).items():
        await db.add_consumable(interaction.user.id, item_id, qty)
    for item_id, qty in Counter(food_ids).items():
        await db.add_consumable(interaction.user.id, item_id, qty)
    for item_id, qty in Counter(rune_ids).items():
        await db.add_consumable(interaction.user.id, item_id, qty)

    await db.update_player(
        interaction.user.id,
        gold        = new_gold,
        xp          = new_xp,
        level       = new_level,
        last_daily  = now.isoformat(),
        daily_streak= streak,
    )

    def _fmt_items(ids: list[str]) -> str:
        return ", ".join(
            f"{CONSUMABLES[i]['emoji']} **{CONSUMABLES[i]['name']}**" + (f" ×{c}" if c > 1 else "")
            for i, c in Counter(ids).items()
        )

    embed = discord.Embed(
        title=f"🎁 Récompense Quotidienne — Jour {streak} !",
        color=0xFFD700,
    )
    embed.add_field(
        name="💰 Or & XP",
        value=f"💰 **{rewards['gold']:,}** golds\n✨ **{rewards['xp']:,}** XP",
        inline=False,
    )
    embed.add_field(
        name=f"🎒 Items obtenus ({n} de chaque)",
        value=(
            f"💊 {_fmt_items(potion_ids)}\n"
            f"🍞 {_fmt_items(food_ids)}\n"
            f"🔮 {_fmt_items(rune_ids)}"
        ),
        inline=False,
    )
    if streak > 1:
        next_bonus = 7 - (streak % 7) if streak % 7 != 0 else 7
        embed.add_field(
            name="🔥 Streak",
            value=f"**{streak}** jours consécutifs ! *(+1 item dans {next_bonus} jour{'s' if next_bonus > 1 else ''})*",
            inline=False,
        )
    embed.set_footer(text="Reviens demain pour continuer ta streak !")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # Vérifier titres
    from bot.cogs.rpg.core import check_all_titles
    player_new = await db.get_player(interaction.user.id)
    await check_all_titles(interaction.user.id, player_new)


# ─── Build hub ─────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="👤 Hub Profil",
        description=(
            "Gérez votre aventure depuis ce hub :\n\n"
            "**👤 Voir Profil** — Vos stats, niveau, zone, prestige\n"
            "**🎒 Inventaire** — Équipements équipés et en stock\n"
            "**🎽 Sac à dos** — Consommables (potions, nourriture, runes)\n"
            "**⚒️ Forge** — Améliorez vos équipements & enchantez des runes\n"
            "**✨ Prestige** — Recommencez plus fort\n"
            "**🎁 Récompense Quotidienne** — Clique chaque jour pour des bonus !\n"
        ),
        color=0x5865F2,
    )
    embed.set_footer(text="Cliquez sur un bouton pour accéder à la section.")
    view = ProfilHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
