"""
Hub Raids — combats d'équipe (5 joueurs max).
Canal : 1479297621007798283
"""
from __future__ import annotations
import asyncio
import json
import discord
from discord.ext import commands

from bot.cogs.rpg import database as db
from bot.cogs.rpg.models import (
    compute_total_stats, compute_max_hp, get_set_bonus, level_up, ENERGY_COST,
    STAT_FR, compute_relic_effects,
)
from bot.cogs.rpg.enemies import RAID_BOSSES, RAID_DROP_SOURCE, generate_raid_boss, format_enemy_stats
from bot.cogs.rpg.items import get_equipment_drops, format_item_name
from bot.cogs.rpg.combat import (
    CombatStats, CombatState, hp_bar,
    build_combat_state, apply_spell, tick_spell_effects, get_spell_buttons_data,
    format_status_effects, _class_to_spell_key,
    calc_physical_damage, calc_magical_damage, apply_player_passive,
    apply_player_post_attack, apply_crit, apply_damage_to_target,
)
from bot.cogs.rpg.models import CLASS_SPELLS
from bot.cogs.rpg.core import increment_and_check_title

# États de raid actifs : raid_id → {enemy_hp, enemy_max_hp, enemy_data, turn, shields, logs, finished}
_active_raids: dict[int, dict] = {}
ATTACK_TIMEOUT = 60  # secondes par joueur pour attaquer

_FOOD_STAT_BUFFS = ("stat_def", "stat_speed", "stat_patk", "stat_matk", "elixir_patk", "elixir_matk", "elixir_def", "elixir_speed", "elixir_crit", "elixir_all")

async def _consume_raid_food_buffs(user_id: int) -> None:
    """Décrémente les compteurs de combats des buffs alimentaires de stats après un raid."""
    p = await db.get_player(user_id)
    if not p:
        return
    food_raw = p.get("food_buffs")
    if not food_raw:
        return
    try:
        fb = json.loads(food_raw)
        changed = False
        for key in _FOOD_STAT_BUFFS:
            if key in fb:
                fb[key]["combats"] = fb[key].get("combats", 0) - 1
                if fb[key]["combats"] <= 0:
                    del fb[key]
                changed = True
        if changed:
            await db.update_player(user_id, food_buffs=json.dumps(fb))
    except Exception:
        pass


