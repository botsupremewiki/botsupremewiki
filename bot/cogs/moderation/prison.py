# bot/cogs/prison.py
# discord.py 2.x (app_commands)
#
# /prison @member seconds
# - Sauvegarde rôles -> retire rôles -> ajoute rôle prison -> déplace en vocal prison
# - Timer démarre au déplacement (ou tout de suite si pas en vocal)
# - Fin: restore rôles + retire rôle prison + nettoie l'entrée JSON
# - Multi-prisonniers OK + reprise après redémarrage

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)

# =============================
# CONFIG
# =============================
PRISON_VOICE_CHANNEL_ID = 1463052911629041838  # vocal prison
PRISON_ROLE_ID = 1477560410843516939           # rôle prison

PRISON_STATE_FILE = "bot/data/prison_state.json"

MIN_SECONDS = 5
MAX_SECONDS = 60 * 60 * 24 * 7  # 7 jours


# =============================
# JSON helpers
# =============================
def _ensure_dir(path: str) -> None:
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)


def _load_state(path: str) -> Dict[str, Any]:
    _ensure_dir(path)
    if not os.path.exists(path):
        return {"guilds": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"guilds": {}}
        data.setdefault("guilds", {})
        return data
    except Exception:
        return {"guilds": {}}


def _save_state(path: str, data: Dict[str, Any]) -> None:
    _ensure_dir(path)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


