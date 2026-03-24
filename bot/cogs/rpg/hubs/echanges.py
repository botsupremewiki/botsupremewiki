"""
Hub Échanges (trades entre joueurs).
Canal : 1479297820706996254
"""
from __future__ import annotations
import asyncio
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.items import format_item_name, format_eq_name

# initiator_id → target_id (sélection en cours via UserSelect)
_pending_targets: dict[int, int] = {}

# session_id → TradeSession
_trade_sessions: dict[int, "TradeSession"] = {}
_next_session_id = 0


class TradeSession:
    def __init__(self, sid: int, initiator_id: int, target_id: int):
        self.sid = sid
        self.initiator_id = initiator_id
        self.target_id = target_id
        self.init_gold = 0
        self.target_gold = 0
        self.init_items: list[int] = []    # ids d'inventory_equipment
        self.target_items: list[int] = []  # ids d'inventory_equipment
        self.init_ok = False
        self.target_ok = False
        self.message: discord.Message | None = None

    def get_side(self, user_id: int) -> str | None:
        if user_id == self.initiator_id:
            return "init"
        if user_id == self.target_id:
            return "target"
        return None

    def ready(self) -> bool:
        return self.init_ok and self.target_ok


def _build_trade_embed(session: TradeSession, initiator_name: str, target_name: str,
                       init_items_data: list, target_items_data: list) -> discord.Embed:
    embed = discord.Embed(title="🤝 Échange en cours", color=0x5865F2)

    init_lines = []
    if session.init_gold > 0:
        init_lines.append(f"💰 **{session.init_gold:,}** golds")
    for item in init_items_data:
        name = format_eq_name(item)
        init_lines.append(f"⚔️ {name}")

    target_lines = []
    if session.target_gold > 0:
        target_lines.append(f"💰 **{session.target_gold:,}** golds")
    for item in target_items_data:
        name = format_eq_name(item)
        target_lines.append(f"⚔️ {name}")

    init_status = "✅ Validé" if session.init_ok else "⏳ En attente"
    target_status = "✅ Validé" if session.target_ok else "⏳ En attente"

    embed.add_field(
        name=f"**{initiator_name}** — {init_status}",
        value="\n".join(init_lines) or "*Rien*",
        inline=True,
    )
    embed.add_field(
        name=f"**{target_name}** — {target_status}",
        value="\n".join(target_lines) or "*Rien*",
        inline=True,
    )
    embed.set_footer(text="Les deux joueurs doivent valider pour finaliser l'échange.")
    return embed


