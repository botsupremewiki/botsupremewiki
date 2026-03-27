"""
Hub Titres & Succès.
Canal : 1465433147167477871

Architecture :
- Hub principal  : embed statique + boutons catégories + bouton "Mes Bonus"
- Vue catégorie  : embed paginé (8 titres/page) + select pour équiper
- Bonus passifs  : tous les titres débloqués s'accumulent, affichés au joueur
"""
from __future__ import annotations
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import TITLES, TITLE_CATEGORIES

_TITLES_LIST: list[tuple[str, dict]] = list(TITLES.items())
_TITLES_PER_PAGE = 10


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _fmt_num(n: int | float) -> str:
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(int(n))


def _format_req(title: dict) -> str:
    rt        = title["req_type"]
    req       = title["req"]
    req_class = title.get("req_class")
    class_prefix = f"[{req_class}] " if req_class else ""
    mapping = {
        "level":                    f"{class_prefix}Niveau {req:,}",
        "prestige":                 f"{class_prefix}Prestige {req:,}",
        "total_gold":               f"{class_prefix}{_fmt_num(req)} golds gagnés au total",
        "zone":                     f"{class_prefix}Zone {req:,} atteinte",
        "dungeon_best_classique":   f"{class_prefix}Donjon classique niveau {req} atteint",
        "dungeon_best_elite":       f"{class_prefix}Donjon élite niveau {req} atteint",
        "dungeon_best_abyssal":     f"{class_prefix}Donjon abyssal niveau {req} atteint",
        "raid_clears":              f"{req:,} raids complétés",
        "raid_max_completed":       f"{class_prefix}Raid niveau {req} complété",
        "wb_total_damage":          f"{class_prefix}{_fmt_num(req)} dégâts au World Boss",
        "harvest_level":            f"Niveau {req} en récolte",
        "craft_level":              f"Niveau {req} en artisanat",
        "conception_level":         f"Niveau {req} en conception",
        "market_sales":             f"{req:,} ventes à l'HDV",
        "pvp_wins":                 f"{req:,} victoires PvP",
        "pvp_elo":                  f"ELO {req:,} en PvP",
        "global_rank1":             "Être classé #1 au Classement Général",
        "pvp_rank1":                "Être classé #1 au Classement PvP",
        "wb_rank1":                 "Être classé #1 au World Boss",
    }
    return mapping.get(rt, f"{rt} ≥ {req}")


def _format_bonus(title: dict) -> str:
    bt = title.get("bonus_type")
    bv = title.get("bonus_value", 0)
    if not bt or not bv:
        return "✨ Cosmétique"
    mapping = {
        "xp_pct":               f"✨ +{bv}% XP global",
        "prestige_bonus_pct":   f"⭐ +{bv}% efficacité du prestige",
        "gold_pct":             f"💰 +{bv}% gold global",
        "monde_loot_pct":       f"📦 +{bv}% loot (Monde)",
        "djc_stats_pct":        f"🏰 +{bv}% stats donjon classique",
        "dje_stats_pct":        f"🏰 +{bv}% stats donjon élite",
        "dja_stats_pct":        f"🏰 +{bv}% stats donjon abyssal",
        "raid_stats_pct":       f"👥 +{bv}% stats en raid",
        "wb_stats_pct":         f"🐉 +{bv}% stats World Boss",
        "harvest_xp_pct":       f"⛏️ +{bv}% XP récolte",
        "craft_xp_pct":         f"🔨 +{bv}% XP artisanat",
        "conception_xp_pct":    f"🔮 +{bv}% XP conception",
        "hdv_discount_pct":     f"🏪 -{bv}% commission HDV",
    }
    return mapping.get(bt, f"+{bv} {bt}")


