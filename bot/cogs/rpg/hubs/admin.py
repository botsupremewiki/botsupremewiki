"""
Hub Administration RPG.
Canal : 1476717910365044807
Réservé aux administrateurs du serveur.
"""
from __future__ import annotations
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import compute_total_stats, compute_max_hp, get_set_bonus, ROLE_RPG, level_up

# admin_user_id → target_user_id sélectionné
_admin_selections: dict[int, int] = {}


def _check_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator


class AdminHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

        # ── Ligne 1 : actions rapides ────────────────────────────────────────
        reset_btn = discord.ui.Button(
            label="Reset messages hubs", style=discord.ButtonStyle.danger,
            emoji="🔄", custom_id="rpg:admin:reset_hubs", row=0,
        )
        reset_btn.callback = self._reset_hubs
        self.add_item(reset_btn)

        heal_btn = discord.ui.Button(
            label="Heal cible 100% HP", style=discord.ButtonStyle.success,
            emoji="❤️", custom_id="rpg:admin:heal", row=0,
        )
        heal_btn.callback = self._heal
        self.add_item(heal_btn)

        xp_btn = discord.ui.Button(
            label="Donner XP à la cible", style=discord.ButtonStyle.secondary,
            emoji="✨", custom_id="rpg:admin:give_xp", row=0,
        )
        xp_btn.callback = self._give_xp
        self.add_item(xp_btn)

        energy_btn = discord.ui.Button(
            label="Donner énergie à la cible", style=discord.ButtonStyle.secondary,
            emoji="⚡", custom_id="rpg:admin:give_energy", row=0,
        )
        energy_btn.callback = self._give_energy
        self.add_item(energy_btn)

        # ── Ligne 2 : actions destructives ───────────────────────────────────
        gold_btn = discord.ui.Button(
            label="Donner Gold à la cible", style=discord.ButtonStyle.success,
            emoji="💰", custom_id="rpg:admin:give_gold", row=1,
        )
        gold_btn.callback = self._give_gold
        self.add_item(gold_btn)

        delete_btn = discord.ui.Button(
            label="Supprimer joueur DB", style=discord.ButtonStyle.danger,
            emoji="🗑️", custom_id="rpg:admin:delete_player", row=1,
        )
        delete_btn.callback = self._delete_player
        self.add_item(delete_btn)

        # ── Ligne 3 : dropdown membre RPG ────────────────────────────────────
        user_select = discord.ui.UserSelect(
            placeholder="Choisir un membre cible...",
            custom_id="rpg:admin:select_user",
            row=2,
        )
        user_select.callback = self._select_user
        self.add_item(user_select)

    # ── Sélection de la cible ─────────────────────────────────────────────────

    async def _select_user(self, interaction: discord.Interaction):
        if not _check_admin(interaction):
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        selected = interaction.data["values"]
        if not selected:
            await interaction.response.defer()
            return

        target_id = int(selected[0])

        # Vérifier que le joueur a le rôle RPG
        guild  = interaction.guild
        member = guild.get_member(target_id) if guild else None
        if member is None:
            try:
                member = await guild.fetch_member(target_id)
            except Exception:
                member = None

        if member and not any(r.id == ROLE_RPG for r in member.roles):
            await interaction.response.send_message(
                f"⚠️ <@{target_id}> n'a pas le rôle RPG — sélection ignorée.", ephemeral=True
            )
            return

        _admin_selections[interaction.user.id] = target_id
        target_name = member.display_name if member else str(target_id)
        await interaction.response.send_message(
            f"✅ Cible sélectionnée : **{target_name}** (`{target_id}`)", ephemeral=True
        )

    # ── Reset messages hubs ───────────────────────────────────────────────────

    async def _reset_hubs(self, interaction: discord.Interaction):
        if not _check_admin(interaction):
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        await interaction.response.send_message("🔄 Réinitialisation des messages hubs en cours...", ephemeral=True)

        cog = interaction.client.cogs.get("RPGCore")
        if cog:
            await cog._setup_hub_messages()
            await interaction.edit_original_response(content="✅ Tous les messages hubs ont été réinitialisés.")
        else:
            await interaction.edit_original_response(content="❌ Cog RPGCore introuvable.")

    # ── Helper : récupérer la cible ───────────────────────────────────────────

    async def _get_target(self, interaction: discord.Interaction) -> tuple[int, dict] | None:
        """Renvoie (target_id, player_dict) ou None si pas de cible sélectionnée."""
        target_id = _admin_selections.get(interaction.user.id)
        if not target_id:
            await interaction.response.send_message(
                "❌ Sélectionne d'abord un membre dans le dropdown.", ephemeral=True
            )
            return None
        player = await db.get_player(target_id)
        if not player or not player.get("class"):
            await interaction.response.send_message(
                f"❌ <@{target_id}> n'a pas de profil RPG.", ephemeral=True
            )
            return None
        return target_id, player

    # ── Heal ─────────────────────────────────────────────────────────────────

    async def _heal(self, interaction: discord.Interaction):
        if not _check_admin(interaction):
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        result = await self._get_target(interaction)
        if result is None:
            return
        target_id, player = result

        equipment = await db.get_equipment(target_id)
        equipped   = [e for e in equipment if e.get("slot_equipped")]
        set_bonus  = get_set_bonus(equipped)
        total_stats = compute_total_stats(
            player["class"], player["level"], player.get("prestige_level", 0),
            equipped, set_bonus["stats"],
        )
        max_hp = compute_max_hp(total_stats)
        await db.update_player(target_id, current_hp=max_hp)

        await interaction.response.send_message(
            f"❤️ <@{target_id}> soigné à **{max_hp:,} HP** (100%).", ephemeral=True
        )

    # ── Donner XP ────────────────────────────────────────────────────────────

    async def _give_xp(self, interaction: discord.Interaction):
        if not _check_admin(interaction):
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        result = await self._get_target(interaction)
        if result is None:
            return
        target_id, player = result

        modal = AmountModal(title="Donner de l'XP", label="Quantité d'XP", target_id=target_id)
        modal.action = "xp"
        await interaction.response.send_modal(modal)

    # ── Donner énergie ────────────────────────────────────────────────────────

    async def _give_energy(self, interaction: discord.Interaction):
        if not _check_admin(interaction):
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        result = await self._get_target(interaction)
        if result is None:
            return
        target_id, player = result

        modal = AmountModal(title="Donner de l'énergie", label="Quantité d'énergie", target_id=target_id)
        modal.action = "energy"
        await interaction.response.send_modal(modal)

    # ── Donner gold ───────────────────────────────────────────────────────────

    async def _give_gold(self, interaction: discord.Interaction):
        if not _check_admin(interaction):
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        result = await self._get_target(interaction)
        if result is None:
            return
        target_id, player = result

        modal = AmountModal(title="Donner de l'or", label="Quantité d'or", target_id=target_id)
        modal.action = "gold"
        await interaction.response.send_modal(modal)

    # ── Supprimer joueur ──────────────────────────────────────────────────────

    async def _delete_player(self, interaction: discord.Interaction):
        if not _check_admin(interaction):
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        result = await self._get_target(interaction)
        if result is None:
            return
        target_id, player = result

        embed = discord.Embed(
            title="⚠️ Confirmation",
            description=(
                f"Tu es sur le point de **supprimer définitivement** le profil RPG de <@{target_id}>.\n"
                f"Cette action est **irréversible** et effacera toutes ses données (équipement, gold, progression...)."
            ),
            color=0xFF4444,
        )
        view = ConfirmDeleteView(target_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ── Modal montant ─────────────────────────────────────────────────────────────

class AmountModal(discord.ui.Modal):
    def __init__(self, title: str, label: str, target_id: int):
        super().__init__(title=title)
        self.target_id = target_id
        self.action    = ""  # "xp" | "energy" | "gold"
        self.amount_input = discord.ui.TextInput(
            label=label,
            placeholder="Ex: 10000",
            min_length=1,
            max_length=12,
        )
        self.add_item(self.amount_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value.replace(" ", "").replace(",", ""))
        except ValueError:
            await interaction.response.send_message("❌ Montant invalide.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("❌ Le montant doit être positif.", ephemeral=True)
            return

        player = await db.get_player(self.target_id)
        if not player:
            await interaction.response.send_message("❌ Joueur introuvable.", ephemeral=True)
            return

        if self.action == "xp":
            new_xp    = player["xp"] + amount
            new_level, new_xp = level_up(player["level"], new_xp)
            await db.update_player(self.target_id, xp=new_xp, level=new_level)
            lvl_txt = f" (niveau {new_level} !" if new_level > player["level"] else ""
            await interaction.response.send_message(
                f"✨ **+{amount:,} XP** donné à <@{self.target_id}>{lvl_txt})", ephemeral=True
            )

        elif self.action == "energy":
            new_energy = min(player.get("max_energy", 2000), player.get("energy", 0) + amount)
            await db.update_player(self.target_id, energy=new_energy)
            await interaction.response.send_message(
                f"⚡ **+{amount:,} énergie** donné à <@{self.target_id}> "
                f"(maintenant : **{new_energy}/{player.get('max_energy', 2000)}**).", ephemeral=True
            )

        elif self.action == "gold":
            new_gold = player["gold"] + amount
            await db.update_player(self.target_id, gold=new_gold)
            await interaction.response.send_message(
                f"💰 **+{amount:,} golds** donné à <@{self.target_id}> "
                f"(total : **{new_gold:,}**).", ephemeral=True
            )


# ── Confirmation suppression ──────────────────────────────────────────────────

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, target_id: int):
        super().__init__(timeout=30)
        self.target_id = target_id

        confirm_btn = discord.ui.Button(
            label="Confirmer la suppression", style=discord.ButtonStyle.danger, emoji="🗑️"
        )
        confirm_btn.callback = self._confirm
        self.add_item(confirm_btn)

        cancel_btn = discord.ui.Button(
            label="Annuler", style=discord.ButtonStyle.secondary, emoji="❌"
        )
        cancel_btn.callback = self._cancel
        self.add_item(cancel_btn)

    async def _confirm(self, interaction: discord.Interaction):
        if not _check_admin(interaction):
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        await db.delete_player(self.target_id)
        # Retirer la sélection admin
        _admin_selections.pop(interaction.user.id, None)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="✅ Joueur supprimé",
                description=f"Le profil RPG de <@{self.target_id}> a été supprimé.",
                color=0x00FF88,
            ),
            view=None,
        )

    async def _cancel(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=discord.Embed(title="❌ Suppression annulée", color=0x888888),
            view=None,
        )


# ── Build hub ─────────────────────────────────────────────────────────────────

def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🔧 Administration",
        description=(
            "🔧 Outils de maintenance et d'administration du système RPG.\n"
            "Réservé aux administrateurs du serveur.\n\n"
            "*RPG • Utilise les boutons ci-dessous pour naviguer.*"
        ),
        color=0xFF6B35,
    )
    view = AdminHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
