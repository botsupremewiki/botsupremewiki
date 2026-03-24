"""
Hub Banque — stockage sécurisé persistant aux prestiges.
Canal : 1479297760833437808
"""
from __future__ import annotations
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.items import (
    MATERIALS, CONSUMABLES, EQUIPMENT_CATALOG, format_item_name, format_eq_name,
    get_material_value, get_consumable_value,
)
from bot.cogs.rpg.models import RARITY_EMOJI

ITEMS_PER_PAGE  = 20
WITHDRAW_FEE    = 0.10  # 10% sur tous les retraits

# Frais de retrait équipement (basés sur rareté car level non stocké en banque)
_EQ_FEE_BASE: dict[str, int] = {
    "commun": 500, "peu_commun": 2_000, "rare": 8_000,
    "épique": 40_000, "légendaire": 200_000,
}

def _eq_fee(rarity: str, enhancement: int = 0) -> int:
    return max(1, int(_EQ_FEE_BASE.get(rarity, 500) * (1 + enhancement * 0.10)))


# ─── Hub principal ──────────────────────────────────────────────────────────

class BanqueHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Voir ma Banque", style=discord.ButtonStyle.primary, emoji="🏦", custom_id="rpg:banque:voir", row=0)
    async def voir_banque(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        embed, view = await build_banque_embed(interaction.user, page=0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Déposer", style=discord.ButtonStyle.success, emoji="📥", custom_id="rpg:banque:deposer", row=0)
    async def deposer(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        embed = discord.Embed(
            title="📥 Déposer en Banque",
            description="Que souhaitez-vous déposer ?\n✅ Le dépôt est **gratuit**.",
            color=0x4CAF50,
        )
        await interaction.response.send_message(embed=embed, view=DepositTypeView(interaction.user.id, player), ephemeral=True)

    @discord.ui.button(label="Retirer", style=discord.ButtonStyle.secondary, emoji="📤", custom_id="rpg:banque:retirer", row=0)
    async def retirer(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        embed, view = await build_withdraw_embed(interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ─── Affichage banque ───────────────────────────────────────────────────────

async def build_banque_embed(user: discord.User, page: int = 0) -> tuple:
    gold_banque = await db.get_bank_gold(user.id)
    equipments  = await db.get_bank_equipment(user.id)
    materials   = await db.get_bank_materials(user.id)
    consumables = await db.get_bank_consumables(user.id)

    lines = [f"**💰 Or en banque : {gold_banque:,}** golds", ""]

    if equipments:
        lines.append("**⚔️ Équipements**")
        for eq in equipments:
            name = format_eq_name(eq)
            fee  = _eq_fee(eq.get("rarity", "commun"), eq.get("enhancement", 0))
            lines.append(f"  {name} *(retrait : {fee:,} golds)*")

    if materials:
        lines.append("**📦 Matériaux**")
        for mat in materials:
            md       = MATERIALS.get(mat["item_id"], {})
            fee_unit = int(get_material_value(mat["item_id"]) * WITHDRAW_FEE)
            lines.append(f"  {md.get('emoji','?')} {md.get('name', mat['item_id'])} ×{mat['quantity']} *(retrait : {fee_unit:,}/u)*")

    if consumables:
        lines.append("**🧪 Consommables**")
        for cons in consumables:
            cd       = CONSUMABLES.get(cons["item_id"], {})
            fee_unit = int(get_consumable_value(cons["item_id"]) * WITHDRAW_FEE)
            lines.append(f"  {cd.get('emoji','?')} {cd.get('name', cons['item_id'])} ×{cons['quantity']} *(retrait : {fee_unit:,}/u)*")

    if not equipments and not materials and not consumables and gold_banque == 0:
        lines.append("*La banque est vide.*")

    total_pages = max(1, (len(lines) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page_lines  = lines[page * ITEMS_PER_PAGE:(page + 1) * ITEMS_PER_PAGE]

    embed = discord.Embed(
        title=f"🏦 Banque — {user.display_name}",
        description="\n".join(page_lines),
        color=0xFFD700,
    )
    embed.set_footer(text=f"Page {page + 1}/{total_pages} | Dépôt gratuit • Retrait : 10% de frais")
    return embed, BanqueVoirView(user.id, page, total_pages)


class BanqueVoirView(discord.ui.View):
    def __init__(self, user_id: int, page: int, total_pages: int):
        super().__init__(timeout=120)
        self.user_id     = user_id
        self.page        = page
        self.total_pages = total_pages
        if total_pages > 1:
            prev = discord.ui.Button(label="◀", style=discord.ButtonStyle.secondary, disabled=(page == 0))
            prev.callback = self._prev
            self.add_item(prev)
            nxt = discord.ui.Button(label="▶", style=discord.ButtonStyle.secondary, disabled=(page >= total_pages - 1))
            nxt.callback = self._next
            self.add_item(nxt)

    async def _prev(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        embed, view = await build_banque_embed(interaction.user, max(0, self.page - 1))
        await interaction.response.edit_message(embed=embed, view=view)

    async def _next(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        embed, view = await build_banque_embed(interaction.user, self.page + 1)
        await interaction.response.edit_message(embed=embed, view=view)


# ─── Dépôt : sélection du type ─────────────────────────────────────────────

class DepositTypeView(discord.ui.View):
    def __init__(self, user_id: int, player: dict):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.player  = player
        for label, emoji, t in [
            ("Or", "💰", "gold"), ("Équipements", "⚔️", "equipment"),
            ("Matériaux", "📦", "material"), ("Consommables", "🧪", "consumable"),
        ]:
            btn = discord.ui.Button(label=label, emoji=emoji, style=discord.ButtonStyle.primary)
            btn.callback = self._make_cb(t)
            self.add_item(btn)
        all_btn = discord.ui.Button(label="Tout déposer", emoji="📦", style=discord.ButtonStyle.danger, row=1)
        all_btn.callback = self._deposit_all
        self.add_item(all_btn)

    async def _deposit_all(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        player    = await db.get_player(self.user_id)
        equipment = await db.get_equipment(self.user_id)
        mats      = await db.get_materials(self.user_id)
        cons      = await db.get_consumables(self.user_id)
        gold      = player["gold"] if player else 0
        unequipped = [e for e in equipment if not e.get("slot_equipped")]
        lines = []
        if gold > 0:      lines.append(f"💰 **{gold:,}** golds")
        if unequipped:    lines.append(f"⚔️ **{len(unequipped)}** équipement(s)")
        if mats:          lines.append(f"📦 **{len(mats)}** type(s) de matériaux")
        if cons:          lines.append(f"🧪 **{len(cons)}** type(s) de consommables")
        if not lines:
            await interaction.response.send_message("❌ Tu n'as rien à déposer.", ephemeral=True); return
        embed = discord.Embed(
            title="📦 Tout déposer en Banque",
            description="Voici ce qui sera déposé :\n" + "\n".join(lines) + "\n\n✅ Dépôt entièrement **gratuit**.",
            color=0x4CAF50,
        )
        await interaction.response.edit_message(embed=embed, view=ConfirmDepositAllView(self.user_id))

    def _make_cb(self, type_: str):
        async def cb(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return

            if type_ == "gold":
                player = await db.get_player(self.user_id)
                gold   = player["gold"] if player else 0
                if gold <= 0:
                    await interaction.response.send_message("❌ Tu n'as pas d'or à déposer.", ephemeral=True); return
                embed = discord.Embed(
                    title="📥 Déposer de l'or",
                    description=f"💰 Tu as **{gold:,}** golds en main.\n✅ Le dépôt est **gratuit**.",
                    color=0x4CAF50,
                )
                await interaction.response.edit_message(embed=embed, view=GoldDepositView(self.user_id, gold))

            elif type_ == "equipment":
                equipment  = await db.get_equipment(self.user_id)
                unequipped = [e for e in equipment if not e.get("slot_equipped")][:25]
                if not unequipped:
                    await interaction.response.send_message("❌ Aucun équipement non équipé à déposer.", ephemeral=True); return
                options = [
                    discord.SelectOption(
                        label=format_eq_name(e)[:100],
                        value=str(e["id"]),
                        description=f"Rareté : {e.get('rarity', 'commun')}"[:100],
                    ) for e in unequipped
                ]
                embed = discord.Embed(title="📥 Déposer un équipement", description="Sélectionne l'équipement *(dépôt gratuit)* :", color=0x4CAF50)
                await interaction.response.edit_message(embed=embed, view=DepositEquipmentView(self.user_id, options))

            elif type_ == "material":
                mats = await db.get_materials(self.user_id)
                if not mats:
                    await interaction.response.send_message("❌ Aucun matériau à déposer.", ephemeral=True); return
                options = [
                    discord.SelectOption(
                        label=f"{MATERIALS.get(m['item_id'], {}).get('name', m['item_id'])} ×{m['quantity']}"[:100],
                        value=m["item_id"],
                        description=f"Disponible : {m['quantity']}"[:100],
                    ) for m in mats[:25]
                ]
                embed = discord.Embed(title="📥 Déposer des matériaux", description="Sélectionne le matériau *(dépôt gratuit)* :", color=0x4CAF50)
                await interaction.response.edit_message(embed=embed, view=DepositItemView(self.user_id, "material", options, mats))

            else:  # consumable
                cons = await db.get_consumables(self.user_id)
                if not cons:
                    await interaction.response.send_message("❌ Aucun consommable à déposer.", ephemeral=True); return
                options = [
                    discord.SelectOption(
                        label=f"{CONSUMABLES.get(c['item_id'], {}).get('name', c['item_id'])} ×{c['quantity']}"[:100],
                        value=c["item_id"],
                        description=f"Disponible : {c['quantity']}"[:100],
                    ) for c in cons[:25]
                ]
                embed = discord.Embed(title="📥 Déposer des consommables", description="Sélectionne le consommable *(dépôt gratuit)* :", color=0x4CAF50)
                await interaction.response.edit_message(embed=embed, view=DepositItemView(self.user_id, "consumable", options, cons))
        return cb


# ─── Dépôt : Tout déposer ──────────────────────────────────────────────────

class ConfirmDepositAllView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        c = discord.ui.Button(label="✅ Confirmer", style=discord.ButtonStyle.success)
        c.callback = self._confirm; self.add_item(c)
        a = discord.ui.Button(label="❌ Annuler", style=discord.ButtonStyle.danger)
        a.callback = self._cancel; self.add_item(a)

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        player    = await db.get_player(self.user_id)
        equipment = await db.get_equipment(self.user_id)
        mats      = await db.get_materials(self.user_id)
        cons      = await db.get_consumables(self.user_id)
        gold      = player["gold"] if player else 0
        unequipped = [e for e in equipment if not e.get("slot_equipped")]
        lines = []
        # Or
        if gold > 0:
            await db.update_player(self.user_id, gold=0)
            await db.add_bank_gold(self.user_id, gold)
            lines.append(f"💰 **{gold:,}** golds")
        # Équipements
        for item in unequipped:
            await db.remove_equipment(self.user_id, item["id"])
            await db.deposit_bank_equipment(self.user_id, item["item_id"], item.get("rarity", "commun"), item.get("enhancement", 0), item.get("level", 1), item.get("rune_bonuses"))
        if unequipped:
            lines.append(f"⚔️ **{len(unequipped)}** équipement(s)")
        # Matériaux
        for mat in mats:
            await db.remove_material(self.user_id, mat["item_id"], mat["quantity"])
            await db.deposit_bank_material(self.user_id, mat["item_id"], mat["quantity"])
        if mats:
            lines.append(f"📦 **{len(mats)}** type(s) de matériaux")
        # Consommables
        for con in cons:
            await db.remove_consumable(self.user_id, con["item_id"], con["quantity"])
            await db.deposit_bank_consumable(self.user_id, con["item_id"], con["quantity"])
        if cons:
            lines.append(f"🧪 **{len(cons)}** type(s) de consommables")
        if not lines:
            await interaction.response.edit_message(embed=discord.Embed(description="❌ Rien à déposer.", color=0xFF0000), view=None); return
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="✅ Tout déposé !",
                description="\n".join(lines) + "\n\nTout a été déposé gratuitement en banque.",
                color=0x00FF88,
            ),
            view=None,
        )

    async def _cancel(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        await interaction.response.edit_message(embed=discord.Embed(description="❌ Dépôt annulé.", color=0xFF0000), view=None)


# ─── Dépôt : Or ────────────────────────────────────────────────────────────

class GoldDepositView(discord.ui.View):
    def __init__(self, user_id: int, gold: int):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.gold    = gold
        all_btn = discord.ui.Button(label=f"Tout déposer ({gold:,} golds)", style=discord.ButtonStyle.success, emoji="💰")
        all_btn.callback = self._deposit_all
        self.add_item(all_btn)
        custom_btn = discord.ui.Button(label="Montant précis", style=discord.ButtonStyle.secondary, emoji="✏️")
        custom_btn.callback = self._deposit_custom
        self.add_item(custom_btn)

    async def _deposit_all(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        player = await db.get_player(self.user_id)
        amount = player["gold"] if player else 0
        if amount <= 0:
            await interaction.response.edit_message(embed=discord.Embed(description="❌ Tu n'as pas d'or.", color=0xFF0000), view=None); return
        embed = discord.Embed(
            title="📥 Confirmer le dépôt",
            description=f"💰 Déposer **{amount:,}** golds en banque ?\n✅ Dépôt **gratuit**.",
            color=0x4CAF50,
        )
        await interaction.response.edit_message(embed=embed, view=ConfirmGoldDepositView(self.user_id, amount))

    async def _deposit_custom(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        await interaction.response.send_modal(GoldDepositModal(self.user_id, self.gold))


class GoldDepositModal(discord.ui.Modal, title="Déposer de l'or en banque"):
    amount_input = discord.ui.TextInput(label="Montant à déposer (golds)", min_length=1, max_length=15)

    def __init__(self, user_id: int, gold: int):
        super().__init__()
        self.user_id = user_id
        self.amount_input.placeholder = f"Max : {gold:,}"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value.replace(" ", "").replace(",", "").replace(".", ""))
        except ValueError:
            await interaction.response.send_message("❌ Montant invalide.", ephemeral=True); return
        if amount <= 0:
            await interaction.response.send_message("❌ Le montant doit être positif.", ephemeral=True); return
        player = await db.get_player(self.user_id)
        if not player or player["gold"] < amount:
            await interaction.response.send_message(f"❌ Tu n'as que **{player.get('gold', 0):,}** golds.", ephemeral=True); return
        embed = discord.Embed(
            title="📥 Confirmer le dépôt",
            description=f"💰 Déposer **{amount:,}** golds en banque ?\n✅ Dépôt **gratuit**.",
            color=0x4CAF50,
        )
        await interaction.response.send_message(embed=embed, view=ConfirmGoldDepositView(self.user_id, amount), ephemeral=True)


class ConfirmGoldDepositView(discord.ui.View):
    def __init__(self, user_id: int, amount: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.amount  = amount
        c = discord.ui.Button(label="✅ Confirmer", style=discord.ButtonStyle.success)
        c.callback = self._confirm; self.add_item(c)
        a = discord.ui.Button(label="❌ Annuler", style=discord.ButtonStyle.danger)
        a.callback = self._cancel; self.add_item(a)

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        player = await db.get_player(self.user_id)
        if not player or player["gold"] < self.amount:
            await interaction.response.edit_message(embed=discord.Embed(description="❌ Pas assez d'or !", color=0xFF0000), view=None); return
        await db.update_player(self.user_id, gold=player["gold"] - self.amount)
        await db.add_bank_gold(self.user_id, self.amount)
        await interaction.response.edit_message(
            embed=discord.Embed(title="✅ Dépôt effectué !", description=f"💰 **{self.amount:,}** golds déposés gratuitement.", color=0x00FF88),
            view=None,
        )

    async def _cancel(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        await interaction.response.edit_message(embed=discord.Embed(description="❌ Dépôt annulé.", color=0xFF0000), view=None)


# ─── Dépôt : Équipement ────────────────────────────────────────────────────

class DepositEquipmentView(discord.ui.View):
    def __init__(self, user_id: int, options: list):
        super().__init__(timeout=120)
        self.user_id  = user_id
        self.selected: int | None = None
        s = discord.ui.Select(placeholder="Choisir un équipement...", options=options)
        s.callback = self._on_select; self.add_item(s)
        b = discord.ui.Button(label="Déposer (gratuit)", style=discord.ButtonStyle.success, emoji="📥")
        b.callback = self._deposit; self.add_item(b)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        self.selected = int(interaction.data["values"][0])
        await interaction.response.defer()

    async def _deposit(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        if self.selected is None:
            await interaction.response.send_message("❌ Sélectionne d'abord un équipement.", ephemeral=True); return
        equipment = await db.get_equipment(self.user_id)
        item = next((e for e in equipment if e["id"] == self.selected), None)
        if not item:
            await interaction.response.send_message("❌ Équipement introuvable.", ephemeral=True); return
        await db.remove_equipment(self.user_id, self.selected)
        await db.deposit_bank_equipment(self.user_id, item["item_id"], item.get("rarity", "commun"), item.get("enhancement", 0), item.get("level", 1), item.get("rune_bonuses"))
        name = format_eq_name(item)
        await interaction.response.edit_message(
            embed=discord.Embed(title="✅ Déposé !", description=f"⚔️ **{name}** est maintenant en banque.", color=0x00FF88),
            view=None,
        )


# ─── Dépôt : Matériaux / Consommables ──────────────────────────────────────

class DepositItemView(discord.ui.View):
    def __init__(self, user_id: int, item_type: str, options: list, items: list):
        super().__init__(timeout=120)
        self.user_id   = user_id
        self.item_type = item_type
        self.items     = items
        self.selected: str | None = None
        s = discord.ui.Select(placeholder="Choisir un item...", options=options)
        s.callback = self._on_select; self.add_item(s)
        b1 = discord.ui.Button(label="Tout déposer", style=discord.ButtonStyle.success, emoji="📥")
        b1.callback = self._deposit_all; self.add_item(b1)
        b2 = discord.ui.Button(label="Quantité précise", style=discord.ButtonStyle.secondary, emoji="✏️")
        b2.callback = self._deposit_custom; self.add_item(b2)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        self.selected = interaction.data["values"][0]
        await interaction.response.defer()

    async def _deposit_all(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        if not self.selected:
            await interaction.response.send_message("❌ Sélectionne d'abord un item.", ephemeral=True); return
        await self._do_deposit(interaction, qty=None)

    async def _deposit_custom(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        if not self.selected:
            await interaction.response.send_message("❌ Sélectionne d'abord un item.", ephemeral=True); return
        item = next((i for i in self.items if i["item_id"] == self.selected), None)
        max_qty = item["quantity"] if item else 1
        await interaction.response.send_modal(DepositQuantityModal(self.user_id, self.item_type, self.selected, max_qty))

    async def _do_deposit(self, interaction: discord.Interaction, qty: int | None):
        if self.item_type == "material":
            items = await db.get_materials(self.user_id)
            item  = next((m for m in items if m["item_id"] == self.selected), None)
            if not item:
                await interaction.response.send_message("❌ Matériau introuvable.", ephemeral=True); return
            qty = min(qty or item["quantity"], item["quantity"])
            await db.remove_material(self.user_id, self.selected, qty)
            await db.deposit_bank_material(self.user_id, self.selected, qty)
            name = MATERIALS.get(self.selected, {}).get("name", self.selected)
            emoji = "📦"
        else:
            items = await db.get_consumables(self.user_id)
            item  = next((c for c in items if c["item_id"] == self.selected), None)
            if not item:
                await interaction.response.send_message("❌ Consommable introuvable.", ephemeral=True); return
            qty = min(qty or item["quantity"], item["quantity"])
            await db.remove_consumable(self.user_id, self.selected, qty)
            await db.deposit_bank_consumable(self.user_id, self.selected, qty)
            name = CONSUMABLES.get(self.selected, {}).get("name", self.selected)
            emoji = "🧪"
        await interaction.response.edit_message(
            embed=discord.Embed(title="✅ Déposé !", description=f"{emoji} **{name}** ×{qty} déposé(s) gratuitement.", color=0x00FF88),
            view=None,
        )


class DepositQuantityModal(discord.ui.Modal, title="Quantité à déposer"):
    qty_input = discord.ui.TextInput(label="Quantité", min_length=1, max_length=10)

    def __init__(self, user_id: int, item_type: str, item_id: str, max_qty: int):
        super().__init__()
        self.user_id   = user_id
        self.item_type = item_type
        self.item_id   = item_id
        self.max_qty   = max_qty
        self.qty_input.placeholder = f"Entre 1 et {max_qty}"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qty = int(self.qty_input.value.strip())
        except ValueError:
            await interaction.response.send_message("❌ Quantité invalide.", ephemeral=True); return
        if qty <= 0 or qty > self.max_qty:
            await interaction.response.send_message(f"❌ Quantité invalide (1 à {self.max_qty}).", ephemeral=True); return
        if self.item_type == "material":
            ok   = await db.remove_material(self.user_id, self.item_id, qty)
            if ok: await db.deposit_bank_material(self.user_id, self.item_id, qty)
            name  = MATERIALS.get(self.item_id, {}).get("name", self.item_id)
            emoji = "📦"
        else:
            ok   = await db.remove_consumable(self.user_id, self.item_id, qty)
            if ok: await db.deposit_bank_consumable(self.user_id, self.item_id, qty)
            name  = CONSUMABLES.get(self.item_id, {}).get("name", self.item_id)
            emoji = "🧪"
        if not ok:
            await interaction.response.send_message("❌ Pas assez d'items.", ephemeral=True); return
        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Déposé !", description=f"{emoji} **{name}** ×{qty} déposé(s) gratuitement.", color=0x00FF88),
            ephemeral=True,
        )


# ─── Retrait ───────────────────────────────────────────────────────────────

async def build_withdraw_embed(user: discord.User) -> tuple:
    gold_banque = await db.get_bank_gold(user.id)
    equipments  = await db.get_bank_equipment(user.id)
    materials   = await db.get_bank_materials(user.id)
    consumables = await db.get_bank_consumables(user.id)
    embed = discord.Embed(
        title=f"📤 Retirer de la Banque — {user.display_name}",
        description=f"💰 **Or en banque : {gold_banque:,}** golds\n⚠️ Frais de retrait : **10%** sur tous les retraits",
        color=0xFF9800,
    )
    return embed, WithdrawTypeView(user.id, equipments, materials, consumables, gold_banque)


class WithdrawTypeView(discord.ui.View):
    def __init__(self, user_id: int, equipments: list, materials: list, consumables: list, gold: int):
        super().__init__(timeout=120)
        self.user_id     = user_id
        self.equipments  = equipments
        self.materials   = materials
        self.consumables = consumables
        self.gold        = gold
        if equipments:
            b = discord.ui.Button(label="Équipements", emoji="⚔️", style=discord.ButtonStyle.primary)
            b.callback = self._eq; self.add_item(b)
        if materials:
            b = discord.ui.Button(label="Matériaux", emoji="📦", style=discord.ButtonStyle.primary)
            b.callback = self._mat; self.add_item(b)
        if consumables:
            b = discord.ui.Button(label="Consommables", emoji="🧪", style=discord.ButtonStyle.primary)
            b.callback = self._cons; self.add_item(b)
        if gold > 0:
            b = discord.ui.Button(label="Or", emoji="💰", style=discord.ButtonStyle.success)
            b.callback = self._gold; self.add_item(b)

    async def _eq(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        options = [
            discord.SelectOption(
                label=format_eq_name(e)[:100],
                value=str(e["id"]),
                description=f"Frais : {_eq_fee(e.get('rarity','commun'), e.get('enhancement',0)):,} golds"[:100],
            ) for e in self.equipments[:25]
        ]
        embed = discord.Embed(title="📤 Retirer un équipement", description="⚠️ Frais (10% de la valeur) payés en or depuis ton inventaire.", color=0xFF9800)
        await interaction.response.edit_message(embed=embed, view=WithdrawEquipmentView(self.user_id, options, self.equipments))

    async def _mat(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        options = [
            discord.SelectOption(
                label=f"{MATERIALS.get(m['item_id'], {}).get('name', m['item_id'])} ×{m['quantity']}"[:100],
                value=m["item_id"],
                description=f"Frais : {int(get_material_value(m['item_id']) * WITHDRAW_FEE):,} golds/u"[:100],
            ) for m in self.materials[:25]
        ]
        embed = discord.Embed(title="📤 Retirer des matériaux", description="⚠️ Frais (10% de la valeur/unité) payés en or.", color=0xFF9800)
        await interaction.response.edit_message(embed=embed, view=WithdrawItemView(self.user_id, "material", options, self.materials))

    async def _cons(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        options = [
            discord.SelectOption(
                label=f"{CONSUMABLES.get(c['item_id'], {}).get('name', c['item_id'])} ×{c['quantity']}"[:100],
                value=c["item_id"],
                description=f"Frais : {int(get_consumable_value(c['item_id']) * WITHDRAW_FEE):,} golds/u"[:100],
            ) for c in self.consumables[:25]
        ]
        embed = discord.Embed(title="📤 Retirer des consommables", description="⚠️ Frais (10% de la valeur/unité) payés en or.", color=0xFF9800)
        await interaction.response.edit_message(embed=embed, view=WithdrawItemView(self.user_id, "consumable", options, self.consumables))

    async def _gold(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        gold = await db.get_bank_gold(self.user_id)
        if gold <= 0:
            await interaction.response.send_message("❌ Pas d'or en banque.", ephemeral=True); return
        receive = int(gold * (1 - WITHDRAW_FEE))
        fee     = gold - receive
        embed = discord.Embed(
            title="📤 Retirer de l'or",
            description=f"💰 **{gold:,}** golds en banque.\nTout retirer → **{receive:,}** golds (frais : **{fee:,}**)",
            color=0xFF9800,
        )
        await interaction.response.edit_message(embed=embed, view=GoldWithdrawView(self.user_id, gold))


# ─── Retrait : Or ──────────────────────────────────────────────────────────

class GoldWithdrawView(discord.ui.View):
    def __init__(self, user_id: int, gold_in_bank: int):
        super().__init__(timeout=120)
        self.user_id      = user_id
        self.gold_in_bank = gold_in_bank
        receive = int(gold_in_bank * (1 - WITHDRAW_FEE))
        fee     = gold_in_bank - receive
        b1 = discord.ui.Button(label=f"Tout retirer → {receive:,} golds (-{fee:,})", style=discord.ButtonStyle.success, emoji="💰")
        b1.callback = self._all; self.add_item(b1)
        b2 = discord.ui.Button(label="Montant précis", style=discord.ButtonStyle.secondary, emoji="✏️")
        b2.callback = self._custom; self.add_item(b2)

    async def _all(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        gold    = await db.get_bank_gold(self.user_id)
        receive = int(gold * (1 - WITHDRAW_FEE))
        fee     = gold - receive
        embed = discord.Embed(
            title="📤 Confirmer le retrait d'or",
            description=f"💰 Retirer **{gold:,}** golds\n💸 Frais (10%) : **{fee:,}** golds\n✅ Vous recevrez : **{receive:,}** golds",
            color=0xFF9800,
        )
        await interaction.response.edit_message(embed=embed, view=ConfirmGoldWithdrawView(self.user_id, gold, receive))

    async def _custom(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        await interaction.response.send_modal(GoldWithdrawModal(self.user_id, self.gold_in_bank))


class GoldWithdrawModal(discord.ui.Modal, title="Retirer de l'or (frais 10%)"):
    amount_input = discord.ui.TextInput(label="Montant à retirer de la banque", min_length=1, max_length=15)

    def __init__(self, user_id: int, gold_in_bank: int):
        super().__init__()
        self.user_id = user_id
        self.amount_input.placeholder = f"Max : {gold_in_bank:,} — vous recevrez 90%"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value.replace(" ", "").replace(",", "").replace(".", ""))
        except ValueError:
            await interaction.response.send_message("❌ Montant invalide.", ephemeral=True); return
        if amount <= 0:
            await interaction.response.send_message("❌ Le montant doit être positif.", ephemeral=True); return
        gold = await db.get_bank_gold(self.user_id)
        if amount > gold:
            await interaction.response.send_message(f"❌ Tu n'as que **{gold:,}** golds en banque.", ephemeral=True); return
        receive = int(amount * (1 - WITHDRAW_FEE))
        fee     = amount - receive
        embed = discord.Embed(
            title="📤 Confirmer le retrait d'or",
            description=f"💰 Retirer **{amount:,}** golds\n💸 Frais (10%) : **{fee:,}** golds\n✅ Vous recevrez : **{receive:,}** golds",
            color=0xFF9800,
        )
        await interaction.response.send_message(embed=embed, view=ConfirmGoldWithdrawView(self.user_id, amount, receive), ephemeral=True)


class ConfirmGoldWithdrawView(discord.ui.View):
    def __init__(self, user_id: int, amount_from_bank: int, amount_received: int):
        super().__init__(timeout=60)
        self.user_id          = user_id
        self.amount_from_bank = amount_from_bank
        self.amount_received  = amount_received
        c = discord.ui.Button(label="✅ Confirmer", style=discord.ButtonStyle.success)
        c.callback = self._confirm; self.add_item(c)
        a = discord.ui.Button(label="❌ Annuler", style=discord.ButtonStyle.danger)
        a.callback = self._cancel; self.add_item(a)

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        if not await db.remove_bank_gold(self.user_id, self.amount_from_bank):
            await interaction.response.edit_message(embed=discord.Embed(description="❌ Or en banque insuffisant.", color=0xFF0000), view=None); return
        player = await db.get_player(self.user_id)
        await db.update_player(self.user_id, gold=player["gold"] + self.amount_received)
        fee = self.amount_from_bank - self.amount_received
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="✅ Retrait effectué !",
                description=f"💰 Retiré : **{self.amount_from_bank:,}** golds\n💸 Frais : **{fee:,}** golds\n✅ Reçus : **{self.amount_received:,}** golds",
                color=0x00FF88,
            ),
            view=None,
        )

    async def _cancel(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        await interaction.response.edit_message(embed=discord.Embed(description="❌ Retrait annulé.", color=0xFF0000), view=None)


# ─── Retrait : Équipement ──────────────────────────────────────────────────

class WithdrawEquipmentView(discord.ui.View):
    def __init__(self, user_id: int, options: list, equipments: list):
        super().__init__(timeout=120)
        self.user_id    = user_id
        self.equipments = equipments
        self.selected: int | None = None
        s = discord.ui.Select(placeholder="Choisir un équipement...", options=options)
        s.callback = self._on_select; self.add_item(s)
        b = discord.ui.Button(label="Retirer", style=discord.ButtonStyle.success, emoji="📤")
        b.callback = self._withdraw; self.add_item(b)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        self.selected = int(interaction.data["values"][0])
        eq = next((e for e in self.equipments if e["id"] == self.selected), None)
        if eq:
            name = format_eq_name(eq)
            fee  = _eq_fee(eq.get("rarity", "commun"), eq.get("enhancement", 0))
            embed = discord.Embed(
                title="📤 Retirer un équipement",
                description=f"⚔️ **{name}**\n💸 Frais de retrait : **{fee:,}** golds *(depuis ton inventaire)*",
                color=0xFF9800,
            )
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    async def _withdraw(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        if self.selected is None:
            await interaction.response.send_message("❌ Sélectionne d'abord un équipement.", ephemeral=True); return
        eq = next((e for e in self.equipments if e["id"] == self.selected), None)
        if not eq:
            await interaction.response.send_message("❌ Équipement introuvable.", ephemeral=True); return
        fee  = _eq_fee(eq.get("rarity", "commun"), eq.get("enhancement", 0))
        name = format_eq_name(eq)
        embed = discord.Embed(
            title="📤 Confirmer le retrait",
            description=f"⚔️ **{name}**\n💸 Frais : **{fee:,}** golds prélevés de ton inventaire.",
            color=0xFF9800,
        )
        await interaction.response.edit_message(embed=embed, view=ConfirmItemWithdrawView(self.user_id, "equipment", self.selected, None, fee, name))


# ─── Retrait : Matériaux / Consommables ────────────────────────────────────

class WithdrawItemView(discord.ui.View):
    def __init__(self, user_id: int, item_type: str, options: list, items: list):
        super().__init__(timeout=120)
        self.user_id   = user_id
        self.item_type = item_type
        self.items     = items
        self.selected: str | None = None
        s = discord.ui.Select(placeholder="Choisir un item...", options=options)
        s.callback = self._on_select; self.add_item(s)
        b1 = discord.ui.Button(label="Tout retirer", style=discord.ButtonStyle.success, emoji="📤")
        b1.callback = self._all; self.add_item(b1)
        b2 = discord.ui.Button(label="Quantité précise", style=discord.ButtonStyle.secondary, emoji="✏️")
        b2.callback = self._custom; self.add_item(b2)

    def _fee_unit(self, item_id: str) -> int:
        if self.item_type == "material":
            return int(get_material_value(item_id) * WITHDRAW_FEE)
        return int(get_consumable_value(item_id) * WITHDRAW_FEE)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        self.selected = interaction.data["values"][0]
        item = next((i for i in self.items if i["item_id"] == self.selected), None)
        if item:
            if self.item_type == "material":
                name = MATERIALS.get(self.selected, {}).get("name", self.selected)
            else:
                name = CONSUMABLES.get(self.selected, {}).get("name", self.selected)
            fee_u = self._fee_unit(self.selected)
            qty   = item["quantity"]
            embed = discord.Embed(
                title="📤 Retirer des items",
                description=f"**{name}** ×{qty}\n💸 Frais : **{fee_u:,}** golds/u → tout retirer = **{fee_u * qty:,}** golds",
                color=0xFF9800,
            )
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    async def _all(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        if not self.selected:
            await interaction.response.send_message("❌ Sélectionne d'abord un item.", ephemeral=True); return
        item = next((i for i in self.items if i["item_id"] == self.selected), None)
        if not item:
            await interaction.response.send_message("❌ Item introuvable.", ephemeral=True); return
        await self._show_confirm(interaction, item["quantity"])

    async def _custom(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        if not self.selected:
            await interaction.response.send_message("❌ Sélectionne d'abord un item.", ephemeral=True); return
        item = next((i for i in self.items if i["item_id"] == self.selected), None)
        max_qty = item["quantity"] if item else 1
        fee_u   = self._fee_unit(self.selected)
        await interaction.response.send_modal(WithdrawQuantityModal(self.user_id, self.item_type, self.selected, max_qty, fee_u))

    async def _show_confirm(self, interaction: discord.Interaction, qty: int):
        if self.item_type == "material":
            name = MATERIALS.get(self.selected, {}).get("name", self.selected)
        else:
            name = CONSUMABLES.get(self.selected, {}).get("name", self.selected)
        fee_u     = self._fee_unit(self.selected)
        total_fee = fee_u * qty
        embed = discord.Embed(
            title="📤 Confirmer le retrait",
            description=f"**{name}** ×{qty}\n💸 Frais : **{total_fee:,}** golds ({fee_u:,}/u × {qty})\n*(prélevés de ton inventaire)*",
            color=0xFF9800,
        )
        await interaction.response.edit_message(
            embed=embed,
            view=ConfirmItemWithdrawView(self.user_id, self.item_type, None, self.selected, total_fee, name, qty),
        )


class WithdrawQuantityModal(discord.ui.Modal, title="Quantité à retirer"):
    qty_input = discord.ui.TextInput(label="Quantité", min_length=1, max_length=10)

    def __init__(self, user_id: int, item_type: str, item_id: str, max_qty: int, fee_unit: int):
        super().__init__()
        self.user_id   = user_id
        self.item_type = item_type
        self.item_id   = item_id
        self.max_qty   = max_qty
        self.fee_unit  = fee_unit
        self.qty_input.placeholder = f"Entre 1 et {max_qty} (frais : {fee_unit:,}/u)"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qty = int(self.qty_input.value.strip())
        except ValueError:
            await interaction.response.send_message("❌ Quantité invalide.", ephemeral=True); return
        if qty <= 0 or qty > self.max_qty:
            await interaction.response.send_message(f"❌ Quantité invalide (1 à {self.max_qty}).", ephemeral=True); return
        if self.item_type == "material":
            name = MATERIALS.get(self.item_id, {}).get("name", self.item_id)
        else:
            name = CONSUMABLES.get(self.item_id, {}).get("name", self.item_id)
        total_fee = self.fee_unit * qty
        embed = discord.Embed(
            title="📤 Confirmer le retrait",
            description=f"**{name}** ×{qty}\n💸 Frais : **{total_fee:,}** golds ({self.fee_unit:,}/u × {qty})\n*(prélevés de ton inventaire)*",
            color=0xFF9800,
        )
        await interaction.response.send_message(
            embed=embed,
            view=ConfirmItemWithdrawView(self.user_id, self.item_type, None, self.item_id, total_fee, name, qty),
            ephemeral=True,
        )


class ConfirmItemWithdrawView(discord.ui.View):
    def __init__(self, user_id: int, item_type: str, bank_id: int | None, item_id: str | None,
                 fee: int, item_name: str, qty: int = 1):
        super().__init__(timeout=60)
        self.user_id   = user_id
        self.item_type = item_type
        self.bank_id   = bank_id
        self.item_id   = item_id
        self.fee       = fee
        self.item_name = item_name
        self.qty       = qty
        c = discord.ui.Button(label="✅ Confirmer", style=discord.ButtonStyle.success)
        c.callback = self._confirm; self.add_item(c)
        a = discord.ui.Button(label="❌ Annuler", style=discord.ButtonStyle.danger)
        a.callback = self._cancel; self.add_item(a)

    async def _confirm(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        player = await db.get_player(self.user_id)
        if not player or player["gold"] < self.fee:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=f"❌ Pas assez d'or pour les frais ! ({self.fee:,} requis, tu as {player.get('gold', 0):,})",
                    color=0xFF0000,
                ), view=None,
            ); return

        if self.item_type == "equipment":
            item = await db.withdraw_bank_equipment(self.user_id, self.bank_id)
            if not item:
                await interaction.response.edit_message(embed=discord.Embed(description="❌ Équipement introuvable en banque.", color=0xFF0000), view=None); return
            await db.add_equipment(self.user_id, item["item_id"], item.get("rarity", "commun"), item.get("enhancement", 0), item.get("level", 1), item.get("rune_bonuses"))
        elif self.item_type == "material":
            if not await db.withdraw_bank_material(self.user_id, self.item_id, self.qty):
                await interaction.response.edit_message(embed=discord.Embed(description="❌ Matériau introuvable en banque.", color=0xFF0000), view=None); return
            await db.add_material(self.user_id, self.item_id, self.qty)
        else:
            if not await db.withdraw_bank_consumable(self.user_id, self.item_id, self.qty):
                await interaction.response.edit_message(embed=discord.Embed(description="❌ Consommable introuvable en banque.", color=0xFF0000), view=None); return
            await db.add_consumable(self.user_id, self.item_id, self.qty)

        await db.update_player(self.user_id, gold=player["gold"] - self.fee)
        qty_txt = f" ×{self.qty}" if self.qty > 1 else ""
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="✅ Retrait effectué !",
                description=f"**{self.item_name}**{qty_txt} retiré(s) de la banque.\n💸 Frais prélevés : **{self.fee:,}** golds",
                color=0x00FF88,
            ), view=None,
        )

    async def _cancel(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True); return
        await interaction.response.edit_message(embed=discord.Embed(description="❌ Retrait annulé.", color=0xFF0000), view=None)


# ─── Build hub ─────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🏦 Banque du Royaume",
        description=(
            "La banque est un coffre-fort sécurisé qui conserve vos biens, "
            "même après un **Prestige**.\n\n"
            "**Règles :**\n"
            "• 📥 **Dépôt** : totalement **gratuit**\n"
            "• 📤 **Retrait** : frais de **10%**\n"
            "  — Or : vous recevez 90% du montant retiré\n"
            "  — Items : vous payez 10% de la valeur de base en or\n\n"
            "**Ce que vous pouvez stocker :**\n"
            "⚔️ Équipements • 📦 Matériaux • 🧪 Consommables • 💰 Or\n\n"
            "*Idéal pour protéger vos meilleurs items avant un Prestige !*"
        ),
        color=0xFFD700,
    )
    return embed, BanqueHubView(bot)


async def setup(bot: commands.Bot):
    pass
