import discord
from discord.ext import commands, tasks
from discord import app_commands
from .utils import _load_json, _save_json, update_elo
import asyncio

MORPION_CHANNEL_ID = 1475332850294329577
MORPION_DATA_FILE = "bot/data/morpion_leaderboard.json"
REQUIRED_ROLE_ID = 1475346687085252648

def update_morpion_elo(winner_id: str, loser_id: str, is_draw: bool = False):
    return update_elo(MORPION_DATA_FILE, winner_id, loser_id, k=24, is_draw=is_draw)

class MorpionButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(style=discord.ButtonStyle.secondary, label="⬛", row=y)
        self.x, self.y = x, y
    async def callback(self, it):
        v = self.view
        if it.user.id not in [v.p1.id, v.p2.id]: return await it.response.send_message("❌ Pas ta partie", ephemeral=True)
        if it.user.id != v.current_turn: return await it.response.send_message("❌ Pas ton tour", ephemeral=True)
        self.disabled = True
        if v.current_turn == v.p1.id:
            self.style, self.label = discord.ButtonStyle.primary, "❌"
            v.board[self.y][self.x] = 1; v.current_turn = v.p2.id
        else:
            self.style, self.label = discord.ButtonStyle.success, "⭕"
            v.board[self.y][self.x] = 2; v.current_turn = v.p1.id
        await v.check_game_over(it)

class MorpionGameView(discord.ui.View):
    def __init__(self, cog, p1, p2):
        super().__init__(timeout=300); self.cog, self.p1, self.p2 = cog, p1, p2
        self.current_turn = p1.id; self.board = [[0,0,0],[0,0,0],[0,0,0]]
        for y in range(3):
            for x in range(3): self.add_item(MorpionButton(x,y))
    def check_winner(self):
        b = self.board
        for i in range(3):
            if b[i][0]==b[i][1]==b[i][2]!=0: return b[i][0]
            if b[0][i]==b[1][i]==b[2][i]!=0: return b[0][i]
        if b[0][0]==b[1][1]==b[2][2]!=0: return b[0][0]
        if b[0][2]==b[1][1]==b[2][0]!=0: return b[0][2]
        if all(c!=0 for r in b for c in r): return -1
        return 0
    async def check_game_over(self, it):
        win = self.check_winner()
        if win == 0:
            next_p = self.p1 if self.current_turn==self.p1.id else self.p2
            e = discord.Embed(title=f"⚔️ MORPION: {self.p1.display_name} vs {self.p2.display_name}", description=f"Tour de {next_p.mention} ({'❌' if next_p==self.p1 else '⭕'})", color=discord.Color.blue())
            return await it.response.edit_message(embed=e, view=self)
        for c in self.children: c.disabled = True
        if win == -1:
            nw1, nw2, d = update_morpion_elo(str(self.p1.id), str(self.p2.id), True)
            e = discord.Embed(title="🤝 ÉGALITÉ !", color=discord.Color.light_grey())
            e.add_field(name="Elo", value=f"{self.p1.mention}: **{nw1}**\n{self.p2.mention}: **{nw2}**")
        else:
            w, l = (self.p1, self.p2) if win==1 else (self.p2, self.p1)
            nw, nl, d = update_morpion_elo(str(w.id), str(l.id))
            e = discord.Embed(title=f"🏆 VICTOIRE DE {w.display_name.upper()} !", color=discord.Color.gold())
            e.add_field(name="Elo", value=f"📈 {w.mention}: **{nw}** (+{d})\n📉 {l.mention}: **{nl}** (-{d})")
        await it.response.edit_message(embed=e, view=self)
        self.stop(); await it.message.delete(delay=10); asyncio.create_task(self.cog._update_leaderboard())

class ChallengeView(discord.ui.View):
    def __init__(self, cog, p1, p2):
        super().__init__(timeout=120); self.cog, self.p1, self.p2 = cog, p1, p2
    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.success)
    async def accept(self, it, b):
        if it.user.id != self.p2.id: return await it.response.send_message("❌ Ce n'est pas ton défi !", ephemeral=True)
        v = MorpionGameView(self.cog, self.p1, self.p2); e = discord.Embed(title="Morpion", description="C'est parti !", color=discord.Color.blue())
        await it.response.edit_message(embed=e, view=v); self.stop()
    @discord.ui.button(label="Décliner", style=discord.ButtonStyle.danger)
    async def decline(self, it, b):
        if it.user.id != self.p2.id: return await it.response.send_message("❌ Ce n'est pas ton défi !", ephemeral=True)
        await it.response.edit_message(content=f"❌ {self.p2.mention} a décliné le défi de {self.p1.mention}.", embed=None, view=None)
        self.stop()

