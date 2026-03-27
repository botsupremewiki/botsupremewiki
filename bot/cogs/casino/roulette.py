import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
import time
from .core import (
    load_casino, save_casino, add_balance, add_game_count,
    get_seated_game, set_seated_game,
    ROULETTE_RED, ROULETTE_BLACK, ROULETTE_COLORS,
    ROULETTE_CHANNEL_ID
)

MAX_ROULETTE_SEATS = 10

_GAME_LABELS = {
    "roulette": "🎡 Roulette",
    "blackjack": "🃏 Blackjack",
}

def _seated_game_label(game: str) -> str:
    if not game:
        return game
    if game.startswith("slots_"):
        return f"🎰 Machine à Sous #{game.split('_')[1]}"
    if game.startswith("poker_"):
        return f"♠️ Poker — Table {game.split('_', 1)[1]}"
    return _GAME_LABELS.get(game, game)

def _parse_currency(raw: str) -> str:
    """Parse 'J'/'j' → 'Jetons', anything else → 'Freebets'."""
    return "Jetons" if raw.strip().upper() == "J" else "Freebets"


# ─── Modals ───────────────────────────────────────────────────────────────────

class RouletteSimpleModal(discord.ui.Modal):
    def __init__(self, cog, bet_type: str, bet_label: str):
        super().__init__(title=f"🎡 {bet_label}")
        self.cog = cog
        self.bet_type = bet_type
        self.amount_input = discord.ui.TextInput(
            label="Mise", placeholder="ex: 500", required=True
        )
        self.currency_input = discord.ui.TextInput(
            label="Devise  (J = Jetons 🪙 / F = Freebets 🎟️)",
            placeholder="J ou F",
            default="J",
            min_length=1, max_length=1, required=True
        )
        self.add_item(self.amount_input)
        self.add_item(self.currency_input)

    async def on_submit(self, interaction: discord.Interaction):
        currency = _parse_currency(self.currency_input.value)
        await self.cog.process_bet(interaction, self.bet_type, self.amount_input.value, None, currency)


class RouletteNumberModal(discord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="🎯 Numéro(s) — x36")
        self.cog = cog
        self.number_input = discord.ui.TextInput(
            label="Numéro(s) (ex: 0, 17, 32)",
            placeholder="Sépare par des virgules", required=True
        )
        self.amount_input = discord.ui.TextInput(
            label="Mise PAR numéro", placeholder="ex: 500", required=True
        )
        self.currency_input = discord.ui.TextInput(
            label="Devise  (J = Jetons 🪙 / F = Freebets 🎟️)",
            placeholder="J ou F",
            default="J",
            min_length=1, max_length=1, required=True
        )
        self.add_item(self.number_input)
        self.add_item(self.amount_input)
        self.add_item(self.currency_input)

    async def on_submit(self, interaction: discord.Interaction):
        currency = _parse_currency(self.currency_input.value)
        await self.cog.process_bet(interaction, "number_list", self.amount_input.value, self.number_input.value, currency)


# ─── Vue éphémère (pour joueurs assis) ───────────────────────────────────────

