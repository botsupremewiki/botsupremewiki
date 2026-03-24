import discord
from discord.ext import commands, tasks
from discord import app_commands
from .utils import _load_json, _save_json, update_elo
import asyncio

P4_CHANNEL_ID = 1475338861197529118
P4_DATA_FILE = "bot/data/p4_leaderboard.json"
REQUIRED_ROLE_ID = 1475346687085252648

def update_p4_elo(winner_id: str, loser_id: str, is_draw: bool = False):
    return update_elo(P4_DATA_FILE, winner_id, loser_id, k=28, is_draw=is_draw)

class P4ColumnButton(discord.ui.Button):
    def __init__(self, idx): super().__init__(style=discord.ButtonStyle.secondary, label=str(idx+1)); self.idx = idx
    async def callback(self, it):
        v = self.view
        if it.user.id not in [v.p1.id, v.p2.id]: return await it.response.send_message("❌ Pas ta partie", ephemeral=True)
        if it.user.id != v.current_turn: return await it.response.send_message("❌ Pas ton tour", ephemeral=True)
        if not v.drop_token(self.idx, 1 if v.current_turn==v.p1.id else 2): return await it.response.send_message("❌ Colonne pleine", ephemeral=True)
        v.current_turn = v.p2.id if v.current_turn==v.p1.id else v.p1.id
        await v.check_game_over(it)

class Connect4GameView(discord.ui.View):
    def __init__(self, cog, p1, p2):
        super().__init__(timeout=600); self.cog, self.p1, self.p2 = cog, p1, p2
        self.rows, self.cols = 6, 7; self.board = [[0 for _ in range(7)] for _ in range(6)]
        self.current_turn = p1.id
        for i in range(7): self.add_item(P4ColumnButton(i))
    def drop_token(self, c, p):
        for r in range(5,-1,-1):
            if self.board[r][c]==0: self.board[r][c]=p; return True
        return False
    def render_board(self):
        ic = {0:"⚫", 1:"🔴", 2:"🟨"}
        return "\n".join("".join(ic[c] for c in r) for r in self.board) + "\n1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
    def check_winner(self):
        b = self.board
        for r in range(6):
            for c in range(4):
                if b[r][c]!=0 and b[r][c]==b[r][c+1]==b[r][c+2]==b[r][c+3]: return b[r][c]
        for c in range(7):
            for r in range(3):
                if b[r][c]!=0 and b[r][c]==b[r+1][c]==b[r+2][c]==b[r+3][c]: return b[r][c]
        for r in range(3):
            for c in range(4):
                if b[r][c]!=0 and b[r][c]==b[r+1][c+1]==b[r+2][c+2]==b[r+3][c+3]: return b[r][c]
        for r in range(3,6):
            for c in range(4):
                if b[r][c]!=0 and b[r][c]==b[r-1][c+1]==b[r-2][c+2]==b[r-3][c+3]: return b[r][c]
        if 0 not in b[0]: return -1
        return 0
    async def check_game_over(self, it):
        win = self.check_winner()
        if win == 0:
            np = self.p1 if self.current_turn==self.p1.id else self.p2
            e = discord.Embed(title=f"🔴 P4: {self.p1.display_name} vs {self.p2.display_name} 🟨", description=f"Tour de {np.mention} ({'🔴' if np==self.p1 else '🟨'})\n\n{self.render_board()}", color=discord.Color.blue())
            return await it.response.edit_message(embed=e, view=self)
        for c in self.children: c.disabled = True
        if win == -1:
            nw1, nw2, d = update_p4_elo(str(self.p1.id), str(self.p2.id), True)
            e = discord.Embed(title="🤝 ÉGALITÉ !", description=self.render_board(), color=discord.Color.greyple())
            e.add_field(name="Elo", value=f"{self.p1.mention}: **{nw1}**\n{self.p2.mention}: **{nw2}**")
        else:
            w, l = (self.p1, self.p2) if win==1 else (self.p2, self.p1)
            nw, nl, d = update_p4_elo(str(w.id), str(l.id))
            e = discord.Embed(title=f"🏆 VICTOIRE DE {w.display_name.upper()} !", description=f"{w.mention} a aligné 4 jetons !\n\n{self.render_board()}", color=discord.Color.gold())
            e.add_field(name="Elo", value=f"📈 {w.mention}: **{nw}** (+{d})\n📉 {l.mention}: **{nl}** (-{d})")
        await it.response.edit_message(embed=e, view=self)
        self.stop(); await it.message.delete(delay=10); asyncio.create_task(self.cog._update_leaderboard())