class TradeSessionView(discord.ui.View):
    def __init__(self, session: TradeSession, initiator_name: str, target_name: str):
        super().__init__(timeout=600)
        self.session = session
        self.initiator_name = initiator_name
        self.target_name = target_name

        gold_btn = discord.ui.Button(label="Ajouter Gold", style=discord.ButtonStyle.primary, emoji="💰", row=0)
        gold_btn.callback = self._add_gold
        self.add_item(gold_btn)

        item_btn = discord.ui.Button(label="Ajouter Item", style=discord.ButtonStyle.primary, emoji="⚔️", row=0)
        item_btn.callback = self._add_item
        self.add_item(item_btn)

        valid_btn = discord.ui.Button(label="Valider ✅", style=discord.ButtonStyle.success, row=0)
        valid_btn.callback = self._validate
        self.add_item(valid_btn)

        cancel_btn = discord.ui.Button(label="Annuler ❌", style=discord.ButtonStyle.danger, row=0)
        cancel_btn.callback = self._cancel
        self.add_item(cancel_btn)

    async def _check_side(self, interaction: discord.Interaction) -> str | None:
        side = self.session.get_side(interaction.user.id)
        if not side:
            await interaction.response.send_message("❌ Tu ne participes pas à cet échange.", ephemeral=True)
        return side

    async def _refresh_public(self):
        all_init_eq = await db.get_equipment(self.session.initiator_id)
        all_target_eq = await db.get_equipment(self.session.target_id)
        init_items_data = [e for e in all_init_eq if e["id"] in self.session.init_items]
        target_items_data = [e for e in all_target_eq if e["id"] in self.session.target_items]
        embed = _build_trade_embed(self.session, self.initiator_name, self.target_name, init_items_data, target_items_data)
        await self.session.message.edit(embed=embed, view=self)

    async def _add_gold(self, interaction: discord.Interaction):
        side = await self._check_side(interaction)
        if not side:
            return
        if (side == "init" and self.session.init_ok) or (side == "target" and self.session.target_ok):
            await interaction.response.send_message("❌ Tu as déjà validé. Annule pour modifier.", ephemeral=True)
            return
        modal = AddGoldModal(self.session, side, self.initiator_name, self.target_name)
        await interaction.response.send_modal(modal)

    async def _add_item(self, interaction: discord.Interaction):
        side = await self._check_side(interaction)
        if not side:
            return
        if (side == "init" and self.session.init_ok) or (side == "target" and self.session.target_ok):
            await interaction.response.send_message("❌ Tu as déjà validé. Annule pour modifier.", ephemeral=True)
            return
        user_id = self.session.initiator_id if side == "init" else self.session.target_id
        already_in = self.session.init_items if side == "init" else self.session.target_items
        equipment = await db.get_equipment(user_id)
        available = [e for e in equipment if not e.get("slot_equipped") and e["id"] not in already_in]
        if not available:
            await interaction.response.send_message("❌ Aucun équipement disponible.", ephemeral=True)
            return
        options = []
        for item in available[:25]:
            name = format_eq_name(item)
            options.append(discord.SelectOption(label=name[:100], value=str(item["id"])))
        view = AddItemView(self.session, side, options, self.initiator_name, self.target_name)
        await interaction.response.send_message("Sélectionne un équipement à ajouter :", view=view, ephemeral=True)

    async def _validate(self, interaction: discord.Interaction):
        side = await self._check_side(interaction)
        if not side:
            return
        if side == "init":
            self.session.init_ok = True
        else:
            self.session.target_ok = True
        if self.session.ready():
            await self._execute_trade(interaction)
        else:
            await interaction.response.defer()
            await self._refresh_public()

    async def _cancel(self, interaction: discord.Interaction):
        side = await self._check_side(interaction)
        if not side:
            return
        if self.session.sid in _trade_sessions:
            del _trade_sessions[self.session.sid]
        self.stop()
        cancel_embed = discord.Embed(
            title="❌ Échange annulé",
            description=f"Annulé par **{interaction.user.display_name}**. Suppression dans 5 secondes.",
            color=0xFF4444,
        )
        await interaction.response.edit_message(embed=cancel_embed, view=None)
        await asyncio.sleep(5)
        try:
            await self.session.message.delete()
        except Exception:
            pass

    async def _execute_trade(self, interaction: discord.Interaction):
        session = self.session
        init_player = await db.get_player(session.initiator_id)
        target_player = await db.get_player(session.target_id)
        if not init_player or not target_player:
            await interaction.response.send_message("❌ Profil introuvable.", ephemeral=True)
            session.init_ok = False
            session.target_ok = False
            return
        if init_player["gold"] < session.init_gold:
            await interaction.response.send_message(f"❌ {self.initiator_name} n'a pas assez de golds.", ephemeral=True)
            session.init_ok = False
            return
        if target_player["gold"] < session.target_gold:
            await interaction.response.send_message(f"❌ {self.target_name} n'a pas assez de golds.", ephemeral=True)
            session.target_ok = False
            return

        # Transférer les golds
        await db.update_player(session.initiator_id,
                               gold=init_player["gold"] - session.init_gold + session.target_gold)
        await db.update_player(session.target_id,
                               gold=target_player["gold"] - session.target_gold + session.init_gold)

        # Transférer les équipements
        import aiosqlite
        async with aiosqlite.connect(db.DB_PATH) as conn:
            for item_id in session.init_items:
                await conn.execute(
                    "UPDATE inventory_equipment SET user_id=?, slot_equipped=NULL WHERE id=? AND user_id=?",
                    (session.target_id, item_id, session.initiator_id),
                )
            for item_id in session.target_items:
                await conn.execute(
                    "UPDATE inventory_equipment SET user_id=?, slot_equipped=NULL WHERE id=? AND user_id=?",
                    (session.initiator_id, item_id, session.target_id),
                )
            await conn.commit()

        if session.sid in _trade_sessions:
            del _trade_sessions[session.sid]
        self.stop()

        await db.increment_quest_stat(session.initiator_id, "trade_count")
        await db.increment_quest_stat(session.target_id, "trade_count")

        done_embed = discord.Embed(
            title="✅ Échange finalisé !",
            description=(
                f"L'échange entre **{self.initiator_name}** et **{self.target_name}** est terminé !\n"
                "Ce message sera supprimé dans 5 secondes."
            ),
            color=0x00FF88,
        )
        await interaction.response.edit_message(embed=done_embed, view=None)
        await asyncio.sleep(5)
        try:
            await session.message.delete()
        except Exception:
            pass


class AddGoldModal(discord.ui.Modal, title="Ajouter de l'or"):
    amount_input = discord.ui.TextInput(
        label="Montant d'or à offrir",
        placeholder="Ex: 10000",
        min_length=1,
        max_length=12,
    )

    def __init__(self, session: TradeSession, side: str, initiator_name: str, target_name: str):
        super().__init__()
        self.session = session
        self.side = side
        self.initiator_name = initiator_name
        self.target_name = target_name

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value.replace(",", "").replace(" ", ""))
            if amount < 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("❌ Montant invalide.", ephemeral=True)
            return
        if self.side == "init":
            self.session.init_gold = amount
        else:
            self.session.target_gold = amount
        # Reset validations
        self.session.init_ok = False
        self.session.target_ok = False
        await interaction.response.defer()
        # Refresh public message
        all_init_eq = await db.get_equipment(self.session.initiator_id)
        all_target_eq = await db.get_equipment(self.session.target_id)
        init_items_data = [e for e in all_init_eq if e["id"] in self.session.init_items]
        target_items_data = [e for e in all_target_eq if e["id"] in self.session.target_items]
        embed = _build_trade_embed(self.session, self.initiator_name, self.target_name, init_items_data, target_items_data)
        view = TradeSessionView(self.session, self.initiator_name, self.target_name)
        await self.session.message.edit(embed=embed, view=view)


