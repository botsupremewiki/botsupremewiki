"""
Hub Taverne — PvP Classique & PvP Classé.
Canal : 1480734240625918144
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    compute_total_stats, compute_max_hp, get_set_bonus,
    compute_class_stats, SET_BONUSES, RARITY_MULT, SOURCE_POWER_MULT,
)
from bot.cogs.rpg.combat import (
    build_combat_state, run_pvp_turn, hp_bar,
    CombatState, get_spell_buttons_data, format_status_effects,
)

# ─── Global State ──────────────────────────────────────────────────────────

_pvp_sessions:   dict[int, "PvPSession"]       = {}   # challenger_id → session (combat en cours)
_taverne_lobby:  dict[int, dict]               = {}   # user_id → {name, elo, joined_at}
_ranked_pending: dict[tuple[int, int], "RankedPending"] = {}  # (min_id, max_id) → pending

_ELO_K        = 32
MAX_RANKED_DAY = 5

# Classes disponibles en classé (affichage → préfixe clé panoplie dans SET_BONUSES)
_CLASSES: dict[str, str] = {
    "Guerrier":         "guerrier",
    "Assassin":         "assassin",
    "Mage":             "mage",
    "Tireur":           "tireur",
    "Support":          "support",
    "Vampire":          "vampire",
    "Gardien du Temps": "gardien",
    "Ombre Venin":      "ombre",
    "Pyromancien":      "pyro",
    "Paladin":          "paladin",
}

_SOURCES_DISPLAY: dict[str, str] = {
    "monde":            "Monde",
    "donjon_classique": "Classique",
    "craft":            "Craft",
    "donjon_elite":     "Élite",
    "donjon_abyssal":   "Abyssal",
    "raid":             "Raid",
}


# ─── Helpers ───────────────────────────────────────────────────────────────


def _elo_change(elo_a: int, elo_b: int, won: bool) -> int:
    expected = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    actual   = 1.0 if won else 0.0
    return round(_ELO_K * (actual - expected))


def _get_rank_label(elo: int) -> str:
    if elo >= 2400: return "Maître Absolu 👑"
    if elo >= 2000: return "Maître ⚜️"
    if elo >= 1800: return "Diamant 💎"
    if elo >= 1600: return "Platine 🪙"
    if elo >= 1400: return "Or 🥇"
    if elo >= 1200: return "Argent 🥈"
    if elo >= 1000: return "Bronze 🥉"
    return "Fer 🔩"


def _get_rank_color(elo: int) -> int:
    if elo >= 2400: return 0xFFD700
    if elo >= 2000: return 0xE040FB
    if elo >= 1800: return 0x40C4FF
    if elo >= 1600: return 0x80DEEA
    if elo >= 1400: return 0xFFD54F
    if elo >= 1200: return 0xB0BEC5
    if elo >= 1000: return 0xA1887F
    return 0x757575


def _compute_ranked_stats(class_name: str, panoplie_key: str) -> dict:
    """Stats normalisées pour le PvP classé : niveau 500, craft × rare, 7 pièces."""
    base = compute_class_stats(class_name, 500, 0)
    set_data = SET_BONUSES.get(panoplie_key, {})
    multiplier = min(RARITY_MULT["rare"] * SOURCE_POWER_MULT["craft"], 20.0)  # 3.06
    bonus: dict[str, int] = {}
    for pcs_key in ("2pcs", "4pcs", "5pcs"):
        for k, v in set_data.get(pcs_key, {}).items():
            if k != "passive":
                bonus[k] = bonus.get(k, 0) + int(v * multiplier)
    total = dict(base)
    for k, v in bonus.items():
        total[k] = total.get(k, 0) + v
    return total


def _panoplies_for_class(class_key: str) -> list[tuple[str, str]]:
    """Retourne [(panoplie_key, label)] pour la classe donnée."""
    results = []
    for source_key, source_label in _SOURCES_DISPLAY.items():
        pano_key = f"{class_key}_{source_key}"
        if pano_key in SET_BONUSES:
            set_data = SET_BONUSES[pano_key]
            results.append((pano_key, f"{set_data.get('name', pano_key)} ({source_label})"))
    return results


async def _check_ranked_daily(player: dict) -> tuple[bool, int]:
    """Vérifie si le joueur peut encore faire un combat classé aujourd'hui.
    Retourne (peut_combattre, fights_restants)."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    reset_str = player.get("pvp_ranked_reset")
    count = player.get("pvp_ranked_today", 0) if reset_str == today_str else 0
    can = count < MAX_RANKED_DAY
    return can, MAX_RANKED_DAY - count


async def _increment_ranked_daily(user_id: int):
    p = await db.get_player(user_id)
    if not p:
        return
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    reset_str = p.get("pvp_ranked_reset")
    count = p.get("pvp_ranked_today", 0) if reset_str == today_str else 0
    await db.update_player(user_id, pvp_ranked_today=count + 1, pvp_ranked_reset=today_str)


# ─── PvPSession ────────────────────────────────────────────────────────────


class PvPSession:
    def __init__(
        self,
        challenger_id: int,
        target_id:     int,
        state:         CombatState,
        t_state:       CombatState,
        c_name:        str,
        t_name:        str,
        c_class:       str = "",
        t_class:       str = "",
        c_elo:         int = 1000,
        t_elo:         int = 1000,
        mode:          str = "classique",  # "classique" | "ranked"
        use_buffs:     bool = True,
    ):
        self.challenger_id   = challenger_id
        self.target_id       = target_id
        self.state           = state
        self.t_state         = t_state
        self.c_name          = c_name
        self.t_name          = t_name
        self.c_class         = c_class
        self.t_class         = t_class
        self.c_elo           = c_elo
        self.t_elo           = t_elo
        self.mode            = mode
        self.use_buffs       = use_buffs
        self.current_attacker = "challenger"
        self.message: discord.Message | None = None

    def sync_hp_to_t_state(self):
        self.t_state.player_stats.hp     = self.state.enemy_stats.hp
        self.t_state.player_stats.max_hp = self.state.enemy_stats.max_hp
        self.t_state.enemy_stats.hp      = self.state.player_stats.hp
        self.t_state.enemy_stats.max_hp  = self.state.player_stats.max_hp
        self.t_state.turn                = self.state.turn

    def sync_hp_from_t_state(self):
        self.state.player_stats.hp  = self.t_state.enemy_stats.hp
        self.state.enemy_stats.hp   = self.t_state.player_stats.hp
        self.state.turn             = self.t_state.turn


