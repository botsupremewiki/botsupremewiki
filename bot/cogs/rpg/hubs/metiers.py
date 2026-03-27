"""
Hub Métiers — récolte, craft, conception.
Canal : 1479293726667964517
"""
from __future__ import annotations
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    roll_craft_rarity, get_craft_rarity_weights,
    RARITIES, RARITY_EMOJI, ALL_CLASSES, CLASS_EMOJI,
    STAT_FR, STAT_EMOJI, item_tier_label,
)
from bot.cogs.rpg.items import (
    MATERIALS, CONSUMABLES, PROFESSION_MATERIALS,
    CONCEPTION_RECIPES, CRAFT_RECIPES, EQUIPMENT_CATALOG,
    format_item_name, harvest_drop_bonus, get_equipment_stats,
    get_material_value, max_ingredient_tier,
)

STAT_SHORT = {
    "hp": "PV", "p_atk": "ATK Physique", "m_atk": "ATK Magique",
    "p_def": "DEF Physique", "m_def": "DEF Magique", "p_pen": "PEN Physique",
    "m_pen": "PEN Magique", "speed": "Vitesse", "crit_chance": "Crit%", "crit_damage": "CritDMG%",
}


def _get_craft_set_key(class_name: str) -> str | None:
    from bot.cogs.rpg.models import SET_BONUSES
    for set_key, set_data in SET_BONUSES.items():
        if set_data.get("class") == class_name and set_data.get("source") == "craft":
            return set_key
    return None


def _format_ingredients(ingredients: dict) -> str:
    parts = []
    for mid, qty in ingredients.items():
        mat_data = MATERIALS.get(mid, {})
        name = mat_data.get("name", mid)
        tier = mat_data.get("tier")
        tier_str = f" [T{tier}]" if tier else ""
        emoji = mat_data.get("emoji", "")
        parts.append(f"{emoji} {name}{tier_str} ×{qty}")
    return ", ".join(parts)

HARVEST_PROFESSIONS = {
    "mineur":     {"name": "Mineur",     "emoji": "⛏️",  "desc": "Extrait des minerais et pierres précieuses des profondeurs."},
    "bucheron":   {"name": "Bûcheron",   "emoji": "🪓",   "desc": "Abat des arbres pour obtenir différents types de bois."},
    "herboriste": {"name": "Herboriste", "emoji": "🌿",   "desc": "Cueille herbes, fleurs et champignons magiques."},
    "chasseur":   {"name": "Chasseur",   "emoji": "🏹",   "desc": "Traque les bêtes pour obtenir cuirs, plumes et os."},
    "fermier":    {"name": "Fermier",    "emoji": "🌾",   "desc": "Cultive et récolte des produits agricoles et rares."},
}

# Métiers de récolte recommandés par classe (pour l'équipement d'artisanat)
_CLASS_HARVEST_RECO: dict[str, tuple[str, str]] = {
    "Guerrier":         ("mineur",     "bucheron"),
    "Assassin":         ("herboriste", "chasseur"),
    "Mage":             ("herboriste", "mineur"),
    "Tireur":           ("bucheron",   "chasseur"),
    "Support":          ("mineur",     "fermier"),
    "Vampire":          ("chasseur",   "fermier"),
    "Gardien du Temps": ("mineur",     "bucheron"),   # + herboriste idéalement
    "Ombre Venin":      ("herboriste", "fermier"),
    "Pyromancien":      ("mineur",     "chasseur"),
    "Paladin":          ("bucheron",   "fermier"),
}

CRAFT_PROFESSIONS = {
    "heaumier":  {"name": "Heaumier",   "emoji": "⛑️",  "slot": "casque",      "desc": "Fabrique des casques et protections de tête."},
    "armurier":  {"name": "Armurier",   "emoji": "🦺",   "slot": "plastron",    "desc": "Forge des plastrons et armures de torse."},
    "tailleur":  {"name": "Tailleur",   "emoji": "👖",   "slot": "pantalon",    "desc": "Confectionne des jambières et protections de jambes."},
    "cordonnier":{"name": "Cordonnier", "emoji": "👟",   "slot": "chaussures",  "desc": "Crée des chaussures et bottes pour aventuriers."},
    "forgeron":  {"name": "Forgeron",   "emoji": "⚔️",   "slot": "arme",        "desc": "Forge des armes tranchantes et contondantes."},
    "joaillier": {"name": "Joaillier",  "emoji": "📿",   "slot": "amulette",    "desc": "Façonne des amulettes et bijoux magiques."},
    "orfèvre":   {"name": "Orfèvre",    "emoji": "💍",   "slot": "anneau",      "desc": "Crée des anneaux aux propriétés mystiques."},
}

CONCEPTION_PROFESSIONS = {
    "alchimiste": {"name": "Alchimiste", "emoji": "🧪",  "desc": "Prépare potions et élixirs aux effets puissants."},
    "boulanger":  {"name": "Boulanger",  "emoji": "🍞",   "desc": "Cuisine des aliments qui restaurent l'énergie."},
    "enchanteur": {"name": "Enchanteur", "emoji": "🔮",   "desc": "Crée des runes pour améliorer les équipements."},
}