_BONUS_META: list[tuple[str, str, str]] = [
    ("xp_pct",             "✨", "XP global"),
    ("prestige_bonus_pct", "⭐", "efficacité prestige"),
    ("gold_pct",           "💰", "gold global"),
    ("monde_loot_pct",     "📦", "loot Monde"),
    ("djc_stats_pct",      "🏰", "stats donj. classiques"),
    ("dje_stats_pct",      "🏰", "stats donj. élites"),
    ("dja_stats_pct",      "🏰", "stats donj. abyssaux"),
    ("raid_stats_pct",     "👥", "stats raids"),
    ("wb_stats_pct",       "🐉", "stats World Boss"),
    ("harvest_xp_pct",     "⛏️",  "XP récolte"),
    ("craft_xp_pct",       "🔨", "XP artisanat"),
    ("conception_xp_pct",  "🔮", "XP conception"),
    ("hdv_discount_pct",   "🏪", "remise commission HDV"),
]


def _build_bonus_field(title_bonuses: dict) -> str:
    lines = []
    for key, emoji, label in _BONUS_META:
        val = title_bonuses.get(key, 0)
        if not val:
            continue
        sign = "-" if key == "hdv_discount_pct" else "+"
        lines.append(f"{emoji} **{sign}{val:.4g}%** {label}")
    return "\n".join(lines) if lines else "*Aucun bonus actif pour l'instant.*"


# ─── Hub principal ────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    """Embed persistant du hub (statique, sans donnée joueur)."""
    cat_lines = []
    for cat_id, cat_label in TITLE_CATEGORIES.items():
        count = sum(1 for _, td in _TITLES_LIST if td.get("cat") == cat_id)
        cat_lines.append(f"{cat_label} — **{count} titres**")

    embed = discord.Embed(
        title="🏅 Hub Titres & Succès",
        description=(
            "Débloque des titres en accomplissant des exploits dans le jeu !\n"
            "La plupart des titres activent un **bonus passif permanent** — ils s'accumulent tous.\n"
            "Les titres ⭐ **Spéciaux** sont purement cosmétiques : ils affichent un nom stylé dans les classements.\n\n"
            "**Catégories disponibles :**\n" + "\n".join(cat_lines) + "\n\n"
            "📊 Clique sur **Mes Bonus** pour voir tous tes bonus actifs.\n"
            "🏷️ Clique sur une catégorie pour parcourir les titres et en équiper un."
        ),
        color=0xFFD700,
    )
    view = TitresHubView(bot)
    return embed, view


class TitresHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

        # Bouton "Mes Bonus" en premier
        bonus_btn = discord.ui.Button(
            label="📊 Mes Bonus",
            style=discord.ButtonStyle.success,
            custom_id="rpg:titres:mes_bonus",
            row=0,
        )
        bonus_btn.callback = self._mes_bonus
        self.add_item(bonus_btn)

        # Boutons catégories (row 1 et 2)
        cat_ids = list(TITLE_CATEGORIES.keys())
        for i, cat_id in enumerate(cat_ids):
            cat_label = TITLE_CATEGORIES[cat_id]
            row = 1 if i < 4 else 2
            btn = discord.ui.Button(
                label=cat_label,
                style=discord.ButtonStyle.primary,
                custom_id=f"rpg:titres:cat:{cat_id}",
                row=row,
            )
            btn.callback = self._make_cat_callback(cat_id)
            self.add_item(btn)

    async def _mes_bonus(self, interaction: discord.Interaction):
        player = await db.get_or_create_player(
            interaction.user.id, display_name=interaction.user.display_name
        )
        if not player.get("class"):
            await interaction.response.send_message(
                "❌ Tu n'as pas encore choisi de classe !", ephemeral=True
            )
            return

        player_titles  = await db.get_player_titles(interaction.user.id)
        title_bonuses  = await db.get_title_bonuses(interaction.user.id)
        unlocked_ids   = {t["title_id"] for t in player_titles}
        active_name    = player.get("active_title", "")
        total_unlocked = len(unlocked_ids)
        total_titles   = len(TITLES)

        # Progression par catégorie
        cat_lines = []
        for cat_id, cat_label in TITLE_CATEGORIES.items():
            cat_titles = [(tid, td) for tid, td in _TITLES_LIST if td.get("cat") == cat_id]
            total = len(cat_titles)
            done  = sum(1 for tid, _ in cat_titles if tid in unlocked_ids)
            bar   = "█" * int(done / total * 10) + "░" * (10 - int(done / total * 10)) if total else ""
            cat_lines.append(f"{cat_label}\n`{bar}` **{done}/{total}**")

        embed = discord.Embed(
            title="📊 Mes Bonus Passifs — Titres",
            description=(
                f"**{total_unlocked}/{total_titles}** titres débloqués\n"
                f"Titre équipé : **{active_name}** ✦" if active_name else
                f"**{total_unlocked}/{total_titles}** titres débloqués\n"
                "*Aucun titre équipé*"
            ),
            color=0xFFD700,
        )
        embed.add_field(
            name="⚡ Bonus passifs actifs",
            value=_build_bonus_field(title_bonuses),
            inline=False,
        )
        embed.add_field(
            name="📈 Progression par catégorie",
            value="\n".join(cat_lines),
            inline=False,
        )
        embed.set_footer(text="Les bonus s'accumulent pour tous les titres débloqués, pas seulement l'équipé.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def _make_cat_callback(self, cat_id: str):
        async def callback(interaction: discord.Interaction):
            player = await db.get_or_create_player(
                interaction.user.id, display_name=interaction.user.display_name
            )
            if not player.get("class"):
                await interaction.response.send_message(
                    "❌ Tu n'as pas encore choisi de classe !", ephemeral=True
                )
                return
            await _show_category(interaction, cat_id, page=0)
        return callback


# ─── Vue catégorie paginée ────────────────────────────────────────────────────

async def _show_category(
    interaction: discord.Interaction,
    cat_id: str,
    page: int = 0,
    already_deferred: bool = False,
):
    player        = await db.get_or_create_player(interaction.user.id)
    player_titles = await db.get_player_titles(interaction.user.id)
    title_bonuses = await db.get_title_bonuses(interaction.user.id)
    unlocked_ids  = {t["title_id"] for t in player_titles}
    active_name   = player.get("active_title", "")

    cat_titles  = [(tid, td) for tid, td in _TITLES_LIST if td.get("cat") == cat_id]
    cat_label   = TITLE_CATEGORIES.get(cat_id, cat_id)
    total_pages = max(1, (len(cat_titles) + _TITLES_PER_PAGE - 1) // _TITLES_PER_PAGE)
    page        = max(0, min(page, total_pages - 1))
    page_slice  = cat_titles[page * _TITLES_PER_PAGE: (page + 1) * _TITLES_PER_PAGE]

    unlocked_count = sum(1 for tid, _ in cat_titles if tid in unlocked_ids)

    # ── Lignes titre ──
    lines = []
    for tid, td in page_slice:
        is_unlocked = tid in unlocked_ids
        is_active   = td["name"] == active_name
        if is_active:
            icon = "✦"
        elif is_unlocked:
            icon = "✅"
        else:
            icon = "🔒"

        name_str  = f"**{td['name']}**" + (" *(équipé)*" if is_active else "")
        cond_str  = _format_req(td)
        bonus_str = _format_bonus(td)
        lines.append(
            f"{icon} {name_str}\n"
            f"   📋 {cond_str}\n"
            f"   {bonus_str}"
        )

    # ── Bonus actif dans cette catégorie ──
    cat_bonus_keys = {
        "global":   ["xp_pct", "prestige_bonus_pct", "gold_pct"],
        "monde":    ["monde_loot_pct"],
        "donjons":  ["djc_stats_pct", "dje_stats_pct", "dja_stats_pct"],
        "raids":    ["raid_stats_pct"],
        "wb":       ["wb_stats_pct"],
        "metiers":  ["harvest_xp_pct", "craft_xp_pct", "conception_xp_pct"],
        "hdv":      ["hdv_discount_pct"],
        "pvp":      [],
        "special":  [],
    }
    relevant_keys = cat_bonus_keys.get(cat_id, [])
    cat_bonus_lines = []
    for key, emoji, label in _BONUS_META:
        if key not in relevant_keys:
            continue
        val = title_bonuses.get(key, 0)
        sign = "-" if key == "hdv_discount_pct" else "+"
        cat_bonus_lines.append(
            f"{emoji} **{sign}{val:.4g}%** {label}" if val
            else f"{emoji} +0% {label}"
        )

    embed = discord.Embed(
        title=f"{cat_label} — {unlocked_count}/{len(cat_titles)} débloqués",
        description="\n\n".join(lines),
        color=0xFFD700,
    )
    if cat_bonus_lines:
        embed.add_field(
            name="⚡ Tes bonus actifs (cette catégorie)",
            value="\n".join(cat_bonus_lines),
            inline=False,
        )

    footer_parts = ["✅ débloqué", "🔒 verrouillé", "✦ équipé"]
    if total_pages > 1:
        footer_parts.insert(0, f"Page {page + 1}/{total_pages}")
    embed.set_footer(text=" • ".join(footer_parts))

    view = CategoryView(
        user_id=interaction.user.id,
        cat_id=cat_id,
        page_slice=page_slice,
        unlocked_ids=unlocked_ids,
        active_name=active_name,
        page=page,
        total_pages=total_pages,
    )

    if already_deferred:
        await interaction.edit_original_response(embed=embed, view=view)
    elif interaction.response.is_done():
        await interaction.edit_original_response(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class CategoryView(discord.ui.View):
    def __init__(
        self,
        user_id: int,
        cat_id: str,
        page_slice: list[tuple[str, dict]],
        unlocked_ids: set[str],
        active_name: str,
        page: int,
        total_pages: int,
    ):
        super().__init__(timeout=120)
        self.user_id     = user_id
        self.cat_id      = cat_id
        self.page        = page
        self.total_pages = total_pages

        # ── Select pour équiper (titres débloqués de la page) ──
        equippable = [(tid, td) for tid, td in page_slice if tid in unlocked_ids]
        if equippable:
            options = []
            for tid, td in equippable:
                is_active = td["name"] == active_name
                label_txt = f"{'✦ ' if is_active else ''}{td['name']}"
                desc_txt  = f"{_format_req(td)} • {_format_bonus(td)}"[:100]
                options.append(discord.SelectOption(
                    label=label_txt[:100],
                    value=tid,
                    description=desc_txt,
                    emoji="✦" if is_active else "✅",
                    default=is_active,
                ))
            sel = discord.ui.Select(
                placeholder="🏷️ Équiper / retirer un titre...",
                options=options,
                row=0,
            )
            sel.callback = self._on_equip
            self.add_item(sel)

        # ── Navigation ──
        if total_pages > 1:
            prev_btn = discord.ui.Button(
                label="◀",
                style=discord.ButtonStyle.secondary,
                disabled=(page == 0),
                row=1,
            )
            prev_btn.callback = self._prev
            self.add_item(prev_btn)

            self.add_item(discord.ui.Button(
                label=f"Page {page + 1} / {total_pages}",
                style=discord.ButtonStyle.secondary,
                disabled=True,
                row=1,
            ))

            next_btn = discord.ui.Button(
                label="▶",
                style=discord.ButtonStyle.secondary,
                disabled=(page >= total_pages - 1),
                row=1,
            )
            next_btn.callback = self._next
            self.add_item(next_btn)

    async def _on_equip(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)

        tid        = interaction.data["values"][0]
        title      = TITLES.get(tid)
        if not title:
            return
        player     = await db.get_or_create_player(interaction.user.id)
        title_name = title["name"]

        if player.get("active_title", "") == title_name:
            await db.update_player(interaction.user.id, active_title="")
        else:
            await db.update_player(interaction.user.id, active_title=title_name)

        await _show_category(interaction, self.cat_id, self.page, already_deferred=True)

    async def _prev(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return
        await interaction.response.defer(ephemeral=True)
        await _show_category(interaction, self.cat_id, self.page - 1, already_deferred=True)

    async def _next(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return
        await interaction.response.defer(ephemeral=True)
        await _show_category(interaction, self.cat_id, self.page + 1, already_deferred=True)


async def setup(bot: commands.Bot):
    pass