# ─── RankedPending ─────────────────────────────────────────────────────────


@dataclass
class RankedPending:
    challenger_id: int
    target_id:     int
    c_name:        str
    t_name:        str
    c_elo:         int
    t_elo:         int
    channel_id:    int
    c_class:       str | None = None
    t_class:       str | None = None
    c_pano:        str | None = None
    t_pano:        str | None = None
    phase:         str        = "class"   # "class" | "pano" | "done"
    message: discord.Message | None = field(default=None, repr=False)

    def key(self) -> tuple[int, int]:
        a, b = self.challenger_id, self.target_id
        return (min(a, b), max(a, b))


# ─── Hub View ──────────────────────────────────────────────────────────────


class TaverneHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="PvP Classique", style=discord.ButtonStyle.secondary,
                       emoji="⚔️", custom_id="rpg:taverne:classique", row=0)
    async def classique(self, interaction: discord.Interaction, _: discord.ui.Button):
        await _handle_classique(interaction)

    @discord.ui.button(label="PvP Classé", style=discord.ButtonStyle.danger,
                       emoji="🏆", custom_id="rpg:taverne:ranked", row=0)
    async def ranked(self, interaction: discord.Interaction, _: discord.ui.Button):
        await _handle_ranked_lobby(interaction)

    @discord.ui.button(label="Mon classement", style=discord.ButtonStyle.secondary,
                       emoji="📊", custom_id="rpg:taverne:rank", row=1)
    async def rank(self, interaction: discord.Interaction, _: discord.ui.Button):
        await _handle_pvp_rank(interaction)

    @discord.ui.button(label="Classement Global", style=discord.ButtonStyle.secondary,
                       emoji="🏅", custom_id="rpg:taverne:leaderboard", row=1)
    async def leaderboard(self, interaction: discord.Interaction, _: discord.ui.Button):
        await _handle_pvp_leaderboard(interaction)


# ══════════════════════════════════════════════════════════════════════════
# PVP CLASSIQUE
# ══════════════════════════════════════════════════════════════════════════


async def _handle_classique(interaction: discord.Interaction):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    if not player.get("class"):
        await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
        return
    if interaction.user.id in _pvp_sessions:
        await interaction.response.send_message("❌ Tu as déjà un combat PvP en cours !", ephemeral=True)
        return

    embed = discord.Embed(
        title="⚔️ PvP Classique",
        description=(
            "Sélectionne un joueur à défier.\n\n"
            "**Mode Classique :** stats et équipements réels, pas d'Élo, sans coût d'énergie.\n"
            "Tu peux activer ou désactiver les buffs alimentaires/reliques."
        ),
        color=0x607D8B,
    )
    view = ClassiqueSetupView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ClassiqueSetupView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id   = user_id
        self.target_id: int | None = None
        self.use_buffs = True

        sel = discord.ui.UserSelect(
            placeholder="Sélectionne un joueur à défier...",
            min_values=1, max_values=1,
        )
        sel.callback = self._select_target
        self.add_item(sel)

        self._buff_btn = discord.ui.Button(
            label="Buffs ON", emoji="🍞", style=discord.ButtonStyle.success, row=1,
        )
        self._buff_btn.callback = self._toggle_buffs
        self.add_item(self._buff_btn)

        go_btn = discord.ui.Button(
            label="Défier !", emoji="⚔️", style=discord.ButtonStyle.danger, row=1,
        )
        go_btn.callback = self._challenge
        self.add_item(go_btn)

    async def _select_target(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        self.target_id = int(interaction.data["values"][0])
        await interaction.response.defer()

    async def _toggle_buffs(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)
            return
        self.use_buffs = not self.use_buffs
        self._buff_btn.label  = "Buffs ON"  if self.use_buffs else "Buffs OFF"
        self._buff_btn.style  = discord.ButtonStyle.success if self.use_buffs else discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)

    async def _challenge(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)
            return
        if self.target_id is None:
            await interaction.response.send_message("❌ Sélectionne d'abord un joueur !", ephemeral=True)
            return
        if self.target_id == self.user_id:
            await interaction.response.send_message("❌ Tu ne peux pas te battre contre toi-même.", ephemeral=True)
            return
        await _start_classique_combat(interaction, self.user_id, self.target_id, self.use_buffs)


