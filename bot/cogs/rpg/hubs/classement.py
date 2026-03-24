"""
Hub Classements.
Canal : 1468963280218362019
"""
from __future__ import annotations
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import BASE_STATS, CLASS_EMOJI

_PAGE_SIZE = 20


class ClassementHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Classement Général", style=discord.ButtonStyle.primary,
                       emoji="🌍", custom_id="rpg:classement:global", row=0)
    async def global_lb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_global_leaderboard(interaction)

    @discord.ui.button(label="Classement PvP", style=discord.ButtonStyle.danger,
                       emoji="⚔️", custom_id="rpg:classement:pvp", row=0)
    async def pvp_lb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_pvp_leaderboard(interaction)

    @discord.ui.button(label="Classement World Boss", style=discord.ButtonStyle.secondary,
                       emoji="🌋", custom_id="rpg:classement:wb", row=0)
    async def wb_lb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_wb_leaderboard(interaction)


async def _handle_global_leaderboard(interaction: discord.Interaction):
    await db.update_player(interaction.user.id, display_name=interaction.user.display_name)
    rows = await db.get_global_leaderboard()

    embed = discord.Embed(
        title="🌍 Classement Général — Top joueurs",
        description="Classement par **prestige** (puis niveau, puis zone en cas d'égalité).",
        color=0x2196F3,
    )

    if not rows:
        embed.description = "*Aucun joueur enregistré.*"
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    medals = ["🥇", "🥈", "🥉"] + [f"#{i+1}" for i in range(3, _PAGE_SIZE)]
    lines = []
    for i, row in enumerate(rows[:_PAGE_SIZE]):
        medal  = medals[i] if i < len(medals) else f"#{i+1}"
        cls    = row.get("class", "?")
        emoji  = CLASS_EMOJI.get(cls, "❓")
        prestige = row.get("prestige_level", 0)
        level    = row.get("level", 1)
        zone     = row.get("zone", 1)
        stage    = row.get("stage", 1)
        stage_txt = "Boss" if str(stage) == "boss" else str(stage)
        title    = row.get("active_title", "")
        name     = row.get("display_name") or f"Joueur {row['user_id']}"

        header = f"{medal} {emoji} **{name}**"
        if title:
            header += f"  *{title}*"
        lines.append(
            f"{header}\n"
            f"┗ Prestige **{prestige}** · Niveau **{level}** · Zone **{zone}-{stage_txt}**"
        )

    embed.description = "Classement par **prestige**, puis **niveau**, puis **zone**.\n\n" + "\n".join(lines)

    player_row = next((r for r in rows if r["user_id"] == interaction.user.id), None)
    if player_row:
        rank  = rows.index(player_row) + 1
        p_stage = player_row.get("stage", 1)
        p_stage_txt = "Boss" if str(p_stage) == "boss" else str(p_stage)
        embed.set_footer(text=f"Ta position : #{rank} · Niv. {player_row.get('level', 1)} · Zone {player_row.get('zone', 1)}-{p_stage_txt}")
    else:
        embed.set_footer(text="Tu n'es pas encore dans le classement.")

    await interaction.response.send_message(embed=embed, ephemeral=True)


