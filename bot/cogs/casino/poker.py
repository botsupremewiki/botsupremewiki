import discord
from discord.ext import commands, tasks
import asyncio
import random
import time
import itertools
from collections import Counter
from functools import cmp_to_key
from .core import (
    load_casino, save_casino, get_balance, add_balance,
    POKER_CHANNEL_ID
)

# ═══════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i for i, r in enumerate(RANKS)}

PHASE_NAMES = {
    "WAITING":  "⏸️ En attente",
    "PREFLOP":  "🃏 Pré-Flop",
    "FLOP":     "🌊 Flop",
    "TURN":     "🔄 Turn",
    "RIVER":    "🏁 River",
    "SHOWDOWN": "🔥 Showdown",
}

# ═══════════════════════════════════════════════════════════
#  HAND EVALUATION
# ═══════════════════════════════════════════════════════════
def evaluate_hand(cards_str: list) -> tuple:
    if not cards_str or len(cards_str) < 5:
        return (0, [])

    cards = []
    for c in cards_str:
        suit_char = c[-1]
        rank_str  = c[:-1]
        cards.append((RANK_VALUES[rank_str], suit_char))

    best_score = -1
    best_tie   = []

    for combo in itertools.combinations(cards, 5):
        combo  = sorted(combo, key=lambda x: x[0], reverse=True)
        ranks  = [x[0] for x in combo]
        suits  = [x[1] for x in combo]

        is_flush    = len(set(suits)) == 1
        is_straight = False
        straight_top = ranks[0]

        if ranks == list(range(ranks[0], ranks[0] - 5, -1)):
            is_straight = True
        elif sorted(ranks) == [0, 1, 2, 3, 12]:
            is_straight  = True
            straight_top = 3

        counts = Counter(ranks)
        freq   = sorted(counts.values(), reverse=True)

        score = 0
        tie   = []

        if is_flush and is_straight:
            score = 9 if straight_top == 12 else 8
            tie   = [straight_top]
        elif freq == [4, 1]:
            score  = 7
            quad   = [r for r, c in counts.items() if c == 4][0]
            kicker = [r for r, c in counts.items() if c == 1][0]
            tie    = [quad, kicker]
        elif freq == [3, 2]:
            score = 6
            trip  = [r for r, c in counts.items() if c == 3][0]
            pair  = [r for r, c in counts.items() if c == 2][0]
            tie   = [trip, pair]
        elif is_flush:
            score = 5
            tie   = ranks
        elif is_straight:
            score = 4
            tie   = [straight_top]
        elif freq == [3, 1, 1]:
            score   = 3
            trip    = [r for r, c in counts.items() if c == 3][0]
            kickers = sorted([r for r, c in counts.items() if c == 1], reverse=True)
            tie     = [trip] + kickers
        elif freq == [2, 2, 1]:
            score  = 2
            pairs  = sorted([r for r, c in counts.items() if c == 2], reverse=True)
            kicker = [r for r, c in counts.items() if c == 1][0]
            tie    = pairs + [kicker]
        elif freq == [2, 1, 1, 1]:
            score   = 1
            pair    = [r for r, c in counts.items() if c == 2][0]
            kickers = sorted([r for r, c in counts.items() if c == 1], reverse=True)
            tie     = [pair] + kickers
        else:
            score = 0
            tie   = ranks

        if score > best_score:
            best_score = score
            best_tie   = tie
        elif score == best_score:
            for i in range(min(len(tie), len(best_tie))):
                if tie[i] > best_tie[i]:
                    best_tie = tie
                    break
                elif tie[i] < best_tie[i]:
                    break

    return (best_score, best_tie)


def format_hand_name(score: int) -> str:
    names = ["Hauteur", "Paire", "Double Paire", "Brelan", "Quinte",
             "Couleur", "Full House", "Carré", "Quinte Flush", "Quinte Flush Royale"]
    return names[score] if 0 <= score <= 9 else "?"


def compare_hands(h1, h2):
    if h1[0] > h2[0]: return 1
    if h1[0] < h2[0]: return -1
    for x, y in zip(h1[1], h2[1]):
        if x > y: return 1
        if x < y: return -1
    return 0