async def _start_classique_combat(
    interaction: discord.Interaction,
    challenger_id: int,
    target_id: int,
    use_buffs: bool,
):
    challenger = await db.get_player(challenger_id)
    target     = await db.get_player(target_id)

    if not target or not target.get("class"):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="❌ Joueur introuvable",
                description="Ce joueur n'a pas de profil RPG valide.",
                color=0xFF4444,
            ), view=None,
        )
        return

    if challenger and challenger.get("in_combat", 0):
        await interaction.response.edit_message(
            embed=discord.Embed(title="⚔️ Déjà en combat", description="Tu es déjà en combat ! Termine ton combat actuel avant d'en lancer un nouveau.", color=0xFF4444),
            view=None,
        )
        return

    if target and target.get("in_combat", 0):
        await interaction.response.edit_message(
            embed=discord.Embed(title="⚔️ Adversaire en combat", description="Ton adversaire est déjà en combat ! Réessaie plus tard.", color=0xFF4444),
            view=None,
        )
        return

    if challenger_id in _pvp_sessions:
        await interaction.response.edit_message(
            embed=discord.Embed(title="❌ Combat en cours", description="Tu as déjà un combat PvP actif.", color=0xFF4444),
            view=None,
        )
        return

    # Vérifier et déduire l'énergie du challenger
    from bot.cogs.rpg.models import ENERGY_COST
    pvp_cost = ENERGY_COST.get("pvp", 5)
    if challenger and challenger.get("energy", 0) < pvp_cost:
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="⚡ Énergie insuffisante",
                description=f"Il te faut **{pvp_cost}** énergie pour lancer un combat PvP (tu en as **{challenger.get('energy', 0)}**).",
                color=0xFF4444,
            ), view=None,
        )
        return

    # Construire états de combat
    c_eq      = await db.get_equipment(challenger_id)
    c_relics  = await db.get_relics(challenger_id)
    c_equipped = [e for e in c_eq if e.get("slot_equipped")]
    c_sb      = get_set_bonus(c_equipped)
    c_stats   = compute_total_stats(
        challenger["class"], challenger["level"], challenger.get("prestige_level", 0),
        c_equipped, c_sb["stats"],
    )
    c_max_hp  = compute_max_hp(c_stats)

    t_eq      = await db.get_equipment(target_id)
    t_relics  = await db.get_relics(target_id)
    t_equipped = [e for e in t_eq if e.get("slot_equipped")]
    t_sb      = get_set_bonus(t_equipped)
    t_stats   = compute_total_stats(
        target["class"], target["level"], target.get("prestige_level", 0),
        t_equipped, t_sb["stats"],
    )
    t_max_hp  = compute_max_hp(t_stats)

    ignore = not use_buffs

    t_proxy = {
        "hp": t_max_hp, "p_atk": t_stats.get("p_atk", 0), "m_atk": t_stats.get("m_atk", 0),
        "p_def": t_stats.get("p_def", 0), "m_def": t_stats.get("m_def", 0),
        "p_pen": t_stats.get("p_pen", 0), "m_pen": t_stats.get("m_pen", 0),
        "speed": t_stats.get("speed", 10), "crit_chance": t_stats.get("crit_chance", 5),
        "crit_damage": t_stats.get("crit_damage", 150), "type": "pvp", "passif": "",
    }
    state = build_combat_state(challenger, t_proxy, c_eq, c_relics if use_buffs else [], c_max_hp, ignore_food_buffs=ignore)
    state.enemy_stats.hp     = t_max_hp
    state.enemy_stats.max_hp = t_max_hp

    c_proxy = {
        "hp": c_max_hp, "p_atk": c_stats.get("p_atk", 0), "m_atk": c_stats.get("m_atk", 0),
        "p_def": c_stats.get("p_def", 0), "m_def": c_stats.get("m_def", 0),
        "p_pen": c_stats.get("p_pen", 0), "m_pen": c_stats.get("m_pen", 0),
        "speed": c_stats.get("speed", 10), "crit_chance": c_stats.get("crit_chance", 5),
        "crit_damage": c_stats.get("crit_damage", 150), "type": "pvp", "passif": "",
    }
    t_state = build_combat_state(target, c_proxy, t_eq, t_relics if use_buffs else [], t_max_hp, ignore_food_buffs=ignore)
    t_state.enemy_stats.hp     = c_max_hp
    t_state.enemy_stats.max_hp = c_max_hp

    c_name = challenger.get("display_name") or interaction.user.display_name
    t_discord = interaction.client.get_user(target_id)
    t_name = target.get("display_name") or (t_discord.display_name if t_discord else f"Joueur {target_id}")

    session = PvPSession(
        challenger_id=challenger_id, target_id=target_id,
        state=state, t_state=t_state,
        c_name=c_name, t_name=t_name,
        c_class=challenger.get("class", ""), t_class=target.get("class", ""),
        c_elo=challenger.get("pvp_elo", 1000), t_elo=target.get("pvp_elo", 1000),
        mode="classique", use_buffs=use_buffs,
    )
    _pvp_sessions[challenger_id] = session
    new_c_energy = max(0, (challenger.get("energy", 0) - pvp_cost))
    await db.update_player(challenger_id, in_combat=1, energy=new_c_energy)
    await db.update_player(target_id, in_combat=1)

    embed = _build_pvp_embed(session)
    view  = PvPCombatView(session)
    msg   = await interaction.channel.send(embed=embed, view=view)
    session.message = msg

    buffs_txt = "buffs activés" if use_buffs else "buffs désactivés"
    await interaction.response.edit_message(
        embed=discord.Embed(
            title="⚔️ PvP Classique lancé !",
            description=f"Combat contre **{t_name}** en cours ({buffs_txt}).",
            color=0x607D8B,
        ), view=None,
    )


# ══════════════════════════════════════════════════════════════════════════
# PVP CLASSÉ — LOBBY
# ══════════════════════════════════════════════════════════════════════════


async def _handle_ranked_lobby(interaction: discord.Interaction):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    if not player.get("class"):
        await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
        return

    can, remaining = await _check_ranked_daily(player)
    user_id = interaction.user.id
    in_lobby = user_id in _taverne_lobby
    in_session = user_id in _pvp_sessions or any(
        p.challenger_id == user_id or p.target_id == user_id
        for p in _ranked_pending.values()
    )

    embed = _build_lobby_embed(player, remaining)
    view  = RankedLobbyView(user_id, can, in_lobby, in_session)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def _build_lobby_embed(player: dict, remaining: int) -> discord.Embed:
    elo   = player.get("pvp_elo", 1000)
    rw    = player.get("pvp_ranked_wins", 0)
    rl    = player.get("pvp_ranked_losses", 0)
    embed = discord.Embed(
        title="🏆 Taverne — PvP Classé",
        description=(
            f"**Système Élo :** tu combats avec des stats normalisées (niv. 500, panoplie craft, rare).\n"
            f"Aucun buff externe. Le choix de classe et de panoplie est **secret**.\n\n"
            f"**Ton Élo :** {elo} — {_get_rank_label(elo)}\n"
            f"**Classé :** {rw}V / {rl}D · Combats restants aujourd'hui : **{remaining}/{MAX_RANKED_DAY}**"
        ),
        color=0xE040FB,
    )

    if _taverne_lobby:
        lines = []
        for uid, info in _taverne_lobby.items():
            rank = _get_rank_label(info["elo"])
            lines.append(f"• **{info['name']}** — Élo {info['elo']} ({rank})")
        embed.add_field(name=f"🍺 Joueurs en attente ({len(_taverne_lobby)})", value="\n".join(lines), inline=False)
    else:
        embed.add_field(name="🍺 Taverne vide", value="*Personne n'attend pour l'instant.*", inline=False)

    return embed


