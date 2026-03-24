import discord
from discord.ext import commands, tasks
import random
import time
import asyncio
import logging
from .core import (
    load_casino, save_casino, get_balance, add_balance, add_wager,
    BLACKJACK_CHANNEL_ID
)

logger = logging.getLogger(__name__)

def calculate_hand(hand: list) -> int:
    total, aces = 0, 0
    for card in hand:
        if card in ("J", "Q", "K"): total += 10
        elif card == "A": aces += 1; total += 11
        else: total += int(card)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

def draw_card() -> str:
    return random.choice(["2","3","4","5","6","7","8","9","10","J","Q","K","A"])

class BJPlayerState:
    def __init__(self, member: discord.Member, bet: int, seat_index: int, currency: str):
        self.member = member
        self.bet = bet
        self.currency = currency
        self.seat_index = seat_index
        self.hands = [[]]
        self.bets = [bet]
        self.current_hand_idx = 0
        self.done = False
        self.winnings = 0

class BlackjackView(discord.ui.View):
    def __init__(self, engine):
        super().__init__(timeout=None)
        self.engine = engine
        self.user_currencies = {}
        for i in range(5):
            occ = engine.seats[i]
            label = f"Siège {i+1}" + (f" ({occ.display_name[:10]})" if occ else "")
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.secondary if occ else discord.ButtonStyle.primary, custom_id=f"bj_seat_{i}", row=0)
            btn.callback = self.make_seat_callback(i)
            self.add_item(btn)
        cur_options = [
            discord.SelectOption(label="Jetons", value="Jetons", emoji="🪙"),
            discord.SelectOption(label="Freebits", value="Freebets", emoji="🎟️")
        ]
        self.currency_select = discord.ui.Select(placeholder="🔄 Changer ta devise par défaut...", options=cur_options, custom_id="bj_curr_sel", row=3)
        self.currency_select.callback = self.currency_select_callback
        self.add_item(self.currency_select)
        
        self.currency_btn = discord.ui.Button(label="Ma Devise Actuelle", style=discord.ButtonStyle.secondary, custom_id="bj_curr_info", row=4)
        self.currency_btn.callback = self.currency_info_callback
        self.add_item(self.currency_btn)
        self.btn_bet = discord.ui.Button(label="💰 Miser", style=discord.ButtonStyle.success, custom_id="bj_bet", row=1, disabled=(engine.state not in ("IDLE", "BETTING")))
        self.btn_bet.callback = self._btn_bet
        self.add_item(self.btn_bet)
        self.btn_quit = discord.ui.Button(label="🚪 Quitter", style=discord.ButtonStyle.danger, custom_id="bj_quit", row=1)
        self.btn_quit.callback = self._btn_quit
        self.add_item(self.btn_quit)
        if engine.state == "PLAYING":
            cp = engine.players[engine.current_turn_idx] if engine.current_turn_idx < len(engine.players) else None
            h = discord.ui.Button(label="🃏 Tirer", style=discord.ButtonStyle.primary, row=2)
            h.callback = self._btn_hit; self.add_item(h)
            s = discord.ui.Button(label="🛑 Rester", style=discord.ButtonStyle.danger, row=2)
            s.callback = self._btn_stand; self.add_item(s)
            d = discord.ui.Button(label="✌️ Doubler", style=discord.ButtonStyle.success, row=2)
            d.callback = self._btn_double
            if cp and (len(cp.hands[cp.current_hand_idx]) > 2 or get_balance(cp.member.id) < cp.bets[cp.current_hand_idx] or cp.currency == "Freebets"):
                d.disabled = True
            self.add_item(d)
            sp = discord.ui.Button(label="✂️ Split", style=discord.ButtonStyle.secondary, row=2)
            sp.callback = self._btn_split
            if cp:
                hand = cp.hands[cp.current_hand_idx]
                if len(hand) > 2 or (calculate_hand([hand[0]]) != calculate_hand([hand[1]]) and hand[0] != hand[1]) or get_balance(cp.member.id) < cp.bets[cp.current_hand_idx] or cp.currency == "Freebets":
                    sp.disabled = True
            self.add_item(sp)

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

    def make_seat_callback(self, idx):
        async def cb(interaction: discord.Interaction):
            engine = self.engine
            user = interaction.user
            curr = next((i for i, s in enumerate(engine.seats) if s and s.id == user.id), None)
            if engine.seats[idx] and engine.seats[idx].id != user.id:
                return await interaction.response.send_message("❌ Occupé", ephemeral=True)
            if curr == idx:
                return await interaction.response.send_message("ℹ️ Déjà assis", ephemeral=True)
            if engine.state == "PLAYING":
                if curr is not None:
                    engine.next_seats[user.id] = idx
                else:
                    engine.seats[idx] = user
                    await engine.update_ui()
                return await interaction.response.defer()
            if curr is not None:
                engine.seats[curr] = None
            engine.seats[idx] = user
            await engine.update_ui()
            await interaction.response.defer()
        return cb

    async def _btn_bet(self, interaction: discord.Interaction):
        if not any(s and s.id == interaction.user.id for s in self.engine.seats):
            return await interaction.response.send_message("❌ Assieds-toi", ephemeral=True)
        if interaction.user.id in self.engine.round_bets:
            return await interaction.response.send_message("❌ Déjà misé", ephemeral=True)
        data = load_casino()
        curr = data["players"].get(str(interaction.user.id), {}).get("currency", "Jetons")
        try:
            await interaction.response.send_modal(BlackjackBetModal(self.engine, curr))
        except discord.errors.NotFound: pass

    async def _btn_quit(self, interaction: discord.Interaction):
        seat = next((i for i, s in enumerate(self.engine.seats) if s and s.id == interaction.user.id), None)
        if seat is None:
            return await interaction.response.send_message("❌ Pas à table", ephemeral=True)
        if self.engine.state == "PLAYING" and any(p.member.id == interaction.user.id for p in self.engine.players):
            if interaction.user.id not in self.engine.waitlist_leave:
                self.engine.waitlist_leave.append(interaction.user.id)
            return await interaction.response.send_message("👋 Tu quitteras la table à la **fin de la partie**.", ephemeral=True)
        self.engine.seats[seat] = None
        self.engine.round_bets.pop(interaction.user.id, None)
        await interaction.response.send_message("👋 Quitté", ephemeral=True)
        await self.engine.update_ui()

    async def _btn_hit(self, interaction: discord.Interaction): await self.engine.handle_action(interaction, "hit")
    async def _btn_stand(self, interaction: discord.Interaction): await self.engine.handle_action(interaction, "stand")
    async def _btn_double(self, interaction: discord.Interaction): await self.engine.handle_action(interaction, "double")
    async def _btn_split(self, interaction: discord.Interaction): await self.engine.handle_action(interaction, "split")