class AddItemView(discord.ui.View):
    def __init__(self, session: TradeSession, side: str, options: list,
                 initiator_name: str, target_name: str):
        super().__init__(timeout=60)
        self.session = session
        self.side = side
        self.initiator_name = initiator_name
        self.target_name = target_name
        select = discord.ui.Select(placeholder="Choisir un équipement...", options=options)
        select.callback = self._on_select
        self.add_item(select)

    async def _on_select(self, interaction: discord.Interaction):
        item_id = int(interaction.data["values"][0])
        if self.side == "init":
            if item_id not in self.session.init_items:
                self.session.init_items.append(item_id)
        else:
            if item_id not in self.session.target_items:
                self.session.target_items.append(item_id)
        self.session.init_ok = False
        self.session.target_ok = False
        # Refresh public message
        all_init_eq = await db.get_equipment(self.session.initiator_id)
        all_target_eq = await db.get_equipment(self.session.target_id)
        init_items_data = [e for e in all_init_eq if e["id"] in self.session.init_items]
        target_items_data = [e for e in all_target_eq if e["id"] in self.session.target_items]
        embed = _build_trade_embed(self.session, self.initiator_name, self.target_name, init_items_data, target_items_data)
        view = TradeSessionView(self.session, self.initiator_name, self.target_name)
        await self.session.message.edit(embed=embed, view=view)
        await interaction.response.edit_message(content="✅ Item ajouté à l'échange !", view=None)


class EchangesHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

        user_select = discord.ui.UserSelect(
            placeholder="Sélectionner un joueur pour l'échange...",
            custom_id="rpg:echanges:target",
            row=0,
        )
        user_select.callback = self._on_user_select
        self.add_item(user_select)

    @discord.ui.button(label="Proposer un échange 🤝", style=discord.ButtonStyle.primary,
                       custom_id="rpg:echanges:initier", row=1)
    async def initier(self, interaction: discord.Interaction, button: discord.ui.Button):
        target_id = _pending_targets.get(interaction.user.id)
        if not target_id:
            await interaction.response.send_message(
                "❌ Sélectionne d'abord un joueur dans le menu ci-dessus.", ephemeral=True
            )
            return

        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return

        if target_id == interaction.user.id:
            await interaction.response.send_message("❌ Tu ne peux pas t'échanger avec toi-même.", ephemeral=True)
            return

        target_player = await db.get_player(target_id)
        if not target_player or not target_player.get("class"):
            await interaction.response.send_message("❌ Ce joueur n'a pas de profil RPG.", ephemeral=True)
            return

        # Vérifier si déjà un échange actif
        for session in _trade_sessions.values():
            if interaction.user.id in (session.initiator_id, session.target_id):
                await interaction.response.send_message("❌ Tu as déjà un échange en cours.", ephemeral=True)
                return

        global _next_session_id
        _next_session_id += 1
        sid = _next_session_id

        session = TradeSession(sid, interaction.user.id, target_id)
        _trade_sessions[sid] = session

        # Noms d'affichage
        target_member = interaction.guild.get_member(target_id) if interaction.guild else None
        if target_member:
            target_name = target_member.display_name
        else:
            try:
                target_user = await interaction.client.fetch_user(target_id)
                target_name = target_user.display_name
            except Exception:
                target_name = f"Joueur {target_id}"
        initiator_name = interaction.user.display_name

        embed = _build_trade_embed(session, initiator_name, target_name, [], [])
        view = TradeSessionView(session, initiator_name, target_name)

        message = await interaction.channel.send(
            content=f"🤝 <@{interaction.user.id}> propose un échange à <@{target_id}> !",
            embed=embed,
            view=view,
        )
        session.message = message
        await interaction.response.send_message("✅ Échange proposé !", ephemeral=True)

    async def _on_user_select(self, interaction: discord.Interaction):
        values = interaction.data.get("values", [])
        if values:
            _pending_targets[interaction.user.id] = int(values[0])
        await interaction.response.defer()


def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🤝 Hub Échanges",
        description=(
            "Échangez équipements et golds avec d'autres joueurs !\n\n"
            "**Comment échanger :**\n"
            "1️⃣ Sélectionne un joueur dans le menu déroulant\n"
            "2️⃣ Clique sur **Proposer un échange**\n"
            "3️⃣ Les deux joueurs ajoutent leurs offres (golds & items)\n"
            "4️⃣ Les deux joueurs valident → l'échange est exécuté !\n\n"
            "⚠️ L'échange public est visible dans ce salon.\n"
            "Il se supprime automatiquement après finalisation ou annulation."
        ),
        color=0x5865F2,
    )
    view = EchangesHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