class RankedLobbyView(discord.ui.View):
    def __init__(self, user_id: int, can_fight: bool, in_lobby: bool, in_session: bool):
        super().__init__(timeout=120)
        self.user_id    = user_id
        self.can_fight  = can_fight
        self.in_lobby   = in_lobby
        self.in_session = in_session
        self._build()

    def _build(self):
        self.clear_items()

        if self.in_session:
            btn = discord.ui.Button(label="Combat en cours...", style=discord.ButtonStyle.secondary, disabled=True)
            self.add_item(btn)
            return

        if not self.can_fight:
            btn = discord.ui.Button(
                label=f"Limite journalière atteinte ({MAX_RANKED_DAY}/{MAX_RANKED_DAY})",
                style=discord.ButtonStyle.secondary, disabled=True,
            )
            self.add_item(btn)
            return

        if self.in_lobby:
            leave_btn = discord.ui.Button(label="Quitter la Taverne", emoji="🚪", style=discord.ButtonStyle.secondary)
            leave_btn.callback = self._leave_lobby
            self.add_item(leave_btn)
        else:
            join_btn = discord.ui.Button(label="Rejoindre la Taverne", emoji="🍺", style=discord.ButtonStyle.success)
            join_btn.callback = self._join_lobby
            self.add_item(join_btn)

        if _taverne_lobby:
            challenge_opponents = [uid for uid in _taverne_lobby if uid != self.user_id]
            if challenge_opponents:
                sel = discord.ui.Select(
                    placeholder="Défier un joueur de la taverne...",
                    options=[
                        discord.SelectOption(
                            label=_taverne_lobby[uid]["name"][:100],
                            value=str(uid),
                            description=f"Élo {_taverne_lobby[uid]['elo']} — {_get_rank_label(_taverne_lobby[uid]['elo'])}",
                        )
                        for uid in challenge_opponents[:25]
                    ],
                    row=1,
                )
                sel.callback = self._challenge_select
                self.add_item(sel)

    async def _join_lobby(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)
            return
        player = await db.get_player(self.user_id)
        _taverne_lobby[self.user_id] = {
            "name": player.get("display_name") or interaction.user.display_name,
            "elo":  player.get("pvp_elo", 1000),
            "joined_at": datetime.now(timezone.utc).isoformat(),
        }
        self.in_lobby = True
        can, remaining = await _check_ranked_daily(player)
        embed = _build_lobby_embed(player, remaining)
        self._build()
        await interaction.response.edit_message(embed=embed, view=self)

    async def _leave_lobby(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)
            return
        _taverne_lobby.pop(self.user_id, None)
        self.in_lobby = False
        player = await db.get_player(self.user_id)
        can, remaining = await _check_ranked_daily(player)
        embed = _build_lobby_embed(player, remaining)
        self._build()
        await interaction.response.edit_message(embed=embed, view=self)

    async def _challenge_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return
        target_id = int(interaction.data["values"][0])
        if target_id not in _taverne_lobby:
            await interaction.response.send_message("❌ Ce joueur a quitté la taverne.", ephemeral=True)
            return
        if self.user_id in _pvp_sessions or any(
            p.challenger_id == self.user_id or p.target_id == self.user_id
            for p in _ranked_pending.values()
        ):
            await interaction.response.send_message("❌ Tu as déjà un combat en cours.", ephemeral=True)
            return

        player   = await db.get_player(self.user_id)
        can, _   = await _check_ranked_daily(player)
        if not can:
            await interaction.response.send_message(f"❌ Tu as atteint la limite de {MAX_RANKED_DAY} combats classés pour aujourd'hui.", ephemeral=True)
            return

        challenger_name = player.get("display_name") or interaction.user.display_name
        target_info     = _taverne_lobby[target_id]

        # Message public d'invitation
        accept_embed = discord.Embed(
            title="⚔️ Défi Classé !",
            description=(
                f"**{challenger_name}** défie **{target_info['name']}** en PvP Classé !\n\n"
                f"<@{target_id}>, acceptes-tu le défi ?"
            ),
            color=0xE040FB,
        )
        accept_view = AcceptChallengeView(
            challenger_id=self.user_id,
            target_id=target_id,
            challenger_name=challenger_name,
            target_name=target_info["name"],
            c_elo=player.get("pvp_elo", 1000),
            t_elo=target_info["elo"],
        )
        msg = await interaction.channel.send(embed=accept_embed, view=accept_view)
        accept_view.challenge_msg = msg

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="⏳ Défi envoyé",
                description=f"En attente de la réponse de **{target_info['name']}**...",
                color=0xE040FB,
            ),
            view=None,
        )


class AcceptChallengeView(discord.ui.View):
    def __init__(
        self,
        challenger_id: int,
        target_id: int,
        challenger_name: str,
        target_name: str,
        c_elo: int,
        t_elo: int,
    ):
        super().__init__(timeout=60)
        self.challenger_id   = challenger_id
        self.target_id       = target_id
        self.challenger_name = challenger_name
        self.target_name     = target_name
        self.c_elo           = c_elo
        self.t_elo           = t_elo
        self.challenge_msg: discord.Message | None = None

    @discord.ui.button(label="Accepter", emoji="✅", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, _: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)
            return
        self.stop()
        _taverne_lobby.pop(self.challenger_id, None)
        _taverne_lobby.pop(self.target_id, None)
        await _start_ranked_selection(interaction, self)

    @discord.ui.button(label="Refuser", emoji="❌", style=discord.ButtonStyle.danger)
    async def refuse(self, interaction: discord.Interaction, _: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)
            return
        self.stop()
        embed = discord.Embed(
            title="❌ Défi refusé",
            description=f"**{self.target_name}** a refusé le défi de **{self.challenger_name}**.",
            color=0xFF4444,
        )
        await interaction.response.edit_message(embed=embed, view=None)
        await asyncio.sleep(8)
        try:
            await interaction.message.delete()
        except Exception:
            pass

    async def on_timeout(self):
        if self.challenge_msg:
            try:
                embed = discord.Embed(
                    title="⏰ Défi expiré",
                    description=f"**{self.target_name}** n'a pas répondu à temps.",
                    color=0x607D8B,
                )
                await self.challenge_msg.edit(embed=embed, view=None)
                await asyncio.sleep(8)
                await self.challenge_msg.delete()
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════════════
# PVP CLASSÉ — PHASE DE SÉLECTION
# ══════════════════════════════════════════════════════════════════════════


async def _start_ranked_selection(interaction: discord.Interaction, challenge_view: AcceptChallengeView):
    """Démarre la phase de sélection secrète après acceptation du défi."""
    c_id = challenge_view.challenger_id
    t_id = challenge_view.target_id

    pending = RankedPending(
        challenger_id=c_id, target_id=t_id,
        c_name=challenge_view.challenger_name, t_name=challenge_view.target_name,
        c_elo=challenge_view.c_elo, t_elo=challenge_view.t_elo,
        channel_id=interaction.channel_id,
        phase="class",
    )
    _ranked_pending[pending.key()] = pending

    sel_embed = _build_selection_embed(pending)
    sel_view  = SelectionPhaseView(pending)
    # Éditer le message de challenge pour devenir le message de sélection
    await interaction.response.edit_message(embed=sel_embed, view=sel_view)
    pending.message = interaction.message


