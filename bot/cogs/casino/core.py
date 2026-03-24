import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import time
import asyncio
import random
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════
WELCOME_CHANNEL_ID   = 1475325945001807952
ROULETTE_CHANNEL_ID  = 1480224572275032135
BLACKJACK_CHANNEL_ID = 1480224707575021769
POKER_CHANNEL_ID     = 1480224841830236331
CASINO_FILE          = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "casino.json")

ROULETTE_RED   = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
ROULETTE_BLACK = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
ROULETTE_COLORS = {0: "🟢", **{n: "🔴" for n in ROULETTE_RED}, **{n: "⚫" for n in ROULETTE_BLACK}}

PANEL_CHANNEL_MAP = {
    "welcome":             WELCOME_CHANNEL_ID,
    "leaderboard":         WELCOME_CHANNEL_ID,
    "roulette":            ROULETTE_CHANNEL_ID,
    "blackjack":           BLACKJACK_CHANNEL_ID,
    "poker_débutant":      POKER_CHANNEL_ID,
    "poker_intermédiaire": POKER_CHANNEL_ID,
    "poker_expert":        POKER_CHANNEL_ID,
    "poker_des légendes":  POKER_CHANNEL_ID,
}

# ── GANG RANKS DEFINITIONS ────────────────────────────────
GANG_RANKS = {
    "roulette": {
        1000:      {"label": "Mule",              "emoji": "🐴", "bonus": 500},
        10000:     {"label": "Dealer",            "emoji": "📦", "bonus": 500},
        100000:    {"label": "Distributor",       "emoji": "🚛", "bonus": 500},
        1000000:   {"label": "Lieutenant",        "emoji": "⚓", "bonus": 500},
        10000000:  {"label": "El Jefe",           "emoji": "🔥", "bonus": 500},
        100000000: {"label": "El Patron",         "emoji": "👑", "bonus": 500},
    },
    "blackjack": {
        1000:      {"label": "Nobody",            "emoji": "👤", "bonus": 500},
        10000:     {"label": "Associate",         "emoji": "🤝", "bonus": 500},
        100000:    {"label": "Soldato",           "emoji": "🔫", "bonus": 500},
        1000000:   {"label": "Capo",              "emoji": "👔", "bonus": 500},
        10000000:  {"label": "Consigliere",       "emoji": "⚖️", "bonus": 500},
        100000000: {"label": "Don",               "emoji": "🍷", "bonus": 500},
    },
    "total_bet": {
        1000:      {"label": "Pickpocket",        "emoji": "🕵️", "bonus": 500},
        10000:     {"label": "Escroc",            "emoji": "🎭", "bonus": 500},
        100000:    {"label": "Scammeur",          "emoji": "💻", "bonus": 500},
        1000000:   {"label": "Cerveau",           "emoji": "🧠", "bonus": 500},
        10000000:  {"label": "Chef",              "emoji": "👨‍🍳", "bonus": 500},
        100000000: {"label": "Caïd",              "emoji": "⛓️", "bonus": 500},
    },
    "holdings": {
        1000:      {"label": "Apprenti",          "emoji": "📖", "bonus": 500},
        10000:     {"label": "Livreur",           "emoji": "🎒", "bonus": 500},
        100000:    {"label": "Contrebandier",     "emoji": "🧥", "bonus": 500},
        1000000:   {"label": "Marchand d'armes",  "emoji": "🚀", "bonus": 500},
        10000000:  {"label": "Maître de l'arsenal","emoji": "🛡️", "bonus": 500},
        100000000: {"label": "Seigneur de guerre","emoji": "⚔️", "bonus": 500},
    }
}

