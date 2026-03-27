"""
Hub Quêtes — Mode Histoire Linéaire.
Canal : 1481409415046365245

Deux chaînes indépendantes :
  - Principales  : progression solo (zones, niveaux, donjons, world boss)
  - Secondaires  : métiers, commerce, raids, PvP
"""
from __future__ import annotations
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.quests import (
    MAIN_QUESTS, SECONDARY_QUESTS,
    get_progress_value, get_active_quest, progress_bar,
)

_COMPLETED_HISTORY = 3   # nombre de quêtes complétées affichées


# ─── Hub View (persistante) ───────────────────────────────────────────────────

class QuetesHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Quêtes Principales", style=discord.ButtonStyle.primary,
                       emoji="📖", custom_id="rpg:quetes:main", row=0)
    async def main_quests(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _show_quests(interaction, "main")

    @discord.ui.button(label="Quêtes Secondaires", style=discord.ButtonStyle.secondary,
                       emoji="🌐", custom_id="rpg:quetes:secondary", row=0)
    async def secondary_quests(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _show_quests(interaction, "secondary")


# ─── Logique d'affichage ──────────────────────────────────────────────────────

async def _show_quests(interaction: discord.Interaction, chain: str):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    if not player.get("class"):
        await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
        return

    prof  = await db.get_professions(interaction.user.id)
    stats = await db.get_quest_stats(interaction.user.id)
    claimed_ids = await db.get_claimed_quests(interaction.user.id)

    quest_list = MAIN_QUESTS if chain == "main" else SECONDARY_QUESTS
    active     = get_active_quest(quest_list, claimed_ids)
    embed, claimable = _build_embed(chain, quest_list, active, claimed_ids, player, prof, stats)

    view = QuestChainView(interaction.user.id, chain, claimable)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def _build_embed(
    chain: str,
    quest_list: list[dict],
    active: dict | None,
    claimed_ids: set[str],
    player: dict,
    prof: dict,
    stats: dict,
) -> tuple[discord.Embed, bool]:
    """Construit l'embed de la chaîne. Retourne (embed, claimable)."""

    is_main = chain == "main"
    title   = "📖 Quêtes Principales" if is_main else "🌐 Quêtes Secondaires"
    color   = 0x5865F2 if is_main else 0x57F287

    completed_count = sum(1 for q in quest_list if q["id"] in claimed_ids)
    total           = len(quest_list)

    embed = discord.Embed(title=title, color=color)
    embed.description = (
        f"**Progression :** {completed_count}/{total} quêtes complétées  "
        f"{progress_bar(completed_count, total, 10)}"
    )

    # ── Historique des dernières quêtes complétées ────────────────────────────
    completed_quests = [q for q in quest_list if q["id"] in claimed_ids]
    recent = completed_quests[-_COMPLETED_HISTORY:]
    if recent:
        lines = [f"✅ ~~{q['emoji']} {q['name']}~~" for q in recent]
        embed.add_field(name="Récemment complétées", value="\n".join(lines), inline=False)

    # ── Quête active ──────────────────────────────────────────────────────────
    claimable = False
    if active is None:
        embed.add_field(
            name="🎉 Chaîne complétée !",
            value="Tu as accompli toutes les quêtes de cette chaîne. Félicitations !",
            inline=False,
        )
    else:
        current_val = get_progress_value(active, player, prof, stats)
        threshold   = active["threshold"]
        is_done     = current_val >= threshold
        claimable   = is_done

        if is_done:
            status = "🎁 **Prête à réclamer !**"
            bar    = progress_bar(threshold, threshold)
        else:
            status = f"**{current_val:,} / {threshold:,}**  {progress_bar(current_val, threshold)}"
            bar    = ""

        special_line = ""
        if active.get("special_desc"):
            special_line = f"\n{active['special_desc']}"

        reward_line = (
            "🌱 Récompense : **+0,1 énergie/cycle** et **+0,1% régén. HP** (passif permanent)"
            if is_main else
            "⚡ Récompense : **+0,5% de chance** de gagner **+1 énergie** après un combat gagné (cumulatif)"
        )
        embed.add_field(
            name=f"⚡ Quête active — {active['emoji']} {active['name']}",
            value=(
                f"{active['desc']}\n"
                f"{status}{special_line}\n"
                f"{reward_line}"
            ),
            inline=False,
        )

    # ── Quêtes à venir (cachées) ──────────────────────────────────────────────
    if active:
        future_idx = next((i for i, q in enumerate(quest_list) if q["id"] == active["id"]), -1)
        upcoming   = quest_list[future_idx + 1: future_idx + 4]
        if upcoming:
            lines = [f"🔒 {q['emoji']} ??? *(débloquée après la quête actuelle)*" for q in upcoming[:2]]
            if len(upcoming) >= 3:
                lines.append(f"🔒 *... et {total - completed_count - 1} autres quêtes*")
            embed.add_field(name="À venir", value="\n".join(lines), inline=False)

    embed.set_footer(text="Les quêtes se débloquent une par une — complète la quête active pour progresser.")
    return embed, claimable


# ─── Vue interactive ──────────────────────────────────────────────────────────

class QuestChainView(discord.ui.View):
    def __init__(self, user_id: int, chain: str, claimable: bool):
        super().__init__(timeout=180)
        self.user_id   = user_id
        self.chain     = chain
        self.claimable = claimable

        if claimable:
            btn = discord.ui.Button(
                label="Réclamer la récompense",
                style=discord.ButtonStyle.success,
                emoji="🎁",
            )
            btn.callback = self._claim
            self.add_item(btn)

        refresh_btn = discord.ui.Button(
            label="Actualiser",
            style=discord.ButtonStyle.secondary,
            emoji="🔄",
        )
        refresh_btn.callback = self._refresh
        self.add_item(refresh_btn)

    async def _claim(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton menu !", ephemeral=True)
            return

        player = await db.get_or_create_player(interaction.user.id)
        prof   = await db.get_professions(interaction.user.id)
        stats  = await db.get_quest_stats(interaction.user.id)
        claimed_ids  = await db.get_claimed_quests(interaction.user.id)

        quest_list = MAIN_QUESTS if self.chain == "main" else SECONDARY_QUESTS
        active     = get_active_quest(quest_list, claimed_ids)

        if active is None:
            await interaction.response.send_message("❌ Aucune quête à réclamer.", ephemeral=True)
            return

        current_val = get_progress_value(active, player, prof, stats)
        if current_val < active["threshold"]:
            await interaction.response.send_message("❌ Objectif pas encore atteint !", ephemeral=True)
            return

        # Réclamer
        await db.claim_quest(interaction.user.id, active["id"])

        # Récompense selon la chaîne
        if self.chain == "main":
            reward_text = "🌱 **+0,1 énergie/cycle** et **+0,1% régén. HP** (passif permanent)"
        else:
            # Quête secondaire : +0,5% chance de gagner +1 énergie après combat gagné
            current_chance = player.get("energy_on_win_chance", 0.0)
            await db.update_player(interaction.user.id, energy_on_win_chance=round(current_chance + 0.005, 4))
            total_pct = round((current_chance + 0.005) * 100, 1)
            reward_text = f"⚡ **+0,5% chance énergie/combat** (total : **{total_pct}%**)"

        # Réclamation faite — on regénère l'embed avec la nouvelle quête
        claimed_ids.add(active["id"])
        next_active = get_active_quest(quest_list, claimed_ids)

        # Confirmation rapide
        confirm = discord.Embed(
            title=f"✅ {active['emoji']} {active['name']} — Complétée !",
            description=(
                f"**Récompense :**\n"
                f"{reward_text}\n\n"
                + (f"➡️ Prochaine quête : **{next_active['emoji']} {next_active['name']}**" if next_active
                   else "🏆 Tu as complété toute la chaîne !")
            ),
            color=0x57F287,
        )

        new_embed, new_claimable = _build_embed(
            self.chain, quest_list, next_active, claimed_ids, player, prof, stats
        )
        new_view = QuestChainView(interaction.user.id, self.chain, new_claimable)

        await interaction.response.edit_message(embed=confirm, view=None)
        await interaction.followup.send(embed=new_embed, view=new_view, ephemeral=True)

    async def _refresh(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton menu !", ephemeral=True)
            return

        player = await db.get_or_create_player(interaction.user.id)
        prof   = await db.get_professions(interaction.user.id)
        stats  = await db.get_quest_stats(interaction.user.id)
        claimed_ids  = await db.get_claimed_quests(interaction.user.id)

        quest_list = MAIN_QUESTS if self.chain == "main" else SECONDARY_QUESTS
        active     = get_active_quest(quest_list, claimed_ids)

        embed, claimable = _build_embed(self.chain, quest_list, active, claimed_ids, player, prof, stats)
        new_view = QuestChainView(interaction.user.id, self.chain, claimable)
        await interaction.response.edit_message(embed=embed, view=new_view)


# ─── Message Hub ─────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="📖 Hub Quêtes",
        description=(
            "Les quêtes te guident à travers toute l'aventure, **une par une**.\n\n"
            "**📖 Quêtes Principales**\n"
            "Progression solo : zones, niveaux, donjons, World Boss.\n"
            "Complète-les dans l'ordre pour débloquer la suite.\n\n"
            "**🌐 Quêtes Secondaires**\n"
            "Activités variées : métiers, commerce, raids, PvP.\n"
            "Une chaîne parallèle — progresse dans toutes les directions !\n\n"
            "🎁 Certaines quêtes débloquent des **récompenses spéciales permanentes**."
        ),
        color=0x5865F2,
    )
    view = QuetesHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