def _build_selection_embed(pending: RankedPending) -> discord.Embed:
    if pending.phase == "class":
        title = "🔒 Phase de sélection — Classe"
        desc  = "Chaque joueur choisit sa **classe** en secret."
    else:
        title = "🔒 Phase de sélection — Panoplie"
        desc  = "Chaque joueur choisit sa **panoplie** en secret."

    c_status = "✅ Sélectionné" if (pending.c_class if pending.phase == "class" else pending.c_pano) else "⏳ En attente"
    t_status = "✅ Sélectionné" if (pending.t_class if pending.phase == "class" else pending.t_pano) else "⏳ En attente"

    embed = discord.Embed(title=title, description=desc, color=0xE040FB)
    embed.add_field(name=f"👤 {pending.c_name}", value=c_status, inline=True)
    embed.add_field(name=f"👤 {pending.t_name}", value=t_status, inline=True)
    embed.set_footer(text="Les sélections sont gardées secrètes jusqu'au début du combat.")
    return embed


class SelectionPhaseView(discord.ui.View):
    def __init__(self, pending: RankedPending):
        super().__init__(timeout=120)
        self.pending = pending
        self._build()

    def _build(self):
        self.clear_items()
        pending = self.pending

        c_done = (pending.c_class if pending.phase == "class" else pending.c_pano) is not None
        t_done = (pending.t_class if pending.phase == "class" else pending.t_pano) is not None

        label_prefix = "Classe" if pending.phase == "class" else "Panoplie"

        c_btn = discord.ui.Button(
            label=f"{'✅' if c_done else '🔒'} {label_prefix} — {pending.c_name}",
            style=discord.ButtonStyle.success if c_done else discord.ButtonStyle.blurple,
            disabled=c_done,
            row=0,
        )
        c_btn.callback = self._make_select_cb(pending.challenger_id)
        self.add_item(c_btn)

        t_btn = discord.ui.Button(
            label=f"{'✅' if t_done else '🔒'} {label_prefix} — {pending.t_name}",
            style=discord.ButtonStyle.success if t_done else discord.ButtonStyle.blurple,
            disabled=t_done,
            row=0,
        )
        t_btn.callback = self._make_select_cb(pending.target_id)
        self.add_item(t_btn)

    def _make_select_cb(self, player_id: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != player_id:
                await interaction.response.send_message("❌ Ce bouton n'est pas pour toi.", ephemeral=True)
                return
            await self._open_selection(interaction, player_id)
        return callback

    async def _open_selection(self, interaction: discord.Interaction, player_id: int):
        pending = self.pending
        if pending.phase == "class":
            options = [
                discord.SelectOption(label=cls_name, value=cls_name)
                for cls_name in _CLASSES
            ]
            prompt = "Choisis ta classe pour ce combat :"
        else:
            # Panoplie phase — need class to be known
            cls_name = pending.c_class if player_id == pending.challenger_id else pending.t_class
            cls_key  = _CLASSES.get(cls_name, cls_name.lower())
            panoplies = _panoplies_for_class(cls_key)
            if not panoplies:
                await interaction.response.send_message("❌ Pas de panoplie disponible pour cette classe.", ephemeral=True)
                return
            options = [
                discord.SelectOption(label=label[:100], value=pano_key)
                for pano_key, label in panoplies
            ]
            prompt = "Choisis ta panoplie pour ce combat :"

        sel_view = _EphemeralSelectView(
            player_id=player_id,
            options=options,
            prompt=prompt,
            pending=pending,
            phase_view=self,
        )
        embed = discord.Embed(
            title="🔒 Sélection secrète",
            description=prompt,
            color=0xE040FB,
        )
        await interaction.response.send_message(embed=embed, view=sel_view, ephemeral=True)

    async def on_timeout(self):
        pending = self.pending
        _ranked_pending.pop(pending.key(), None)
        if pending.message:
            try:
                embed = discord.Embed(
                    title="⏰ Sélection expirée",
                    description="La phase de sélection a expiré.",
                    color=0x607D8B,
                )
                await pending.message.edit(embed=embed, view=None)
                await asyncio.sleep(5)
                await pending.message.delete()
            except Exception:
                pass


class _EphemeralSelectView(discord.ui.View):
    """Vue éphémère pour sélectionner classe ou panoplie en secret."""

    def __init__(
        self,
        player_id: int,
        options: list[discord.SelectOption],
        prompt: str,
        pending: RankedPending,
        phase_view: SelectionPhaseView,
    ):
        super().__init__(timeout=120)
        self.player_id  = player_id
        self.pending    = pending
        self.phase_view = phase_view
        self.selected: str | None = None

        sel = discord.ui.Select(placeholder=prompt[:150], options=options[:25])
        sel.callback = self._on_select
        self.add_item(sel)

    async def _on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("❌ Ce menu n'est pas pour toi.", ephemeral=True)
            return

        self.selected = interaction.data["values"][0]
        pending = self.pending
        is_challenger = self.player_id == pending.challenger_id

        if pending.phase == "class":
            if is_challenger:
                pending.c_class = self.selected
            else:
                pending.t_class = self.selected
            # Check if both selected
            both_done = pending.c_class and pending.t_class
        else:
            if is_challenger:
                pending.c_pano = self.selected
            else:
                pending.t_pano = self.selected
            both_done = pending.c_pano and pending.t_pano

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="✅ Sélection confirmée",
                description=f"Tu as sélectionné **{self.selected}**. En attente de l'autre joueur...",
                color=0x00FF88,
            ),
            view=None,
        )

        # Update the public selection message
        if pending.message:
            self.phase_view._build()
            sel_embed = _build_selection_embed(pending)
            try:
                await pending.message.edit(embed=sel_embed, view=self.phase_view)
            except Exception:
                pass

        if both_done:
            if pending.phase == "class":
                # Move to panoplie phase
                pending.phase = "pano"
                self.phase_view._build()
                if pending.message:
                    try:
                        await pending.message.edit(
                            embed=_build_selection_embed(pending),
                            view=self.phase_view,
                        )
                    except Exception:
                        pass
            else:
                # Both panoplies selected → start ranked combat
                if pending.message:
                    try:
                        await pending.message.edit(
                            embed=discord.Embed(
                                title="⚔️ Combat Classé en préparation...",
                                description="Les sélections sont terminées, le combat va commencer !",
                                color=0xE040FB,
                            ),
                            view=None,
                        )
                    except Exception:
                        pass
                pending.phase = "done"
                _ranked_pending.pop(pending.key(), None)
                await _start_ranked_combat(pending)


