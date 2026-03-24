import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
import time
from .core import (
    load_casino, save_casino, add_balance,
    ROULETTE_RED, ROULETTE_BLACK, ROULETTE_COLORS,
    ROULETTE_CHANNEL_ID
)

class RouletteSimpleModal(discord.ui.Modal):
    def __init__(self, cog, bet_type: str, bet_label: str, currency: str):
        display_name = "Freebits 🎟️" if currency == "Freebets" else "Jetons 🪙"
        super().__init__(title=f"🎡 {bet_label} ({display_name})")
        self.cog = cog
        self.bet_type = bet_type
        self.currency = currency
        self.amount_input = discord.ui.TextInput(label=f"Combien de {display_name} ?", placeholder="ex: 500", required=True)
        self.add_item(self.amount_input)

    async def on_submit(self, interaction: discord.Interaction):
        await self.cog.process_bet(interaction, self.bet_type, self.amount_input.value, None, self.currency)

class RouletteNumberModal(discord.ui.Modal):
    number_input = discord.ui.TextInput(label="Numéro(s) (ex: 0, 17, 32)", placeholder="Sépare par des virgules", required=True)
    amount_input = discord.ui.TextInput(label="Mise PAR numéro (Jetons 🪙/Freebits 🎟️)", placeholder="ex: 500", required=True)
    def __init__(self, cog, currency: str):
        display_name = "Freebits 🎟️" if currency == "Freebets" else "Jetons 🪙"
        super().__init__(title=f"🎯 Numéro(s) — x36 ({display_name})")
        self.cog = cog
        self.currency = currency
    async def on_submit(self, interaction: discord.Interaction):
        await self.cog.process_bet(interaction, "number_list", self.amount_input.value, self.number_input.value, self.currency)

class RouletteView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        self.user_currencies = {}
        options = [
            discord.SelectOption(label="Numéro(s) 0–36", value="number", emoji="🎯"),
            discord.SelectOption(label="Rouge", value="red", emoji="🔴"),
            discord.SelectOption(label="Noir", value="black", emoji="⚫"),
            discord.SelectOption(label="Pair", value="even", emoji="✌️"),
            discord.SelectOption(label="Impair", value="odd", emoji="☝️"),
            discord.SelectOption(label="Manque (1–18)", value="low", emoji="🔽"),
            discord.SelectOption(label="Passe (19–36)", value="high", emoji="🔼"),
            discord.SelectOption(label="1ère Douzaine", value="d1", emoji="1️⃣"),
            discord.SelectOption(label="2ème Douzaine", value="d2", emoji="2️⃣"),
            discord.SelectOption(label="3ème Douzaine", value="d3", emoji="3️⃣"),
            discord.SelectOption(label="1ère Colonne", value="c1", emoji="🟦"),
            discord.SelectOption(label="2ème Colonne", value="c2", emoji="🟦"),
            discord.SelectOption(label="3ème Colonne", value="c3", emoji="🟦"),
        ]
        self.select = discord.ui.Select(placeholder="🎰 Choisis ta mise...", options=options, custom_id="roulette_select", row=0)
        self.select.callback = self.select_callback
        self.add_item(self.select)
        cur_options = [
            discord.SelectOption(label="Jetons", value="Jetons", emoji="🪙"),
            discord.SelectOption(label="Freebits", value="Freebets", emoji="🎟️")
        ]
        self.currency_select = discord.ui.Select(placeholder="🔄 Changer ta devise par défaut...", options=cur_options, custom_id="roulette_curr_sel", row=1)
        self.currency_select.callback = self.currency_select_callback
        self.add_item(self.currency_select)
        
        self.currency_btn = discord.ui.Button(label="Ma Devise Actuelle", style=discord.ButtonStyle.secondary, custom_id="roulette_curr_info", row=2)
        self.currency_btn.callback = self.currency_info_callback
        self.add_item(self.currency_btn)

    async def currency_select_callback(self, interaction: discord.Interaction):
        data = load_casino()
        uid = str(interaction.user.id)
        if uid not in data["players"]:
            return await interaction.response.send_message("❌ Fais d'abord `/cash` pour t'inscrire !", ephemeral=True)
        val = self.currency_select.values[0]
        data["players"][uid]["currency"] = val
        save_casino(data)
        display_name = "Freebits 🎟️" if val == "Freebets" else "Jetons 🪙"
        try:
            await interaction.response.send_message(f"✅ Ta devise de mise est maintenant : **{display_name}**", ephemeral=True)
        except discord.errors.NotFound: pass

    async def currency_info_callback(self, interaction: discord.Interaction):
        data = load_casino()
        val = data["players"].get(str(interaction.user.id), {}).get("currency", "Jetons")
        display_name = "Freebits 🎟️" if val == "Freebets" else "Jetons 🪙"
        try:
            await interaction.response.send_message(f"ℹ️ Ta devise par défaut est actuellement : **{display_name}**", ephemeral=True)
        except discord.errors.NotFound: pass

    async def select_callback(self, interaction: discord.Interaction):
        val = self.select.values[0]
        data = load_casino()
        curr = data["players"].get(str(interaction.user.id), {}).get("currency", "Jetons")
        try:
            if val == "number": await interaction.response.send_modal(RouletteNumberModal(self.cog, curr))
            else:
                labels = {"red":"Rouge","black":"Noir","even":"Pair","odd":"Impair","low":"Manque","high":"Passe","d1":"1ère Douzaine","d2":"2ème Douzaine","d3":"3ème Douzaine","c1":"1ère Colonne","c2":"2ème Colonne","c3":"3ème Colonne"}
                await interaction.response.send_modal(RouletteSimpleModal(self.cog, val, labels[val], curr))
        except discord.errors.NotFound: pass

class RouletteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bets = []
        self.timer_end = 0
        self.spinning = False

    async def cog_load(self):
        self.bot.add_view(RouletteView(self))
        self.auto_setup.start()

    @tasks.loop(count=1)
    async def auto_setup(self):
        await self.bot.wait_until_ready()
        if not self.spinning:
            await self._update_message(
                "✅ **La table est ouverte.**\n"
                "• Utilise le bouton **Devise** pour choisir entre **Jetons 🪙** et **Freebits 🎟️**.\n"
                "• La roulette se lancera **45 secondes** après la première mise !\n"
                "• Les **Freebits 🎟️** ne paient que le profit net en **Jetons 🪙**."
            )

    def _format_history(self) -> str:
        data = load_casino()
        history = data.get("roulette_history", [])
        if not history:
            return ""
        
        last_5 = " ".join([f"{ROULETTE_COLORS.get(n, '🟢')} **{n}**" for n in history[-1:-6:-1]])
        
        counts = {i: 0 for i in range(37)}
        for n in history:
            counts[n] += 1
            
        sorted_counts = sorted(counts.items(), key=lambda x: x[1])
        cold = sorted_counts[:3]
        hot = sorted_counts[-3:]
        hot.reverse()
        
        hot_str = "  ".join([f"{ROULETTE_COLORS.get(n[0], '🟢')} **{n[0]}**" for n in hot if n[1] > 0])
        cold_str = "  ".join([f"{ROULETTE_COLORS.get(n[0], '🟢')} **{n[0]}**" for n in cold])
        
        if not hot_str: hot_str = "Aucun"
        if not cold_str: cold_str = "Aucun"
        
        return (
            f"\n\n### 📊 Statistiques (100 derniers)\n"
            f"**Derniers tirages :** {last_5}\n"
            f"**🔥 Numéros chauds :** {hot_str}\n"
            f"**❄️ Numéros froids :** {cold_str}"
        )

    async def _update_message(self, text: str, color: discord.Color = discord.Color.blurple()):
        casino_cog = self.bot.get_cog("Casino")
        if casino_cog:
            stats = self._format_history()
            
            bets_str = ""
            if self.bets:
                lines = []
                labels = {"red":"🔴 Rouge","black":"⚫ Noir","even":"✌️ Pair","odd":"☝️ Impair","low":"🔽 Manque","high":"🔼 Passe","d1":"1️⃣ 1ère Douzaine","d2":"2️⃣ 2ème Douzaine","d3":"3️⃣ 3ème Douzaine","c1":"🟦 1ère Colonne","c2":"🟦 2ème Colonne","c3":"🟦 3ème Colonne"}
                for b in self.bets:
                    c_emoji = "🎟️" if b["currency"] == "Freebets" else "🪙"
                    t_lbl = f"🎯 {b['target']}" if b["type"] == "number" else labels.get(b["type"], b["type"])
                    lines.append(f"• **{b['user'].display_name}** : {b['amount']:,} {c_emoji} sur {t_lbl}".replace(",", " "))
                bets_str = "\n\n### 💵 Mises en cours\n" + "\n".join(lines)
                
            embed = discord.Embed(title="🎡  ROULETTE EUROPÉENNE", description=text + bets_str + stats, color=color)
            await casino_cog.upsert_panel_message("roulette", embed=embed, view=RouletteView(self))

    async def process_bet(self, interaction: discord.Interaction, bet_type: str, amount_str: str, target_str: str | None, currency: str):
        try:
            amount = int(amount_str)
            if amount <= 0: raise ValueError
        except: return await interaction.response.send_message("❌ Mise invalide.", ephemeral=True)
        
        targets = []
        if bet_type == "number_list":
            targets = [int(x.strip()) for x in target_str.replace(",", " ").split() if x.strip().isdigit()]
            targets = [t for t in targets if 0 <= t <= 36]
            if not targets: return await interaction.response.send_message("❌ Numéros invalides.", ephemeral=True)
        
        total = amount * (len(targets) if targets else 1)
        data = load_casino()
        uid = str(interaction.user.id)
        p = data["players"].get(uid, {"balance":0,"freebets":0})
        
        if currency == "Jetons":
            if p["balance"] < total: return await interaction.response.send_message("❌ Pas assez de jetons !", ephemeral=True)
            p["balance"] -= total
            p["total_wagered_roulette"] = p.get("total_wagered_roulette", 0) + total
        else:
            if p.get("freebets", 0) < total: return await interaction.response.send_message("❌ Pas assez de freebets !", ephemeral=True)
            p["freebets"] -= total

        p["username"] = interaction.user.display_name
        save_casino(data)
        casino_cog = self.bot.get_cog("Casino")
        if casino_cog: casino_cog.trigger_leaderboard_update()
        
        if targets:
            for t in targets: self.bets.append({"user": interaction.user, "type": "number", "target": t, "amount": amount, "currency": currency})
        else:
            self.bets.append({"user": interaction.user, "type": bet_type, "target": None, "amount": amount, "currency": currency})
        
        await interaction.response.defer()
        if not self.timer_end:
            self.timer_end = time.time() + 45
            self.bot.loop.create_task(self.run_timer())
            await self._update_message(
                f"🎰 **Faites vos jeux !**\n"
                f"La roulette tourne <t:{int(self.timer_end)}:R>\n\n"
                f"**Rappel :** Les **Freebits 🎟️** paient le profit net. Les **Jetons 🪙** paient la mise totale."
            )
        else:
            await self._update_message(
                f"🎰 **Faites vos jeux !**\n"
                f"La roulette tourne <t:{int(self.timer_end)}:R>\n\n"
                f"**Rappel :** Les **Freebits 🎟️** paient le profit net. Les **Jetons 🪙** paient la mise totale."
            )

    async def run_timer(self):
        await self._update_message(f"🎰 **Faites vos jeux !** La roulette tourne <t:{int(self.timer_end)}:R>")
        # Simple sleep until timer ends — the 5s flush loop handles any queued updates
        while time.time() < self.timer_end:
            await asyncio.sleep(5)
        self.spinning = True
        await self.resolve()

    async def resolve(self):
        await self._update_message("🚫 **RIEN NE VA PLUS !**\n🎡 La roulette tourne...", discord.Color.greyple())
        await asyncio.sleep(4)
        win = random.randint(0, 36)
        
        data = load_casino()
        data.setdefault("roulette_history", []).append(win)
        if len(data["roulette_history"]) > 100:
            data["roulette_history"].pop(0)
        save_casino(data)
        
        color_emoji = ROULETTE_COLORS[win]
        results = [f"## {color_emoji} Numéro gagnant : **{win}** !\n"]
        winners = 0
        for b in self.bets:
            won = False
            p = 0
            t = b["type"]
            v = b["target"]
            a = b["amount"]
            if t == "number" and v == win: won = True; p = a * 36
            elif t == "red" and win in ROULETTE_RED: won = True; p = a * 2
            elif t == "black" and win in ROULETTE_BLACK: won = True; p = a * 2
            elif t == "even" and win != 0 and win % 2 == 0: won = True; p = a * 2
            elif t == "odd" and win % 2 != 0: won = True; p = a * 2
            elif t == "low" and 1 <= win <= 18: won = True; p = a * 2
            elif t == "high" and 19 <= win <= 36: won = True; p = a * 2
            elif t.startswith("d") and win != 0:
                if t == "d1" and 1 <= win <= 12: won = True; p = a * 3
                if t == "d2" and 13 <= win <= 24: won = True; p = a * 3
                if t == "d3" and 25 <= win <= 36: won = True; p = a * 3
            elif t.startswith("c") and win != 0:
                if t == "c1" and win % 3 == 1: won = True; p = a * 3
                if t == "c2" and win % 3 == 2: won = True; p = a * 3
                if t == "c3" and win % 3 == 0: won = True; p = a * 3
            if won:
                profit = p - a if b["currency"] == "Freebets" else p
                if profit > 0:
                    add_balance(b["user"].id, profit, username=b["user"].display_name)
                    c_name = "Freebits 🎟️" if b["currency"] == "Freebets" else "Jetons 🪙"
                    results.append(f"🎉 **{b['user'].display_name}** gagne **+{profit:,} 🪙** (mise de {a} {c_name})".replace(",", " "))
                    winners += 1
                elif profit == 0:
                    c_name = "Freebits 🎟️" if b["currency"] == "Freebets" else "Jetons 🪙"
                    results.append(f"🤝 **{b['user'].display_name}** est remboursé (mise de {a} {c_name})")
                    winners += 1
        if not winners and self.bets: results.append("📉 Aucun gagnant cette fois.")
        mc = discord.Color.green() if win == 0 else (discord.Color.red() if win in ROULETTE_RED else discord.Color.dark_theme())
        await self._update_message("\n".join(results), mc)
        self.bets = []; self.timer_end = 0; self.spinning = False
        casino_cog = self.bot.get_cog("Casino")
        if casino_cog: casino_cog.trigger_leaderboard_update()
        await asyncio.sleep(10)
        await self.auto_setup()

async def setup(bot):
    await bot.add_cog(RouletteCog(bot))