def _check_has_prof(player_prof: dict, prof_type: str) -> str | None:
    """Retourne le métier actuel d'un type (harvest/craft/conception) ou None."""
    if prof_type == "harvest":
        return player_prof.get("harvest_type")
    elif prof_type == "craft":
        return player_prof.get("craft_type")
    elif prof_type == "conception":
        return player_prof.get("conception_type")
    return None


# ─── Hub principal ─────────────────────────────────────────────────────────

class MetiersHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Métier de Récolte", style=discord.ButtonStyle.primary, emoji="⛏️", custom_id="rpg:metiers:choose_harvest", row=0)
    async def choose_harvest(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        prof = await db.get_professions(interaction.user.id)
        current = _check_has_prof(prof or {}, "harvest")
        player_class = player.get("class")
        embed, view = build_choose_profession_embed("harvest", HARVEST_PROFESSIONS, current, player_class=player_class)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Métier de Craft", style=discord.ButtonStyle.primary, emoji="⚒️", custom_id="rpg:metiers:choose_craft", row=0)
    async def choose_craft(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        prof = await db.get_professions(interaction.user.id)
        current = _check_has_prof(prof or {}, "craft")
        embed, view = build_choose_profession_embed("craft", CRAFT_PROFESSIONS, current)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Métier de Conception", style=discord.ButtonStyle.primary, emoji="🔮", custom_id="rpg:metiers:choose_conception", row=0)
    async def choose_conception(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        prof = await db.get_professions(interaction.user.id)
        current = _check_has_prof(prof or {}, "conception")
        embed, view = build_choose_profession_embed("conception", CONCEPTION_PROFESSIONS, current)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Mes Métiers", style=discord.ButtonStyle.secondary, emoji="🎓", custom_id="rpg:metiers:mes_metiers", row=1)
    async def mes_metiers(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        prof = await db.get_professions(interaction.user.id)
        embed = await build_mes_metiers_embed(interaction.user, prof or {})
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Mes Matériaux", style=discord.ButtonStyle.secondary, emoji="📦", custom_id="rpg:metiers:materiaux", row=1)
    async def mes_materiaux(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        materials = await db.get_materials(interaction.user.id)
        embed, view = build_materiaux_embed(interaction.user, materials, page=0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Craft", style=discord.ButtonStyle.success, emoji="⚔️", custom_id="rpg:metiers:craft", row=1)
    async def craft(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        prof = await db.get_professions(interaction.user.id)
        craft_type = _check_has_prof(prof or {}, "craft")
        if not craft_type:
            await interaction.response.send_message("❌ Tu n'as pas de métier de craft.", ephemeral=True)
            return
        embed, view = build_craft_class_select_embed(interaction.user, prof, craft_type)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Conception", style=discord.ButtonStyle.success, emoji="🧪", custom_id="rpg:metiers:conception", row=1)
    async def conception(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        prof = await db.get_professions(interaction.user.id)
        conc_type = _check_has_prof(prof or {}, "conception")
        if not conc_type:
            await interaction.response.send_message("❌ Tu n'as pas de métier de conception.", ephemeral=True)
            return
        embed, view = await build_conception_embed(interaction.user, player, prof, conc_type, page=0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ─── Choix de profession ──────────────────────────────────────────────────

def build_choose_profession_embed(prof_type: str, professions: dict, current: str | None, player_class: str | None = None) -> tuple:
    type_names = {"harvest": "Récolte", "craft": "Craft", "conception": "Conception"}
    embed = discord.Embed(
        title=f"🔨 Choisir un métier de {type_names.get(prof_type, prof_type)}",
        color=0x5865F2,
    )
    if current:
        embed.description = f"⚠️ Tu as actuellement : **{current}**\nChanger de métier te fera **perdre** ton niveau actuel et recommencer au niveau 1."
    else:
        embed.description = "Choisissez votre métier ci-dessous :"

    # Recommandation par classe pour les métiers de récolte
    if prof_type == "harvest" and player_class and player_class in _CLASS_HARVEST_RECO:
        reco = _CLASS_HARVEST_RECO[player_class]
        reco_names = " + ".join(
            f"{HARVEST_PROFESSIONS[k]['emoji']} **{HARVEST_PROFESSIONS[k]['name']}**"
            for k in reco if k in HARVEST_PROFESSIONS
        )
        extra = " *(+ Herboriste idéalement)*" if player_class == "Gardien du Temps" else ""
        embed.add_field(
            name=f"💡 Recommandé pour {player_class}",
            value=f"{reco_names}{extra} — pour crafter ton équipement de classe.",
            inline=False,
        )

    for key, data in professions.items():
        embed.add_field(
            name=f"{data['emoji']} {data['name']}" + (" *(actuel)*" if key == current else ""),
            value=data["desc"],
            inline=False,
        )

    view = ChooseProfessionView(prof_type, professions, current)
    return embed, view


class ChooseProfessionView(discord.ui.View):
    def __init__(self, prof_type: str, professions: dict, current: str | None):
        super().__init__(timeout=120)
        self.prof_type = prof_type
        for key, data in professions.items():
            btn = discord.ui.Button(
                label=data["name"],
                emoji=data["emoji"],
                style=discord.ButtonStyle.success if key == current else discord.ButtonStyle.primary,
                disabled=(key == current),
                custom_id=f"rpg:metiers:setprof:{prof_type}:{key}",
            )
            btn.callback = self._make_callback(key, data["name"])
            self.add_item(btn)

    def _make_callback(self, prof_key: str, prof_name: str):
        async def callback(interaction: discord.Interaction):
            prof = await db.get_professions(interaction.user.id)
            current = _check_has_prof(prof or {}, self.prof_type)
            if current == prof_key:
                await interaction.response.send_message(f"❌ Tu as déjà le métier **{prof_name}**.", ephemeral=True)
                return
            # Appliquer
            updates = {}
            if self.prof_type == "harvest":
                updates = {"harvest_type": prof_key, "harvest_level": 1, "harvest_xp": 0}
            elif self.prof_type == "craft":
                updates = {"craft_type": prof_key, "craft_level": 1, "craft_xp": 0}
            elif self.prof_type == "conception":
                updates = {"conception_type": prof_key, "conception_level": 1, "conception_xp": 0}
            await db.update_professions(interaction.user.id, **updates)
            embed = discord.Embed(
                title=f"✅ Métier choisi : {prof_name}",
                description=f"Tu commences au **niveau 1** dans ce métier.\nGagne de l'XP de métier en craftant ou en lootant des matériaux !",
                color=0x00FF88,
            )
            await interaction.response.edit_message(embed=embed, view=None)
        return callback


# ─── Mes Métiers ───────────────────────────────────────────────────────────

async def build_mes_metiers_embed(user: discord.User, prof: dict) -> discord.Embed:
    from bot.cogs.rpg.items import get_material_drop_table, MATERIALS

    embed = discord.Embed(
        title=f"🎓 Mes Métiers — {user.display_name}",
        color=0xFF9800,
    )

    # Métier de récolte
    harvest_type  = prof.get("harvest_type")
    harvest_level = prof.get("harvest_level", 1)
    harvest_xp    = prof.get("harvest_xp", 0)
    if harvest_type:
        h_data = HARVEST_PROFESSIONS.get(harvest_type, {})
        xp_next = db.xp_for_prof_level(harvest_level + 1)
        # Top 10 matériaux dropables à niveau actuel
        drop_table = get_material_drop_table(zone=1, harvest_profession=harvest_type, harvest_level=harvest_level)
        drop_table.sort(key=lambda x: x["chance"], reverse=True)
        drop_lines = []
        for drop in drop_table[:10]:
            mat_data = MATERIALS.get(drop["item_id"], {})
            req_level = mat_data.get("level_req", 1)
            can_drop = harvest_level >= req_level
            lock_icon = "" if can_drop else f" 🔒(Niv.{req_level})"
            tier = mat_data.get("tier")
            tier_str = f" [T{tier}]" if tier else ""
            drop_lines.append(f"  {mat_data.get('emoji', '?')} {mat_data.get('name', drop['item_id'])}{tier_str} — {drop['chance']:.1f}%{lock_icon}")
        mats_text = "**Matériaux dropables :**\n" + "\n".join(drop_lines) if drop_lines else "*(aucun)*"
        embed.add_field(
            name=f"{h_data.get('emoji', '⛏️')} {h_data.get('name', harvest_type)} — Niv. {harvest_level}",
            value=f"XP : **{harvest_xp}/{xp_next}**\n{mats_text}",
            inline=False,
        )
    else:
        embed.add_field(name="⛏️ Récolte", value="*Aucun métier choisi*", inline=False)

    # Métier de craft
    craft_type  = prof.get("craft_type")
    craft_level = prof.get("craft_level", 1)
    craft_xp    = prof.get("craft_xp", 0)
    if craft_type:
        c_data = CRAFT_PROFESSIONS.get(craft_type, {})
        xp_next = db.xp_for_prof_level(craft_level + 1)
        embed.add_field(
            name=f"{c_data.get('emoji', '⚒️')} {c_data.get('name', craft_type)} — Niv. {craft_level}",
            value=f"XP : **{craft_xp}/{xp_next}**\nSlot craftable : **{c_data.get('slot', '?')}**",
            inline=False,
        )
    else:
        embed.add_field(name="⚒️ Craft", value="*Aucun métier choisi*", inline=False)

    # Métier de conception
    conc_type  = prof.get("conception_type")
    conc_level = prof.get("conception_level", 1)
    conc_xp    = prof.get("conception_xp", 0)
    if conc_type:
        co_data = CONCEPTION_PROFESSIONS.get(conc_type, {})
        xp_next = db.xp_for_prof_level(conc_level + 1)
        embed.add_field(
            name=f"{co_data.get('emoji', '🧪')} {co_data.get('name', conc_type)} — Niv. {conc_level}",
            value=f"XP : **{conc_xp}/{xp_next}**\n{co_data.get('desc', '')}",
            inline=False,
        )
    else:
        embed.add_field(name="🧪 Conception", value="*Aucun métier choisi*", inline=False)

    embed.set_footer(text="XP de métier gagné en récoltant des matériaux, en craftant et en concevant.")
    return embed


# ─── Matériaux ─────────────────────────────────────────────────────────────

MATS_PER_PAGE = 25

def build_materiaux_embed(user: discord.User, materials: list[dict], page: int = 0) -> tuple:
    # Grouper par profession
    by_prof: dict[str, list] = {}
    for mat in materials:
        mat_data = MATERIALS.get(mat["item_id"], {})
        prof = mat_data.get("profession", "autre")
        by_prof.setdefault(prof, []).append(mat)

    all_lines = []
    for prof_key in ["mineur", "bucheron", "herboriste", "chasseur", "fermier"]:
        if prof_key not in by_prof:
            continue
        prof_data = HARVEST_PROFESSIONS.get(prof_key, {})
        all_lines.append(f"**{prof_data.get('emoji', '')} {prof_data.get('name', prof_key)}**")
        sorted_mats = sorted(by_prof[prof_key], key=lambda m: MATERIALS.get(m["item_id"], {}).get("tier", 0))
        for mat in sorted_mats:
            mat_data = MATERIALS.get(mat["item_id"], {})
            tier = mat_data.get("tier")
            tier_str = f" [T{tier}]" if tier else ""
            all_lines.append(f"  {mat_data.get('emoji', '?')} {mat_data.get('name', mat['item_id'])}{tier_str} ×**{mat['quantity']}**")

    total = len(all_lines)
    total_pages = max(1, (total + MATS_PER_PAGE - 1) // MATS_PER_PAGE)
    page_lines  = all_lines[page * MATS_PER_PAGE:(page + 1) * MATS_PER_PAGE]

    embed = discord.Embed(
        title=f"📦 Matériaux — {user.display_name}",
        description="\n".join(page_lines) if page_lines else "*Aucun matériau*",
        color=0x9C27B0,
    )
    embed.set_footer(text=f"Page {page + 1}/{total_pages} | {sum(m['quantity'] for m in materials)} matériaux au total")

    view = NavigationView(user.id, page, total_pages, "materiaux")
    return embed, view


# ─── Craft d'équipements — sélection de classe ────────────────────────────

def build_craft_class_select_embed(user: discord.User, prof: dict, craft_type: str) -> tuple:
    craft_level = prof.get("craft_level", 1)
    craft_xp    = prof.get("craft_xp", 0)
    slot        = CRAFT_PROFESSIONS[craft_type]["slot"]

    current_tier = min(10, max(1, (craft_level - 1) // 10 + 1))

    # Toutes les classes sont disponibles dès le niveau 1 (tier 1 existe pour toutes)
    class_entries = []
    for class_name in ALL_CLASSES:
        set_key = _get_craft_set_key(class_name)
        if not set_key:
            continue
        item_id   = f"eq_{set_key}_{slot}"
        item_data = EQUIPMENT_CATALOG.get(item_id, {})
        recipe_id = f"crec_{set_key}_{slot}_t{current_tier}"
        recipe    = CRAFT_RECIPES.get(recipe_id, {})
        ingredients = recipe.get("ingredients", {})
        class_entries.append((class_name, item_data, ingredients, current_tier))

    unlocked_lines = []
    options        = []
    for class_name, item_data, ingredients, tier in class_entries:
        item_name = item_data.get("name", f"eq_?_{slot}")
        emoji     = CLASS_EMOJI.get(class_name, "❓")
        ingr_str  = _format_ingredients(ingredients)
        unlocked_lines.append(f"{emoji} **{class_name}** — *{item_name}* [T{tier}]\n  └ {ingr_str}")
        options.append(discord.SelectOption(label=class_name, value=class_name, emoji=emoji))
    locked_lines = []

    lines = unlocked_lines
    if locked_lines:
        lines = unlocked_lines + [""] + locked_lines

    embed = discord.Embed(
        title=f"⚒️ Craft — {CRAFT_PROFESSIONS[craft_type]['name']} (Niv. {craft_level})",
        description=(
            f"Slot craftable : **{slot}** | XP : **{craft_xp}/{db.xp_for_prof_level(craft_level + 1)}**\n"
            f"Choisissez la classe pour laquelle crafter :\n\n"
            + "\n".join(lines)
        ),
        color=0xFF9800,
    )
    view = CraftClassSelectView(user.id, prof, craft_type, options)
    return embed, view


class CraftClassSelectView(discord.ui.View):
    def __init__(self, user_id: int, prof: dict, craft_type: str, options: list):
        super().__init__(timeout=180)
        self.user_id    = user_id
        self.prof       = prof
        self.craft_type = craft_type
        self.selected_class: str | None = None

        if options:
            select = discord.ui.Select(
                placeholder="Choisir une classe...",
                options=options,
                custom_id="rpg:craft:class_select",
                row=0,
            )
            select.callback = self._on_select
            self.add_item(select)

            btn = discord.ui.Button(
                label="Choisir", style=discord.ButtonStyle.primary,
                emoji="✅", custom_id="rpg:craft:class_confirm", row=1,
            )
            btn.callback = self._confirm
            self.add_item(btn)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_class = interaction.data["values"][0]
        await interaction.response.defer()

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_class:
            await interaction.response.send_message("❌ Sélectionne d'abord une classe.", ephemeral=True)
            return
        prof = await db.get_professions(self.user_id)
        embed, view = build_craft_item_detail_embed(interaction.user, prof or self.prof, self.craft_type, self.selected_class)
        await interaction.response.edit_message(embed=embed, view=view)


# ─── Craft d'équipements — détail de l'item par rareté ────────────────────

def build_craft_item_detail_embed(user: discord.User, prof: dict, craft_type: str, selected_class: str) -> tuple:
    craft_level = prof.get("craft_level", 1)
    slot        = CRAFT_PROFESSIONS[craft_type]["slot"]
    item_level  = min(craft_level * 10, 1000)

    set_key   = _get_craft_set_key(selected_class)
    item_id   = f"eq_{set_key}_{slot}"
    tier      = min(10, max(1, (craft_level - 1) // 10 + 1))
    recipe_id = f"crec_{set_key}_{slot}_t{tier}"
    item_data = EQUIPMENT_CATALOG.get(item_id, {})
    recipe    = CRAFT_RECIPES.get(recipe_id, {})
    item_name = item_data.get("name", item_id)
    ingr_str  = _format_ingredients(recipe.get("ingredients", {}))

    weights = get_craft_rarity_weights(craft_level)
    total   = sum(weights)

    lines = []
    for i, rarity in enumerate(RARITIES):
        stats   = get_equipment_stats(item_id, rarity, 0, item_level)
        pct     = weights[i] / total * 100
        emoji   = RARITY_EMOJI.get(rarity, "⬜")
        stat_str = " | ".join(
            f"{STAT_EMOJI.get(k, '')} {STAT_FR.get(k, k)} **{v}**{'%' if k in ('crit_chance', 'crit_damage') else ''}"
            for k, v in stats.items()
        )
        lines.append(f"{emoji} **{rarity.capitalize()}** ({pct:.1f}%) — {stat_str}")

    embed = discord.Embed(
        title=f"⚒️ {item_name} — Niv. {item_level} [{selected_class}]",
        description=f"**Ingrédients :** {ingr_str}\n\n" + "\n".join(lines),
        color=0xFF9800,
    )
    view = CraftItemDetailView(user.id, prof, craft_type, selected_class, item_id, recipe_id)
    return embed, view


class CraftItemDetailView(discord.ui.View):
    def __init__(self, user_id: int, prof: dict, craft_type: str, selected_class: str, item_id: str, recipe_id: str):
        super().__init__(timeout=180)
        self.user_id        = user_id
        self.prof           = prof
        self.craft_type     = craft_type
        self.selected_class = selected_class
        self.item_id        = item_id
        self.recipe_id      = recipe_id

        back_btn = discord.ui.Button(
            label="← Retour", style=discord.ButtonStyle.secondary,
            custom_id="rpg:craft:back", row=0,
        )
        back_btn.callback = self._back
        self.add_item(back_btn)

        confirm_btn = discord.ui.Button(
            label="Confirmer le craft", style=discord.ButtonStyle.success,
            emoji="⚒️", custom_id="rpg:craft:confirm", row=0,
        )
        confirm_btn.callback = self._confirm
        self.add_item(confirm_btn)

    async def _back(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        prof = await db.get_professions(self.user_id)
        embed, view = build_craft_class_select_embed(interaction.user, prof or self.prof, self.craft_type)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        recipe = CRAFT_RECIPES.get(self.recipe_id)
        if not recipe:
            await interaction.response.send_message("❌ Recette introuvable.", ephemeral=True)
            return
        for mat_id, qty in recipe["ingredients"].items():
            if not await db.remove_material(self.user_id, mat_id, qty):
                mat_name = MATERIALS.get(mat_id, {}).get("name", mat_id)
                await interaction.response.send_message(f"❌ Il te manque des **{mat_name}**.", ephemeral=True)
                return
        prof        = await db.get_professions(self.user_id)
        craft_level = prof.get("craft_level", 1) if prof else 1
        rarity      = roll_craft_rarity(craft_level)
        item_level  = min(craft_level * 10, 1000)
        await db.add_equipment(self.user_id, self.item_id, rarity, 0, item_level)
        item_tier = recipe.get("tier", 1)
        xp_gain = item_tier * item_tier * 50
        title_bonuses = await db.get_title_bonuses(self.user_id)
        xp_gain = int(xp_gain * (1 + title_bonuses.get("craft_xp_pct", 0) / 100))
        _, new_level, leveled = await db.add_profession_xp(self.user_id, "craft", xp_gain)
        item_name = format_item_name(self.item_id, rarity)
        tier_lbl = item_tier_label(self.item_id)
        tier_str = f" [{tier_lbl}]" if tier_lbl else ""
        msg = f"✅ Tu as crafté : **{item_name}**{tier_str} *(nv. {item_level})* !\n+{xp_gain} XP de craft"
        if leveled:
            msg += f"\n🎉 Tu es passé au niveau **{new_level}** en {CRAFT_PROFESSIONS.get(self.craft_type, {}).get('name', self.craft_type)} !"
        await interaction.response.send_message(msg, ephemeral=True)


# ─── Conception ───────────────────────────────────────────────────────────

CONCEPTION_PER_PAGE = 10

async def build_conception_embed(user: discord.User, player: dict, prof: dict, conc_type: str, page: int = 0) -> tuple:
    conc_level = prof.get("conception_level", 1)
    conc_xp    = prof.get("conception_xp", 0)

    max_tier_allowed = conc_level // 10 + 1
    all_for_prof = [
        (rid, rdata) for rid, rdata in CONCEPTION_RECIPES.items()
        if rdata.get("profession") == conc_type
    ]
    # Split into unlocked (sortable by level_req) and locked (sorted by unlock tier)
    unlocked_recipes = sorted(
        [(rid, rdata) for rid, rdata in all_for_prof
         if max_ingredient_tier(rdata.get("ingredients", {})) <= max_tier_allowed],
        key=lambda x: x[1].get("level_req", 1),
    )
    locked_recipes = sorted(
        [(rid, rdata) for rid, rdata in all_for_prof
         if max_ingredient_tier(rdata.get("ingredients", {})) > max_tier_allowed],
        key=lambda x: max_ingredient_tier(x[1].get("ingredients", {})),
    )

    total_pages = max(1, (len(unlocked_recipes) + CONCEPTION_PER_PAGE - 1) // CONCEPTION_PER_PAGE)
    recipe_list = unlocked_recipes[page * CONCEPTION_PER_PAGE:(page + 1) * CONCEPTION_PER_PAGE]
    materials   = {m["item_id"]: m["quantity"] for m in await db.get_materials(user.id)}

    embed = discord.Embed(
        title=f"🧪 Conception — {CONCEPTION_PROFESSIONS.get(conc_type, {}).get('name', conc_type)} (Niv. {conc_level})",
        color=0x9C27B0,
    )
    embed.add_field(name="📊 Progression", value=f"XP : {conc_xp}/{db.xp_for_prof_level(conc_level + 1)}", inline=True)

    options = []
    for recipe_id, recipe in recipe_list:
        result_data = CONSUMABLES.get(recipe["result"], {})
        ingr_ok  = all(materials.get(mid, 0) >= qty for mid, qty in recipe["ingredients"].items())
        level_ok = conc_level >= recipe.get("level_req", 1)
        available = "✅" if ingr_ok and level_ok else "❌"
        ingr_str  = ", ".join(
            f"{MATERIALS.get(mid, {}).get('emoji', '')} {MATERIALS.get(mid, {}).get('name', mid)}"
            + (f" [T{MATERIALS.get(mid, {}).get('tier')}]" if MATERIALS.get(mid, {}).get('tier') else "")
            + f" ×{qty}"
            for mid, qty in recipe["ingredients"].items()
        )
        embed.add_field(
            name=f"{available} {result_data.get('emoji', '')} **{result_data.get('name', recipe['result'])}** (Niv. requis : {recipe.get('level_req', 1)})",
            value=f"Ingrédients : {ingr_str}",
            inline=False,
        )
        if ingr_ok and level_ok:
            options.append(discord.SelectOption(
                label=result_data.get("name", recipe["result"])[:100],
                value=recipe_id,
                description=f"Niv. {recipe.get('level_req', 1)} requis",
            ))

    # Show locked recipe stubs on the last page
    if locked_recipes and page == total_pages - 1:
        lock_lines = []
        for _, rdata in locked_recipes[:8]:
            result_data = CONSUMABLES.get(rdata["result"], {})
            ing_tier = max_ingredient_tier(rdata.get("ingredients", {}))
            unlock_level = (ing_tier - 1) * 10
            lock_lines.append(
                f"🔒 {result_data.get('emoji', '')} **{result_data.get('name', rdata['result'])}** — Niv. {unlock_level}+"
            )
        embed.add_field(
            name="🔒 Recettes verrouillées",
            value="\n".join(lock_lines),
            inline=False,
        )

    view = ConceptionView(user.id, player, prof, conc_type, page, total_pages, options)
    return embed, view


class ConceptionQtyModal(discord.ui.Modal, title="Quantité à concevoir"):
    quantity = discord.ui.TextInput(
        label="Quantité",
        placeholder="Ex: 5 (max 99)",
        default="1",
        min_length=1,
        max_length=2,
        required=True,
    )

    def __init__(self, parent_view: "ConceptionView", recipe: dict):
        super().__init__()
        self.parent_view = parent_view
        self.recipe      = recipe

    async def on_submit(self, interaction: discord.Interaction):
        try:
            times = max(1, min(99, int(self.quantity.value)))
        except ValueError:
            await interaction.response.send_message("❌ Quantité invalide.", ephemeral=True)
            return

        recipe = self.recipe
        user_id = self.parent_view.user_id

        # Vérifier et retirer tous les ingrédients d'un coup
        for mat_id, qty_per_craft in recipe["ingredients"].items():
            total_needed = qty_per_craft * times
            if not await db.remove_material(user_id, mat_id, total_needed):
                mat_name = MATERIALS.get(mat_id, {}).get("name", mat_id)
                # Calcule le max craftable
                stock = await db.get_material_qty(user_id, mat_id)
                max_times = stock // qty_per_craft if qty_per_craft > 0 else 0
                if max_times == 0:
                    await interaction.response.send_message(
                        f"❌ Il te manque des **{mat_name}** (×{total_needed} nécessaires).", ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        f"❌ Pas assez de **{mat_name}** pour ×{times}. Tu peux en concevoir ×{max_times} max.", ephemeral=True
                    )
                return

        result_id = recipe["result"]
        await db.add_consumable(user_id, result_id, times)

        item_tier = min(10, recipe.get("level_req", 0) // 10 + 1)
        xp_gain = item_tier * item_tier * 50 * times
        title_bonuses = await db.get_title_bonuses(user_id)
        xp_gain = int(xp_gain * (1 + title_bonuses.get("conception_xp_pct", 0) / 100))
        _, new_level, leveled = await db.add_profession_xp(user_id, "conception", xp_gain)

        result_data = CONSUMABLES.get(result_id, {})
        msg = f"✅ Tu as conçu : {result_data.get('emoji', '')} **{result_data.get('name', result_id)}** ×{times} !\n+{xp_gain} XP de conception"
        if leveled:
            conc_type = self.parent_view.conc_type
            msg += f"\n🎉 Niveau **{new_level}** en {CONCEPTION_PROFESSIONS.get(conc_type, {}).get('name', conc_type)} !"
        await interaction.response.send_message(msg, ephemeral=True)


class ConceptionView(discord.ui.View):
    def __init__(self, user_id: int, player: dict, prof: dict, conc_type: str, page: int, total_pages: int, options: list):
        super().__init__(timeout=180)
        self.user_id    = user_id
        self.player     = player
        self.prof       = prof
        self.conc_type  = conc_type
        self.page       = page
        self.total_pages= total_pages
        self.selected_recipe: str | None = None

        if options:
            select = discord.ui.Select(placeholder="Choisir une recette...", options=options, custom_id="rpg:conc:select", row=0)
            select.callback = self._on_select
            self.add_item(select)

        conc_btn = discord.ui.Button(label="Concevoir", style=discord.ButtonStyle.success, emoji="🧪", custom_id="rpg:conc:do", row=1)
        conc_btn.callback = self._do_conc
        self.add_item(conc_btn)

        if total_pages > 1:
            prev = discord.ui.Button(label="◀", style=discord.ButtonStyle.secondary, disabled=(page == 0), custom_id="rpg:conc:prev", row=2)
            prev.callback = self._prev
            self.add_item(prev)
            nxt  = discord.ui.Button(label="▶", style=discord.ButtonStyle.secondary, disabled=(page >= total_pages - 1), custom_id="rpg:conc:next", row=2)
            nxt.callback = self._next
            self.add_item(nxt)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_recipe = interaction.data["values"][0]
        await interaction.response.defer()

    async def _do_conc(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected_recipe:
            await interaction.response.send_message("❌ Sélectionne d'abord une recette.", ephemeral=True)
            return
        recipe = CONCEPTION_RECIPES.get(self.selected_recipe)
        if not recipe:
            await interaction.response.send_message("❌ Recette introuvable.", ephemeral=True)
            return
        modal = ConceptionQtyModal(self, recipe)
        await interaction.response.send_modal(modal)

    async def _prev(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        prof   = await db.get_professions(self.user_id)
        embed, view = await build_conception_embed(interaction.user, player, prof, self.conc_type, max(0, self.page - 1))
        await interaction.response.edit_message(embed=embed, view=view)

    async def _next(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        prof   = await db.get_professions(self.user_id)
        embed, view = await build_conception_embed(interaction.user, player, prof, self.conc_type, self.page + 1)
        await interaction.response.edit_message(embed=embed, view=view)


# ─── Navigation générique ──────────────────────────────────────────────────

class NavigationView(discord.ui.View):
    def __init__(self, user_id: int, page: int, total_pages: int, context: str):
        super().__init__(timeout=120)
        self.user_id     = user_id
        self.page        = page
        self.total_pages = total_pages
        self.context     = context
        if total_pages > 1:
            prev = discord.ui.Button(label="◀", style=discord.ButtonStyle.secondary, disabled=(page == 0), custom_id=f"rpg:{context}:nav_prev")
            prev.callback = self._prev
            self.add_item(prev)
            nxt  = discord.ui.Button(label="▶", style=discord.ButtonStyle.secondary, disabled=(page >= total_pages - 1), custom_id=f"rpg:{context}:nav_next")
            nxt.callback = self._next
            self.add_item(nxt)

        sell_btn = discord.ui.Button(label="Vendre", style=discord.ButtonStyle.success, emoji="💰")
        sell_btn.callback = self._sell
        self.add_item(sell_btn)

    async def _prev(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        materials = await db.get_materials(self.user_id)
        embed, view = build_materiaux_embed(interaction.user, materials, max(0, self.page - 1))
        await interaction.response.edit_message(embed=embed, view=view)

    async def _next(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        materials = await db.get_materials(self.user_id)
        embed, view = build_materiaux_embed(interaction.user, materials, self.page + 1)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _sell(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        materials = await db.get_materials(self.user_id)
        if not materials:
            await interaction.response.send_message("❌ Aucun matériau à vendre.", ephemeral=True)
            return
        embed = discord.Embed(
            title="💰 Vendre un matériau",
            description="Sélectionne le matériau à vendre au marchand :",
            color=0xFF9800,
        )
        await interaction.response.edit_message(embed=embed, view=SellMaterialSelectView(self.user_id, materials))


class SellMaterialSelectView(discord.ui.View):
    def __init__(self, user_id: int, materials: list):
        super().__init__(timeout=120)
        self.user_id   = user_id
        self.materials = materials
        self.selected: str | None = None

        options = [
            discord.SelectOption(
                label=f"{MATERIALS.get(m['item_id'], {}).get('name', m['item_id'])} ×{m['quantity']}"[:100],
                value=m["item_id"],
                description=f"Valeur : {get_material_value(m['item_id']):,} golds/u"[:100],
            )
            for m in materials[:25]
        ]
        select = discord.ui.Select(placeholder="Choisir un matériau...", options=options)
        select.callback = self._on_select
        self.add_item(select)

        sell_all_btn = discord.ui.Button(label="Vendre tout", style=discord.ButtonStyle.danger, emoji="💰", row=1)
        sell_all_btn.callback = self._sell_all
        self.add_item(sell_all_btn)

        qty_btn = discord.ui.Button(label="Quantité précise", style=discord.ButtonStyle.primary, emoji="✏️", row=1)
        qty_btn.callback = self._sell_custom
        self.add_item(qty_btn)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected = interaction.data["values"][0]
        mat = next((m for m in self.materials if m["item_id"] == self.selected), None)
        unit_val = get_material_value(self.selected)
        mat_name = MATERIALS.get(self.selected, {}).get("name", self.selected)
        mat_emoji = MATERIALS.get(self.selected, {}).get("emoji", "")
        qty = mat["quantity"] if mat else 0
        embed = discord.Embed(
            title="💰 Vendre un matériau",
            description=(
                f"{mat_emoji} **{mat_name}** ×{qty}\n"
                f"Valeur unitaire : **{unit_val:,}** golds\n"
                f"Valeur totale : **{unit_val * qty:,}** golds"
            ),
            color=0xFF9800,
        )
        await interaction.response.edit_message(embed=embed)

    async def _sell_all(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected:
            await interaction.response.send_message("❌ Sélectionne d'abord un matériau.", ephemeral=True)
            return
        mat = next((m for m in self.materials if m["item_id"] == self.selected), None)
        if not mat:
            await interaction.response.send_message("❌ Matériau introuvable.", ephemeral=True)
            return
        await self._do_sell(interaction, mat["quantity"])

    async def _sell_custom(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if not self.selected:
            await interaction.response.send_message("❌ Sélectionne d'abord un matériau.", ephemeral=True)
            return
        mat = next((m for m in self.materials if m["item_id"] == self.selected), None)
        if not mat:
            await interaction.response.send_message("❌ Matériau introuvable.", ephemeral=True)
            return
        unit_val = get_material_value(self.selected)
        await interaction.response.send_modal(
            SellMaterialQtyModal(self.user_id, self.selected, mat["quantity"], unit_val)
        )

    async def _do_sell(self, interaction: discord.Interaction, qty: int):
        ok = await db.remove_material(self.user_id, self.selected, qty)
        if not ok:
            await interaction.response.send_message("❌ Quantité insuffisante.", ephemeral=True)
            return
        unit_val = get_material_value(self.selected)
        gold_earned = unit_val * qty
        player = await db.get_player(self.user_id)
        await db.update_player(self.user_id, gold=player["gold"] + gold_earned)
        mat_name = MATERIALS.get(self.selected, {}).get("name", self.selected)
        mat_emoji = MATERIALS.get(self.selected, {}).get("emoji", "")
        embed = discord.Embed(
            title="✅ Vente effectuée",
            description=(
                f"Tu as vendu {mat_emoji} **{mat_name}** ×{qty}\n"
                f"Tu reçois : **{gold_earned:,}** golds 💰"
            ),
            color=0x00FF88,
        )
        await interaction.response.edit_message(embed=embed, view=None)


class SellMaterialQtyModal(discord.ui.Modal, title="Quantité à vendre"):
    quantity = discord.ui.TextInput(label="Quantité", placeholder="ex: 10", min_length=1, max_length=6)

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
        ok = await db.remove_material(self.user_id, self.item_id, qty)
        if not ok:
            await interaction.response.send_message("❌ Quantité insuffisante.", ephemeral=True)
            return
        gold_earned = self.unit_val * qty
        player = await db.get_player(self.user_id)
        await db.update_player(self.user_id, gold=player["gold"] + gold_earned)
        mat_name = MATERIALS.get(self.item_id, {}).get("name", self.item_id)
        mat_emoji = MATERIALS.get(self.item_id, {}).get("emoji", "")
        await interaction.response.send_message(
            f"✅ Vendu {mat_emoji} **{mat_name}** ×{qty} pour **{gold_earned:,}** golds 💰",
            ephemeral=True,
        )


# ─── Build hub ─────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🔨 Hub Métiers",
        description=(
            "Les métiers permettent de **collecter** des ressources, **crafter** des équipements et **concevoir** des consommables.\n\n"
            "**Métiers de Récolte** *(boost de loot de matériaux)*\n"
            + "\n".join(f"{v['emoji']} **{v['name']}** — {v['desc']}" for v in HARVEST_PROFESSIONS.values())
            + "\n\n**Métiers de Craft** *(fabrication d'équipements)*\n"
            + "\n".join(f"{v['emoji']} **{v['name']}** — Slot : {v['slot']}" for v in CRAFT_PROFESSIONS.values())
            + "\n\n**Métiers de Conception** *(consommables)*\n"
            + "\n".join(f"{v['emoji']} **{v['name']}** — {v['desc']}" for v in CONCEPTION_PROFESSIONS.values())
            + "\n\n⚠️ Tu ne peux avoir qu'**un seul métier par catégorie**. Changer efface le niveau actuel."
        ),
        color=0xFF9800,
    )
    view = MetiersHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