async def _start_ranked_combat(pending: RankedPending):
    """Lance le combat classé avec les stats normalisées."""
    c_class_key = _CLASSES.get(pending.c_class, "guerrier")
    t_class_key = _CLASSES.get(pending.t_class, "guerrier")

    c_total = _compute_ranked_stats(pending.c_class, pending.c_pano)
    t_total = _compute_ranked_stats(pending.t_class, pending.t_pano)

    c_max_hp = compute_max_hp(c_total)
    t_max_hp = compute_max_hp(t_total)

    # Fake player data for build_combat_state (class + level + prestige)
    c_fake = {"class": pending.c_class, "level": 500, "prestige_level": 0, "food_buffs": None}
    t_fake = {"class": pending.t_class, "level": 500, "prestige_level": 0, "food_buffs": None}

    # We build manually using the already-computed total stats to bypass equipment
    from bot.cogs.rpg.combat import CombatStats, CombatState

    c_ps = CombatStats.from_dict(c_total)
    c_ps.max_hp = c_max_hp
    c_ps.hp     = c_max_hp

    t_ps = CombatStats.from_dict(t_total)
    t_ps.max_hp = t_max_hp
    t_ps.hp     = t_max_hp

    t_proxy = {
        "hp": t_max_hp, "p_atk": t_total.get("p_atk", 0), "m_atk": t_total.get("m_atk", 0),
        "p_def": t_total.get("p_def", 0), "m_def": t_total.get("m_def", 0),
        "p_pen": t_total.get("p_pen", 0), "m_pen": t_total.get("m_pen", 0),
        "speed": t_total.get("speed", 10), "crit_chance": t_total.get("crit_chance", 5),
        "crit_damage": t_total.get("crit_damage", 150), "type": "pvp", "passif": "",
    }
    c_proxy = {
        "hp": c_max_hp, "p_atk": c_total.get("p_atk", 0), "m_atk": c_total.get("m_atk", 0),
        "p_def": c_total.get("p_def", 0), "m_def": c_total.get("m_def", 0),
        "p_pen": c_total.get("p_pen", 0), "m_pen": c_total.get("m_pen", 0),
        "speed": c_total.get("speed", 10), "crit_chance": c_total.get("crit_chance", 5),
        "crit_damage": c_total.get("crit_damage", 150), "type": "pvp", "passif": "",
    }

    c_es = CombatStats.from_dict(t_proxy)
    c_es.max_hp = t_max_hp

    t_es = CombatStats.from_dict(c_proxy)
    t_es.max_hp = c_max_hp

    state = CombatState(
        player_stats=c_ps, enemy_stats=c_es,
        player_class=pending.c_class, enemy_data=t_proxy,
    )
    t_state = CombatState(
        player_stats=t_ps, enemy_stats=t_es,
        player_class=pending.t_class, enemy_data=c_proxy,
    )

    session = PvPSession(
        challenger_id=pending.challenger_id, target_id=pending.target_id,
        state=state, t_state=t_state,
        c_name=pending.c_name, t_name=pending.t_name,
        c_class=pending.c_class, t_class=pending.t_class,
        c_elo=pending.c_elo, t_elo=pending.t_elo,
        mode="ranked", use_buffs=False,
    )
    _pvp_sessions[pending.challenger_id] = session
    await db.update_player(pending.challenger_id, in_combat=1)
    await db.update_player(pending.target_id, in_combat=1)

    # Find the channel to send the combat message
    if pending.message:
        channel = pending.message.channel
    else:
        return

    pano_c = SET_BONUSES.get(pending.c_pano, {}).get("name", pending.c_pano)
    pano_t = SET_BONUSES.get(pending.t_pano, {}).get("name", pending.t_pano)

    embed = _build_pvp_embed(session)
    embed.add_field(
        name="🎯 Builds révélés",
        value=(
            f"**{pending.c_name}** : {pending.c_class} — {pano_c}\n"
            f"**{pending.t_name}** : {pending.t_class} — {pano_t}"
        ),
        inline=False,
    )
    view = PvPCombatView(session)
    msg = await channel.send(embed=embed, view=view)
    session.message = msg


# ══════════════════════════════════════════════════════════════════════════
# EMBED & VUE DE COMBAT PVP (commun classique + classé)
# ══════════════════════════════════════════════════════════════════════════


def _build_pvp_embed(session: PvPSession, log_lines: list[str] | None = None) -> discord.Embed:
    state = session.state
    current_name = session.c_name if session.current_attacker == "challenger" else session.t_name
    active_class  = session.c_class if session.current_attacker == "challenger" else session.t_class
    active_state  = session.state   if session.current_attacker == "challenger" else session.t_state

    spell_btns = get_spell_buttons_data(active_class, active_state) if active_class else []
    res_line   = f"\n{spell_btns[0]['resource_label']}" if spell_btns else ""

    mode_emoji = "🏆" if session.mode == "ranked" else "⚔️"
    mode_label = "Classé" if session.mode == "ranked" else "Classique"

    embed = discord.Embed(
        title=f"{mode_emoji} PvP {mode_label} — {session.c_name} vs {session.t_name}",
        description=f"⚡ C'est au tour de **{current_name}** d'attaquer !{res_line}",
        color=0xE040FB if session.mode == "ranked" else 0x607D8B,
    )
    embed.add_field(
        name=f"👤 {session.c_name}",
        value=(
            f"❤️ {hp_bar(state.player_stats.hp, state.player_stats.max_hp, 12)}\n"
            f"{state.player_stats.hp:,}/{state.player_stats.max_hp:,}"
        ),
        inline=True,
    )
    embed.add_field(
        name=f"👤 {session.t_name}",
        value=(
            f"❤️ {hp_bar(state.enemy_stats.hp, state.enemy_stats.max_hp, 12)}\n"
            f"{state.enemy_stats.hp:,}/{state.enemy_stats.max_hp:,}"
        ),
        inline=True,
    )

    status_txt = format_status_effects(active_state)
    if status_txt:
        embed.add_field(name="⚡ Effets actifs", value=status_txt[:512], inline=False)

    if log_lines:
        embed.add_field(name="📜 Dernier tour", value="\n".join(log_lines)[:800], inline=False)

    if session.mode == "ranked":
        embed.set_footer(text=f"Tour {state.turn} | Élo : {session.c_name} {session.c_elo} — {session.t_name} {session.t_elo}")
    else:
        buffs_txt = "buffs ON" if session.use_buffs else "buffs OFF"
        embed.set_footer(text=f"Tour {state.turn} | Mode Classique ({buffs_txt})")

    return embed