_BET_OPTIONS = [
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

_BET_LABELS = {
    "red": "Rouge", "black": "Noir", "even": "Pair", "odd": "Impair",
    "low": "Manque", "high": "Passe",
    "d1": "1ère Douzaine", "d2": "2ème Douzaine", "d3": "3ème Douzaine",
    "c1": "1ère Colonne", "c2": "2ème Colonne", "c3": "3ème Colonne",
}


class RouletteSeatView(discord.ui.View):
    """Vue éphémère affichée au joueur assis — dropdown de mise + Se lever."""

    def __init__(self, cog: "RouletteCog", user_id: int):
        super().__init__(timeout=300)
        self.cog = cog

        self.select = discord.ui.Select(
            placeholder="🎰 Choisis ta mise...",
            options=_BET_OPTIONS,
            custom_id=f"roulette_seat_sel_{user_id}",
            row=0,
        )
        self.select.callback = self._select_cb
        self.add_item(self.select)

        leave_btn = discord.ui.Button(
            label="🚪 Se lever",
            style=discord.ButtonStyle.danger,
            custom_id=f"roulette_seat_lv_{user_id}",
            row=1,
        )
        leave_btn.callback = self._leave_cb
        self.add_item(leave_btn)

    async def _select_cb(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        data = load_casino()
        if uid not in data.get("roulette_seats", []):
            return await interaction.response.send_message(
                "❌ Tu n'es plus assis(e). Clique de nouveau sur **S'asseoir**.",
                ephemeral=True
            )
        val = self.select.values[0]
        if val == "number":
            await interaction.response.send_modal(RouletteNumberModal(self.cog))
        else:
            await interaction.response.send_modal(RouletteSimpleModal(self.cog, val, _BET_LABELS[val]))
        await interaction.edit_original_response(view=RouletteSeatView(self.cog, interaction.user.id))

    async def _leave_cb(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        data = load_casino()
        seats = data.get("roulette_seats", [])
        if uid not in seats:
            return await interaction.response.edit_message(
                content="❌ Tu n'étais déjà plus assis(e).", view=None
            )
        seats.remove(uid)
        set_seated_game(uid, None, data)
        save_casino(data)
        await interaction.response.edit_message(
            content="👋 Tu as quitté la table de roulette.", view=None
        )
        status = (
            f"🎰 **Table ouverte** — {len(seats)}/{MAX_ROULETTE_SEATS} joueur(s) assis(e)(s).\n"
            "• La roulette tourne **45 secondes** après la première mise !"
            if seats else self._IDLE_STATUS
        )
        await self.cog._update_message(status)

    _IDLE_STATUS = (
        "✅ **La table est ouverte.**\n"
        "• Clique sur **🪑 S'asseoir** pour rejoindre la table.\n"
        "• La roulette se lancera **45 secondes** après la première mise !\n"
        "• **J = Jetons 🪙** | **F = Freebets 🎟️** dans le formulaire de mise.\n"
        "• Les **Freebets 🎟️** ne paient que le profit net en **Jetons 🪙**."
    )


# ─── Vue principale (message public, persistant) ──────────────────────────────

class RouletteView(discord.ui.View):
    """Vue permanente sur le message public — un seul bouton S'asseoir."""

    def __init__(self, cog: "RouletteCog"):
        super().__init__(timeout=None)
        self.cog = cog

        sit_btn = discord.ui.Button(
            label="🪑 S'asseoir",
            style=discord.ButtonStyle.success,
            custom_id="roulette_sit",
            row=0,
        )
        sit_btn.callback = self._sit_cb
        self.add_item(sit_btn)

    async def _sit_cb(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        data = load_casino()

        # Déjà assis ici → re-montrer l'éphémère
        if uid in data.get("roulette_seats", []):
            view = RouletteSeatView(self.cog, interaction.user.id)
            return await interaction.response.send_message(
                "🎰 Tu es assis(e) à la Roulette — utilise le menu pour miser !\n"
                "• **J = Jetons 🪙** | **F = Freebets 🎟️**\n"
                "• Les **Freebets 🎟️** ne paient que le profit net en **Jetons 🪙**.",
                view=view,
                ephemeral=True,
            )

        # Assis ailleurs
        seated_game = get_seated_game(uid, data)
        if seated_game:
            label = _seated_game_label(seated_game)
            return await interaction.response.send_message(
                f"❌ Tu es déjà assis(e) à **{label}**. Lève-toi d'abord !", ephemeral=True
            )

        # Table pleine
        seats = data.setdefault("roulette_seats", [])
        if len(seats) >= MAX_ROULETTE_SEATS:
            return await interaction.response.send_message(
                f"❌ La table est pleine ({MAX_ROULETTE_SEATS}/{MAX_ROULETTE_SEATS} sièges).",
                ephemeral=True,
            )

        # S'asseoir
        seats.append(uid)
        set_seated_game(uid, "roulette", data)
        save_casino(data)

        view = RouletteSeatView(self.cog, interaction.user.id)
        await interaction.response.send_message(
            "✅ Tu es maintenant assis(e) à la Roulette !\n"
            "• Utilise le menu ci-dessous pour choisir ta mise.\n"
            "• **J = Jetons 🪙** | **F = Freebets 🎟️**\n"
            "• Les **Freebets 🎟️** ne paient que le profit net en **Jetons 🪙**.",
            view=view,
            ephemeral=True,
        )
        await self.cog._update_message(
            f"🎰 **Table ouverte** — {len(seats)}/{MAX_ROULETTE_SEATS} joueur(s) assis(e)(s).\n"
            "• La roulette tourne **45 secondes** après la première mise !"
        )


# ─── Cog ──────────────────────────────────────────────────────────────────────

class RouletteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bets = []
        self.timer_end = 0
        self.spinning = False
        self._status_text = ""

    async def cog_load(self):
        self.bot.add_view(RouletteView(self))
        self.auto_setup.start()

    _IDLE_STATUS = (
        "✅ **La table est ouverte.**\n"
        "• Clique sur **🪑 S'asseoir** pour rejoindre la table.\n"
        "• La roulette se lancera **45 secondes** après la première mise !\n"
        "• **J = Jetons 🪙** | **F = Freebets 🎟️** dans le formulaire de mise.\n"
        "• Les **Freebets 🎟️** ne paient que le profit net en **Jetons 🪙**."
    )

    @tasks.loop(count=1)
    async def auto_setup(self):
        await self.bot.wait_until_ready()
        if not self.spinning:
            self.bot._startup_queue.put_nowait(lambda: self._update_message(self._IDLE_STATUS))

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
        self._status_text = text
        casino_cog = self.bot.get_cog("Casino")
        if casino_cog:
            data = load_casino()
            seats = data.get("roulette_seats", [])
            stats = self._format_history()

            bets_str = ""
            if self.bets:
                lines = []
                labels = {
                    "red": "🔴 Rouge", "black": "⚫ Noir", "even": "✌️ Pair", "odd": "☝️ Impair",
                    "low": "🔽 Manque", "high": "🔼 Passe",
                    "d1": "1️⃣ 1ère Douzaine", "d2": "2️⃣ 2ème Douzaine", "d3": "3️⃣ 3ème Douzaine",
                    "c1": "🟦 1ère Colonne", "c2": "🟦 2ème Colonne", "c3": "🟦 3ème Colonne",
                }
                for b in self.bets:
                    c_emoji = "🎟️" if b["currency"] == "Freebets" else "🪙"
                    t_lbl = f"🎯 {b['target']}" if b["type"] == "number" else labels.get(b["type"], b["type"])
                    lines.append(f"• **{b['user'].display_name}** : {b['amount']:,} {c_emoji} sur {t_lbl}".replace(",", " "))
                bets_str = "\n\n### 💵 Mises en cours\n" + "\n".join(lines)

            seat_names = []
            for uid in seats:
                p = data.get("players", {}).get(uid, {})
                name = p.get("username") or f"Joueur {uid[-4:]}"
                seat_names.append(name)
            seats_str = f"\n\n### 🪑 Joueurs assis ({len(seats)}/{MAX_ROULETTE_SEATS})\n"
            seats_str += (", ".join(seat_names) if seat_names else "*Personne*")

            embed = discord.Embed(
                title="🎡  ROULETTE EUROPÉENNE",
                description=text + bets_str + seats_str + stats,
                color=color
            )
            await casino_cog.upsert_panel_message("roulette", embed=embed, view=RouletteView(self))

    async def process_bet(self, interaction: discord.Interaction, bet_type: str, amount_str: str, target_str: str | None, currency: str):
        try:
            amount = int(amount_str)
            if amount <= 0: raise ValueError
        except:
            return await interaction.response.send_message("❌ Mise invalide.", ephemeral=True)

        targets = []
        if bet_type == "number_list":
            targets = [int(x.strip()) for x in target_str.replace(",", " ").split() if x.strip().isdigit()]
            targets = [t for t in targets if 0 <= t <= 36]
            if not targets:
                return await interaction.response.send_message("❌ Numéros invalides.", ephemeral=True)

        total = amount * (len(targets) if targets else 1)
        data = load_casino()
        uid = str(interaction.user.id)

        if uid not in data.get("roulette_seats", []):
            return await interaction.response.send_message(
                "❌ Tu n'es plus assis(e) à cette table.", ephemeral=True
            )

        p = data["players"].get(uid, {"balance": 0, "freebets": 0})

        if currency == "Jetons":
            if p["balance"] < total:
                return await interaction.response.send_message("❌ Pas assez de jetons !", ephemeral=True)
            p["balance"] -= total
            p["total_wagered_roulette"] = p.get("total_wagered_roulette", 0) + total
        else:
            if p.get("freebets", 0) < total:
                return await interaction.response.send_message("❌ Pas assez de freebets !", ephemeral=True)
            p["freebets"] -= total

        p["username"] = interaction.user.display_name
        save_casino(data)
        casino_cog = self.bot.get_cog("Casino")
        if casino_cog: casino_cog.trigger_leaderboard_update()

        if targets:
            for t in targets:
                self.bets.append({"user": interaction.user, "type": "number", "target": t, "amount": amount, "currency": currency})
        else:
            self.bets.append({"user": interaction.user, "type": bet_type, "target": None, "amount": amount, "currency": currency})

        await interaction.response.defer()
        if not self.timer_end:
            self.timer_end = time.time() + 45
            self.bot.loop.create_task(self.run_timer())
        await self._update_message(
            f"🎰 **Faites vos jeux !**\n"
            f"La roulette tourne <t:{int(self.timer_end)}:R>\n\n"
            f"**Rappel :** **J = Jetons 🪙** paient la mise totale. **F = Freebets 🎟️** paient le profit net."
        )

    async def run_timer(self):
        await self._update_message(f"🎰 **Faites vos jeux !** La roulette tourne <t:{int(self.timer_end)}:R>")
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
                    c_name = "Freebets 🎟️" if b["currency"] == "Freebets" else "Jetons 🪙"
                    results.append(f"🎉 **{b['user'].display_name}** gagne **+{profit:,} 🪙** (mise de {a} {c_name})".replace(",", " "))
                    winners += 1
                elif profit == 0:
                    c_name = "Freebets 🎟️" if b["currency"] == "Freebets" else "Jetons 🪙"
                    results.append(f"🤝 **{b['user'].display_name}** est remboursé (mise de {a} {c_name})")
                    winners += 1
        if not winners and self.bets:
            results.append("📉 Aucun gagnant cette fois.")
        mc = discord.Color.green() if win == 0 else (discord.Color.red() if win in ROULETTE_RED else discord.Color.dark_theme())
        await self._update_message("\n".join(results), mc)
        seen_players = set()
        for b in self.bets:
            uid = b["user"].id
            if uid not in seen_players:
                seen_players.add(uid)
                add_game_count(uid, "roulette", username=b["user"].display_name)
        # Éjecter les joueurs assis qui n'ont pas misé pendant ce tour
        if self.bets:
            players_who_bet = {str(b["user"].id) for b in self.bets}
            kick_data = load_casino()
            seats = kick_data.get("roulette_seats", [])
            idle = [uid for uid in list(seats) if uid not in players_who_bet]
            for uid in idle:
                seats.remove(uid)
                set_seated_game(uid, None, kick_data)
            if idle:
                save_casino(kick_data)

        self.bets = []; self.timer_end = 0; self.spinning = False
        casino_cog = self.bot.get_cog("Casino")
        if casino_cog: casino_cog.trigger_leaderboard_update()
        await asyncio.sleep(5)
        await self._update_message(self._IDLE_STATUS)


async def setup(bot):
    await bot.add_cog(RouletteCog(bot))