async def _handle_pvp_leaderboard(interaction: discord.Interaction):
    await db.update_player(interaction.user.id, display_name=interaction.user.display_name)
    rows = await db.get_pvp_leaderboard()

    embed = discord.Embed(
        title="⚔️ Classement PvP — Top 20",
        description="Classement par **Élo PvP**.",
        color=0xFF6B35,
    )

    if not rows:
        embed.description = "*Aucun combat PvP enregistré.*"
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    medals = ["🥇", "🥈", "🥉"] + [f"#{i+1}" for i in range(3, 20)]
    lines = []
    for i, row in enumerate(rows[:_PAGE_SIZE]):
        medal = medals[i] if i < len(medals) else f"#{i+1}"
        elo    = row.get("pvp_elo", 1000)
        wins   = row.get("pvp_wins", 0)
        losses = row.get("pvp_losses", 0)
        total  = wins + losses
        wr = f"{wins/total*100:.0f}%" if total > 0 else "N/A"
        rank_label = _get_rank_label(elo)
        name = row.get("display_name") or f"Joueur {row['user_id']}"
        title = row.get("active_title", "")
        header = f"{medal} **{name}**" + (f"  *{title}*" if title else "")
        lines.append(
            f"{header}\n"
            f"   Élo **{elo}** ({rank_label}) — {wins}V/{losses}D ({wr})"
        )

    embed.description = "\n".join(lines)

    player_row = next((r for r in rows if r["user_id"] == interaction.user.id), None)
    if player_row:
        rank = rows.index(player_row) + 1
        embed.set_footer(text=f"Ta position : #{rank} — Élo {player_row.get('pvp_elo', 1000)}")
    else:
        embed.set_footer(text="Tu n'es pas encore classé en PvP.")

    await interaction.response.send_message(embed=embed, ephemeral=True)


async def _handle_wb_leaderboard(interaction: discord.Interaction):
    await db.update_player(interaction.user.id, display_name=interaction.user.display_name)
    from bot.cogs.rpg.models import WB_RANK_REWARDS, RELICS
    rows = await db.get_wb_leaderboard()

    embed = discord.Embed(
        title="🌋 Classement World Boss — Semaine en cours",
        description="Classement par **dégâts totaux** infligés au World Boss cette semaine.\nRécompenses distribuées le **lundi à minuit UTC**.",
        color=0xFF4444,
    )

    if not rows:
        embed.description += "\n\n*Aucun dégât enregistré cette semaine.*"
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    medals = ["🥇", "🥈", "🥉"] + ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = []
    for i, row in enumerate(rows[:10]):
        medal = medals[i] if i < len(medals) else f"#{i+1}"
        reward = WB_RANK_REWARDS.get(i + 1, {})
        gold_reward = reward.get("gold", 0)
        relic_info_str = ""
        if reward.get("relic"):
            rel = RELICS.get(reward["relic"])
            if rel:
                relic_info_str = f" + {rel['emoji']}"
        name  = row.get("display_name") or f"Joueur {row['user_id']}"
        title = row.get("active_title", "")
        header = f"{medal} **{name}**" + (f"  *{title}*" if title else "")
        lines.append(
            f"{header}\n"
            f"   {row.get('damage', 0):,} dégâts | Récompense : {gold_reward:,}g{relic_info_str}"
        )

    embed.description = "\n".join(lines)

    player_row = next((r for r in rows if r["user_id"] == interaction.user.id), None)
    if player_row:
        rank = rows.index(player_row) + 1
        embed.set_footer(text=f"Ta position : #{rank} — {player_row.get('damage', 0):,} dégâts")
    else:
        embed.set_footer(text="Tu n'es pas encore dans le classement WB cette semaine.")

    await interaction.response.send_message(embed=embed, ephemeral=True)


def _get_rank_label(elo: int) -> str:
    if elo >= 2400:  return "Maître Absolu 👑"
    if elo >= 2000:  return "Maître ⚜️"
    if elo >= 1800:  return "Diamant 💎"
    if elo >= 1600:  return "Platine 🪙"
    if elo >= 1400:  return "Or 🥇"
    if elo >= 1200:  return "Argent 🥈"
    if elo >= 1000:  return "Bronze 🥉"
    return "Fer 🔩"


def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="📊 Hub Classements",
        description=(
            "Retrouve tous les classements du jeu ici !\n\n"
            "**Classements disponibles :**\n\n"
            "🌍 **Général** — Classement par prestige, puis niveau, puis zone\n"
            "⚔️ **PvP** — Classement par Élo PvP\n"
            "🌋 **World Boss** — Dégâts hebdomadaires\n\n"
            "*Les classements sont mis à jour en temps réel.*\n"
            "*Le classement World Boss est réinitialisé chaque lundi.*"
        ),
        color=0x2196F3,
    )
    view = ClassementHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