# =============================
# COG
# =============================
class PrisonCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._lock = asyncio.Lock()
        self._tasks: Dict[tuple[int, int], asyncio.Task] = {}  # (guild_id, user_id) -> task

    async def cog_load(self) -> None:
        await self._reschedule_all()

    async def cog_unload(self) -> None:
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()

    # -------------------------
    # Reschedule on restart
    # -------------------------
    async def _reschedule_all(self) -> None:
        async with self._lock:
            state = _load_state(PRISON_STATE_FILE)

        now = int(time.time())
        guilds = state.get("guilds", {}) if isinstance(state, dict) else {}

        for g_id_str, gdata in guilds.items():
            try:
                guild_id = int(g_id_str)
            except ValueError:
                continue

            users = (gdata or {}).get("users", {})
            if not isinstance(users, dict):
                continue

            for u_id_str, udata in users.items():
                try:
                    user_id = int(u_id_str)
                except ValueError:
                    continue

                release_at = int((udata or {}).get("release_at", 0))
                delay = max(0, release_at - now)
                self._schedule_release(guild_id, user_id, delay)

    def _schedule_release(self, guild_id: int, user_id: int, delay: int) -> None:
        key = (guild_id, user_id)
        existing = self._tasks.get(key)
        if existing and not existing.done():
            existing.cancel()
        self._tasks[key] = asyncio.create_task(self._release_after(guild_id, user_id, delay))

    async def _release_after(self, guild_id: int, user_id: int, delay: int) -> None:
        try:
            if delay > 0:
                await asyncio.sleep(delay)
            await self._release_member(guild_id, user_id)
        except asyncio.CancelledError:
            return
        except Exception as e:
            logger.error("_release_after(%s, %s): erreur inattendue: %s", guild_id, user_id, e)

    # -------------------------
    # Release logic
    # -------------------------
    async def _release_member(self, guild_id: int, user_id: int) -> None:
        guild = self.bot.get_guild(guild_id)

        # Lire données prison
        async with self._lock:
            state = _load_state(PRISON_STATE_FILE)
            g = state.setdefault("guilds", {}).setdefault(str(guild_id), {})
            users = g.setdefault("users", {})
            udata = users.get(str(user_id))

        if not udata or not isinstance(udata, dict):
            return

        saved_roles = udata.get("roles", [])
        if not isinstance(saved_roles, list):
            saved_roles = []

        # Si guild inexistante, nettoyer l'entrée
        if guild is None:
            async with self._lock:
                state = _load_state(PRISON_STATE_FILE)
                g = state.setdefault("guilds", {}).setdefault(str(guild_id), {})
                users = g.setdefault("users", {})
                users.pop(str(user_id), None)
                _save_state(PRISON_STATE_FILE, state)
            return

        member = guild.get_member(user_id)
        if member is None:
            # Membre parti: on nettoie juste son entrée
            async with self._lock:
                state = _load_state(PRISON_STATE_FILE)
                g = state.setdefault("guilds", {}).setdefault(str(guild_id), {})
                users = g.setdefault("users", {})
                users.pop(str(user_id), None)
                _save_state(PRISON_STATE_FILE, state)
            return

        me = guild.me
        prison_role = guild.get_role(PRISON_ROLE_ID)

        # Si on ne peut pas vérifier le bot ou le rôle prison, on nettoie au moins l'entrée
        if me is None or prison_role is None:
            async with self._lock:
                state = _load_state(PRISON_STATE_FILE)
                g = state.setdefault("guilds", {}).setdefault(str(guild_id), {})
                users = g.setdefault("users", {})
                users.pop(str(user_id), None)
                _save_state(PRISON_STATE_FILE, state)
            return

        # ⚠️ Si le rôle prison est au-dessus (ou égal) au bot, Discord refusera de l'enlever
        if me.top_role <= prison_role:
            # Ici on ne peut rien faire côté code, donc on nettoie juste le JSON.
            async with self._lock:
                state = _load_state(PRISON_STATE_FILE)
                g = state.setdefault("guilds", {}).setdefault(str(guild_id), {})
                users = g.setdefault("users", {})
                users.pop(str(user_id), None)
                _save_state(PRISON_STATE_FILE, state)
            return

        # Construire la liste finale des rôles à appliquer EN UNE FOIS
        # On conserve ce qu'on ne peut pas retirer (managed / au-dessus du bot)
        final_roles: list[discord.Role] = []

        for r in member.roles:
            if r.is_default():
                continue
            if r.id == PRISON_ROLE_ID:
                continue  # on enlève prison
            if r.managed:
                final_roles.append(r)
                continue
            if me.top_role <= r:
                final_roles.append(r)
                continue

        # Ajouter les rôles sauvegardés (si possibles)
        for rid in saved_roles:
            try:
                rid_int = int(rid)
            except Exception:
                continue
            if rid_int == PRISON_ROLE_ID:
                continue
            role = guild.get_role(rid_int)
            if role is None:
                continue
            if role.is_default() or role.managed:
                continue
            if me.top_role <= role:
                continue
            if role not in final_roles:
                final_roles.append(role)

        try:
            await member.edit(roles=final_roles, reason="Prison: fin de peine (restore roles)")
        except (discord.Forbidden, discord.HTTPException):
            # Si ça rate, on ne bloque pas le nettoyage JSON
            pass

        # Nettoyage : supprime uniquement CE membre
        async with self._lock:
            state = _load_state(PRISON_STATE_FILE)
            g = state.setdefault("guilds", {}).setdefault(str(guild_id), {})
            users = g.setdefault("users", {})
            users.pop(str(user_id), None)
            _save_state(PRISON_STATE_FILE, state)

        # Nettoyage task
        key = (guild_id, user_id)
        t = self._tasks.get(key)
        if t and not t.done():
            t.cancel()
        self._tasks.pop(key, None)

    # =============================
    # /prison
    # =============================
    @app_commands.command(
        name="prison",
        description="Met un membre en prison X secondes."
    )
    @app_commands.describe(
        member="Membre à emprisonner",
        seconds="Durée (secondes)"
    )
    @app_commands.checks.has_permissions(manage_roles=True, move_members=True)
    async def prison(self, interaction: discord.Interaction, member: discord.Member, seconds: int):
        # Répondre vite -> évite "l'application ne répond plus"
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if guild is None:
            return await interaction.followup.send("❌ Utilisable uniquement sur un serveur.", ephemeral=True)

        if seconds < MIN_SECONDS or seconds > MAX_SECONDS:
            return await interaction.followup.send(
                f"❌ Durée invalide ({MIN_SECONDS} à {MAX_SECONDS}s).",
                ephemeral=True
            )

        me = guild.me
        if me is None:
            return await interaction.followup.send("❌ Impossible de vérifier mes permissions.", ephemeral=True)

        if member.top_role >= me.top_role and guild.owner_id != me.id:
            return await interaction.followup.send("❌ Je ne peux pas gérer ce membre (rôle trop haut).", ephemeral=True)

        prison_role = guild.get_role(PRISON_ROLE_ID)
        if prison_role is None:
            return await interaction.followup.send("❌ Rôle prison introuvable (ID).", ephemeral=True)
        if me.top_role <= prison_role:
            return await interaction.followup.send("❌ Mon rôle est sous le rôle prison.", ephemeral=True)

        # 1) Sauvegarde rôles (tous sauf @everyone)
        saved_role_ids = [r.id for r in member.roles if not r.is_default()]

        # Ne pas écraser la sauvegarde si déjà emprisonné
        async with self._lock:
            state = _load_state(PRISON_STATE_FILE)
            g = state.setdefault("guilds", {}).setdefault(str(guild.id), {})
            users = g.setdefault("users", {})
            existing = users.get(str(member.id))
            if not (existing and isinstance(existing, dict) and "roles" in existing):
                users[str(member.id)] = {"roles": saved_role_ids, "start_at": None, "release_at": None}
                _save_state(PRISON_STATE_FILE, state)

        # 2) Retirer un max de rôles en 1 call: conserver managed + rôles au-dessus du bot
        keep_roles: list[discord.Role] = []
        for r in member.roles:
            if r.is_default():
                continue
            if r.managed:
                keep_roles.append(r)
                continue
            if me.top_role <= r:
                keep_roles.append(r)
                continue

        keep_roles.append(prison_role)

        try:
            await member.edit(roles=keep_roles, reason=f"Prison by {interaction.user}")
        except discord.Forbidden:
            return await interaction.followup.send("❌ Pas la permission de modifier les rôles.", ephemeral=True)
        except discord.HTTPException:
            return await interaction.followup.send("❌ Erreur Discord en modifiant les rôles.", ephemeral=True)

        # 3) Déplacer en vocal prison si en vocal, et démarrer timer après déplacement
        moved = False
        dest = guild.get_channel(PRISON_VOICE_CHANNEL_ID)
        start_at = int(time.time())

        if member.voice and member.voice.channel and isinstance(dest, (discord.VoiceChannel, discord.StageChannel)):
            try:
                await member.move_to(dest, reason=f"Prison by {interaction.user}")
                moved = True
            except (discord.Forbidden, discord.HTTPException):
                moved = False

        release_at = start_at + int(seconds)

        # 4) Sauver start/release (ou update si déjà emprisonné)
        async with self._lock:
            state = _load_state(PRISON_STATE_FILE)
            g = state.setdefault("guilds", {}).setdefault(str(guild.id), {})
            users = g.setdefault("users", {})
            udata = users.get(str(member.id))
            if not udata or not isinstance(udata, dict):
                users[str(member.id)] = {"roles": saved_role_ids, "start_at": start_at, "release_at": release_at}
            else:
                udata["start_at"] = start_at
                udata["release_at"] = release_at
            _save_state(PRISON_STATE_FILE, state)

        # 5) Planifier libération
        delay = max(0, release_at - int(time.time()))
        self._schedule_release(guild.id, member.id, delay)

        txt = f"⛓️ {member.mention} prison **{seconds}s**."
        txt += " 🎙️ déplacé (timer ok)." if moved else " (timer ok)."
        await interaction.followup.send(txt, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(PrisonCog(bot))