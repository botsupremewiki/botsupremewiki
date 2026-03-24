"""
Tâches de fond du RPG :
- Régénération passive (HP + énergie toutes les 10 min)
- Reset hebdomadaire du World Boss (lundi minuit UTC)
- Récompenses World Boss de fin de semaine
- Initialisation des messages hub
"""
from __future__ import annotations
import asyncio
import logging
import discord
from datetime import datetime, timezone, timedelta
from discord.ext import commands, tasks

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    HUB_CHANNELS, PASSIVE_REGEN_HP_PCT, PASSIVE_REGEN_ENERGY,
    PASSIVE_REGEN_INTERVAL, MAX_ENERGY, WB_RANK_REWARDS
)

logger = logging.getLogger(__name__)


class RPGCore(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._hub_views_registered = False

    async def cog_load(self):
        await db.init_db()
        self.passive_regen_task.start()
        self.wb_weekly_reset_task.start()

    async def cog_unload(self):
        self.passive_regen_task.cancel()
        self.wb_weekly_reset_task.cancel()

    # ─── Regen passive ─────────────────────────────────────────────────────

    @tasks.loop(seconds=PASSIVE_REGEN_INTERVAL)
    async def passive_regen_task(self):
        """Régénère HP et énergie pour tous les joueurs toutes les 10 minutes."""
        try:
            import aiosqlite
            async with aiosqlite.connect(db.DB_PATH) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute("SELECT user_id, class, current_hp, energy, max_energy, regen_blocked_until FROM players WHERE class IS NOT NULL") as cur:
                    players = [dict(r) for r in await cur.fetchall()]

            updates = []
            for p in players:
                if p["class"] is None:
                    continue
                from bot.cogs.rpg.models import compute_class_stats, compute_max_hp
                # Calculer les stats de classe pour avoir le max HP
                # (version simplifiée sans équipements pour le regen passif)
                try:
                    from bot.cogs.rpg import database as db2
                    player_full = await db2.get_player(p["user_id"])
                    if not player_full or not player_full.get("class"):
                        continue
                    cs = compute_class_stats(player_full["class"], player_full["level"], player_full["prestige_level"])
                    max_hp = compute_max_hp(cs)
                except Exception:
                    max_hp = 1000

                current_hp = p["current_hp"] if p["current_hp"] is not None else max_hp
                current_energy = p["energy"] if p["energy"] is not None else 0
                max_energy = p["max_energy"] or MAX_ENERGY

                # Vérifier si la regen est bloquée (pénalité de mort 1h)
                blocked_until = p["regen_blocked_until"]
                if blocked_until:
                    from datetime import datetime, timezone
                    try:
                        blocked_dt = datetime.fromisoformat(blocked_until)
                        if datetime.now(timezone.utc) < blocked_dt:
                            continue
                    except Exception:
                        pass

                hp_regen = max(1, int(max_hp * PASSIVE_REGEN_HP_PCT / 100))
                new_hp     = min(max_hp, current_hp + hp_regen)

                # Bonus regen alimentaire (food_buff energy_regen)
                food_energy_regen_bonus = 0.0
                food_buffs_raw = p.get("food_buffs") or player_full.get("food_buffs")
                if food_buffs_raw:
                    try:
                        import json
                        from datetime import datetime, timezone
                        fb = json.loads(food_buffs_raw)
                        er = fb.get("energy_regen")
                        if er:
                            exp = er.get("expires")
                            if exp and datetime.now(timezone.utc) < datetime.fromisoformat(exp):
                                food_energy_regen_bonus = er.get("value", 0) / 100
                    except Exception:
                        pass

                energy_regen_total = PASSIVE_REGEN_ENERGY * (1 + food_energy_regen_bonus)
                new_energy = min(max_energy, current_energy + int(energy_regen_total))

                if new_hp != current_hp or new_energy != current_energy:
                    updates.append((new_hp, new_energy, p["user_id"]))

            if updates:
                import aiosqlite
                async with aiosqlite.connect(db.DB_PATH) as conn:
                    await conn.executemany(
                        "UPDATE players SET current_hp=?, energy=? WHERE user_id=?",
                        updates
                    )
                    await conn.commit()
                logger.debug("[RPG] Regen passive : %d joueurs mis à jour.", len(updates))
        except Exception as e:
            logger.error("[RPG] Erreur regen passive : %s", e)

    @passive_regen_task.before_loop
    async def before_passive_regen(self):
        await self.bot.wait_until_ready()

    # ─── Reset hebdomadaire World Boss ──────────────────────────────────────

    @tasks.loop(hours=1)
    async def wb_weekly_reset_task(self):
        """Vérifie si on est lundi et distribue les récompenses World Boss."""
        now = datetime.now(timezone.utc)
        # On déclenche le lundi à 0h UTC
        if now.weekday() != 0 or now.hour != 0:
            return
        await self._do_wb_weekly_reset()

    @wb_weekly_reset_task.before_loop
    async def before_wb_weekly_reset(self):
        await self.bot.wait_until_ready()

    async def _do_wb_weekly_reset(self):
        """Distribue les récompenses World Boss et reset le classement."""
        try:
            # Récupérer la semaine passée
            now = datetime.now(timezone.utc)
            last_monday = now - timedelta(days=7)
            week_str = last_monday.strftime("%Y-%m-%d")

            leaderboard = await db.get_wb_leaderboard(week=week_str)
            if not leaderboard:
                return

            logger.info("[RPG] Distribution récompenses World Boss semaine %s", week_str)

            default_reward = WB_RANK_REWARDS["default"]
            for rank, entry in enumerate(leaderboard, start=1):
                user_id = entry["user_id"]
                reward = WB_RANK_REWARDS.get(rank, default_reward)

                # Donner gold et relique
                player = await db.get_player(user_id)
                if player:
                    await db.update_player(user_id, gold=player["gold"] + reward["gold"])
                    await db.add_relic(user_id, reward["relic"])

                    # Notifier le joueur si possible
                    try:
                        discord_user = await self.bot.fetch_user(user_id)
                        if discord_user:
                            rank_txt = f"**#{rank}**" if rank <= 10 else f"#{rank}"
                            await discord_user.send(
                                f"🏆 **Récompense World Boss (Semaine {week_str})** !\n"
                                f"Tu t'es classé {rank_txt} avec **{entry['damage']:,}** dégâts.\n"
                                f"Récompenses : **{reward['gold']:,}** golds + **Relique** obtenue !"
                            )
                    except Exception:
                        pass

            # Titres WB — top 1 semaine
            if leaderboard:
                wb_top_uid = leaderboard[0]["user_id"]
                for tid in ("t_wb_rank1", "t_spec_wb_top1"):
                    await db.increment_title_progress(wb_top_uid, tid)
                    await _check_title(wb_top_uid, tid)

            # Titres Global / PvP — top 1 hebdomadaire
            try:
                global_lb = await db.get_global_leaderboard(limit=1)
                if global_lb:
                    g_uid = global_lb[0]["user_id"]
                    await db.increment_title_progress(g_uid, "t_spec_global_top1")
                    await _check_title(g_uid, "t_spec_global_top1")

                pvp_lb = await db.get_pvp_leaderboard(limit=1)
                if pvp_lb:
                    p_uid = pvp_lb[0]["user_id"]
                    await db.increment_title_progress(p_uid, "t_spec_pvp_top1")
                    await _check_title(p_uid, "t_spec_pvp_top1")
            except Exception as e_rank:
                logger.error("[RPG] Erreur titres rang top1 : %s", e_rank)

        except Exception as e:
            logger.error("[RPG] Erreur reset World Boss : %s", e)

    # ─── Initialisation des messages hub ────────────────────────────────────

    @commands.Cog.listener()
    async def on_ready(self):
        if self._hub_views_registered:
            return
        self._hub_views_registered = True
        await db.reset_all_in_combat()
        # Laisser un moment pour que les autres cogs s'enregistrent
        await asyncio.sleep(2)
        await self._setup_hub_messages()

    async def _setup_hub_messages(self):
        """Crée ou met à jour les messages hub dans chaque salon."""
        from bot.cogs.rpg.hubs import bienvenue, classe, profil, metiers
        from bot.cogs.rpg.hubs import banque, monde, donjons, raids
        from bot.cogs.rpg.hubs import world_boss, hotel_ventes, echanges
        from bot.cogs.rpg.hubs import titres, pvp, classement, admin, quetes

        hub_modules = {
            "bienvenue":    bienvenue,
            "classe":       classe,
            "profil":       profil,
            "metiers":      metiers,
            "banque":       banque,
            "monde":        monde,
            "donjons":      donjons,
            "raids":        raids,
            "world_boss":   world_boss,
            "hotel_ventes": hotel_ventes,
            "echanges":     echanges,
            "titres":       titres,
            "pvp":          pvp,
            "classement":   classement,
            "admin":        admin,
            "quetes":       quetes,
        }

        for hub_name, module in hub_modules.items():
            await self._setup_one_hub(hub_name, module)
            # Petite pause entre chaque hub pour éviter le burst de rate limit
            await asyncio.sleep(1.5)

    async def _setup_one_hub(self, hub_name: str, module, max_retries: int = 10):
        """Crée ou édite le message d'un hub, avec retry automatique sur rate limit."""
        channel_id = HUB_CHANNELS.get(hub_name)
        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            logger.warning("[RPG] Canal introuvable pour hub '%s' (id=%s)", hub_name, channel_id)
            return

        for attempt in range(max_retries):
            try:
                existing = await db.get_hub_message(hub_name)
                embed, view = module.build_hub_message(self.bot)

                if existing:
                    try:
                        msg = await channel.fetch_message(existing["message_id"])
                        await msg.edit(embed=embed, view=view)
                        return
                    except discord.NotFound:
                        # Message supprimé → on en crée un nouveau
                        pass

                # Créer le message
                msg = await channel.send(embed=embed, view=view)
                await db.set_hub_message(hub_name, channel_id, msg.id)
                return

            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(getattr(e, "retry_after", 5))
                    logger.warning(
                        "[RPG] Rate limit sur hub '%s' — retry dans %.1fs (tentative %d/%d)",
                        hub_name, retry_after, attempt + 1, max_retries
                    )
                    await asyncio.sleep(retry_after + 0.5)
                else:
                    logger.error("[RPG] Erreur HTTP hub '%s' : %s", hub_name, e)
                    return
            except Exception as e:
                logger.error("[RPG] Erreur setup hub '%s' : %s", hub_name, e)
                return


# ─── Vérification des titres ──────────────────────────────────────────────

async def _check_title(user_id: int, title_id: str):
    """Vérifie si un titre peut être débloqué et l'accorde si oui."""
    from bot.cogs.rpg.models import TITLES
    title = TITLES.get(title_id)
    if not title:
        return False
    progress = await db.get_title_progress(user_id, title_id)
    if progress >= title["req"]:
        unlocked = await db.unlock_title(user_id, title_id)
        if unlocked:
            reward_gold = title.get("reward_gold", 0)
            if reward_gold:
                player = await db.get_player(user_id)
                if player:
                    await db.update_player(user_id, gold=player["gold"] + reward_gold)
            return True
    return False


async def check_all_titles(user_id: int, player: dict, professions: dict = None):
    """Vérifie tous les titres liés à un joueur après une action."""
    from bot.cogs.rpg.models import TITLES

    for title_id, title in TITLES.items():
        req_type = title["req_type"]
        req      = title["req"]
        value    = None

        if req_type == "level":
            value = player.get("level", 1)
        elif req_type == "prestige":
            value = player.get("prestige_level", 0)
        elif req_type == "zone":
            value = player.get("zone", 1)
        elif req_type == "pvp_elo":
            value = player.get("pvp_elo", 1000)
        elif req_type == "total_gold":
            value = player.get("total_gold", player.get("gold", 0))
        elif professions:
            if req_type == "harvest_level":
                value = professions.get("harvest_level", 0)
            elif req_type == "craft_level":
                value = professions.get("craft_level", 0)
            elif req_type == "conception_level":
                value = professions.get("conception_level", 0)

        if value is not None and value >= req:
            await db.update_title_progress(user_id, title_id, value)
            await _check_title(user_id, title_id)


async def increment_and_check_title(user_id: int, title_id: str, amount: int = 1) -> bool:
    """Incrémente la progression d'un titre et vérifie si débloqué."""
    await db.increment_title_progress(user_id, title_id, amount)
    return await _check_title(user_id, title_id)


# ─── Setup ─────────────────────────────────────────────────────────────────

async def setup(bot: commands.Bot):
    await bot.add_cog(RPGCore(bot))