class ChallengeView(discord.ui.View):
    def __init__(self, cog, p1, p2):
        super().__init__(timeout=120); self.cog, self.p1, self.p2 = cog, p1, p2
    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.success)
    async def accept(self, it, b):
        if it.user.id != self.p2.id: return await it.response.send_message("❌ Ce n'est pas ton défi !", ephemeral=True)
        v = Connect4GameView(self.cog, self.p1, self.p2); e = discord.Embed(title="P4", description="C'est parti !", color=discord.Color.blue())
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

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Choisis un adversaire...", custom_id="p4:select_user")
    async def user_select(self, it: discord.Interaction, select: discord.ui.UserSelect):
        await it.response.defer(ephemeral=True)

    @discord.ui.button(label="🥊 Défier", style=discord.ButtonStyle.primary, custom_id="p4:challenge")
    async def challenge_btn(self, it: discord.Interaction, button: discord.ui.Button):
        select = discord.utils.get(self.children, custom_id="p4:select_user")
        if not select or not select.values:
            return await it.response.send_message("❌ Tu dois d'abord choisir un adversaire dans le menu !", ephemeral=True)
        
        target = select.values[0]
        if target.id == it.user.id:
            return await it.response.send_message("❌ Tu ne peux pas te défier toi-même !", ephemeral=True)
        
        if target.bot:
            return await it.response.send_message("❌ Tu ne peux pas défier un bot !", ephemeral=True)

        if isinstance(target, discord.Member):
            if not any(role.id == REQUIRED_ROLE_ID for role in target.roles):
                return await it.response.send_message(f"❌ {target.mention} n'a pas le rôle requis pour jouer !", ephemeral=True)
        else:
            member = it.guild.get_member(target.id)
            if not member or not any(role.id == REQUIRED_ROLE_ID for role in member.roles):
                return await it.response.send_message(f"❌ {target.mention} n'a pas le rôle requis pour jouer !", ephemeral=True)

        view = ChallengeView(self.cog, it.user, target)
        await it.channel.send(f"🥊 {target.mention}, défi de {it.user.mention} au **Puissance 4** !", view=view)
        await it.response.send_message(f"Défi envoyé à {target.mention} !", ephemeral=True)

class Puissance4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def cog_load(self): self.setup_task.start()
    @tasks.loop(count=1)
    async def setup_task(self):
        await self.bot.wait_until_ready()
        await self._update_launcher()
        await self._update_leaderboard()

    async def _update_launcher(self):
        ch = self.bot.get_channel(P4_CHANNEL_ID)
        if not ch: return
        data = _load_json(P4_DATA_FILE, {"messages":{}, "players":{}})
        
        embed = discord.Embed(
            title="🔴 PUISSANCE 4 🟨",
            description=(
                "### ⚔️ Défie tes rivaux !\n"
                "Sélectionne un joueur dans le menu ci-dessous puis clique sur **Défier**.\n\n"
                "> ⚠️ Seuls les joueurs avec le rôle approprié peuvent être défiés."
            ),
            color=discord.Color.red()
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
        _save_json(P4_DATA_FILE, data)

    async def _update_leaderboard(self):
        ch = self.bot.get_channel(P4_CHANNEL_ID)
        if not ch: return
        data = _load_json(P4_DATA_FILE, {"messages":{}, "players":{}})
        s = sorted(data["players"].items(), key=lambda x: x[1].get("elo",1000), reverse=True)
        e = discord.Embed(title="🏆 TOP PUISSANCE 4", description="\n".join(f"{i+1}. <@{u}>: {p['elo']} Elo" for i, (u, p) in enumerate(s[:10]) if p.get('wins', 0) > 0 or p.get('losses', 0) > 0), color=discord.Color.red())
        mid = data["messages"].get("leaderboard")
        if mid:
            try:
                m = await ch.fetch_message(mid); await m.edit(embed=e); return
            except Exception: pass
        m = await ch.send(embed=e); data["messages"]["leaderboard"] = m.id; _save_json(P4_DATA_FILE, data)

async def setup(bot):
    cog = Puissance4(bot)
    await bot.add_cog(cog)