class RaidsHubView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Afficher les Raids", style=discord.ButtonStyle.primary, emoji="👥", custom_id="rpg:raids:afficher", row=0)
    async def afficher_raids(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        embed, view = build_raid_list_embed(player)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def build_raid_list_embed(player: dict) -> tuple:
    embed = discord.Embed(
        title="👥 Raids Disponibles",
        description=(
            f"**Coût** : {ENERGY_COST['raid']} énergies par raid\n"
            f"⚡ Énergie actuelle : **{player.get('energy', 0)}/{player.get('max_energy', 2000)}**\n\n"
            "Sélectionnez un raid pour voir ses détails et créer un groupe !"
        ),
        color=0x9C27B0,
    )
    player_level = player.get("level", 1)
    for boss in RAID_BOSSES:
        level_req = boss.get("level_req", 100)
        unlocked = player_level >= level_req
        lock_icon = "🔓" if unlocked else "🔒"
        spells = boss.get("spells", {})
        s1_name  = spells.get("s1",       {}).get("name", "—")
        ult_name = spells.get("ultimate",  {}).get("name", "—")
        embed.add_field(
            name=f"{lock_icon} {boss['emoji']} Raid {boss['raid_level']} — {boss['name']} (niv. {level_req}+)",
            value=f"Classe : **{boss['class']}** | Sorts : *{s1_name}* & *{ult_name}*",
            inline=False,
        )
    view = RaidListView(player)
    return embed, view


class RaidListView(discord.ui.View):
    def __init__(self, player: dict):
        super().__init__(timeout=120)
        self.player = player

        player_level = player.get("level", 1)
        for boss in RAID_BOSSES:
            level_req = boss.get("level_req", 100)
            unlocked = player_level >= level_req
            btn = discord.ui.Button(
                label=f"Raid {boss['raid_level']} — {boss['name'][:25]}",
                emoji=boss["emoji"],
                style=discord.ButtonStyle.primary if unlocked else discord.ButtonStyle.secondary,
                custom_id=f"rpg:raids:create:{boss['id']}",
                disabled=not unlocked,
            )
            btn.callback = self._make_cb(boss)
            self.add_item(btn)

    def _make_cb(self, boss: dict):
        async def callback(interaction: discord.Interaction):
            player = await db.get_player(interaction.user.id)
            if not player:
                await interaction.response.send_message("❌ Profil introuvable.", ephemeral=True)
                return
            if player.get("energy", 0) < ENERGY_COST["raid"]:
                await interaction.response.send_message(f"❌ Pas assez d'énergie ! (besoin : {ENERGY_COST['raid']})", ephemeral=True)
                return
            level_req = boss.get("level_req", 100)
            if player.get("level", 1) < level_req:
                await interaction.response.send_message(f"❌ Niveau insuffisant ! Ce raid requiert le niveau **{level_req}**.", ephemeral=True)
                return

            enemy_data = generate_raid_boss(boss["id"])
            channel    = interaction.channel

            # Créer le raid en DB
            raid_id    = await db.create_raid(boss["id"], interaction.user.id, channel.id)

            # Message public dans le salon
            embed = _build_raid_lobby_embed(boss, enemy_data, [interaction.user], raid_id)
            view  = RaidLobbyView(raid_id, boss, enemy_data, interaction.user, interaction.guild)
            msg   = await channel.send(embed=embed, view=view)
            await db.update_raid(raid_id, message_id=msg.id)

            await interaction.response.send_message(
                f"✅ Raid **{boss['name']}** créé ! En attente de joueurs dans ce salon.",
                ephemeral=True,
            )
        return callback


def _build_raid_lobby_embed(boss: dict, enemy_data: dict, participants: list[discord.User], raid_id: int) -> discord.Embed:
    raid_level = boss.get("raid_level", 1)
    level_req  = boss.get("level_req", 100)
    xp_gain    = enemy_data.get("xp", 10000)
    gold_gain  = enemy_data.get("gold", 3000)
    embed = discord.Embed(
        title=f"{boss['emoji']} Raid {raid_level} — {boss['name']}",
        description=(
            f"**Niveau requis** : {level_req}+\n"
            f"**Classe** : {boss['class']}\n"
            f"**Sorts** : *{boss.get('spells', {}).get('s1', {}).get('name', '—')}* & *{boss.get('spells', {}).get('ultimate', {}).get('name', '—')}*\n\n"
            f"**Stats du Boss** :\n{format_enemy_stats(enemy_data)}\n\n"
            f"**Récompenses** : {xp_gain:,} XP & {gold_gain:,} golds par survivant\n\n"
            f"**Joueurs** ({len(participants)}/5) :\n"
            + "\n".join(f"• {p.display_name}" for p in participants)
        ),
        color=0x9C27B0,
    )
    embed.set_footer(text=f"ID Raid : {raid_id} | Max 5 joueurs | Cliquez sur Rejoindre ou Lancer")
    return embed


class RaidLobbyView(discord.ui.View):
    def __init__(self, raid_id: int, boss: dict, enemy_data: dict, leader: discord.User, guild: discord.Guild | None):
        super().__init__(timeout=300)
        self.raid_id    = raid_id
        self.boss       = boss
        self.enemy_data = enemy_data
        self.leader     = leader
        self.guild      = guild

        join_btn = discord.ui.Button(label="Rejoindre", style=discord.ButtonStyle.success, emoji="✅", custom_id=f"rpg:raid:join:{raid_id}")
        join_btn.callback = self._join
        self.add_item(join_btn)

        start_btn = discord.ui.Button(label="Lancer le Raid", style=discord.ButtonStyle.danger, emoji="⚔️", custom_id=f"rpg:raid:start:{raid_id}")
        start_btn.callback = self._start
        self.add_item(start_btn)

        cancel_btn = discord.ui.Button(label="Annuler", style=discord.ButtonStyle.secondary, emoji="❌", custom_id=f"rpg:raid:cancel:{raid_id}")
        cancel_btn.callback = self._cancel
        self.add_item(cancel_btn)

    async def _join(self, interaction: discord.Interaction):
        player = await db.get_or_create_player(interaction.user.id, display_name=interaction.user.display_name)
        if not player.get("class"):
            await interaction.response.send_message("❌ Tu n'as pas encore choisi de classe !", ephemeral=True)
            return
        if player.get("energy", 0) < ENERGY_COST["raid"]:
            await interaction.response.send_message(f"❌ Pas assez d'énergie ! (besoin : {ENERGY_COST['raid']})", ephemeral=True)
            return
        level_req = self.boss.get("level_req", 100)
        if player.get("level", 1) < level_req:
            await interaction.response.send_message(f"❌ Niveau insuffisant ! Ce raid requiert le niveau **{level_req}**.", ephemeral=True)
            return

        raid = await db.get_raid(self.raid_id)
        if not raid or raid["status"] != "waiting":
            await interaction.response.send_message("❌ Ce raid n'est plus disponible.", ephemeral=True)
            return

        success = await db.join_raid(self.raid_id, interaction.user.id)
        if not success:
            await interaction.response.send_message("❌ Le raid est complet (5/5) ou tu es déjà inscrit.", ephemeral=True)
            return

        participants_ids = await db.get_raid_participants(self.raid_id)
        participants = []
        if self.guild:
            for uid in participants_ids:
                member = self.guild.get_member(uid)
                if member:
                    participants.append(member)

        embed = _build_raid_lobby_embed(self.boss, self.enemy_data, participants, self.raid_id)
        await interaction.response.edit_message(embed=embed, view=self)

    async def _start(self, interaction: discord.Interaction):
        if interaction.user.id != self.leader.id:
            await interaction.response.send_message("❌ Seul le chef du raid peut le lancer.", ephemeral=True)
            return
        raid = await db.get_raid(self.raid_id)
        if not raid or raid["status"] != "waiting":
            await interaction.response.send_message("❌ Ce raid n'est plus disponible.", ephemeral=True)
            return

        participants_ids = await db.get_raid_participants(self.raid_id)
        if len(participants_ids) < 1:
            await interaction.response.send_message("❌ Il faut au moins 1 joueur.", ephemeral=True)
            return

        # Vérifier qu'aucun participant n'est déjà en combat
        for uid in participants_ids:
            p = await db.get_player(uid)
            if p and p.get("in_combat", 0):
                member = self.guild.get_member(uid) if self.guild else None
                name = member.display_name if member else str(uid)
                await interaction.response.send_message(
                    f"⚔️ **{name}** est déjà en combat ! Il doit terminer son combat actuel avant de lancer le raid.",
                    ephemeral=True,
                )
                return

        await db.update_raid(self.raid_id, status="active")

        # Déduire l'énergie de chaque participant et verrouiller le combat
        for uid in participants_ids:
            p = await db.get_player(uid)
            if p:
                await db.update_player(uid, energy=max(0, p.get("energy", 0) - ENERGY_COST["raid"]), in_combat=1)

        # Initialiser l'état du raid
        enemy_data = self.enemy_data
        _active_raids[self.raid_id] = {
            "enemy_hp":     enemy_data["hp"],
            "enemy_max_hp": enemy_data["hp"],
            "enemy_data":   enemy_data,
            "turn":         0,
            "order":        list(participants_ids),  # ordre d'attaque défini
            "current_idx":  0,
            "shields":      {},  # user_id → shield_hp
            "finished":     False,
            "logs":         [],
            # Sorts
            "player_classes":         {},          # uid → class str
            "player_resources":       {},          # uid → current resource
            "player_spell_cooldowns": {},          # uid → {spell_key: turns_left}
            "boss_burn_stacks":       0,           # stacks de brûlure sur le boss
            "boss_poison_stacks":     0,           # stacks de poison sur le boss
            "boss_active_debuffs":    [],          # debuffs actifs sur le boss (vitesse, def, etc.)
            "boss_marked":            False,       # marque du Tireur
            "boss_marked_pct":        0,           # bonus dégâts % de la marque
            "boss_marked_turns":      0,           # tours restants de la marque
            "boss_current_stats":     {},          # stats actuelles du boss (après debuffs)
            # Buffs d'équipe
            "team_damage_reduction":  {},          # uid → réduction dégâts temporaire (team_buff)
            "player_spell_state":     {},          # uid → dict of persistent spell state per player
            # Reliques
            "player_relic_effects":   {},          # uid → effets calculés
            # Attaques spéciales boss
            "boss_50pct_triggered":   False,       # rage à 50% HP déjà déclenchée
            # Stacks de statut par joueur (Nyxara poison / Ignareth brûlure)
            "player_poison_stacks":   {},          # uid → stacks de poison reçus
            "player_burn_stacks":     {},          # uid → stacks de brûlure reçus
        }

        # Trier les participants par tankiness décroissante (l'ennemi attaque le + tanky)
        participants_stats = []
        player_relic_effects = {}
        for uid in participants_ids:
            p = await db.get_player(uid)
            eq = await db.get_equipment(uid)
            relics = await db.get_relics(uid)
            if p and p.get("class"):
                eq_equipped = [e for e in eq if e.get("slot_equipped")]
                sb = get_set_bonus(eq_equipped)
                ts = compute_total_stats(p["class"], p["level"], p.get("prestige_level", 0), eq_equipped, sb["stats"])
                # Appliquer bonus titre raid_stats_pct
                title_bonuses = await db.get_title_bonuses(uid)
                raid_bonus_pct = title_bonuses.get("raid_stats_pct", 0)
                pres_bonus_pct = p.get("prestige_level", 0) * title_bonuses.get("prestige_bonus_pct", 0) / 1000
                total_bonus = raid_bonus_pct + pres_bonus_pct
                if total_bonus > 0:
                    ts = {k: int(v * (1 + total_bonus / 100)) if isinstance(v, (int, float)) else v for k, v in ts.items()}
                # Appliquer buffs alimentaires de stats (food_buffs)
                food_raw = p.get("food_buffs")
                if food_raw:
                    try:
                        fb = json.loads(food_raw)
                        _FOOD_STAT_MAP = {
                            "stat_def":   ["p_def", "m_def"],
                            "stat_speed": ["speed"],
                            "stat_patk":  ["p_atk"],
                            "stat_matk":  ["m_atk"],
                        }
                        for buff_key, stat_keys in _FOOD_STAT_MAP.items():
                            buff = fb.get(buff_key)
                            if buff and buff.get("combats", 0) > 0:
                                pct = buff.get("value", 0)
                                for sk in stat_keys:
                                    if sk in ts and isinstance(ts[sk], (int, float)):
                                        ts[sk] = int(ts[sk] * (1 + pct / 100))
                    except Exception:
                        pass
                tank_score = ts.get("p_def", 0) + ts.get("m_def", 0) + ts.get("hp", 0) * 0.1
                participants_stats.append((uid, ts, tank_score))
                player_relic_effects[uid] = compute_relic_effects(relics)
        participants_stats.sort(key=lambda x: x[2], reverse=True)
        _active_raids[self.raid_id]["order"] = [x[0] for x in participants_stats]
        _active_raids[self.raid_id]["player_stats"] = {x[0]: x[1] for x in participants_stats}
        _active_raids[self.raid_id]["player_relic_effects"] = player_relic_effects

        # Initialisation ressources de sorts
        player_classes = {}
        player_resources = {}
        player_spell_cooldowns = {}
        for uid, ts, _ in participants_stats:
            p_tmp = await db.get_player(uid)
            cls = p_tmp.get("class", "") if p_tmp else ""
            player_classes[uid] = cls
            cls_key = _class_to_spell_key(cls) if cls else ""
            init_res = CLASS_SPELLS.get(cls_key, {}).get("resource_per_turn", 0) if cls_key else 0
            player_resources[uid] = init_res
            player_spell_cooldowns[uid] = {}
        _active_raids[self.raid_id]["player_classes"] = player_classes
        _active_raids[self.raid_id]["player_resources"] = player_resources
        _active_raids[self.raid_id]["player_spell_cooldowns"] = player_spell_cooldowns

        _active_raids[self.raid_id]["player_hp"] = {
            uid: min(ts.get("hp", 1), p_data.get("current_hp") or ts.get("hp", 1))
            for uid, ts, _ in participants_stats
            for p_data in [await db.get_player(uid)]
            if p_data
        }
        _active_raids[self.raid_id]["player_max_hp"] = {uid: ts.get("hp", 1) for uid, ts, _ in participants_stats}

        embed = _build_raid_combat_embed(self.raid_id, self.guild)
        view  = RaidCombatView(self.raid_id, self.boss, self.guild)
        await interaction.response.edit_message(embed=embed, view=view)

    async def _cancel(self, interaction: discord.Interaction):
        if interaction.user.id != self.leader.id:
            await interaction.response.send_message("❌ Seul le chef peut annuler le raid.", ephemeral=True)
            return
        await db.update_raid(self.raid_id, status="cancelled")
        await interaction.response.edit_message(
            embed=discord.Embed(title="❌ Raid annulé", color=0xFF4444),
            view=None,
        )


def _build_raid_combat_embed(raid_id: int, guild: discord.Guild | None) -> discord.Embed:
    state = _active_raids.get(raid_id, {})
    enemy_data = state.get("enemy_data", {})
    enemy_hp   = state.get("enemy_hp", 0)
    enemy_max  = state.get("enemy_max_hp", 1)
    turn       = state.get("turn", 0)
    order      = state.get("order", [])
    current_idx= state.get("current_idx", 0)

    embed = discord.Embed(
        title=f"⚔️ Raid — {enemy_data.get('name', '?')} | Tour {turn}",
        color=0x9C27B0,
    )
    enraged = state.get("boss_50pct_triggered", False)
    rage_txt = "  🔴 **ENRAGÉ**" if enraged else ""
    embed.add_field(
        name=f"💀 {enemy_data.get('name', '?')}{rage_txt}",
        value=f"❤️ {hp_bar(enemy_hp, enemy_max, 25)}\n{enemy_hp:,}/{enemy_max:,} HP",
        inline=False,
    )

    # HP de chaque joueur — le boss focus toujours le plus tanky vivant (living[0])
    next_boss_target = next(
        (uid for uid in order if state.get("player_hp", {}).get(uid, 0) > 0),
        None,
    )

    player_lines = []
    for i, uid in enumerate(order):
        p_hp    = state.get("player_hp", {}).get(uid, 0)
        p_max   = state.get("player_max_hp", {}).get(uid, 1)
        is_current = (i == current_idx)
        is_targeted = (uid == next_boss_target)
        member_name = f"<@{uid}>"
        if guild:
            m = guild.get_member(uid)
            if m:
                member_name = m.display_name
        dead = p_hp <= 0
        arrow = " ◄ (ton tour)" if is_current else ""
        target_icon = " 🎯" if is_targeted and not dead else ""
        name_fmt = f"{'**' if is_current else ''}{member_name}{arrow}{'**' if is_current else ''}"
        hp_fmt = f"~~❤️ {p_hp:,}/{p_max:,}~~" if dead else f"❤️ {p_hp:,}/{p_max:,}"
        player_lines.append(f"{name_fmt}{target_icon} — {hp_fmt}")
    embed.add_field(name="👥 Équipe", value="\n".join(player_lines) if player_lines else "*...*", inline=False)

    # Effets sur le boss
    boss_effects = []
    for d in state.get("boss_active_debuffs", []):
        label = d.get("label", d.get("type", "?"))
        boss_effects.append(f"{label} *({d['turns']}t)*")
    if state.get("boss_marked"):
        boss_effects.append(f"🎯 Marqué +{state['boss_marked_pct']}% *({state['boss_marked_turns']}t)*")

    if boss_effects:
        embed.add_field(name="☠️ Effets sur le boss", value="\n".join(boss_effects)[:512], inline=False)

    # Effets sur le joueur actif
    current_uid = order[current_idx] if order and current_idx < len(order) else None
    if current_uid:
        pss = state.get("player_spell_state", {}).get(current_uid, {})
        player_effects = []
        for b in pss.get("spell_active_buffs", []):
            label = b.get("label", b.get("type", "?"))
            player_effects.append(f"{label} *({b['turns']}t)*")
        if pss.get("undying_turns", 0) > 0:
            player_effects.append(f"🛡️ Indestructible *({pss['undying_turns']}t)*")
        if pss.get("extra_lifesteal", 0) > 0 and pss.get("extra_lifesteal_turns", 0) > 0:
            player_effects.append(f"🩸 Vol de vie +{pss['extra_lifesteal']*100:.0f}% *({pss['extra_lifesteal_turns']}t)*")
        if pss.get("spell_no_heal_turns", 0) > 0:
            player_effects.append(f"🦇 Sans soin *({pss['spell_no_heal_turns']}t)*")
        if pss.get("spell_dodge_next", False):
            player_effects.append("💨 Esquive prête")

        if player_effects:
            current_name = f"<@{current_uid}>"
            if guild:
                m = guild.get_member(current_uid)
                if m:
                    current_name = m.display_name
            embed.add_field(name=f"⚡ Effets — {current_name}", value="\n".join(player_effects)[:512], inline=False)

    if state.get("logs"):
        embed.add_field(name="📜 Log", value="\n".join(state["logs"][-5:])[:800], inline=False)

    return embed


def _make_temp_combat_state(uid: int, raid_state: dict) -> CombatState:
    """Construit un CombatState minimal pour appliquer un sort dans le contexte du raid."""
    player_stats_dict = raid_state["player_stats"].get(uid, {})
    enemy_data        = raid_state["enemy_data"]

    ps = CombatStats(
        hp          = raid_state["player_hp"].get(uid, 1),
        max_hp      = raid_state["player_max_hp"].get(uid, 1),
        p_atk       = player_stats_dict.get("p_atk", 0),
        m_atk       = player_stats_dict.get("m_atk", 0),
        p_pen       = player_stats_dict.get("p_pen", 0),
        m_pen       = player_stats_dict.get("m_pen", 0),
        p_def       = player_stats_dict.get("p_def", 0),
        m_def       = player_stats_dict.get("m_def", 0),
        speed       = max(1, player_stats_dict.get("speed", 1)),
        crit_chance = player_stats_dict.get("crit_chance", 5.0),
        crit_damage = player_stats_dict.get("crit_damage", 150.0),
        shield      = raid_state.get("shields", {}).get(uid, 0),
    )
    _bs = raid_state.get("boss_current_stats", {})
    es = CombatStats(
        hp          = raid_state["enemy_hp"],
        max_hp      = raid_state["enemy_max_hp"],
        p_atk       = _bs.get("p_atk", enemy_data.get("p_atk", 0)),
        m_atk       = _bs.get("m_atk", enemy_data.get("m_atk", 0)),
        p_def       = _bs.get("p_def", enemy_data.get("p_def", 0)),
        m_def       = _bs.get("m_def", enemy_data.get("m_def", 0)),
        p_pen       = enemy_data.get("p_pen", 0),
        m_pen       = enemy_data.get("m_pen", 0),
        speed       = max(1, _bs.get("speed", enemy_data.get("speed", 80))),
        crit_chance = enemy_data.get("crit_chance", 5.0),
        crit_damage = enemy_data.get("crit_damage", 150.0),
    )
    cls = raid_state.get("player_classes", {}).get(uid, "")
    state = CombatState(
        player_stats  = ps,
        enemy_stats   = es,
        player_class  = cls,
        enemy_data    = enemy_data,
        player_resource = raid_state.get("player_resources", {}).get(uid, 0),
        enemy_burns     = raid_state.get("boss_burn_stacks", 0),
        enemy_poison_stacks = raid_state.get("boss_poison_stacks", 0),
        relic_effects   = dict(raid_state.get("player_relic_effects", {}).get(uid, {})),
    )
    state.player_burn_stacks   = raid_state.get("player_burn_stacks", {}).get(uid, 0)
    state.spell_cooldowns      = dict(raid_state.get("player_spell_cooldowns", {}).get(uid, {}))
    state.turn                 = raid_state["turn"]
    state.spell_active_debuffs = list(raid_state.get("boss_active_debuffs", []))
    state.enemy_marked         = raid_state.get("boss_marked", False)
    state.enemy_marked_pct     = raid_state.get("boss_marked_pct", 0)
    state.enemy_marked_turns   = raid_state.get("boss_marked_turns", 0)
    pss = raid_state.get("player_spell_state", {}).get(uid, {})
    state.spell_active_buffs       = list(pss.get("spell_active_buffs", []))
    state.undying_turns            = pss.get("undying_turns", 0)
    state.extra_lifesteal          = pss.get("extra_lifesteal", 0.0)
    state.extra_lifesteal_turns    = pss.get("extra_lifesteal_turns", 0)
    state.spell_no_heal_turns      = pss.get("spell_no_heal_turns", 0)
    state.spell_damage_reduction   = pss.get("spell_damage_reduction", 0.0)
    state.spell_damage_amp         = pss.get("spell_damage_amp", 1.0)
    state.spell_dodge_next         = pss.get("spell_dodge_next", False)
    state.spell_dot_amp            = pss.get("spell_dot_amp", 1.0)
    state.paladin_ramp_dmg_red     = pss.get("paladin_ramp_dmg_red", 0.0)
    state.paladin_ramp_dmg_amp     = pss.get("paladin_ramp_dmg_amp", 0.0)
    return state


def _sync_from_temp_state(uid: int, raid_state: dict, temp: CombatState):
    """Reporte les changements du CombatState temporaire vers le raid_state."""
    raid_state["enemy_hp"]               = max(0, temp.enemy_stats.hp)
    raid_state["player_hp"][uid]         = max(0, temp.player_stats.hp)
    raid_state["shields"][uid]           = temp.player_stats.shield
    raid_state["boss_burn_stacks"]                    = temp.enemy_burns
    raid_state["boss_poison_stacks"]                  = temp.enemy_poison_stacks
    raid_state.setdefault("player_burn_stacks", {})[uid]   = temp.player_burn_stacks
    raid_state["player_resources"][uid]       = temp.player_resource
    raid_state["player_spell_cooldowns"][uid] = dict(temp.spell_cooldowns)
    raid_state["boss_active_debuffs"]         = list(temp.spell_active_debuffs)
    raid_state["boss_marked"]                 = temp.enemy_marked
    raid_state["boss_marked_pct"]             = temp.enemy_marked_pct
    raid_state["boss_marked_turns"]           = temp.enemy_marked_turns
    raid_state["boss_current_stats"]          = {
        "p_atk": temp.enemy_stats.p_atk,
        "m_atk": temp.enemy_stats.m_atk,
        "p_def": temp.enemy_stats.p_def,
        "m_def": temp.enemy_stats.m_def,
        "speed": temp.enemy_stats.speed,
    }
    if "player_spell_state" not in raid_state:
        raid_state["player_spell_state"] = {}
    raid_state["player_spell_state"][uid] = {
        "spell_active_buffs":     list(temp.spell_active_buffs),
        "undying_turns":          temp.undying_turns,
        "extra_lifesteal":        temp.extra_lifesteal,
        "extra_lifesteal_turns":  temp.extra_lifesteal_turns,
        "spell_no_heal_turns":    temp.spell_no_heal_turns,
        "spell_damage_reduction": temp.spell_damage_reduction,
        "spell_damage_amp":       temp.spell_damage_amp,
        "spell_dodge_next":       temp.spell_dodge_next,
        "spell_dot_amp":          temp.spell_dot_amp,
        "paladin_ramp_dmg_red":   temp.paladin_ramp_dmg_red,
        "paladin_ramp_dmg_amp":   temp.paladin_ramp_dmg_amp,
    }


class RaidCombatView(discord.ui.View):
    def __init__(self, raid_id: int, boss: dict, guild: discord.Guild | None):
        super().__init__(timeout=600)
        self.raid_id = raid_id
        self.boss    = boss
        self.guild   = guild
        self._build_buttons()

    async def on_timeout(self):
        state = _active_raids.pop(self.raid_id, None)
        if state:
            for uid in state.get("order", []):
                await db.update_player(uid, in_combat=0)
            await db.update_raid(self.raid_id, status="finished")

    def _build_buttons(self):
        """Reconstruit les boutons selon le joueur actif."""
        self.clear_items()

        # Bouton attaque de base
        atk_btn = discord.ui.Button(label="Attaquer", style=discord.ButtonStyle.danger, emoji="⚔️", row=0)
        atk_btn.callback = self._make_action_cb(None)
        self.add_item(atk_btn)

        # Sorts du joueur actif
        state = _active_raids.get(self.raid_id, {})
        order = state.get("order", [])
        idx   = state.get("current_idx", 0)
        if order and idx < len(order):
            uid = order[idx]
            cls = state.get("player_classes", {}).get(uid, "")
            if cls:
                # Construire un état léger pour get_spell_buttons_data
                temp = _make_temp_combat_state(uid, state)
                # Tick ressource pour afficher les valeurs à-jour
                tick_spell_effects(temp)
                for bdata in get_spell_buttons_data(cls, temp):
                    style = discord.ButtonStyle.red if bdata["is_ultimate"] else discord.ButtonStyle.blurple
                    btn = discord.ui.Button(
                        label=bdata["label"],
                        emoji=bdata["emoji"],
                        style=style,
                        disabled=bdata["disabled"],
                        row=1,
                    )
                    btn.callback = self._make_action_cb(bdata["key"])
                    self.add_item(btn)

    def _make_action_cb(self, spell_key: str | None):
        async def callback(interaction: discord.Interaction):
            await self._do_action(interaction, spell_key)
        return callback

    async def _do_action(self, interaction: discord.Interaction, spell_key: str | None):
        import math
        import random as _random

        state = _active_raids.get(self.raid_id)
        if not state or state.get("finished"):
            await interaction.response.send_message("❌ Ce raid est terminé.", ephemeral=True)
            return

        order       = state["order"]
        current_idx = state["current_idx"]
        current_uid = order[current_idx] if order else None

        if interaction.user.id != current_uid:
            await interaction.response.send_message("❌ Ce n'est pas ton tour !", ephemeral=True)
            return

        player = await db.get_player(interaction.user.id)
        if not player:
            await interaction.response.send_message("❌ Profil introuvable.", ephemeral=True)
            return

        uid          = interaction.user.id
        player_stats = state["player_stats"].get(uid, {})
        logs         = []

        # Construire état temporaire pour les sorts
        temp = _make_temp_combat_state(uid, state)

        # Tick (regen ressource + cooldowns)
        tick_spell_effects(temp)

        # DoTs sur le boss (tick à chaque tour d'un joueur)
        if state.get("boss_burn_stacks", 0) > 0:
            burn_dmg = int(player_stats.get("m_atk", 0) * 0.15 * state["boss_burn_stacks"])
            state["enemy_hp"] = max(0, state["enemy_hp"] - burn_dmg)
            temp.enemy_stats.hp = state["enemy_hp"]
            logs.append(f"🔥 Brûlure ({state['boss_burn_stacks']} stacks) : **-{burn_dmg:,}** HP boss")
        if state.get("boss_poison_stacks", 0) > 0:
            poison_dmg = int(player_stats.get("m_atk", 0) * 0.12 * state["boss_poison_stacks"])
            state["enemy_hp"] = max(0, state["enemy_hp"] - poison_dmg)
            temp.enemy_stats.hp = state["enemy_hp"]
            logs.append(f"☠️ Poison ({state['boss_poison_stacks']} stacks) : **-{poison_dmg:,}** HP boss")

        # Action du joueur : sort ou attaque de base
        original_spell_key = spell_key  # garder pour vérification team_buff
        if spell_key:
            result = apply_spell(temp, spell_key)
            logs.extend(result["log"])
            if not result["success"]:
                # Sort raté → attaque de base
                spell_key = None
                original_spell_key = None

        # Buff d'équipe (Guerrier S1 / Support S3 / Paladin S3)
        if original_spell_key and spell_key:
            cls_key_caster = _class_to_spell_key(state.get("player_classes", {}).get(uid, ""))
            if cls_key_caster:
                spell_effects = CLASS_SPELLS.get(cls_key_caster, {}).get(original_spell_key, {}).get("effects", {})
                if spell_effects.get("team_buff"):
                    living_members = [u for u in order if state["player_hp"].get(u, 0) > 0]
                    n_players = len(living_members)
                    efficiency = max(0.60, 1.0 - (n_players - 1) * 0.10)
                    spell_name = CLASS_SPELLS.get(cls_key_caster, {}).get(original_spell_key, {}).get("name", "Sort")
                    team_stat_logged = False
                    team_dr_logged = False
                    # Appliquer buff à chaque joueur vivant (sauf le lanceur qui l'a déjà reçu)
                    for team_uid in living_members:
                        if team_uid == uid:
                            continue  # le lanceur a déjà reçu le buff via apply_spell
                        # Buff stat (Guerrier S1)
                        if "stat_buff" in spell_effects:
                            for stat, pct in spell_effects["stat_buff"].items():
                                if stat == "dmg_pct":
                                    continue  # pas applicable en raid team
                                reduced_pct = int(pct * efficiency)
                                team_stats = state["player_stats"].get(team_uid, {})
                                current_val = team_stats.get(stat, 0)
                                if current_val > 0:
                                    new_val = max(1, int(current_val * (1 + reduced_pct / 100)))
                                    state["player_stats"][team_uid] = dict(team_stats)
                                    state["player_stats"][team_uid][stat] = new_val
                            if not team_stat_logged:
                                stat_names = ", ".join(f"{s} +{int(p * efficiency)}%" for s, p in spell_effects["stat_buff"].items() if s != "dmg_pct")
                                if stat_names:
                                    logs.append(f"✨ {spell_name} boost toute l'équipe ! ({stat_names} chacun, eff. {int(efficiency*100)}%)")
                                    team_stat_logged = True
                        # Réduction dégâts (Support S3, Paladin S3)
                        if "damage_reduction" in spell_effects:
                            reduced_dr = spell_effects["damage_reduction"] * efficiency
                            state.setdefault("team_damage_reduction", {})[team_uid] = max(
                                state.get("team_damage_reduction", {}).get(team_uid, 0.0),
                                reduced_dr,
                            )
                            if not team_dr_logged:
                                logs.append(f"🛡️ {spell_name} protège toute l'équipe ! (-{int(reduced_dr*100)}% dégâts chacun, eff. {int(efficiency*100)}%)")
                                team_dr_logged = True

        # Regen HP relique (début du tour du joueur actif)
        regen_hp_pct = temp.relic_effects.get("regen_hp", 0)
        if regen_hp_pct > 0 and temp.player_stats.hp > 0:
            regen_amt = int(temp.player_stats.max_hp * regen_hp_pct / 100)
            if regen_amt > 0:
                temp.player_stats.hp = min(temp.player_stats.max_hp, temp.player_stats.hp + regen_amt)
                logs.append(f"💚 Régénération Relique : +{regen_amt:,} HP")

        if not spell_key:
            ps = temp.player_stats
            es = temp.enemy_stats
            speed_p     = max(1, ps.speed)
            enemy_speed = max(1, es.speed)
            ref         = min(speed_p, enemy_speed)
            turn_c      = state["turn"] + 1
            attacks     = max(1, math.floor(turn_c * speed_p / ref) - math.floor((turn_c - 1) * speed_p / ref))

            total_damage = 0
            for _ in range(attacks):
                if es.hp <= 0:
                    break
                phys, magic = calc_physical_damage(ps, es), calc_magical_damage(ps, es)
                phys, magic, passive_logs = apply_player_passive(temp, phys, magic)
                logs.extend(passive_logs)
                if "bonus_dmg" in temp.relic_effects:
                    mult_r = 1 + temp.relic_effects["bonus_dmg"] / 100
                    phys  = int(phys  * mult_r)
                    magic = int(magic * mult_r)
                if temp.spell_damage_amp != 1.0:
                    phys  = int(phys  * temp.spell_damage_amp)
                    magic = int(magic * temp.spell_damage_amp)
                combined = phys + magic
                combined, is_crit = apply_crit(combined, ps.crit_chance, ps.crit_damage)
                if temp.enemy_marked and temp.enemy_marked_pct > 0:
                    combined = int(combined * (1 + temp.enemy_marked_pct / 100))
                dmg_done = apply_damage_to_target(es, combined)
                total_damage += dmg_done
                crit_txt = " ✨CRITIQUE!" if is_crit else ""
                logs.append(f"<@{uid}> inflige **{combined:,}** dégâts{crit_txt}")

            # Double frappe relique
            double_frappe_pct = temp.relic_effects.get("double_frappe", 0)
            if double_frappe_pct > 0 and es.hp > 0 and _random.random() < double_frappe_pct / 100:
                phys, magic = calc_physical_damage(ps, es), calc_magical_damage(ps, es)
                phys, magic, _ = apply_player_passive(temp, phys, magic)
                if "bonus_dmg" in temp.relic_effects:
                    mult_r = 1 + temp.relic_effects["bonus_dmg"] / 100
                    phys  = int(phys  * mult_r)
                    magic = int(magic * mult_r)
                combined_df = phys + magic
                combined_df, is_crit_df = apply_crit(combined_df, ps.crit_chance, ps.crit_damage)
                dmg_df = apply_damage_to_target(es, combined_df)
                total_damage += dmg_df
                crit_txt_df = " ✨CRITIQUE!" if is_crit_df else ""
                logs.append(f"⚡ Double Frappe (relique) : **{combined_df:,}** dégâts{crit_txt_df}")

            # Post-attaque : vol de vie classe + relique
            logs.extend(apply_player_post_attack(temp, total_damage))

        # Reporter les changements du sort/attaque
        _sync_from_temp_state(uid, state, temp)

        # Tour de l'ennemi — focus permanent sur le joueur le plus tanky vivant
        enemy_data = state["enemy_data"]
        living = [u for u in order if state["player_hp"].get(u, 0) > 0]
        if living and state["enemy_hp"] > 0:
            target_uid = living[0]  # order trié par tankiness desc à l'init
            t_stats    = state["player_stats"].get(target_uid, {})
            # Stats ennemi actuelles (après debuffs éventuels)
            _bs        = state.get("boss_current_stats", {})
            e_patk     = max(1, _bs.get("p_atk", enemy_data.get("p_atk", 0)) - t_stats.get("p_def", 0))
            e_matk     = max(0, _bs.get("m_atk", enemy_data.get("m_atk", 0)) - t_stats.get("m_def", 0))
            e_dmg      = max(1, e_patk + e_matk)
            if _random.random() < enemy_data.get("crit_chance", 5) / 100:
                e_dmg = int(e_dmg * enemy_data.get("crit_damage", 150) / 100)
            # Réduction dégâts relique du joueur ciblé
            target_relics = state.get("player_relic_effects", {}).get(target_uid, {})
            if "reduction_dmg" in target_relics:
                e_dmg = int(e_dmg * (1 - target_relics["reduction_dmg"] / 100))
            # Réduction dégâts d'équipe (Support S3 / Paladin S3 team_buff)
            team_dr = state.get("team_damage_reduction", {}).get(target_uid, 0.0)
            if team_dr > 0:
                e_dmg = int(e_dmg * (1 - team_dr))
                state.setdefault("team_damage_reduction", {})[target_uid] = 0.0
            # Bouclier
            shield = state.get("shields", {}).get(target_uid, 0)
            if shield > 0:
                absorbed = min(shield, e_dmg)
                e_dmg   -= absorbed
                state["shields"][target_uid] = shield - absorbed
            state["player_hp"][target_uid] = max(0, state["player_hp"][target_uid] - e_dmg)
            # Renvoi relique
            if "reflet" in target_relics and e_dmg > 0:
                reflect_dmg = int(e_dmg * target_relics["reflet"] / 100)
                state["enemy_hp"] = max(0, state["enemy_hp"] - reflect_dmg)
                if reflect_dmg > 0:
                    logs.append(f"🪞 Renvoi : **-{reflect_dmg:,}** HP boss")
            t_name = f"<@{target_uid}>"
            if self.guild:
                m = self.guild.get_member(target_uid)
                if m:
                    t_name = m.display_name
            logs.append(f"💢 L'ennemi attaque **{t_name}** pour **{e_dmg:,}** dégâts")

        # ── Attaques spéciales boss ─────────────────────────────────────────
        living_after = [u for u in order if state["player_hp"].get(u, 0) > 0]
        _bs_sp = state.get("boss_current_stats", {})
        raid_level = enemy_data.get("raid_level", 1)

        def _zone_dmg_for(zu: int, base_pct: float) -> int:
            zt = state["player_stats"].get(zu, {})
            raw = max(1, int((
                max(0, _bs_sp.get("p_atk", enemy_data.get("p_atk", 0)) - zt.get("p_def", 0)) +
                max(0, _bs_sp.get("m_atk", enemy_data.get("m_atk", 0)) - zt.get("m_def", 0))
            ) * base_pct))
            zr = state.get("player_relic_effects", {}).get(zu, {})
            if "reduction_dmg" in zr:
                raw = int(raw * (1 - zr["reduction_dmg"] / 100))
            tdr = state.get("team_damage_reduction", {}).get(zu, 0.0)
            if tdr > 0:
                raw = int(raw * (1 - tdr))
            sh = state.get("shields", {}).get(zu, 0)
            if sh > 0:
                ab = min(sh, raw)
                raw -= ab
                state["shields"][zu] = sh - ab
            return max(0, raw)

        def _member_name(zu: int) -> str:
            name = f"<@{zu}>"
            if self.guild:
                m_z = self.guild.get_member(zu)
                if m_z:
                    name = m_z.display_name
            return name

        # === Rage à 50% HP (une seule fois, ne peut pas tuer) ===
        rage_fired = False
        if (state["enemy_hp"] > 0
                and not state.get("boss_50pct_triggered", False)
                and state["enemy_hp"] <= state["enemy_max_hp"] * 0.5
                and living_after):
            state["boss_50pct_triggered"] = True
            rage_fired = True
            logs.append(f"🔴 **DÉCHAÎNEMENT !** {enemy_data.get('name', '?')} est à 50% — il frappe toute l'équipe !")
            for ru in living_after:
                rdmg = _zone_dmg_for(ru, 0.75)
                # survie garantie : ne peut pas tuer
                cur = state["player_hp"].get(ru, 1)
                rdmg = min(rdmg, max(0, cur - 1))
                state["player_hp"][ru] = max(1, cur - rdmg)
                logs.append(f"  ⚡ **{_member_name(ru)}** : -{rdmg:,} HP *(survie garantie)*")

        # === Attaque de zone (tous les 3 tours, tous les 2 si raid 9-10) ===
        zone_interval = 2 if raid_level >= 9 else 3
        next_turn = state["turn"] + 1   # valeur après incrément
        if (state["enemy_hp"] > 0
                and next_turn % zone_interval == 0
                and not rage_fired              # pas cumulé avec la rage
                and living_after):
            logs.append(f"🌀 **Attaque de Zone** — {enemy_data.get('name', '?')} frappe toute l'équipe !")
            for zu in living_after:
                zdmg = _zone_dmg_for(zu, 0.45)
                state["player_hp"][zu] = max(0, state["player_hp"][zu] - zdmg)
                logs.append(f"  💥 **{_member_name(zu)}** : -{zdmg:,} HP")

        # === Nyxara (raid 8) — Nuage Toxique AoE : poison sur tous les joueurs tous les 4 tours ===
        if (raid_level == 8 and state["enemy_hp"] > 0
                and not rage_fired and next_turn % 4 == 0 and living_after):
            logs.append("☠️ **Nuage Toxique** — Nyxara empoisonne toute l'équipe !")
            pstacks = state.setdefault("player_poison_stacks", {})
            for pu in living_after:
                pstacks[pu] = min(4, pstacks.get(pu, 0) + 1)
                logs.append(f"  🐍 **{_member_name(pu)}** : {pstacks[pu]} stack(s) de poison")

        # === Ignareth (raid 9) — Brasier Collectif AoE : brûlure sur tous les joueurs tous les 5 tours ===
        if (raid_level == 9 and state["enemy_hp"] > 0
                and not rage_fired and next_turn % 5 == 0 and living_after):
            logs.append("🔥 **Brasier Collectif** — Ignareth embrase toute l'équipe !")
            bstacks = state.setdefault("player_burn_stacks", {})
            for bu in living_after:
                bstacks[bu] = min(4, bstacks.get(bu, 0) + 1)
                logs.append(f"  🌋 **{_member_name(bu)}** : {bstacks[bu]} stack(s) de brûlure")

        # === Tick DoT par joueur (poison Nyxara / brûlure Ignareth) ===
        if state["enemy_hp"] > 0 and living_after:
            pstacks = state.get("player_poison_stacks", {})
            bstacks = state.get("player_burn_stacks", {})
            for tu in living_after:
                ps_count = pstacks.get(tu, 0)
                bs_count = bstacks.get(tu, 0)
                max_hp_t = state.get("player_max_hp", {}).get(tu, 1)
                if ps_count > 0:
                    pdmg = int(max_hp_t * 0.02 * ps_count)
                    state["player_hp"][tu] = max(0, state["player_hp"][tu] - pdmg)
                    logs.append(f"  ☠️ Poison ({ps_count} stacks) **{_member_name(tu)}** : -{pdmg:,} HP")
                if bs_count > 0:
                    bdmg = int(max_hp_t * 0.02 * bs_count)
                    state["player_hp"][tu] = max(0, state["player_hp"][tu] - bdmg)
                    logs.append(f"  🔥 Brûlure ({bs_count} stacks) **{_member_name(tu)}** : -{bdmg:,} HP")
                    # Décrémentation brûlure : -1 stack par tour de boss
                    bstacks[tu] = max(0, bs_count - 1)

        state["turn"] += 1
        state["current_idx"] = (current_idx + 1) % len(order)
        for _ in range(len(order)):
            nxt = state["current_idx"]
            if state["player_hp"].get(order[nxt], 0) > 0:
                break
            state["current_idx"] = (nxt + 1) % len(order)

        state["logs"] = (state.get("logs", []) + logs)[-20:]

        all_dead  = all(state["player_hp"].get(u, 0) <= 0 for u in order)
        boss_dead = state["enemy_hp"] <= 0

        if boss_dead or all_dead:
            state["finished"] = True
            if boss_dead:
                desc       = f"✅ **Le boss {enemy_data.get('name', '?')} est vaincu !** en **{state['turn']}** tours !"
                raid_level = enemy_data.get("raid_level", 1)
                zone_equiv = raid_level * 1000
                xp_gain    = zone_equiv * 150
                gold_gain  = zone_equiv * 50
                drop_source = RAID_DROP_SOURCE.get(raid_level, "donjon_classique")
                for u in order:
                    p = await db.get_player(u)
                    if p:
                        eq_drops = get_equipment_drops(zone_equiv, p["class"], "raid",
                                                       drop_source=drop_source)
                        for eq_drop in eq_drops:
                            await db.add_equipment(u, eq_drop["item_id"], eq_drop["rarity"], 0,
                                                   eq_drop.get("level", 1000))
                        new_xp   = p["xp"] + xp_gain
                        new_level, new_xp = level_up(p["level"], new_xp)
                        await db.update_player(u, gold=p["gold"] + gold_gain, xp=new_xp, level=new_level)
                        # Bonus énergie par victoire (food buff energy_on_win)
                        from datetime import datetime as _dt, timezone as _tz
                        food_raw = p.get("food_buffs")
                        if food_raw:
                            try:
                                fb = json.loads(food_raw)
                                eow = fb.get("energy_on_win")
                                if eow:
                                    exp = eow.get("expires")
                                    if exp and _dt.now(_tz.utc) < _dt.fromisoformat(exp):
                                        win_e = eow.get("value", 0)
                                        p_latest = await db.get_player(u)
                                        cur_e = p_latest.get("energy", 0)
                                        max_e = p_latest.get("max_energy", 2000)
                                        await db.update_player(u, energy=min(cur_e + win_e, max_e))
                            except Exception:
                                pass
                        # Consommer les buffs alimentaires de stats après le raid
                        await _consume_raid_food_buffs(u)
                        await increment_and_check_title(u, "t_raider")
                        await increment_and_check_title(u, "t_héros_raid")
                        await increment_and_check_title(u, "t_legende_raid")
                        await db.update_raid_max(u, raid_level)
                color = 0x00FF88
            else:
                desc  = "❌ **L'équipe a été vaincue !**"
                color = 0xFF4444

            del _active_raids[self.raid_id]
            await db.update_raid(self.raid_id, status="finished")
            for u in order:
                await db.update_player(u, in_combat=0)
            embed = discord.Embed(title=f"⚔️ Raid terminé — {enemy_data.get('name', '?')}", description=desc, color=color)
            log_txt = "\n".join(state["logs"][-8:])[:1000]
            if log_txt:
                embed.add_field(name="📜 Fin du combat", value=log_txt, inline=False)
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            self._build_buttons()
            embed = _build_raid_combat_embed(self.raid_id, self.guild)
            await interaction.response.edit_message(embed=embed, view=self)


def build_hub_message(bot: commands.Bot) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="👥 Hub Raids",
        description=(
            "Les raids sont des combats d'**équipe jusqu'à 5 joueurs** contre des boss extrêmement puissants !\n\n"
            "**Fonctionnement :**\n"
            f"• Coût : **{ENERGY_COST['raid']} énergies** par joueur\n"
            "• Le boss cible **en priorité le joueur le plus résistant** (meilleure défense)\n"
            "• Les joueurs attaquent à tour de rôle selon leur **vitesse**\n"
            "• Chaque joueur dispose d'un **timer** pour attaquer (sinon son tour est sauté)\n\n"
            "**Récompenses :**\n"
            "• XP & Gold progressifs selon le niveau du raid\n"
            "• Équipements de qualité croissante (classique → raid)\n\n"
            "**10 niveaux de raid**, du niveau 100 (Raid 1) au niveau 1000 (Raid 10) !\n"
            "Chaque raid est conçu pour **5 joueurs avec équipements épiques** du niveau correspondant."
        ),
        color=0x9C27B0,
    )
    view = RaidsHubView(bot)
    return embed, view


async def setup(bot: commands.Bot):
    pass
