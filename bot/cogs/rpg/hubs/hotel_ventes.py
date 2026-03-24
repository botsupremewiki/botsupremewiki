"""
Hub Hôtel des Ventes.
Canal : 1479297549977256057
"""
from __future__ import annotations
import json
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.items import (
    format_item_name, format_eq_name, MATERIALS, CONSUMABLES,
    get_material_value, get_consumable_value, get_equipment_value,
)
from bot.cogs.rpg.models import RARITIES, RARITY_EMOJI

HDV_COMMISSION   = 0.05   # 5% prélevés sur la vente (gold sink)
HDV_MIN_PRICE_PCT = 1.0   # prix minimum = 100% de la valeur de base

_PAGE_SIZE = 10


class HotelVentesHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Parcourir les annonces", style=discord.ButtonStyle.primary,
                       emoji="🛒", custom_id="rpg:hdv:browse", row=0)
    async def browse(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_browse(interaction, page=0)

    @discord.ui.button(label="Mes annonces", style=discord.ButtonStyle.secondary,
                       emoji="📋", custom_id="rpg:hdv:mine", row=0)
    async def mine(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_my_listings(interaction)

    @discord.ui.button(label="Vendre un item", style=discord.ButtonStyle.success,
                       emoji="💰", custom_id="rpg:hdv:sell", row=0)
    async def sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _handle_sell_menu(interaction)


# ─── Browse ────────────────────────────────────────────────────────────────────

async def _handle_browse(interaction: discord.Interaction, page: int = 0):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    if not player.get("class"):
        await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
        return

    listings = await db.get_market_listings()
    if not listings:
        embed = discord.Embed(
            title="🛒 Hôtel des Ventes — Annonces",
            description="*Aucune annonce disponible pour l'instant.*",
            color=0xFF9800,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    total_pages = max(1, (len(listings) + _PAGE_SIZE - 1) // _PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    slice_ = listings[page * _PAGE_SIZE:(page + 1) * _PAGE_SIZE]

    embed = discord.Embed(
        title="🛒 Hôtel des Ventes — Annonces",
        description=f"Page **{page + 1}/{total_pages}** — {len(listings)} annonce(s)",
        color=0xFF9800,
    )
    for lst in slice_:
        item_type = lst.get("item_type", "equipment")
        if item_type == "equipment":
            name = format_eq_name(lst)
        elif item_type == "material":
            mat = MATERIALS.get(lst["item_id"], {})
            name = f"{mat.get('emoji', '📦')} {mat.get('name', lst['item_id'])}"
        else:
            cons = CONSUMABLES.get(lst["item_id"], {})
            name = f"{cons.get('emoji', '🧪')} {cons.get('name', lst['item_id'])}"

        qty_txt = f" ×{lst['quantity']}" if lst.get("quantity", 1) > 1 else ""
        embed.add_field(
            name=f"{name}{qty_txt}",
            value=(
                f"💰 **{lst['price']:,}** golds\n"
                f"👤 {lst['seller_name']}\n"
                f"🆔 ID: `{lst['id']}`"
            ),
            inline=True,
        )

    view = BrowseView(interaction.user.id, page, total_pages, listings)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class BrowseView(discord.ui.View):
    def __init__(self, user_id: int, page: int, total_pages: int, listings: list):
        super().__init__(timeout=180)
        self.user_id     = user_id
        self.page        = page
        self.total_pages = total_pages
        self.listings    = listings

        if page > 0:
            prev_btn = discord.ui.Button(label="◀ Précédent", style=discord.ButtonStyle.secondary)
            prev_btn.callback = self._prev
            self.add_item(prev_btn)

        if page < total_pages - 1:
            next_btn = discord.ui.Button(label="Suivant ▶", style=discord.ButtonStyle.secondary)
            next_btn.callback = self._next
            self.add_item(next_btn)

        # Dropdown pour acheter
        slice_ = listings[page * _PAGE_SIZE:(page + 1) * _PAGE_SIZE]
        if slice_:
            options = []
            for lst in slice_:
                item_type = lst.get("item_type", "equipment")
                if item_type == "equipment":
                    label = format_eq_name(lst)
                elif item_type == "material":
                    mat = MATERIALS.get(lst["item_id"], {})
                    label = f"{mat.get('name', lst['item_id'])}"
                else:
                    cons = CONSUMABLES.get(lst["item_id"], {})
                    label = f"{cons.get('name', lst['item_id'])}"
                options.append(discord.SelectOption(
                    label=label[:100],
                    value=str(lst["id"]),
                    description=f"{lst['price']:,} golds — {lst['seller_name']}"[:100],
                ))
            select = discord.ui.Select(placeholder="Acheter une annonce...", options=options[:25])
            select.callback = self._buy
            self.add_item(select)

    async def _prev(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        await _handle_browse(interaction, self.page - 1)

    async def _next(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        await _handle_browse(interaction, self.page + 1)

    async def _buy(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        listing_id = int(interaction.data["values"][0])
        listing = next((l for l in self.listings if l["id"] == listing_id), None)
        if not listing:
            await interaction.response.send_message("❌ Annonce introuvable (peut-être déjà vendue).", ephemeral=True)
            return

        if listing["seller_id"] == interaction.user.id:
            await interaction.response.send_message("❌ Tu ne peux pas acheter ta propre annonce.", ephemeral=True)
            return

        player = await db.get_player(interaction.user.id)
        if not player or player["gold"] < listing["price"]:
            await interaction.response.send_message(
                f"❌ Pas assez d'or ! (besoin : **{listing['price']:,}**, tu as : **{player.get('gold', 0):,}**)",
                ephemeral=True
            )
            return

        # Transaction
        ok = await db.remove_market_listing(listing_id)
        if not ok:
            await interaction.response.send_message("❌ Annonce introuvable (peut-être déjà vendue).", ephemeral=True)
            return

        # Commission réduite par les titres HDV du vendeur (plancher 1%)
        seller_title_bonuses = await db.get_title_bonuses(listing["seller_id"])
        discount = seller_title_bonuses.get("hdv_discount_pct", 0) / 100
        effective_commission = max(0.01, HDV_COMMISSION - discount)
        commission    = int(listing["price"] * effective_commission)
        seller_gets   = listing["price"] - commission
        await db.update_player(interaction.user.id, gold=player["gold"] - listing["price"])
        # Créditer le vendeur (moins la commission réduite)
        seller = await db.get_player(listing["seller_id"])
        if seller:
            await db.update_player(listing["seller_id"], gold=seller["gold"] + seller_gets)

        # Donner l'item à l'acheteur
        item_type = listing.get("item_type", "equipment")
        if item_type == "equipment":
            await db.add_equipment(
                interaction.user.id,
                listing["item_id"],
                listing.get("rarity", "commun"),
                listing.get("enhancement", 0),
                listing.get("level", 1),
                listing.get("rune_bonuses"),
            )
            item_name = format_eq_name(listing)
        elif item_type == "material":
            mat = MATERIALS.get(listing["item_id"], {})
            await db.add_material(interaction.user.id, listing["item_id"], listing.get("quantity", 1))
            item_name = mat.get("name", listing["item_id"])
        else:
            cons = CONSUMABLES.get(listing["item_id"], {})
            await db.add_consumable(interaction.user.id, listing["item_id"], listing.get("quantity", 1))
            item_name = cons.get("name", listing["item_id"])

        await db.increment_quest_stat(interaction.user.id, "market_buys")
        embed = discord.Embed(
            title="✅ Achat réussi !",
            description=(
                f"Tu as acheté **{item_name}** pour **{listing['price']:,}** golds.\n"
                f"*(Le vendeur a reçu **{seller_gets:,}** golds après commission de **{commission:,}** — 5%)*"
            ),
            color=0x00FF88,
        )
        await interaction.response.edit_message(embed=embed, view=None)


# ─── Mes annonces ──────────────────────────────────────────────────────────────

async def _handle_my_listings(interaction: discord.Interaction):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    if not player.get("class"):
        await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
        return

    listings = await db.get_market_listings(seller_id=interaction.user.id)
    embed = discord.Embed(
        title="📋 Mes annonces",
        description=f"Tu as **{len(listings)}** annonce(s) active(s).",
        color=0xFF9800,
    )
    if not listings:
        embed.description = "*Aucune annonce active.*"
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    for lst in listings[:25]:
        item_type = lst.get("item_type", "equipment")
        if item_type == "equipment":
            name = format_eq_name(lst)
        elif item_type == "material":
            mat = MATERIALS.get(lst["item_id"], {})
            name = f"{mat.get('name', lst['item_id'])}"
        else:
            cons = CONSUMABLES.get(lst["item_id"], {})
            name = f"{cons.get('name', lst['item_id'])}"
        embed.add_field(
            name=name,
            value=f"💰 **{lst['price']:,}** golds | ID: `{lst['id']}`",
            inline=True,
        )

    view = MyListingsView(interaction.user.id, listings)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class MyListingsView(discord.ui.View):
    def __init__(self, user_id: int, listings: list):
        super().__init__(timeout=180)
        self.user_id  = user_id
        self.listings = listings

        if listings:
            options = []
            for lst in listings[:25]:
                item_type = lst.get("item_type", "equipment")
                if item_type == "equipment":
                    label = format_eq_name(lst)
                elif item_type == "material":
                    mat = MATERIALS.get(lst["item_id"], {})
                    label = mat.get("name", lst["item_id"])
                else:
                    cons = CONSUMABLES.get(lst["item_id"], {})
                    label = cons.get("name", lst["item_id"])
                options.append(discord.SelectOption(
                    label=label[:100],
                    value=str(lst["id"]),
                    description=f"Prix : {lst['price']:,} golds"[:100],
                ))
            select = discord.ui.Select(placeholder="Retirer une annonce...", options=options)
            select.callback = self._cancel
            self.add_item(select)

    async def _cancel(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        listing_id = int(interaction.data["values"][0])
        listing = next((l for l in self.listings if l["id"] == listing_id), None)
        if not listing:
            await interaction.response.send_message("❌ Annonce introuvable.", ephemeral=True)
            return

        ok = await db.remove_market_listing(listing_id)
        if not ok:
            await interaction.response.send_message("❌ Impossible de retirer l'annonce.", ephemeral=True)
            return

        # L'item est envoyé directement en banque (gratuit)
        item_type = listing.get("item_type", "equipment")
        if item_type == "equipment":
            await db.deposit_bank_equipment(
                interaction.user.id,
                listing["item_id"],
                listing.get("rarity", "commun"),
                listing.get("enhancement", 0),
                listing.get("level", 1),
                listing.get("rune_bonuses"),
            )
            item_name = format_eq_name(listing)
        elif item_type == "material":
            mat = MATERIALS.get(listing["item_id"], {})
            await db.deposit_bank_material(interaction.user.id, listing["item_id"], listing.get("quantity", 1))
            item_name = mat.get("name", listing["item_id"])
        else:
            cons = CONSUMABLES.get(listing["item_id"], {})
            await db.deposit_bank_consumable(interaction.user.id, listing["item_id"], listing.get("quantity", 1))
            item_name = cons.get("name", listing["item_id"])

        embed = discord.Embed(
            title="✅ Annonce retirée",
            description=f"**{item_name}** a été retiré de l'HDV et placé dans ta **banque** automatiquement.",
            color=0x00FF88,
        )
        await interaction.response.edit_message(embed=embed, view=None)


# ─── Vendre ────────────────────────────────────────────────────────────────────

async def _handle_sell_menu(interaction: discord.Interaction):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    if not player.get("class"):
        await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
        return

    embed = discord.Embed(
        title="💰 Vendre un item",
        description="Choisis le type d'item que tu veux mettre en vente.",
        color=0xFF9800,
    )
    view = SellTypeView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class SellTypeView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

        eq_btn = discord.ui.Button(label="Équipement", style=discord.ButtonStyle.primary, emoji="⚔️")
        eq_btn.callback = self._sell_equipment
        self.add_item(eq_btn)

        mat_btn = discord.ui.Button(label="Matériaux", style=discord.ButtonStyle.secondary, emoji="📦")
        mat_btn.callback = self._sell_material
        self.add_item(mat_btn)

        cons_btn = discord.ui.Button(label="Consommables", style=discord.ButtonStyle.secondary, emoji="🧪")
        cons_btn.callback = self._sell_consumable
        self.add_item(cons_btn)

    async def _sell_equipment(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        equipment = await db.get_equipment(self.user_id)
        unequipped = [e for e in equipment if not e.get("slot_equipped")]
        if not unequipped:
            await interaction.response.send_message("❌ Aucun équipement non-équipé dans ton inventaire.", ephemeral=True)
            return
        view = SellEquipmentView(self.user_id, unequipped)
        embed = discord.Embed(title="⚔️ Vendre un équipement", description="Sélectionne un item dans le menu ci-dessous :", color=0xFF9800)
        lines = []
        for eq in unequipped[:25]:
            name = format_eq_name(eq)
            lines.append(f"**{name}** — {eq.get('rarity', 'commun')}")
        embed.description += "\n" + "\n".join(lines)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _sell_material(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        materials = await db.get_materials(self.user_id)
        if not materials:
            await interaction.response.send_message("❌ Aucun matériau dans ton inventaire.", ephemeral=True)
            return
        view = SellMaterialView(self.user_id, materials)
        embed = discord.Embed(title="📦 Vendre des matériaux", description="Sélectionne un matériau dans le menu ci-dessous :", color=0xFF9800)
        lines = []
        for mat in materials[:25]:
            mat_info = MATERIALS.get(mat["item_id"], {})
            emoji = mat_info.get("emoji", "📦")
            name = mat_info.get("name", mat["item_id"])
            qty = mat.get("quantity", 1)
            lines.append(f"{emoji} **{name}** ×{qty}")
        embed.description += "\n" + "\n".join(lines)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _sell_consumable(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        consumables = await db.get_consumables(self.user_id)
        if not consumables:
            await interaction.response.send_message("❌ Aucun consommable dans ton inventaire.", ephemeral=True)
            return
        view = SellConsumableView(self.user_id, consumables)
        embed = discord.Embed(title="🧪 Vendre des consommables", description="Sélectionne un consommable dans le menu ci-dessous :", color=0xFF9800)
        lines = []
        for cons in consumables[:25]:
            cons_info = CONSUMABLES.get(cons["item_id"], {})
            emoji = cons_info.get("emoji", "🧪")
            name = cons_info.get("name", cons["item_id"])
            qty = cons.get("quantity", 1)
            lines.append(f"{emoji} **{name}** ×{qty}")
        embed.description += "\n" + "\n".join(lines)
        await interaction.response.edit_message(embed=embed, view=view)


class SellEquipmentView(discord.ui.View):
    def __init__(self, user_id: int, equipment: list):
        super().__init__(timeout=180)
        self.user_id   = user_id
        self.equipment = equipment
        self.selected_eq_id: int | None = None

        options = []
        for eq in equipment[:25]:
            options.append(discord.SelectOption(
                label=format_eq_name(eq)[:100],
                value=str(eq["id"]),
                description=f"Rareté : {eq.get('rarity', 'commun')}"[:100],
            ))
        select = discord.ui.Select(placeholder="Choisir un équipement...", options=options)
        select.callback = self._select_eq
        self.add_item(select)

        price_btn = discord.ui.Button(label="Définir le prix et vendre", style=discord.ButtonStyle.success, emoji="💰")
        price_btn.callback = self._open_price_modal
        self.add_item(price_btn)

    async def _select_eq(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_eq_id = int(interaction.data["values"][0])
        await interaction.response.defer()

    async def _open_price_modal(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if self.selected_eq_id is None:
            await interaction.response.send_message("❌ Sélectionne d'abord un équipement.", ephemeral=True)
            return
        eq = next((e for e in self.equipment if e["id"] == self.selected_eq_id), None)
        if not eq:
            await interaction.response.send_message("❌ Équipement introuvable.", ephemeral=True)
            return
        modal = PriceModal(self.user_id, "equipment", eq)
        await interaction.response.send_modal(modal)


class SellMaterialView(discord.ui.View):
    def __init__(self, user_id: int, materials: list):
        super().__init__(timeout=180)
        self.user_id   = user_id
        self.materials = materials
        self.selected_mat_id: str | None = None

        options = []
        for mat in materials[:25]:
            mat_info = MATERIALS.get(mat["item_id"], {})
            options.append(discord.SelectOption(
                label=f"{mat_info.get('name', mat['item_id'])} ×{mat['quantity']}"[:100],
                value=mat["item_id"],
                description=f"Tier {mat_info.get('tier', 1)}"[:100],
            ))
        select = discord.ui.Select(placeholder="Choisir un matériau...", options=options)
        select.callback = self._select_mat
        self.add_item(select)

        price_btn = discord.ui.Button(label="Définir le prix et vendre", style=discord.ButtonStyle.success, emoji="💰")
        price_btn.callback = self._open_price_modal
        self.add_item(price_btn)

    async def _select_mat(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_mat_id = interaction.data["values"][0]
        await interaction.response.defer()

    async def _open_price_modal(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if self.selected_mat_id is None:
            await interaction.response.send_message("❌ Sélectionne d'abord un matériau.", ephemeral=True)
            return
        mat = next((m for m in self.materials if m["item_id"] == self.selected_mat_id), None)
        if not mat:
            await interaction.response.send_message("❌ Matériau introuvable.", ephemeral=True)
            return
        modal = PriceModal(self.user_id, "material", mat)
        await interaction.response.send_modal(modal)


class SellConsumableView(discord.ui.View):
    def __init__(self, user_id: int, consumables: list):
        super().__init__(timeout=180)
        self.user_id     = user_id
        self.consumables = consumables
        self.selected_cons_id: str | None = None

        options = []
        for cons in consumables[:25]:
            cons_info = CONSUMABLES.get(cons["item_id"], {})
            options.append(discord.SelectOption(
                label=f"{cons_info.get('name', cons['item_id'])} ×{cons['quantity']}"[:100],
                value=cons["item_id"],
            ))
        select = discord.ui.Select(placeholder="Choisir un consommable...", options=options)
        select.callback = self._select_cons
        self.add_item(select)

        price_btn = discord.ui.Button(label="Définir le prix et vendre", style=discord.ButtonStyle.success, emoji="💰")
        price_btn.callback = self._open_price_modal
        self.add_item(price_btn)

    async def _select_cons(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.selected_cons_id = interaction.data["values"][0]
        await interaction.response.defer()

    async def _open_price_modal(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        if self.selected_cons_id is None:
            await interaction.response.send_message("❌ Sélectionne d'abord un consommable.", ephemeral=True)
            return
        cons = next((c for c in self.consumables if c["item_id"] == self.selected_cons_id), None)
        if not cons:
            await interaction.response.send_message("❌ Consommable introuvable.", ephemeral=True)
            return
        modal = PriceModal(self.user_id, "consumable", cons)
        await interaction.response.send_modal(modal)


class PriceModal(discord.ui.Modal, title="Définir le prix de vente"):
    price_input = discord.ui.TextInput(
        label="Prix (en golds)",
        placeholder="Ex: 50000",
        min_length=1,
        max_length=12,
    )
    quantity_input = discord.ui.TextInput(
        label="Quantité (pour matériaux/consommables)",
        placeholder="Ex: 10 (laisser 1 pour équipement)",
        default="1",
        min_length=1,
        max_length=5,
        required=False,
    )

    def __init__(self, user_id: int, item_type: str, item: dict):
        super().__init__()
        self.user_id   = user_id
        self.item_type = item_type
        self.item      = item

    async def on_submit(self, interaction: discord.Interaction):
        try:
            price = int(self.price_input.value.replace(" ", "").replace(",", ""))
            qty   = int(self.quantity_input.value or "1")
        except ValueError:
            await interaction.response.send_message("❌ Prix ou quantité invalide.", ephemeral=True)
            return

        if price < 1:
            await interaction.response.send_message("❌ Le prix doit être au moins 1 gold.", ephemeral=True)
            return

        qty = max(1, qty)

        # Vérification du prix minimum (= valeur de base de l'item)
        if self.item_type == "equipment":
            min_price = get_equipment_value(
                self.item.get("level", 1),
                self.item.get("rarity", "commun"),
                self.item.get("source", "monde"),
                self.item.get("enhancement", 0),
            )
        elif self.item_type == "material":
            min_price = get_material_value(self.item["item_id"]) * qty
        else:
            min_price = get_consumable_value(self.item["item_id"]) * qty

        if price < min_price:
            await interaction.response.send_message(
                f"❌ Prix trop bas ! Le prix minimum pour cet item est **{min_price:,}** golds "
                f"(valeur de base). Les items ne peuvent pas être vendus en dessous de leur valeur de base.",
                ephemeral=True,
            )
            return

        player = await db.get_player(self.user_id)
        if not player:
            await interaction.response.send_message("❌ Profil introuvable.", ephemeral=True)
            return

        seller_name = interaction.user.display_name

        if self.item_type == "equipment":
            # Retirer l'équipement de l'inventaire
            ok = await db.remove_equipment(self.user_id, self.item["id"])
            if not ok:
                await interaction.response.send_message("❌ Impossible de retirer l'équipement.", ephemeral=True)
                return
            await db.add_market_listing(
                seller_id=self.user_id,
                seller_name=seller_name,
                item_type="equipment",
                item_id=self.item["item_id"],
                rarity=self.item.get("rarity", "commun"),
                enhancement=self.item.get("enhancement", 0),
                quantity=1,
                price=price,
                level=self.item.get("level", 1),
                rune_bonuses=self.item.get("rune_bonuses"),
            )
            item_name = format_item_name(self.item["item_id"], self.item.get("rarity", "commun"))

        elif self.item_type == "material":
            qty = min(qty, self.item.get("quantity", 1))
            ok = await db.remove_material(self.user_id, self.item["item_id"], qty)
            if not ok:
                await interaction.response.send_message("❌ Pas assez de matériaux.", ephemeral=True)
                return
            await db.add_market_listing(
                seller_id=self.user_id,
                seller_name=seller_name,
                item_type="material",
                item_id=self.item["item_id"],
                rarity="commun",
                enhancement=0,
                quantity=qty,
                price=price,
            )
            mat_info = MATERIALS.get(self.item["item_id"], {})
            item_name = f"{mat_info.get('name', self.item['item_id'])} ×{qty}"

        else:  # consumable
            qty = min(qty, self.item.get("quantity", 1))
            ok = await db.remove_consumable(self.user_id, self.item["item_id"], qty)
            if not ok:
                await interaction.response.send_message("❌ Pas assez de consommables.", ephemeral=True)
                return
            await db.add_market_listing(
                seller_id=self.user_id,
                seller_name=seller_name,
                item_type="consumable",
                item_id=self.item["item_id"],
                rarity="commun",
                enhancement=0,
                quantity=qty,
                price=price,
            )
            cons_info = CONSUMABLES.get(self.item["item_id"], {})
            item_name = f"{cons_info.get('name', self.item['item_id'])} ×{qty}"

        await db.increment_quest_stat(self.user_id, "market_sells")
        embed = discord.Embed(
            title="✅ Annonce créée !",
            description=f"**{item_name}** mis en vente pour **{price:,}** golds.",
            color=0x00FF88,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ─── Build hub ─────────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🛒 Hôtel des Ventes",
        description=(
            "L'Hôtel des Ventes permet d'**acheter et vendre** des items entre joueurs.\n\n"
            "**Règles :**\n"
            "• 💰 Prix minimum : **valeur de base** de l'item (anti-dump)\n"
            "• 💸 Commission : **5%** prélevés sur le montant reçu par le vendeur\n"
            "• 🏦 Annulation : l'item est automatiquement envoyé en **banque** (sans frais)\n\n"
            "**Types d'items échangeables :**\n"
            "⚔️ Équipements • 📦 Matériaux • 🧪 Consommables\n\n"
            "**Comment vendre :**\n"
            "1. Clique sur **Vendre un item**\n"
            "2. Choisis le type d'item et entre le prix\n"
            "3. Ton annonce est visible par tous !\n\n"
            "**Comment acheter :**\n"
            "1. Clique sur **Parcourir les annonces**\n"
            "2. Sélectionne et confirme l'achat\n\n"
            "*En cas d'annulation, l'item va en banque — le retrait de banque coûte 10%.*"
        ),
        color=0xFF9800,
    )
    view = HotelVentesHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