# ═══════════════════════════════════════════════════════════
#  PLAYER STATE
# ═══════════════════════════════════════════════════════════
class PlayerState:
    def __init__(self, member: discord.Member, buy_in: int):
        self.member           = member
        self.cards            = []
        self.bet_in_round     = 0
        self.total_bet_in_hand= 0
        self.chips            = buy_in
        self.is_folded        = False
        self.is_all_in        = False


# ═══════════════════════════════════════════════════════════
#  POKER ENGINE
# ═══════════════════════════════════════════════════════════
class PokerEngine:
    def __init__(self, bot, channel, table_name: str, big_blind: int, buy_in: int, cog: 'PokerCog'):
        self.bot              = bot
        self.channel          = channel
        self.table_name       = table_name
        self.big_blind        = big_blind
        self.initial_big_blind= big_blind
        self.buy_in           = buy_in
        self.cog              = cog

        self.players          = []   # [PlayerState]
        self.waitlist_join    = []   # [discord.Member]
        self.waitlist_leave   = []   # [discord.Member]

        self.dealer_idx       = 0
        self.current_turn_idx = -1
        self.hand_count       = 0

        self.pot              = 0
        self.board            = []
        self.deck             = []

        self.state            = "WAITING"
        self.current_bet      = 0
        self.last_raiser_idx  = -1
        self.acted_this_round : set = set()

        self.message_id       = None
        self.turn_task        = None
        self.timer_end        = 0
        self.close_after_hand = False
        self.is_running       = True
        self.lock             = asyncio.Lock()
        self.processing_end   = False

    # ── Helpers ───────────────────────────────────────────────────────
    def get_unfolded(self):
        return [p for p in self.players if not p.is_folded]

    def get_active(self):
        return [p for p in self.players if not p.is_folded and not p.is_all_in and p.chips > 0]

    def next_player_idx(self, from_idx: int) -> int:
        n = len(self.players)
        for i in range(1, n + 1):
            idx = (from_idx + i) % n
            p = self.players[idx]
            if not p.is_folded and not p.is_all_in and p.chips > 0:
                return idx
        return -1

    def _deduct(self, p_idx: int, amount: int):
        p      = self.players[p_idx]
        actual = min(p.chips, amount)
        p.chips            -= actual
        p.bet_in_round     += actual
        p.total_bet_in_hand+= actual
        self.pot           += actual
        if p.chips == 0:
            p.is_all_in = True
        return actual

    def _trigger_leaderboard(self):
        cas = self.bot.get_cog("Casino")
        if cas:
            cas.trigger_leaderboard_update()

    def _is_betting_round_over(self) -> bool:
        active = self.get_active()
        if not active:
            return True
        for p in active:
            if p.member.id not in self.acted_this_round:
                return False
            if p.bet_in_round < self.current_bet:
                return False
        return True

    def _fmt_card(self, card: str) -> str:
        return (card
                .replace('♠', '♠️')
                .replace('♥', '♥️')
                .replace('♦', '♦️')
                .replace('♣', '♣️'))

    def _board_display(self) -> str:
        visible = [self._fmt_card(c) for c in self.board]
        hidden  = ["🎴"] * (5 - len(visible))
        return " ".join(visible + hidden)

    # ── Hand flow ─────────────────────────────────────────────────────
    async def start_hand(self):
        if not self.is_running:
            return

        # Process departures
        for member in self.waitlist_leave:
            for p in self.players:
                if p.member.id == member.id and p.chips > 0:
                    add_balance(p.member.id, p.chips, username=member.display_name)
                    break
            self.players = [p for p in self.players if p.member.id != member.id]
            self.cog.active_players.discard(member.id)
        if self.waitlist_leave:
            self._trigger_leaderboard()
        self.waitlist_leave = []

        # Process arrivals
        for member in self.waitlist_join:
            if not any(p.member.id == member.id for p in self.players):
                self.players.append(PlayerState(member, self.buy_in))
        self.waitlist_join = []

        if len(self.players) < 2:
            self.state = "WAITING"
            await self.update_ui("⏸️ **En attente de joueurs...**\nIl faut au moins **2 joueurs** pour commencer.")
            return

        # Blind escalation every 8 hands
        self.hand_count += 1
        if self.hand_count > 1 and (self.hand_count - 1) % 8 == 0:
            new_bb = self.big_blind * 2
            if new_bb < self.buy_in:
                self.big_blind = new_bb
                await self.channel.send(
                    f"🔶 **Les blindes doublent !** SB: **{self.big_blind // 2}** | BB: **{self.big_blind}**"
                )

        self.state       = "PREFLOP"
        self.board       = []
        self.pot         = 0
        self.current_bet = 0
        self.last_raiser_idx = -1

        for p in self.players:
            p.cards             = []
            p.bet_in_round      = 0
            p.total_bet_in_hand = 0
            p.is_folded         = False
            p.is_all_in         = (p.chips <= 0)

        self.deck = [r + s for r in RANKS for s in SUITS]
        random.shuffle(self.deck)

        n      = len(self.players)
        sb_idx = (self.dealer_idx + 1) % n
        bb_idx = (self.dealer_idx + 2) % n
        sb_amt = max(1, self.big_blind // 2)

        self._deduct(sb_idx, sb_amt)
        self._deduct(bb_idx, self.big_blind)
        self.current_bet     = self.big_blind
        self.last_raiser_idx = bb_idx
        self.acted_this_round.clear()

        for _ in range(2):
            for p in self.players:
                p.cards.append(self.deck.pop())

        first_to_act = self.next_player_idx(bb_idx)
        self.current_turn_idx = first_to_act
        await self.start_turn()

    async def start_turn(self):
        if not self.is_running:
            return

        if len(self.get_unfolded()) <= 1:
            await self.end_hand()
            return

        if self._is_betting_round_over():
            await self._advance_phase()
            return

        if self.current_turn_idx == -1:
            await self._advance_phase()
            return

        cp = self.players[self.current_turn_idx]
        self.timer_end = int(time.time()) + 60
        phase = PHASE_NAMES.get(self.state, self.state)
        await self.update_ui(
            f"**{phase}** — C'est au tour de {cp.member.mention} de jouer.\n"
            f"⏳ Fin du temps : <t:{self.timer_end}:R>"
        )

        if self.turn_task:
            self.turn_task.cancel()
        self.turn_task = self.bot.loop.create_task(self._timeout_task())

    async def _timeout_task(self):
        try:
            await asyncio.sleep(60)
            if self.current_turn_idx < 0 or self.current_turn_idx >= len(self.players):
                return
            cp = self.players[self.current_turn_idx]
            if self.current_bet == cp.bet_in_round:
                await self.process_action(cp.member, "check", 0)
            else:
                await self.process_action(cp.member, "fold", 0)
        except asyncio.CancelledError:
            pass

    async def _advance_phase(self):
        for p in self.players:
            p.bet_in_round = 0
        self.current_bet     = 0
        self.last_raiser_idx = -1
        self.acted_this_round.clear()

        if self.state == "PREFLOP":
            self.state = "FLOP"
            for _ in range(3):
                self.board.append(self.deck.pop())
        elif self.state == "FLOP":
            self.state = "TURN"
            self.board.append(self.deck.pop())
        elif self.state == "TURN":
            self.state = "RIVER"
            self.board.append(self.deck.pop())
        elif self.state == "RIVER":
            self.state = "SHOWDOWN"
            await self.end_hand()
            return

        first = self.next_player_idx(self.dealer_idx - 1)
        self.current_turn_idx = first

        phase = PHASE_NAMES.get(self.state, self.state)
        await self.update_ui(f"**{phase} !** ✨ {self._board_display()}")
        await asyncio.sleep(1.5)
        await self.start_turn()

    # ── Actions ───────────────────────────────────────────────────────
    async def process_action(self, member: discord.Member, action: str, amount: int = 0):
        async with self.lock:
            if self.current_turn_idx < 0 or self.current_turn_idx >= len(self.players):
                return False, "❌ Pas de tour en cours."
            cp = self.players[self.current_turn_idx]
            if cp.member.id != member.id:
                return False, "❌ Ce n'est pas ton tour !"

            if self.turn_task:
                self.turn_task.cancel()
                self.turn_task = None

            if action == "fold":
                cp.is_folded = True

            elif action == "check":
                if self.current_bet > cp.bet_in_round:
                    return False, f"❌ Tu ne peux pas checker — la mise est de **{self.current_bet}** !"

            elif action == "call":
                to_call = self.current_bet - cp.bet_in_round
                if to_call <= 0:
                    return False, "❌ Rien à suivre, tu peux checker."
                self._deduct(self.current_turn_idx, to_call)
                self._trigger_leaderboard()

            elif action == "raise":
                if amount <= self.current_bet:
                    return False, f"❌ La relance doit dépasser la mise actuelle de **{self.current_bet}**."
                to_add = amount - cp.bet_in_round
                if to_add <= 0 or to_add > cp.chips:
                    return False, "❌ Montant invalide ou fonds insuffisants."
                self._deduct(self.current_turn_idx, to_add)
                self._trigger_leaderboard()
                self.current_bet     = cp.bet_in_round
                self.last_raiser_idx = self.current_turn_idx

            elif action == "all_in":
                if cp.chips <= 0:
                    return False, "❌ Tu n'as plus de jetons !"
                self._deduct(self.current_turn_idx, cp.chips)
                self._trigger_leaderboard()
                if cp.bet_in_round > self.current_bet:
                    self.current_bet     = cp.bet_in_round
                    self.last_raiser_idx = self.current_turn_idx

            else:
                return False, "❌ Action inconnue."

            self.acted_this_round.add(cp.member.id)

            next_idx = self.next_player_idx(self.current_turn_idx)
            self.current_turn_idx = next_idx if next_idx != -1 else -1

            await self.start_turn()
            return True, ""

    # ── End hand ──────────────────────────────────────────────────────
    async def end_hand(self):
        async with self.lock:
            if self.processing_end:
                return
            self.processing_end = True

            if self.turn_task:
                self.turn_task.cancel()
                self.turn_task = None

            unfolded = self.get_unfolded()
            pot_to_distribute = self.pot
            self.pot = 0 # Reset early to prevent race conditions during sleeps

            if len(unfolded) == 1:
                winner = unfolded[0]
                winner.chips += pot_to_distribute
                self._trigger_leaderboard()
                await self.update_ui(
                    f"🎉 **{winner.member.display_name}** remporte **{pot_to_distribute:,} jetons** !\n"
                    f"*(Les autres se sont tous couchés)*"
                )
            else:
                while len(self.board) < 5:
                    self.board.append(self.deck.pop())

                p_hands = {p: evaluate_hand(p.cards + self.board) for p in unfolded}

                sorted_players = sorted(
                    unfolded,
                    key=cmp_to_key(lambda a, b: compare_hands(p_hands[a], p_hands[b])),
                    reverse=True
                )

                # Build tiers (ex-aequo)
                tiers = []
                if sorted_players:
                    tier = [sorted_players[0]]
                    for p in sorted_players[1:]:
                        if compare_hands(p_hands[tier[0]], p_hands[p]) == 0:
                            tier.append(p)
                        else:
                            tiers.append(tier)
                            tier = [p]
                    tiers.append(tier)

                # Distribute with side-pots
                win_messages = []
                contributors = list(self.players)
                for tier in tiers:
                    if pot_to_distribute <= 0:
                        break
                    candidates = list(tier)
                    while candidates and pot_to_distribute > 0:
                        min_bet_c = [c.total_bet_in_hand for c in candidates if c.total_bet_in_hand > 0]
                        if not min_bet_c:
                            break
                        min_bet = min(min_bet_c)
                        side_pot = 0
                        for c in contributors:
                            pull = min(c.total_bet_in_hand, min_bet)
                            c.total_bet_in_hand -= pull
                            side_pot += pull
                            pot_to_distribute -= pull
                        split = side_pot // len(candidates)
                        rem   = side_pot % len(candidates)
                        for idx, c in enumerate(candidates):
                            gain = split + (1 if idx < rem else 0)
                            c.chips += gain
                            win_messages.append(
                                f"🏆 **{c.member.display_name}** — {format_hand_name(p_hands[c][0])} → **+{gain:,} jetons**"
                            )
                        candidates = [c for c in candidates if c.total_bet_in_hand > 0]

                self._trigger_leaderboard()

                board_str     = " ".join(self._fmt_card(c) for c in self.board)
                showdown_text = f"🔥 **SHOWDOWN !**\nPlateau : **{board_str}**\n\n"
                for p in unfolded:
                    hand_n    = format_hand_name(p_hands[p][0])
                    cards_str = " ".join(self._fmt_card(c) for c in p.cards)
                    showdown_text += f"▶️ **{p.member.display_name}** montre `{cards_str}` → **{hand_n}**\n"
                showdown_text += "\n**Résultats :**\n" + "\n".join(win_messages)
                await self.update_ui(showdown_text)

            await asyncio.sleep(15)

            # Eliminate broke players
            broke = [p for p in self.players if p.chips <= 0]
            for p in broke:
                self.cog.active_players.discard(p.member.id)
                try:
                    await self.channel.send(f"💀 **{p.member.display_name}** est éliminé(e) (plus de chips) !")
                except Exception:
                    pass
            self.players = [p for p in self.players if p.chips > 0]

            if not self.players:
                self.hand_count = 0 
                self.state = "WAITING"
                self.dealer_idx = 0
            else:
                self.dealer_idx = (self.dealer_idx + 1) % len(self.players)

            self.processing_end = False
            await self.start_hand()

    # ── Join helper ───────────────────────────────────────────────────
    async def join_player(self, interaction: discord.Interaction):
        """Vérifie les conditions et ajoute le joueur à la waitlist. Répond à l'interaction."""
        if any(p.member.id == interaction.user.id for p in self.players) or \
           any(m.id == interaction.user.id for m in self.waitlist_join):
            return await interaction.response.send_message("❌ Tu es déjà à cette table.", ephemeral=True)
        if interaction.user.id in self.cog.active_players:
            return await interaction.response.send_message("❌ Tu es déjà actif sur une autre table.", ephemeral=True)
        if get_balance(interaction.user.id) < self.buy_in:
            return await interaction.response.send_message(
                f"❌ Il te faut **{self.buy_in:,}** jetons pour rejoindre cette table.", ephemeral=True
            )
        add_balance(interaction.user.id, -self.buy_in, username=interaction.user.display_name)
        self.waitlist_join.append(interaction.user)
        self.cog.active_players.add(interaction.user.id)
        self._trigger_leaderboard()
        await interaction.response.send_message(
            f"✅ Tu rejoindras **Table {self.table_name}** à la prochaine main avec **{self.buy_in:,}** jetons.",
            ephemeral=True
        )
        await self.update_ui()

    # ── UI ────────────────────────────────────────────────────────────
    async def update_ui(self, status_msg: str = ""):
        if not self.is_running:
            return

        phase     = PHASE_NAMES.get(self.state, self.state)
        color_map = {
            "WAITING":  discord.Color.greyple(),
            "PREFLOP":  discord.Color.blue(),
            "FLOP":     discord.Color.teal(),
            "TURN":     discord.Color.orange(),
            "RIVER":    discord.Color.red(),
            "SHOWDOWN": discord.Color.gold(),
        }
        color = color_map.get(self.state, discord.Color.green())

        embed = discord.Embed(
            title=f"♠️ POKER — Table {self.table_name}  ({phase})",
            description=status_msg or "\u200b",
            color=color
        )

        # Table info
        sb = self.big_blind // 2
        embed.add_field(
            name="🏦 Table",
            value=(
                f"Buy-in: **{self.buy_in:,}** | Blindes: **{sb}/{self.big_blind}**"
                f" | Main #{self.hand_count}\n"
                f"*Cette table accepte uniquement les **Jetons**.*"
            ),
            inline=False
        )

        # Board
        board_str = self._board_display() if self.state != "WAITING" else "*(La partie n'a pas encore commencé)*"
        embed.add_field(name="🃏 Cartes Communes", value=board_str, inline=False)

        # Pot / current bet
        if self.state != "WAITING":
            embed.add_field(name="💰 Pot", value=f"**{self.pot:,}** jetons", inline=True)
        if self.state not in ("WAITING", "SHOWDOWN") and self.current_bet > 0:
            embed.add_field(name="📊 Mise Courante", value=f"**{self.current_bet}**", inline=True)

        # Players
        if self.players:
            n      = len(self.players)
            lines  = []
            for i, p in enumerate(self.players):
                tags = []
                if i == self.dealer_idx:                           tags.append("🔘 Dealer")
                if n >= 2 and i == (self.dealer_idx + 1) % n:     tags.append("SB")
                if n >= 3 and i == (self.dealer_idx + 2) % n:     tags.append("BB")
                tag_str = f" *({', '.join(tags)})*" if tags else ""

                if p.is_folded:
                    st = "~~Se couche~~"
                elif p.is_all_in:
                    st = "🔥 **ALL-IN**"
                elif self.state not in ("WAITING", "SHOWDOWN") and i == self.current_turn_idx:
                    st = "💬 **À TOI !**"
                else:
                    st = f"Mise: **{p.bet_in_round}**" if p.bet_in_round > 0 else "En attente"

                lines.append(f"{p.member.mention}{tag_str} — **{p.chips:,}** 🪙 | {st}")
            embed.add_field(name="👥 Joueurs", value="\n".join(lines), inline=False)

        # Waiting list
        if self.waitlist_join:
            names = ", ".join(m.display_name for m in self.waitlist_join)
            embed.add_field(name="⏳ En attente de la prochaine main", value=names, inline=False)

        # Choose view
        if self.state not in ("WAITING", "SHOWDOWN"):
            view = PokerActionView(self)
        else:
            view = PokerLobbyView(self)

        casino = self.bot.get_cog("Casino")
        if casino:
            msg = await casino.upsert_panel_message(
                f"poker_{self.table_name.lower()}", embed=embed, view=view
            )
            if msg:
                self.message_id = msg.id


# ═══════════════════════════════════════════════════════════
#  ACTION VIEW  (in-game: Fold / Check / Call / Raise / All-In / Voir Cartes)
# ═══════════════════════════════════════════════════════════
class PokerActionView(discord.ui.View):
    def __init__(self, engine: PokerEngine):
        super().__init__(timeout=None)
        self.engine = engine

        cp = None
        if 0 <= engine.current_turn_idx < len(engine.players):
            cp = engine.players[engine.current_turn_idx]

        can_check = cp is not None and engine.current_bet == cp.bet_in_round
        can_call  = (cp is not None
                     and engine.current_bet > cp.bet_in_round
                     and cp.chips > (engine.current_bet - cp.bet_in_round))
        can_raise = cp is not None and cp.chips > 0

        # Row 0 — main actions
        btn_fold = discord.ui.Button(
            label="Se Coucher", style=discord.ButtonStyle.danger,
            custom_id=f"pk_fold_{engine.table_name}", emoji="❌", row=0
        )
        btn_fold.callback = self._btn_fold
        self.add_item(btn_fold)

        btn_check = discord.ui.Button(
            label="Check", style=discord.ButtonStyle.secondary,
            custom_id=f"pk_check_{engine.table_name}", emoji="✋", row=0,
            disabled=not can_check
        )
        btn_check.callback = self._btn_check
        self.add_item(btn_check)

        btn_call = discord.ui.Button(
            label="Suivre", style=discord.ButtonStyle.primary,
            custom_id=f"pk_call_{engine.table_name}", emoji="💰", row=0,
            disabled=not can_call
        )
        btn_call.callback = self._btn_call
        self.add_item(btn_call)

        btn_raise = discord.ui.Button(
            label="Relancer", style=discord.ButtonStyle.success,
            custom_id=f"pk_raise_{engine.table_name}", emoji="📈", row=0,
            disabled=not can_raise
        )
        btn_raise.callback = self._btn_raise
        self.add_item(btn_raise)

        btn_allin = discord.ui.Button(
            label="All-In", style=discord.ButtonStyle.danger,
            custom_id=f"pk_allin_{engine.table_name}", emoji="🔥", row=0,
            disabled=(cp is None or cp.chips <= 0)
        )
        btn_allin.callback = self._btn_allin
        self.add_item(btn_allin)

        # Row 1 — utility
        btn_view = discord.ui.Button(
            label="👀 Voir mes Cartes", style=discord.ButtonStyle.secondary,
            custom_id=f"pk_view_{engine.table_name}", row=1
        )
        btn_view.callback = self._btn_view_cards
        self.add_item(btn_view)

        btn_join = discord.ui.Button(
            label="S'asseoir", style=discord.ButtonStyle.success,
            custom_id=f"pk_join_in_{engine.table_name}", emoji="♠️", row=1
        )
        btn_join.callback = self._btn_join_during_game
        self.add_item(btn_join)

        btn_leave = discord.ui.Button(
            label="🚪 Quitter (fin de main)", style=discord.ButtonStyle.secondary,
            custom_id=f"pk_leave_{engine.table_name}", row=1
        )
        btn_leave.callback = self._btn_leave
        self.add_item(btn_leave)

    async def _btn_fold(self, interaction: discord.Interaction):
        ok, err = await self.engine.process_action(interaction.user, "fold")
        if not ok: await interaction.response.send_message(err, ephemeral=True)
        else:
            try:
                await interaction.response.defer()
            except discord.errors.NotFound:
                pass

    async def _btn_check(self, interaction: discord.Interaction):
        ok, err = await self.engine.process_action(interaction.user, "check")
        if not ok: await interaction.response.send_message(err, ephemeral=True)
        else:
            try:
                await interaction.response.defer()
            except discord.errors.NotFound:
                pass

    async def _btn_call(self, interaction: discord.Interaction):
        ok, err = await self.engine.process_action(interaction.user, "call")
        if not ok: await interaction.response.send_message(err, ephemeral=True)
        else:
            try:
                await interaction.response.defer()
            except discord.errors.NotFound:
                pass

    async def _btn_raise(self, interaction: discord.Interaction):
        if 0 <= self.engine.current_turn_idx < len(self.engine.players):
            if self.engine.players[self.engine.current_turn_idx].member.id != interaction.user.id:
                return await interaction.response.send_message("❌ Ce n'est pas ton tour !", ephemeral=True)
        await interaction.response.send_modal(PokerRaiseModal(self.engine))

    async def _btn_allin(self, interaction: discord.Interaction):
        ok, err = await self.engine.process_action(interaction.user, "all_in")
        if not ok: await interaction.response.send_message(err, ephemeral=True)
        else:
            try:
                await interaction.response.defer()
            except discord.errors.NotFound:
                pass

    async def _btn_view_cards(self, interaction: discord.Interaction):
        for p in self.engine.players:
            if p.member.id == interaction.user.id:
                if not p.cards:
                    return await interaction.response.send_message("Tu n'as pas encore de cartes.", ephemeral=True)
                embed = discord.Embed(
                    title="🃏 Tes Cartes",
                    description=(
                        f"## {self.engine._fmt_card(p.cards[0])}  {self.engine._fmt_card(p.cards[1])}\n\n"
                        f"**Plateau actuel :** {self.engine._board_display()}"
                    ),
                    color=discord.Color.dark_theme()
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message("❌ Tu n'es pas dans cette partie !", ephemeral=True)

    async def _btn_leave(self, interaction: discord.Interaction):
        engine = self.engine
        if any(p.member.id == interaction.user.id for p in engine.players):
            if not any(m.id == interaction.user.id for m in engine.waitlist_leave):
                engine.waitlist_leave.append(interaction.user)
            await interaction.response.send_message(
                f"👋 {interaction.user.display_name} quittera la table à la **fin de la manche**.\n"
                "Ses jetons lui seront restitués automatiquement.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Tu n'es pas dans cette partie.", ephemeral=True)

    async def _btn_join_during_game(self, interaction: discord.Interaction):
        await self.engine.join_player(interaction)


# ═══════════════════════════════════════════════════════════
#  RAISE MODAL
# ═══════════════════════════════════════════════════════════
class PokerRaiseModal(discord.ui.Modal, title="Relancer"):
    amount_input = discord.ui.TextInput(
        label="Ton nouveau total de mise pour ce tour",
        placeholder="ex : 500 (doit dépasser la mise actuelle)",
        required=True
    )

    def __init__(self, engine: PokerEngine):
        super().__init__()
        self.engine = engine

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amt = int(self.amount_input.value)
        except ValueError:
            return await interaction.response.send_message("❌ Montant invalide.", ephemeral=True)
        ok, err = await self.engine.process_action(interaction.user, "raise", amt)
        if not ok: await interaction.response.send_message(err, ephemeral=True)
        else:       await interaction.response.defer()


# ═══════════════════════════════════════════════════════════
#  LOBBY VIEW  (waiting room: S'asseoir / Se lever)
# ═══════════════════════════════════════════════════════════
class PokerLobbyView(discord.ui.View):
    def __init__(self, engine: PokerEngine):
        super().__init__(timeout=None)
        self.engine = engine

    @discord.ui.button(label="S'asseoir", style=discord.ButtonStyle.success, emoji="♠️")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.engine.join_player(interaction)

    @discord.ui.button(label="Lancer la table", style=discord.ButtonStyle.primary, emoji="🚀")
    async def start_manual(self, interaction: discord.Interaction, button: discord.ui.Button):
        engine = self.engine
        async with engine.lock:
            if engine.state != "WAITING":
                return await interaction.response.send_message("❌ La table est déjà lancée.", ephemeral=True)
            
            total_p = len(engine.players) + len(engine.waitlist_join)
            if total_p < 2:
                return await interaction.response.send_message("❌ Il faut au moins **2 joueurs** pour lancer la table.", ephemeral=True)
            
            await interaction.response.send_message("🚀 Lancement de la table...", ephemeral=True)
            await engine.start_hand()

    @discord.ui.button(label="Se lever", style=discord.ButtonStyle.danger, emoji="🚪")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        engine = self.engine

        # In waitlist only (not yet playing)
        if any(m.id == interaction.user.id for m in engine.waitlist_join) and \
           not any(p.member.id == interaction.user.id for p in engine.players):
            engine.waitlist_join = [m for m in engine.waitlist_join if m.id != interaction.user.id]
            engine.cog.active_players.discard(interaction.user.id)
            add_balance(interaction.user.id, engine.buy_in, username=interaction.user.display_name)
            engine._trigger_leaderboard()
            return await interaction.response.send_message(
                f"👋 Tu as quitté la liste d'attente. **{engine.buy_in:,}** jetons remboursés.", ephemeral=True
            )

        # Currently playing
        if any(p.member.id == interaction.user.id for p in engine.players):
            if engine.state != "WAITING":
                if not any(m.id == interaction.user.id for m in engine.waitlist_leave):
                    engine.waitlist_leave.append(interaction.user)
                return await interaction.response.send_message(
                    "👋 Tu quitteras la table à la **fin de la manche**. Tes jetons te seront restitués.",
                    ephemeral=True
                )
            # State is WAITING → leave immediately
            for p in engine.players:
                if p.member.id == interaction.user.id and p.chips > 0:
                    add_balance(interaction.user.id, p.chips, username=interaction.user.display_name)
                    break
            engine.players = [p for p in engine.players if p.member.id != interaction.user.id]
            engine.cog.active_players.discard(interaction.user.id)
            engine._trigger_leaderboard()
            await interaction.response.send_message("👋 Tu as quitté la table.", ephemeral=True)
            await engine.update_ui()
            return

        await interaction.response.send_message("❌ Tu n'es pas à cette table.", ephemeral=True)


# ═══════════════════════════════════════════════════════════
#  COG
# ═══════════════════════════════════════════════════════════
class PokerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot            = bot
        self.tiers          = {}   # {name: PokerEngine}
        self.active_players : set = set()

    async def cog_load(self):
        self.setup_task.start()

    @tasks.loop(count=1)
    async def setup_task(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(POKER_CHANNEL_ID)
        if not channel:
            return

        self.tiers = {
            "Débutant":      PokerEngine(self.bot, channel, "Débutant",      10,   1_000,   self),
            "Intermédiaire": PokerEngine(self.bot, channel, "Intermédiaire", 50,   5_000,   self),
            "Expert":        PokerEngine(self.bot, channel, "Expert",        100,  10_000,  self),
            "Des Légendes":  PokerEngine(self.bot, channel, "Des Légendes",  1000, 100_000, self),
        }

        for engine in self.tiers.values():
            await engine.update_ui("⏸️ **En attente de joueurs...**\nClique sur **S'asseoir** pour rejoindre !")


async def setup(bot: commands.Bot):
    await bot.add_cog(PokerCog(bot))
