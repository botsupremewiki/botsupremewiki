import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice
import math
from .utils import _load_json, _save_json
import asyncio

PFC_CHANNEL_ID = 1468267312493756607
PFC_DATA_FILE = "bot/data/pfc_leaderboard.json"
REQUIRED_ROLE_ID = 1475346687085252648

def update_pfc_elo(winner_id: str, loser_id: str, mode: str):
    data = _load_json(PFC_DATA_FILE, {"messages": {}, "players": {}})
    players = data["players"]
    for uid in [winner_id, loser_id]:
        if uid not in players: players[uid] = {"bo1_elo":1000,"bo1_wins":0,"bo1_losses":0,"bo3_elo":1000,"bo3_wins":0,"bo3_losses":0,"bo5_elo":1000,"bo5_wins":0,"bo5_losses":0}
    k = {"bo1":24, "bo3":32, "bo5":42}[mode]
    ek = f"{mode}_elo"; wk, lk = f"{mode}_wins", f"{mode}_losses"
    r1, r2 = players[winner_id].get(ek, 1000), players[loser_id].get(ek, 1000)
    e1, e2 = 1/(1+10**((r2-r1)/400)), 1/(1+10**((r1-r2)/400))
    nw, nl = round(r1+k*(1-e1)), round(r2+k*(0-e2))
    players[winner_id][ek], players[loser_id][ek], players[winner_id][wk], players[loser_id][lk] = nw, nl, players[winner_id].get(wk,0)+1, players[loser_id].get(lk,0)+1
    _save_json(PFC_DATA_FILE, data); return nw, nl, nw-r1