class MinigameLauncher(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Choisis un adversaire...", custom_id="morpion:select_user")
    async def user_select(self, it: discord.Interaction, select: discord.ui.UserSelect):
        await it.response.defer(ephemeral=True)

    @discord.ui.button(label="🥊 Défier", style=discord.ButtonStyle.primary, custom_id="morpion:challenge")
    async def challenge_btn(self, it: discord.Interaction, button: discord.ui.Button):
        # Find the selection in the children
        select = discord.utils.get(self.children, custom_id="morpion:select_user")
        if not select or not select.values:
            return await it.response.send_message("❌ Tu dois d'abord choisir un adversaire dans le menu !", ephemeral=True)
        
        target = select.values[0]
        if target.id == it.user.id:
            return await it.response.send_message("❌ Tu ne peux pas te défier toi-même !", ephemeral=True)
        
        if target.bot:
            return await it.response.send_message("❌ Tu ne peux pas défier un bot !", ephemeral=True)

        # Check for role
        if isinstance(target, discord.Member):
            if not any(role.id == REQUIRED_ROLE_ID for role in target.roles):
                return await it.response.send_message(f"❌ {target.mention} n'a pas le rôle requis pour jouer !", ephemeral=True)
        else:
            # If target is not a Member (could happen if not in cache, though UserSelect usually returns Members if possible)
            # Try to fetch member
            member = it.guild.get_member(target.id)
            if not member or not any(role.id == REQUIRED_ROLE_ID for role in member.roles):
                return await it.response.send_message(f"❌ {target.mention} n'a pas le rôle requis pour jouer !", ephemeral=True)

        view = ChallengeView(self.cog, it.user, target)
        await it.channel.send(f"🥊 {target.mention}, défi de {it.user.mention} au **Morpion** !", view=view)
        await it.response.send_message(f"Défi envoyé à {target.mention} !", ephemeral=True)

class Morpion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def cog_load(self): self.setup_task.start()
    @tasks.loop(count=1)
    async def setup_task(self):
        await self.bot.wait_until_ready()
        await self._update_launcher()
        await self._update_leaderboard()

    async def _update_launcher(self):
        ch = self.bot.get_channel(MORPION_CHANNEL_ID)
        if not ch: return
        data = _load_json(MORPION_DATA_FILE, {"messages":{}, "players":{}})
        
        embed = discord.Embed(
            title="❌ MORPION ⭕",
            description=(
                "### ⚔️ Défie tes rivaux !\n"
                "Sélectionne un joueur dans le menu ci-dessous puis clique sur **Défier**.\n\n"
                "> ⚠️ Seuls les joueurs avec le rôle approprié peuvent être défiés."
            ),
            color=discord.Color.blue()
        )
        
        msg_id = data["messages"].get("launcher")
        if msg_id:
            try:
                m = await ch.fetch_message(msg_id)
                await m.edit(embed=embed, view=MinigameLauncher(self))
                return
            except Exception: pass
        
        m = await ch.send(embed=embed, view=MinigameLauncher(self))
        data["messages"]["launcher"] = m.id
        _save_json(MORPION_DATA_FILE, data)

    async def _update_leaderboard(self):
        ch = self.bot.get_channel(MORPION_CHANNEL_ID)
        if not ch: return
        data = _load_json(MORPION_DATA_FILE, {"messages":{}, "players":{}})
        s = sorted(data["players"].items(), key=lambda x: x[1].get("elo",1000), reverse=True)
        e = discord.Embed(title="🏆 TOP MORPION", description="\n".join(f"{i+1}. <@{u}>: {p['elo']} Elo" for i, (u, p) in enumerate(s[:10]) if p.get('wins', 0) > 0 or p.get('losses', 0) > 0), color=discord.Color.blue())
        mid = data["messages"].get("leaderboard")
        if mid:
            try:
                m = await ch.fetch_message(mid); await m.edit(embed=e); return
            except Exception: pass
        m = await ch.send(embed=e); data["messages"]["leaderboard"] = m.id; _save_json(MORPION_DATA_FILE, data)

async def setup(bot):
    cog = Morpion(bot)
    await bot.add_cog(cog)