class BlackjackBetModal(discord.ui.Modal):
    def __init__(self, engine, currency: str):
        display_name = "Freebits 🎟️" if currency == "Freebets" else "Jetons 🪙"
        super().__init__(title=f"💰 Mise ({display_name}) — Blackjack")
        self.engine = engine
        self.currency = currency
        self.amount = discord.ui.TextInput(label=f"Combien de {display_name} ?", placeholder="ex: 500")
        self.add_item(self.amount)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.amount.value)
            if val <= 0: raise ValueError
        except:
            return await interaction.response.send_message("❌ Invalide", ephemeral=True)
        data = load_casino()
        uid = str(interaction.user.id)
        p = data["players"].get(uid, {"balance":0,"freebets":0})
        if self.currency == "Jetons":
            if p["balance"] < val:
                return await interaction.response.send_message("❌ Pas assez", ephemeral=True)
            p["balance"] -= val
            p["total_wagered_blackjack"] = p.get("total_wagered_blackjack", 0) + val
        else:
            if p.get("freebets", 0) < val:
                return await interaction.response.send_message("❌ Pas assez", ephemeral=True)
            p["freebets"] -= val
        p["username"] = interaction.user.display_name
        save_casino(data)
        self.engine.round_bets[interaction.user.id] = (val, self.currency)
        display_name = "Freebits 🎟️" if self.currency == "Freebets" else "Jetons 🪙"
        await interaction.response.send_message(f"✅ {val} **{display_name}** misés !", ephemeral=True)
        self.engine.reset_betting_timer()