class PFCGameView(discord.ui.View):
    def __init__(self, cog, p1, p2, mode):
        super().__init__(timeout=300); self.cog, self.p1, self.p2, self.mode = cog, p1, p2, mode
        self.amt = {"bo1":1,"bo3":3,"bo5":5}[mode]; self.req = math.ceil(self.amt/2)
        self.s1, self.s2, self.rd = 0, 0, 1; self.c1, self.c2 = None, None
        self.map = {"rock":"🪨 Pierre", "paper":"📄 Feuille", "scissors":"✂️ Ciseaux"}
    async def process(self, it, choice):
        if it.user.id not in [self.p1.id, self.p2.id]: return await it.response.send_message("❌ Pas toi", ephemeral=True)
        if it.user.id == self.p1.id:
            if self.c1: return await it.response.send_message("❌ Déjà fait", ephemeral=True)
            self.c1 = choice
        else:
            if self.c2: return await it.response.send_message("❌ Déjà fait", ephemeral=True)
            self.c2 = choice
        await it.response.send_message(f"🤫 Choisi {self.map[choice]}", ephemeral=True)
        if self.c1 and self.c2:
            res = ""
            if self.c1 == self.c2: res = "🤝 Égalité !"; self.rd -= 1
            elif (self.c1=="rock" and self.c2=="scissors") or (self.c1=="paper" and self.c2=="rock") or (self.c1=="scissors" and self.c2=="paper"):
                self.s1 += 1; res = f"🎉 {self.p1.display_name} gagne !"
            else: self.s2 += 1; res = f"🎉 {self.p2.display_name} gagne !"
            summ = f"Round {self.rd}: {self.p1.mention} ({self.map[self.c1]}) vs {self.p2.mention} ({self.map[self.c2]})\n{res}"
            if self.s1 >= self.req or self.s2 >= self.req:
                w, l = (self.p1, self.p2) if self.s1 >= self.req else (self.p2, self.p1)
                nw, nl, d = update_pfc_elo(str(w.id), str(l.id), self.mode)
                e = discord.Embed(title=f"🏆 VICTOIRE DE {w.display_name.upper()} !", description=f"Duel BO{self.amt} fini.\n\n{summ}", color=discord.Color.gold())
                e.add_field(name="Score", value=f"{self.p1.mention}: {self.s1}\n{self.p2.mention}: {self.s2}")
                e.add_field(name="Elo", value=f"📈 {w.mention}: **{nw}** (+{d})\n📉 {l.mention}: **{nl}** (-{d})")
                for b in self.children: b.disabled = True
                await it.message.edit(embed=e, view=self); self.stop(); await it.message.delete(delay=10)
                asyncio.create_task(self.cog._update_leaderboard()); return
            self.rd += 1; self.c1, self.c2 = None, None
            e = discord.Embed(title=f"⚔️ PFC: BO{self.amt}", description=f"{summ}\n\n**RD {self.rd}: JOUEZ !**", color=discord.Color.blue())
            e.add_field(name="Score", value=f"{self.p1.display_name}: {self.s1}\n{self.p2.display_name}: {self.s2}")
            await it.message.edit(embed=e, view=self)
    @discord.ui.button(label="Pierre", emoji="🪨")
    async def rock(self, it, b): await self.process(it, "rock")
    @discord.ui.button(label="Feuille", emoji="📄")
    async def paper(self, it, b): await self.process(it, "paper")
    @discord.ui.button(label="Ciseaux", emoji="✂️")
    async def scissors(self, it, b): await self.process(it, "scissors")

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def cog_load(self): self.setup_task.start()
    @tasks.loop(count=1)
    async def setup_task(self):
        await self.bot.wait_until_ready()
        await self._update_launcher()
        await self._update_leaderboard()

    async def _update_launcher(self):
        ch = self.bot.get_channel(PFC_CHANNEL_ID)
        if not ch: return
        data = _load_json(PFC_DATA_FILE, {"messages":{}, "players":{}})
        
        embed = discord.Embed(
            title="🪨 PIERRE FEUILLE CISEAUX ✂️",
            description=(
                "### ⚔️ Défie tes rivaux !\n"
                "1. Choisis un format de match (BO1, BO3, BO5).\n"
                "2. Sélectionne un joueur dans le menu.\n"
                "3. Clique sur **Défier**.\n\n"
                "> ⚠️ Seuls les joueurs avec le rôle approprié peuvent être défiés."
            ),
            color=discord.Color.purple()
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
        _save_json(PFC_DATA_FILE, data)

    async def _update_leaderboard(self):
        ch = self.bot.get_channel(PFC_CHANNEL_ID)
        if not ch: return
        data = _load_json(PFC_DATA_FILE, {"messages":{}, "players":{}})
        e = discord.Embed(title="🏆 TOP PFC", color=discord.Color.purple())
        for m in ["bo1", "bo3", "bo5"]:
            s = sorted(data["players"].items(), key=lambda x: x[1].get(f"{m}_elo",1000), reverse=True)
            txt = "\n".join(f"{i+1}. <@{u}>: {p.get(f'{m}_elo',1000)} Elo" for i, (u, p) in enumerate(s[:5]) if p.get(f"{m}_wins",0)>0)
            e.add_field(name=m.upper(), value=txt or "Aucun match", inline=False)
        mid = data["messages"].get("leaderboard")
        if mid:
            try:
                m = await ch.fetch_message(mid); await m.edit(embed=e); return
            except Exception: pass
        m = await ch.send(embed=e); data["messages"]["leaderboard"] = m.id; _save_json(PFC_DATA_FILE, data)

class PFCChallengeView(discord.ui.View):
    def __init__(self, cog, p1, p2, mode):
        super().__init__(timeout=120); self.cog, self.p1, self.p2, self.mode = cog, p1, p2, mode
    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.success)
    async def accept(self, it, b):
        if it.user.id != self.p2.id: return await it.response.send_message("❌ Ce n'est pas ton défi !", ephemeral=True)
        v = PFCGameView(self.cog, self.p1, self.p2, self.mode); e = discord.Embed(title="PFC", description=f"C'est parti ! (Format: {self.mode.upper()})", color=discord.Color.blue())
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

    @discord.ui.select(
        placeholder="Format du match...", 
        options=[
            discord.SelectOption(label="BO1", value="bo1", description="Premier à 1 point"),
            discord.SelectOption(label="BO3", value="bo3", description="Premier à 2 points"),
            discord.SelectOption(label="BO5", value="bo5", description="Premier à 3 points")
        ],
        custom_id="pfc:select_format",
        row=0
    )
    async def format_select(self, it: discord.Interaction, select: discord.ui.Select):
        await it.response.defer(ephemeral=True)

    @discord.ui.select(cls=discord.ui.UserSelect, placeholder="Choisis un adversaire...", custom_id="pfc:select_user", row=1)
    async def user_select(self, it: discord.Interaction, select: discord.ui.UserSelect):
        await it.response.defer(ephemeral=True)

    @discord.ui.button(label="🥊 Défier", style=discord.ButtonStyle.primary, custom_id="pfc:challenge", row=2)
    async def challenge_btn(self, it: discord.Interaction, button: discord.ui.Button):
        # Format selection
        fmt_select = discord.utils.get(self.children, custom_id="pfc:select_format")
        if not fmt_select or not fmt_select.values:
            return await it.response.send_message("❌ Tu dois d'abord choisir un format (BO1, BO3, BO5) !", ephemeral=True)
        format = fmt_select.values[0]

        # User selection
        user_select = discord.utils.get(self.children, custom_id="pfc:select_user")
        if not user_select or not user_select.values:
            return await it.response.send_message("❌ Tu dois choisir un adversaire !", ephemeral=True)
        
        target = user_select.values[0]
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

        view = PFCChallengeView(self.cog, it.user, target, format)
        await it.channel.send(f"🥊 {target.mention}, défi de {it.user.mention} au **PFC** ({format.upper()}) !", view=view)
        await it.response.send_message(f"Défi envoyé à {target.mention} !", ephemeral=True)

async def setup(bot):
    cog = RockPaperScissors(bot)
    await bot.add_cog(cog)