class PvPCombatView(discord.ui.View):
    def __init__(self, session: PvPSession):
        super().__init__(timeout=300)
        self.session = session
        self._build_buttons()

    def _build_buttons(self):
        self.clear_items()
        session = self.session
        active_class = session.c_class if session.current_attacker == "challenger" else session.t_class
        active_state = session.state   if session.current_attacker == "challenger" else session.t_state

        atk_btn = discord.ui.Button(label="⚔️ Attaquer", style=discord.ButtonStyle.danger, row=0)
        atk_btn.callback = self._make_action_cb(None)
        self.add_item(atk_btn)

        if active_class and active_state:
            for bdata in get_spell_buttons_data(active_class, active_state):
                style = discord.ButtonStyle.red if bdata["is_ultimate"] else discord.ButtonStyle.blurple
                btn = discord.ui.Button(
                    label=bdata["label"], emoji=bdata["emoji"],
                    style=style, disabled=bdata["disabled"], row=1,
                )
                btn.callback = self._make_action_cb(bdata["key"])
                self.add_item(btn)

    def _make_action_cb(self, spell_key: str | None):
        async def callback(interaction: discord.Interaction):
            await self._do_action(interaction, spell_key)
        return callback

    async def on_timeout(self):
        session = self.session
        _pvp_sessions.pop(session.challenger_id, None)
        await db.update_player(session.challenger_id, in_combat=0)
        await db.update_player(session.target_id, in_combat=0)
        if session.message:
            try:
                embed = discord.Embed(
                    title="⏰ Combat PvP — Temps écoulé",
                    description="Le combat a expiré faute d'activité.",
                    color=0x607D8B,
                )
                await session.message.edit(embed=embed, view=None)
            except Exception:
                pass

    async def _do_action(self, interaction: discord.Interaction, spell_key: str | None):
        session = self.session

        if session.current_attacker == "challenger":
            if interaction.user.id != session.challenger_id:
                await interaction.response.send_message(
                    f"⏳ C'est au tour de **{session.c_name}** d'attaquer !", ephemeral=True
                )
                return
            result = run_pvp_turn(session.state, "player", spell_key)
        else:
            if interaction.user.id != session.target_id:
                await interaction.response.send_message(
                    f"⏳ C'est au tour de **{session.t_name}** d'attaquer !", ephemeral=True
                )
                return
            session.sync_hp_to_t_state()
            result = run_pvp_turn(session.t_state, "player", spell_key)
            session.sync_hp_from_t_state()

        is_over        = session.state.player_stats.hp <= 0 or session.state.enemy_stats.hp <= 0
        challenger_won = session.state.enemy_stats.hp <= 0 and session.state.player_stats.hp > 0

        session.current_attacker = "target" if session.current_attacker == "challenger" else "challenger"

        if is_over:
            _pvp_sessions.pop(session.challenger_id, None)

            # HP finaux
            c_final_hp = max(1, session.state.player_stats.hp)
            t_final_hp = max(1, session.t_state.player_stats.hp)

            # Récompenses pvp_wins/pvp_losses (classique + classé)
            c_db = await db.get_player(session.challenger_id)
            t_db = await db.get_player(session.target_id)
            c_wins   = c_db.get("pvp_wins", 0)
            c_losses = c_db.get("pvp_losses", 0)
            t_wins   = t_db.get("pvp_wins", 0)
            t_losses = t_db.get("pvp_losses", 0)

            # Nettoyer les buffs de combat utilisés
            import json as _json
            _FOOD_COMBAT_KEYS = ("stat_def", "stat_speed", "stat_patk", "stat_matk",
                                 "elixir_patk", "elixir_matk", "elixir_def",
                                 "elixir_speed", "elixir_crit", "elixir_all")
            async def _clear_pvp_buffs(uid: int, player_data: dict):
                fb = {}
                try:
                    raw = player_data.get("food_buffs")
                    if raw:
                        fb = _json.loads(raw)
                except Exception:
                    pass
                changed = False
                for k in _FOOD_COMBAT_KEYS:
                    if k in fb:
                        fb[k]["combats"] = fb[k].get("combats", 1) - 1
                        if fb[k]["combats"] <= 0:
                            del fb[k]
                        changed = True
                if changed:
                    await db.update_player(uid, food_buffs=_json.dumps(fb) if fb else None)

            if session.use_buffs:
                await _clear_pvp_buffs(session.challenger_id, c_db)
                await _clear_pvp_buffs(session.target_id, t_db)

            await db.update_player(
                session.challenger_id, in_combat=0,
                current_hp=c_final_hp, potion_revival_active=0, potion_no_passive=0,
                pvp_wins=(c_wins + (1 if challenger_won else 0)),
                pvp_losses=(c_losses + (0 if challenger_won else 1)),
            )
            await db.update_player(
                session.target_id, in_combat=0,
                current_hp=t_final_hp, potion_revival_active=0, potion_no_passive=0,
                pvp_wins=(t_wins + (0 if challenger_won else 1)),
                pvp_losses=(t_losses + (1 if challenger_won else 0)),
            )

            winner_name = session.c_name if challenger_won else session.t_name

            if session.mode == "ranked":
                delta_c = _elo_change(session.c_elo, session.t_elo, challenger_won)
                delta_t = _elo_change(session.t_elo, session.c_elo, not challenger_won)
                new_c_elo = max(0, session.c_elo + delta_c)
                new_t_elo = max(0, session.t_elo + delta_t)

                if challenger_won:
                    await db.update_player(
                        session.challenger_id,
                        pvp_elo=new_c_elo,
                        pvp_ranked_wins=(c_db.get("pvp_ranked_wins", 0) + 1),
                    )
                    await db.update_player(
                        session.target_id,
                        pvp_elo=new_t_elo,
                        pvp_ranked_losses=(t_db.get("pvp_ranked_losses", 0) + 1),
                    )
                else:
                    await db.update_player(
                        session.challenger_id,
                        pvp_elo=new_c_elo,
                        pvp_ranked_losses=(c_db.get("pvp_ranked_losses", 0) + 1),
                    )
                    await db.update_player(
                        session.target_id,
                        pvp_elo=new_t_elo,
                        pvp_ranked_wins=(t_db.get("pvp_ranked_wins", 0) + 1),
                    )

                await _increment_ranked_daily(session.challenger_id)
                await _increment_ranked_daily(session.target_id)

                c_delta_txt = f"{'+' if delta_c >= 0 else ''}{delta_c}"
                t_delta_txt = f"{'+' if delta_t >= 0 else ''}{delta_t}"

                result_desc = (
                    f"🏆 **{winner_name}** remporte le combat !\n\n"
                    f"**{session.c_name}** : Élo {session.c_elo} → **{new_c_elo}** ({c_delta_txt})\n"
                    f"**{session.t_name}** : Élo {session.t_elo} → **{new_t_elo}** ({t_delta_txt})\n\n"
                    f"*Ce message sera supprimé dans 10 secondes.*"
                )
                color = 0xE040FB
            else:
                result_desc = (
                    f"🏆 **{winner_name}** remporte le combat !\n"
                    f"*(Mode Classique — pas d'Élo)*\n\n"
                    f"*Ce message sera supprimé dans 10 secondes.*"
                )
                color = 0x607D8B

            embed = discord.Embed(title="⚔️ Combat PvP — Terminé !", description=result_desc, color=color)
            log_txt = "\n".join(result["log"][-6:])[:800]
            if log_txt:
                embed.add_field(name="📜 Dernier tour", value=log_txt, inline=False)

            await interaction.response.edit_message(embed=embed, view=None)
            await asyncio.sleep(10)
            try:
                await interaction.message.delete()
            except Exception:
                pass
        else:
            self._build_buttons()
            embed = _build_pvp_embed(session, result["log"][-6:])
            await interaction.response.edit_message(embed=embed, view=self)