class BlackjackEngine:
    def __init__(self, bot, channel, message_id, cog):
        self.bot, self.channel, self.message_id, self.cog = bot, channel, message_id, cog
        self.seats = [None]*5; self.next_seats = {}; self.round_bets = {}; self.players = []
        self.dealer_hand = []; self.state = "IDLE"; self.current_turn_idx = 0
        self.betting_timer_end = 0; self.turn_timer_end = 0; self.last_update = 0
        self.waitlist_leave = []
        self.loop_task.start()

    @tasks.loop(seconds=5.0)
    async def loop_task(self):
        if self.state == "BETTING" and self.betting_timer_end and time.time() >= self.betting_timer_end:
            self.betting_timer_end = 0
            await self.start_playing_phase()
        elif self.state == "PLAYING" and self.turn_timer_end and time.time() >= self.turn_timer_end:
            self.turn_timer_end = 0
            if self.current_turn_idx < len(self.players):
                self.players[self.current_turn_idx].done = True
                self.current_turn_idx += 1
            await self.start_turn()

    def reset_betting_timer(self):
        seated = [s for s in self.seats if s]
        full = bool(seated) and all(s.id in self.round_bets for s in seated)
        delay = 10 if full else 45
        self.state = "BETTING"
        self.betting_timer_end = time.time() + delay
        self.bot.loop.create_task(self.update_ui(
            f"💰 **Phase de mise !** Mises fermées <t:{int(self.betting_timer_end)}:R>\n"
            f"• Utilise le sélecteur pour choisir entre **Jetons 🪙** et **Freebits 🎟️**.\n"
            f"• **10 secondes d'urgence** si tous les sièges ont misé !"
        ))

    async def start_playing_phase(self):
        # Éjecter les joueurs assis qui n'ont pas misé
        for i, seat in enumerate(self.seats):
            if seat and seat.id not in self.round_bets:
                self.seats[i] = None
        self.players = [BJPlayerState(s, self.round_bets[s.id][0], i, self.round_bets[s.id][1]) for i, s in enumerate(self.seats) if s and s.id in self.round_bets]
        if not self.players:
            self.state = "IDLE"
            self.round_bets.clear()
            await self.update_ui("⏸️ Table vide")
            return
        self.state = "PLAYING"
        self.dealer_hand = [draw_card(), draw_card()]
        for p in self.players:
            p.hands = [[draw_card(), draw_card()]]
            p.bets = [p.bet]
            p.done = False
        self.current_turn_idx = 0
        await self.start_turn()

    async def start_turn(self):
        while self.current_turn_idx < len(self.players):
            p = self.players[self.current_turn_idx]
            if p.done:
                self.current_turn_idx += 1
                continue
            if calculate_hand(p.hands[p.current_hand_idx]) >= 21:
                await self.next_hand_or_player()
                return
            break
        if self.current_turn_idx >= len(self.players):
            await self.resolve_dealer()
            return
        self.turn_timer_end = int(time.time()) + 30
        await self.update_ui(f"👉 Tour de {self.players[self.current_turn_idx].member.mention}\n⏳ Auto <t:{self.turn_timer_end}:R>")

    async def next_hand_or_player(self):
        p = self.players[self.current_turn_idx]
        if p.current_hand_idx < len(p.hands)-1: p.current_hand_idx += 1
        else: p.done = True; self.current_turn_idx += 1
        await self.start_turn()

    async def handle_action(self, interaction: discord.Interaction, action: str):
        if self.current_turn_idx >= len(self.players): return await interaction.response.send_message("❌ Pas ton tour", ephemeral=True)
        p = self.players[self.current_turn_idx]
        if p.member.id != interaction.user.id: return await interaction.response.send_message("❌ Pas ton tour", ephemeral=True)
        self.turn_timer_end = 0; hand = p.hands[p.current_hand_idx]
        if action == "hit": 
             hand.append(draw_card())
             if calculate_hand(hand) >= 21: await self.next_hand_or_player()
             else: await self.start_turn()
        elif action == "stand": await self.next_hand_or_player()
        elif action == "double":
            need = p.bets[p.current_hand_idx]
            if get_balance(p.member.id) < need: return await interaction.response.send_message("❌ Pas assez", ephemeral=True)
            add_balance(p.member.id, -need, username=p.member.display_name); add_wager(p.member.id, need, "blackjack", username=p.member.display_name); p.bets[p.current_hand_idx] += need
            hand.append(draw_card()); await self.next_hand_or_player()
        elif action == "split":
            need = p.bets[p.current_hand_idx]
            if get_balance(p.member.id) < need: return await interaction.response.send_message("❌ Pas assez", ephemeral=True)
            add_balance(p.member.id, -need, username=p.member.display_name); add_wager(p.member.id, need, "blackjack", username=p.member.display_name)
            c2 = hand.pop(); p.hands.insert(p.current_hand_idx+1, [c2, draw_card()]); p.bets.insert(p.current_hand_idx+1, need); hand.append(draw_card()); await self.start_turn()
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            pass

    async def resolve_dealer(self):
        self.state = "RESOLVING"; self.turn_timer_end = 0
        if any(calculate_hand(h) <= 21 for p in self.players for h in p.hands):
            while calculate_hand(self.dealer_hand) < 17: self.dealer_hand.append(draw_card())
        
        dv = calculate_hand(self.dealer_hand)
        res_str = ""
        data = load_casino()
        for p in self.players:
            j_won = 0
            fb_refund = 0
            cur_emoji = "🎟️" if p.currency == "Freebets" else "🪙"
            for i, hand in enumerate(p.hands):
                v, b = calculate_hand(hand), p.bets[i]; is_bj = (v==21 and len(hand)==2)
                if v > 21:
                    r = f"💥 Sauté (-{b} {cur_emoji})"
                elif dv > 21:
                    w = int(b*2.5) if is_bj else int(b*2)
                    prof = w - b if p.currency == "Freebets" else w
                    j_won += prof
                    r = f"💰 Gagné (+{prof} 🪙) (Croupier Sauté)"
                elif v > dv:
                    w = int(b*2.5) if is_bj else int(b*2)
                    prof = w - b if p.currency == "Freebets" else w
                    j_won += prof
                    r = f"🏆 Blackjack (+{prof} 🪙)" if is_bj else f"💰 Gagné (+{prof} 🪙)"
                elif v == dv:
                    if p.currency == "Freebets": fb_refund += b
                    else: j_won += b
                    r = f"🤝 Égalité (Remboursé {b} {cur_emoji})"
                else: 
                    r = f"💸 Perdu (-{b} {cur_emoji})"
                res_str += f"**{p.member.display_name}** Siège {p.seat_index+1}: {r}\n"
            
            uid = str(p.member.id)
            if uid in data["players"]:
                if j_won > 0:
                    data["players"][uid]["balance"] = data["players"][uid].get("balance", 0) + j_won
                    if data["players"][uid]["balance"] > data["players"][uid].get("max_balance", 0):
                        data["players"][uid]["max_balance"] = data["players"][uid]["balance"]
                if fb_refund > 0: data["players"][uid]["freebets"] = data["players"][uid].get("freebets", 0) + fb_refund
        save_casino(data)
        
        for p_id in self.waitlist_leave:
            seat_idx = next((i for i, s in enumerate(self.seats) if s and s.id == p_id), None)
            if seat_idx is not None:
                self.seats[seat_idx] = None
        self.waitlist_leave.clear()
        
        await self.update_ui(f"🏁 **Résultats du Round**\n\n{res_str}\n*Rappel: Profit net uniquement pour les Freebits 🎟️.*")
        casino = self.bot.get_cog("Casino")
        if casino: casino.trigger_leaderboard_update()
        await asyncio.sleep(8)
        self.round_bets.clear(); self.players = []; self.dealer_hand = []
        # Appliquer les changements de siège en attente
        for user_id, target_idx in list(self.next_seats.items()):
            curr_idx = next((i for i, s in enumerate(self.seats) if s and s.id == user_id), None)
            if curr_idx is not None and self.seats[target_idx] is None:
                self.seats[target_idx] = self.seats[curr_idx]
                self.seats[curr_idx] = None
        self.next_seats.clear()
        self.state = "IDLE"
        await self.update_ui("⏸️ En attente de mises")

    async def update_ui(self, msg: str = ""):
        self.last_update = time.time(); embed = self.cog.create_blackjack_embed(self, msg)
        try:
            m = await self.channel.fetch_message(self.message_id)
            await m.edit(embed=embed, view=BlackjackView(self))
        except Exception as e:
            logger.error("Blackjack update_ui error: %s", e, exc_info=True)

class BlackjackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot; self.engine = None
    async def cog_load(self): self.setup_task.start()
    @tasks.loop(seconds=5)
    async def setup_task(self):
        await self.bot.wait_until_ready()
        if self.engine is not None:
            self.setup_task.stop(); return
        c = self.bot.get_channel(BLACKJACK_CHANNEL_ID)
        if not c: return
        casino = self.bot.get_cog("Casino")
        if not casino: return
        tmp_engine = None
        try:
            # Récupère le message sans passer par upsert_panel_message (évite de queuer un dummy embed)
            data = load_casino()
            msg_id = data.get("messages", {}).get("blackjack")
            m = None
            if msg_id:
                try: m = await c.fetch_message(int(msg_id))
                except discord.NotFound: m = None
            if m is None:
                # Première fois : crée le message directement
                e = discord.Embed(title="🃏 TABLE DE BLACKJACK", description="⏸️ En attente...", color=discord.Color.green())
                m = await casino._do_upsert("blackjack", embed=e)
            if m is None: logger.warning("Blackjack setup: impossible de créer le message, retry..."); return
            tmp_engine = BlackjackEngine(self.bot, c, m.id, self)
            await m.edit(embed=self.create_blackjack_embed(tmp_engine), view=BlackjackView(tmp_engine))
            self.engine = tmp_engine
            tmp_engine = None
            self.setup_task.stop()
        except Exception as ex:
            logger.warning("Blackjack setup: échec (%s), retry in 5s", ex)
            if tmp_engine is not None:
                try: tmp_engine.loop_task.cancel()
                except Exception: pass

    def create_blackjack_embed(self, engine, msg=""):
        e = discord.Embed(title="🃏 BLACKJACK", description=msg or "\u200b", color=discord.Color.green() if engine.state in ("IDLE","BETTING") else discord.Color.gold())
        if engine.state in ("IDLE","BETTING"):
            s_l = ""
            for i in range(5):
                if engine.seats[i]:
                    b_info = ""
                    if engine.seats[i].id in engine.round_bets:
                        amt, cur = engine.round_bets[engine.seats[i].id]
                        c_emoji = "🎟️" if cur == "Freebets" else "🪙"
                        b_info = f"✅ (a misé {amt} {c_emoji})"
                    s_l += f"**Siège {i+1}** : {engine.seats[i].display_name} {b_info}\n"
                else: s_l += f"**Siège {i+1}** : Libre\n"
            e.add_field(name="🪑 Sièges", value=s_l, inline=False)
        else:
            dv = calculate_hand(engine.dealer_hand)
            e.add_field(name=f"🏦 Croupier ({'?' if engine.state=='PLAYING' else dv})", value=f"{engine.dealer_hand[0]} 🎴" if engine.state=="PLAYING" else " ".join(engine.dealer_hand), inline=False)
            p_l = ""
            for p in engine.players:
                h_str = ""
                for i, h in enumerate(p.hands): h_str += f"[{' '.join(h)} => {calculate_hand(h)}] "
                c_emoji = "🎟️" if p.currency == "Freebets" else "🪙"
                b_str = f"Mise: {sum(p.bets)} {c_emoji}"
                turn_str = "👈 **À TOI**" if not p.done and engine.state == "PLAYING" and p == engine.players[engine.current_turn_idx] else ""
                p_l += f"**{p.member.display_name}** (Siège {p.seat_index+1}): {h_str}| {b_str} {turn_str}\n"
            e.add_field(name="👥 Joueurs", value=p_l, inline=False)
        return e

async def setup(bot):
    await bot.add_cog(BlackjackCog(bot))