MAFIA_NPCS = [
    {"name": "Pablo Escobar", "balance": 100000000, "rank": "El Patron", "emoji": "👑"},
    {"name": "El Chapo",      "balance": 10000000,  "rank": "El Jefe",   "emoji": "🔥"},
    {"name": "Al Capone",     "balance": 5000000,   "rank": "Don",       "emoji": "🍷"},
    {"name": "Frank Lucas",   "balance": 1000000,   "rank": "Cerveau",   "emoji": "🧠"},
    {"name": "John Gotti",    "balance": 500000,    "rank": "Capo",      "emoji": "👔"},
]

# ═══════════════════════════════════════════════════════════
#  PERSISTENCE HELPERS
# ═══════════════════════════════════════════════════════════
def load_casino() -> dict:
    if not os.path.exists(CASINO_FILE):
        os.makedirs(os.path.dirname(CASINO_FILE), exist_ok=True)
        return {"players": {}, "messages": {}, "roulette_history": []}
    
    try:
        with open(CASINO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {"players": {}, "messages": {}, "roulette_history": []}
        save_casino(data)
        
    if "players" not in data: data["players"] = {}
    if "messages" not in data: data["messages"] = {}
    if "roulette_history" not in data: data["roulette_history"] = []
    
    for uid in data["players"]:
        p = data["players"][uid]
        if "total_wagered_roulette" not in p:  p["total_wagered_roulette"] = 0
        if "total_wagered_blackjack" not in p: p["total_wagered_blackjack"] = 0
        if "freebets" not in p: p["freebets"] = 0
        if "selected_title" not in p: p["selected_title"] = "Petit Joueur"
        if "currency" not in p: p["currency"] = "Freebets"
        if "max_balance" not in p: p["max_balance"] = p.get("balance", 0)
    return data

def save_casino(data: dict):
    os.makedirs(os.path.dirname(CASINO_FILE), exist_ok=True)
    with open(CASINO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_balance(user_id) -> int:
    data = load_casino()
    return data["players"].get(str(user_id), {}).get("balance", 0)

def add_balance(user_id, amount: int, username: str = None):
    data = load_casino()
    uid  = str(user_id)
    if uid not in data["players"]:
        data["players"][uid] = {"balance": 0, "freebets": 0, "total_wagered_roulette": 0, "total_wagered_blackjack": 0}
    if username:
        data["players"][uid]["username"] = username
    data["players"][uid]["balance"] += amount
    if data["players"][uid]["balance"] > data["players"][uid].get("max_balance", 0):
        data["players"][uid]["max_balance"] = data["players"][uid]["balance"]
    save_casino(data)

def add_wager(user_id, amount: int, game_type: str, username: str = None):
    data = load_casino()
    uid  = str(user_id)
    if uid not in data["players"]:
        data["players"][uid] = {"balance": 0, "freebets": 0, "total_wagered_roulette": 0, "total_wagered_blackjack": 0}
    if username:
        data["players"][uid]["username"] = username
    if game_type == "roulette":
        data["players"][uid]["total_wagered_roulette"] += amount
    elif game_type == "blackjack":
        data["players"][uid]["total_wagered_blackjack"] += amount
    save_casino(data)

def get_player_stats(user_id, data: dict) -> dict:
    uid = str(user_id)
    p = data.get("players", {}).get(uid, {})
    wag_r = p.get("total_wagered_roulette", 0)
    wag_b = p.get("total_wagered_blackjack", 0)
    total_wag = wag_r + wag_b
    balance = p.get("balance", 0)
    
    unlocked_titles = []
    category_progress = {}
    tier_counts = [0] * 6
    
    for cat, ranks in GANG_RANKS.items():
        if cat == "roulette": val = wag_r
        elif cat == "blackjack": val = wag_b
        elif cat == "total_bet": val = total_wag
        else: val = p.get("max_balance", balance) # Holdings / Fortune based on max_balance

        sorted_thresh = sorted(ranks.keys())
        cat_prog = []
        for i, thresh in enumerate(sorted_thresh):
            info = ranks[thresh]
            is_unlocked = val >= thresh
            if is_unlocked:
                unlocked_titles.append(info["label"])
                tier_counts[i] += 1
            cat_prog.append({"label": info["label"], "emoji": info["emoji"], "threshold": thresh, "is_unlocked": is_unlocked, "bonus": info["bonus"]})
        category_progress[cat] = {"current": val, "max": sorted_thresh[-1], "ranks": cat_prog}
        
    completed_tiers = sum(1 for count in tier_counts if count == 4)
    
    combined = [{"id": _uid, "balance": _p.get("balance", 0), "freebets": _p.get("freebets", 0)} for _uid, _p in data.get("players", {}).items()]
    for npc in MAFIA_NPCS: combined.append({"id": "npc", "balance": npc["balance"], "freebets": 0})
    combined.sort(key=lambda x: (x["balance"], x["freebets"]), reverse=True)
    
    rank = next((i + 1 for i, item in enumerate(combined) if item["id"] == uid), 999)
    
    titles_fb = len(unlocked_titles) * 500
    tier_cd_min = completed_tiers * 5
    boss_fb, boss_cd_min, rank_title = 0, 0, None
    if rank == 1:
        boss_fb, boss_cd_min, rank_title = 3000, 20, "Boss"
    elif rank <= 3:
        boss_fb, boss_cd_min, rank_title = 1000, 10, "Bras Droit"
        
    total_fb_bonus = titles_fb + boss_fb
    cooldown = max(60, 3600 - (tier_cd_min * 60) - (boss_cd_min * 60))
    
    return {
        "unlocked_titles": unlocked_titles, "completed_tiers": completed_tiers, "rank": rank, "rank_title": rank_title,
        "total_fb_bonus": total_fb_bonus, "cooldown": cooldown, "titles_fb": titles_fb,
        "tier_cd_min": tier_cd_min, "boss_fb": boss_fb, "boss_cd_min": boss_cd_min,
        "category_progress": category_progress
    }

# ── GANG VIEWS ──────────────────────────────────
class GangCategoryView(discord.ui.View):
    def __init__(self, user_id, category: str):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.category = category
        data = load_casino()
        p = data["players"].get(str(user_id), {})
        stats = get_player_stats(user_id, data)
        current_selected = p.get("selected_title")
        
        cat_info = stats["category_progress"][category]
        
        for rank_info in cat_info["ranks"]:
            is_unlocked = rank_info["is_unlocked"]
            label = rank_info["label"]
            
            style = discord.ButtonStyle.secondary
            if current_selected == rank_info['label']:
                style = discord.ButtonStyle.success
            elif is_unlocked:
                style = discord.ButtonStyle.primary
            
            btn = discord.ui.Button(label=label, style=style, disabled=not is_unlocked)
            btn.callback = self.make_callback(rank_info['label'])
            self.add_item(btn)

    def make_callback(self, title_name):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id: return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
            data = load_casino()
            data["players"][str(interaction.user.id)]["selected_title"] = title_name
            save_casino(data)
            await interaction.response.send_message(f"✅ Titre `{title_name}` équipé cosmétiquement pour le classement !", ephemeral=True)
            cog = interaction.client.get_cog("Casino")
            if cog: cog.trigger_leaderboard_update()
        return callback

class GangSpecialView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id
        data = load_casino()
        p = data["players"].get(str(user_id), {})
        stats = get_player_stats(user_id, data)
        current_selected = p.get("selected_title")
        
        has_bras_droit = stats["rank"] <= 3
        has_boss = stats["rank"] == 1
        
        specials = [
            {"label": "Bras Droit", "unlocked": has_bras_droit},
            {"label": "Boss", "unlocked": has_boss}
        ]
        
        for sp in specials:
            style = discord.ButtonStyle.secondary
            if current_selected == sp["label"]:
                style = discord.ButtonStyle.success
            elif sp["unlocked"]:
                style = discord.ButtonStyle.primary
            
            btn = discord.ui.Button(label=sp["label"], style=style, disabled=not sp["unlocked"])
            btn.callback = self.make_callback(sp["label"])
            self.add_item(btn)

    def make_callback(self, title_name):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id: return await interaction.response.send_message("Ce n'est pas ton menu !", ephemeral=True)
            data = load_casino()
            data["players"][str(interaction.user.id)]["selected_title"] = title_name
            save_casino(data)
            await interaction.response.send_message(f"✅ Titre `{title_name}` équipé cosmétiquement pour le classement !", ephemeral=True)
            cog = interaction.client.get_cog("Casino")
            if cog: cog.trigger_leaderboard_update()
        return callback

class GangMainView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.user_id = user_id

    @discord.ui.button(label="Roulette", style=discord.ButtonStyle.primary)
    async def cat_roulette(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_cat(interaction, "roulette")

    @discord.ui.button(label="Blackjack", style=discord.ButtonStyle.primary)
    async def cat_blackjack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_cat(interaction, "blackjack")

    @discord.ui.button(label="Mises Totales", style=discord.ButtonStyle.primary)
    async def cat_total(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_cat(interaction, "total_bet")

    @discord.ui.button(label="Fortune", style=discord.ButtonStyle.primary)
    async def cat_holdings(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_cat(interaction, "holdings")

    @discord.ui.button(label="Spécial", style=discord.ButtonStyle.danger)
    async def cat_special(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = f"Clique ci-dessous sur l'un de tes titres spéciaux débloqués pour l'équiper sur le système de classement :"
        await interaction.response.send_message(msg, view=GangSpecialView(self.user_id), ephemeral=True)

    async def send_cat(self, interaction, cat_key):
        msg = f"Clique ci-dessous sur l'un de tes titres débloqués pour l'équiper sur le système de classement :"
        await interaction.response.send_message(msg, view=GangCategoryView(self.user_id, cat_key), ephemeral=True)

class CasinoWelcomeView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Cash", style=discord.ButtonStyle.success, custom_id="casino:cash")
    async def cash_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            return

        data = load_casino()
        uid = str(interaction.user.id)
        if uid not in data["players"]:
            data["players"][uid] = {
                "balance": 0,
                "freebets": 0,
                "last_hourly": 0,
                "username": interaction.user.display_name,
                "total_wagered_roulette": 0,
                "total_wagered_blackjack": 0,
                "selected_title": "Petit Joueur",
                "currency": "Freebets",
                "max_balance": 0
            }
        p = data["players"][uid]
        
        stats = get_player_stats(interaction.user.id, data)
        now = time.time()
        
        cooldown = stats["cooldown"]
        base_fb = 1000
        total_fb = base_fb + stats["total_fb_bonus"]
        
        msg_details = "\n\n### 📈 Tes Bonus Actifs :\n"
        msg_details += f"• **Base** : +1000 Freebits 🎟️ (60 minutes ⏳)\n"
        if stats["unlocked_titles"]:
            msg_details += f"• **{len(stats['unlocked_titles'])} Titres Débloqués** : +{stats['titles_fb']} Freebits 🎟️\n"
        if stats["completed_tiers"] > 0:
            msg_details += f"• **Paliers Globaux ({stats['completed_tiers']}/6)** : Cooldown ⏳ réduit de {stats['tier_cd_min']} minutes !\n"
        if stats["rank_title"]:
            msg_details += f"• **Bonus de {stats['rank_title']} (Rang #{stats['rank']})** : +{stats['boss_fb']} Freebits 🎟️, Cooldown ⏳ réduit de {stats['boss_cd_min']} minutes !\n"
            
        msg_details += f"\n🏆 **Total Récompense** : {total_fb} Freebits 🎟️ toutes les {cooldown // 60} minutes ⏳ !"
            
        if now - p.get("last_hourly", 0) < cooldown:
            rem = cooldown - (now - p["last_hourly"])
            return await interaction.followup.send(f"⏳ Patience ! Ta récompense sera disponible dans {int(rem//60)} minutes et {int(rem%60)} secondes." + msg_details, ephemeral=True)
        
        p["freebets"] = p.get("freebets", 0) + total_fb
        p["last_hourly"] = now
        p["username"] = interaction.user.display_name
        if p["balance"] > p.get("max_balance", 0):
            p["max_balance"] = p["balance"]
        save_casino(data)
        
        msg = f"💰 **Récompense Horaire**\nTu as reçu **{total_fb} Freebits 🎟️** !\n" + msg_details
        await interaction.followup.send(msg, ephemeral=True)
        cog = self.bot.get_cog("Casino")
        if cog: cog.trigger_leaderboard_update()

    @discord.ui.button(label="Solde", style=discord.ButtonStyle.secondary, custom_id="casino:balance")
    async def balance_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            return

        data = load_casino()
        if str(interaction.user.id) not in data["players"]:
            return await interaction.followup.send("❌ **Tu n'as pas de profil Casino !** Clique d'abord sur **Cash** pour récupérer tes premiers freebets et t'enregistrer.", ephemeral=True)

        p = data["players"].get(str(interaction.user.id), {"balance": 0, "freebets": 0})
        stats = get_player_stats(interaction.user.id, data)
        sel = p.get("selected_title") or "Petit Joueur"
        
        msg = (
            f"💰 **TA FORTUNE**\n"
            f"--- \n"
            f"🏆 **Rang Global** : #{stats['rank']}\n"
            f"🪙 **Jetons** : {p['balance']:,}\n"
            f"🎟️ **Freebits** : {p['freebets']:,}\n"
            f"🎖️ **Titre Équipé** : `{sel}`\n"
            f"--- \n"
            f"*Mise des jetons pour monter dans le classement !*".replace(",", " ")
        )
        await interaction.followup.send(msg, ephemeral=True)
        cog = self.bot.get_cog("Casino")
        if cog: cog.trigger_leaderboard_update()

    @discord.ui.button(label="Gang", style=discord.ButtonStyle.primary, custom_id="casino:gang")
    async def gang_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            return

        data = load_casino()
        if str(interaction.user.id) not in data["players"]:
            return await interaction.followup.send("❌ **Tu n'as pas de profil Casino !** Clique d'abord sur **Cash** pour récupérer tes premiers Freebits 🎟️ et t'enregistrer.", ephemeral=True)

        stats = get_player_stats(interaction.user.id, data)
        desc = (
            "🏢 **CENTRAL DU GANG**\n"
            "• **Titres** : +500 Freebits 🎟️ / Cash.\n"
            "• **Paliers** : Cooldown ⏳ -5 minutes si les 4 catégories ont le même palier !\n\n"
        )
        
        cat_info_dict = {
            "roulette": ("🎡 Roulette", "Miser des jetons 🪙 à la roulette"),
            "blackjack": ("🃏 Blackjack", "Miser des jetons 🪙 au blackjack"),
            "total_bet": ("💰 Mises", "Miser des jetons 🪙 au total"),
            "holdings": ("🏦 Fortune", "Record de jetons 🪙")
        }
        for cat_key, (cat_title, cat_desc) in cat_info_dict.items():
            desc += f"**{cat_title}** : {cat_desc}\n"
            cat_info = stats["category_progress"][cat_key]
            current_val = cat_info["current"]
            
            for rank_info in cat_info["ranks"]:
                thresh = rank_info["threshold"]
                is_unlocked = rank_info["is_unlocked"]
                display_val = min(current_val, thresh)
                pct = int((display_val / thresh) * 100) if thresh > 0 else 100
                
                status = "✅" if is_unlocked else "❌"
                desc += f"{status} {rank_info['label']} : {display_val:,}/{thresh:,} ({pct}%)\n".replace(",", " ")
            desc += "\n"
            
        desc += "**👑 Titres Spéciaux**\n"
        bd = "✅" if stats["rank"] <= 3 else "❌"
        boss = "✅" if stats["rank"] == 1 else "❌"
        desc += f"{bd} **Bras Droit** : Top 3 | +1000 🎟️ & -10 min ⏳\n"
        desc += f"{boss} **Boss** : Top 1 | +2000 🎟️ & -10 min ⏳\n\n"
        desc += "Équipe tes titres débloqués via les boutons ci-dessous !"
        
        await interaction.followup.send(desc, view=GangMainView(interaction.user.id), ephemeral=True)

class Casino(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._panel_lock = asyncio.Lock()
        self._last_leaderboard_update = 0
        # Pending updates queue: key -> (embed, view)
        self._pending_updates: dict = {}

    async def cog_load(self):
        self.auto_setup_task.start()
        self.flush_updates_task.start()

    @tasks.loop(seconds=5.0)
    async def flush_updates_task(self):
        """Flush all pending message edits every 5 seconds to reduce Discord API calls."""
        if not self._pending_updates:
            return
        pending = dict(self._pending_updates)
        self._pending_updates.clear()
        for key, (embed, view) in pending.items():
            try:
                await self._do_upsert(key, embed=embed, view=view)
            except Exception as e:
                logger.warning("flush_updates_task: échec de l'upsert pour '%s': %s", key, e)

    @flush_updates_task.before_loop
    async def before_flush(self):
        await self.bot.wait_until_ready()

    @tasks.loop(count=1)
    async def auto_setup_task(self):
        await self.bot.wait_until_ready()
        await self._update_welcome_message()
        await self._update_leaderboard()

    async def upsert_panel_message(self, key: str, *, embed: discord.Embed, view: discord.ui.View | None = None):
        channel_id = PANEL_CHANNEL_MAP.get(key)
        if not channel_id: return None

        # Check if message exists; if not, send it immediately (first-time setup)
        data = load_casino()
        msg_id = data.get("messages", {}).get(key)
        if not msg_id:
            return await self._do_upsert(key, embed=embed, view=view)

        # Queue the update — will be flushed by flush_updates_task every 5s
        self._pending_updates[key] = (embed, view)
        # Return a lightweight placeholder so callers don't break
        channel = self.bot.get_channel(channel_id)
        if channel:
            try:
                return await channel.fetch_message(int(msg_id))
            except Exception:
                pass
        return None

    async def _do_upsert(self, key: str, *, embed: discord.Embed, view: discord.ui.View | None = None):
        """Actually perform the Discord API call to edit/send the panel message."""
        channel_id = PANEL_CHANNEL_MAP.get(key)
        if not channel_id: return None
        async with self._panel_lock:
            channel = self.bot.get_channel(channel_id)
            if not channel: return None
            data = load_casino()
            msg_id = data.get("messages", {}).get(key)
            if msg_id:
                try:
                    msg = await channel.fetch_message(int(msg_id))
                    await msg.edit(embed=embed, view=view)
                    return msg
                except Exception as e:
                    logger.warning("_do_upsert: échec de l'édition du message '%s': %s", key, e)
            msg = await channel.send(embed=embed, view=view)
            data.setdefault("messages", {})[key] = msg.id
            save_casino(data)
            return msg

    async def _update_welcome_message(self):
        embed = discord.Embed(
            title="✨  BIENVENUE AU CASINO SUPRÊME  ✨",
            description=(
                "### 🏮 **L'Antre de la Fortune et du Risque**\n"
                "Ici, les légendes naissent et les empires s'effondrent. "
                "Maîtrisez les devises pour devenir le nouveau parrain du crime.\n\n"
                "### 🪙 **Comprendre les Devises**\n"
                "• **Jetons** 🪙 : Ta fortune réelle. Utilisés pour miser partout, y compris au **Poker**. C'est ton score au classement.\n"
                "• **Freebits** 🎟️ : Jetons de 'test' offerts via le bouton **Cash**. "
                "Jouables à la **Roulette** et au **Blackjack**. Seul le profit net est converti en vrais Jetons 🪙 !\n\n"
                "### 💰 **Gagner des Devises**\n"
                "• **Cash** : Reçois **1000 Freebits 🎟️** de base toutes les heures (60 minutes ⏳).\n"
                "• **Bonus Titres** : Chaque titre de Gang débloqué rajoute **+500 Freebits 🎟️** à ton Cash.\n\n"
                "### 👑 **Domination du Gang**\n"
                "• **Progression** : Mise tes Jetons 🪙 ou accumule une fortune pour débloquer des paliers dans 4 catégories.\n"
                "• **Synergie** : Valider le même palier dans les 4 catégories réduit le Cooldown ⏳ du Cash de **5 minutes** !\n"
                "• **Titres Spéciaux** : Sois Top 3 ou Top 1 au classement global pour débloquer **Bras Droit** ou **Boss** et obtenir des bonus massifs.\n\n"
                "--- \n"
                "### 📍 **Nos Salons**\n"
                "🎡 <#1480224572275032135> (Roulette)\n"
                "🃏 <#1480224707575021769> (Blackjack)\n"
                "♠️ <#1480224841830236331> (Poker - *Jetons uniquement*)\n"
                "--- \n"
                "**Choisis ton destin et que la chance soit avec toi.**"
            ),
            color=discord.Color.from_rgb(255, 215, 0)
        )
        embed.set_footer(text="Bot Suprême • Système de Gang & Casino", icon_url=self.bot.user.display_avatar.url)
        await self.upsert_panel_message("welcome", embed=embed, view=CasinoWelcomeView(self.bot))

    async def _update_leaderboard(self):
        data = load_casino()
        combined = []
        for uid, p in data.get("players", {}).items():
            combined.append({
                "type": "player", "id": uid, 
                "name": p.get("username") or f"Joueur {uid[-4:]}", 
                "balance": p.get("balance", 0), 
                "freebets": p.get("freebets", 0), 
                "title": p.get("selected_title") or "Petit Joueur"
            })
        for npc in MAFIA_NPCS:
            combined.append({
                "type": "npc", "name": npc["name"], 
                "balance": npc["balance"], 
                "rank_key": npc["rank"], 
                "emoji": npc["emoji"],
                "freebets": 0,
                "title": npc["rank"]
            })
        
        combined.sort(key=lambda x: (x["balance"], x["freebets"]), reverse=True)
        
        embed = discord.Embed(
            title="🏆  CLASSEMENT DES GRANDS PARRAINS", 
            description="L'élite du crime et de la fortune. Classement sur **Jetons** puis **Freebets**.", 
            color=discord.Color.gold()
        )
        
        board_text = ""
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "11.", "12."]
        
        for i, item in enumerate(combined[:10]):
            medal = medals[i] if i < 10 else f"**{i+1}.**"
            name = item["name"]
            title = f"*{item['title']}*"
            bal = f"{item['balance']:,}".replace(",", " ")
            
            if item["type"] == "player":
                fb = f"{item['freebets']:,}".replace(",", " ")
                board_text += f"{medal} **{name}** | {title}\n ╰ 🪙 **{bal}** Jetons  •  🎟️ **{fb}** Freebets\n\n"
            else:
                board_text += f"{medal} {item['emoji']} **{name}** | {title}\n ╰ 🪙 **{bal}** Jetons\n\n"
        
        embed.description += f"\n\n{board_text if len(combined) > 0 else '*La rue est vide...*'}"
        await self.upsert_panel_message("leaderboard", embed=embed)

    def trigger_leaderboard_update(self):
        now = time.time()
        if now - self._last_leaderboard_update < 5: return
        self._last_leaderboard_update = now
        asyncio.create_task(self._update_leaderboard())

async def setup(bot):
    await bot.add_cog(Casino(bot))