# ══════════════════════════════════════════════════════════════════════════
# CLASSEMENT
# ══════════════════════════════════════════════════════════════════════════


async def _handle_pvp_rank(interaction: discord.Interaction):
    player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
    elo    = player.get("pvp_elo", 1000)
    rw     = player.get("pvp_ranked_wins", 0)
    rl     = player.get("pvp_ranked_losses", 0)
    rtotal = rw + rl
    wr     = (rw / rtotal * 100) if rtotal > 0 else 0
    can, remaining = await _check_ranked_daily(player)

    rank_label = _get_rank_label(elo)
    embed = discord.Embed(title="📊 Mon Classement PvP", color=_get_rank_color(elo))
    embed.add_field(name="🎖️ Rang",                value=f"**{rank_label}**",           inline=True)
    embed.add_field(name="📈 Élo",                  value=f"**{elo}**",                  inline=True)
    embed.add_field(name="\u200b",                  value="\u200b",                      inline=True)
    embed.add_field(name="⚔️ Victoires classées",   value=f"**{rw}**",                   inline=True)
    embed.add_field(name="💀 Défaites classées",    value=f"**{rl}**",                   inline=True)
    embed.add_field(name="📊 Winrate classé",       value=f"**{wr:.1f}%**",              inline=True)
    embed.add_field(name="🗓️ Combats restants",     value=f"**{remaining}/{MAX_RANKED_DAY}** aujourd'hui", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


async def _handle_pvp_leaderboard(interaction: discord.Interaction):
    await db.update_player(interaction.user.id, display_name=interaction.user.display_name)
    rows = await db.get_pvp_leaderboard()

    embed = discord.Embed(title="🏅 Classement PvP Classé — Top 20", color=0xE040FB)

    if not rows:
        embed.description = "*Aucun combat classé enregistré.*"
    else:
        medals = ["🥇", "🥈", "🥉"] + [f"#{i+1}" for i in range(3, 20)]
        lines = []
        for i, row in enumerate(rows[:20]):
            medal  = medals[i] if i < len(medals) else f"#{i+1}"
            elo    = row.get("pvp_elo", 1000)
            rw     = row.get("pvp_ranked_wins", 0)
            rl     = row.get("pvp_ranked_losses", 0)
            rtotal = rw + rl
            wr     = f"{rw/rtotal*100:.0f}%" if rtotal > 0 else "N/A"
            name   = row.get("display_name") or f"Joueur {row['user_id']}"
            lines.append(
                f"{medal} **{name}** — Élo **{elo}** ({_get_rank_label(elo)}) — {rw}V/{rl}D ({wr})"
            )
        embed.description = "\n".join(lines)

    player_row = next((r for r in rows if r["user_id"] == interaction.user.id), None)
    if player_row:
        rank = rows.index(player_row) + 1
        embed.set_footer(text=f"Ta position : #{rank} avec {player_row.get('pvp_elo', 1000)} Élo")
    else:
        embed.set_footer(text="Tu n'es pas encore classé.")

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ══════════════════════════════════════════════════════════════════════════
# HUB MESSAGE
# ══════════════════════════════════════════════════════════════════════════


def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="🍺 Hub Taverne",
        description=(
            "Affronte d'autres joueurs en combat PvP tour par tour !\n\n"
            "**⚔️ PvP Classique**\n"
            "• Stats et équipements réels\n"
            "• Pas d'Élo, pas de coût d'énergie\n"
            "• Option : activer ou désactiver les buffs alimentaires et reliques\n\n"
            "**🏆 PvP Classé**\n"
            "• Stats normalisées (niveau 500, craft, rare, 7 pièces)\n"
            "• Aucun buff externe — uniquement classe + sorts + panoplie\n"
            f"• **{MAX_RANKED_DAY} combats par jour** maximum\n"
            "• Sélection secrète de classe et panoplie avant chaque combat\n"
            "• Système **Élo** (K=32)\n\n"
            "**Rangs :**\n"
            "🔩 Fer (0–999) | 🥉 Bronze (1000–1199)\n"
            "🥈 Argent (1200–1399) | 🥇 Or (1400–1599)\n"
            "🪙 Platine (1600–1799) | 💎 Diamant (1800–1999)\n"
            "⚜️ Maître (2000–2399) | 👑 Maître Absolu (2400+)"
        ),
        color=0xE040FB,
    )
    view = TaverneHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
