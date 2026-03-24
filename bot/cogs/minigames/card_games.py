import discord
from discord.ext import commands, tasks
import random
import asyncio
import time
import os
import json

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════
CARD_GAMES_CHANNEL_ID = 1477368517337550848
CARD_GAMES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "card_games.json")

SUITS = ["♠️", "♥️", "♦️", "♣️"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

def make_deck():
    d = [{"rank": r, "suit": s} for r in RANKS for s in SUITS]
    random.shuffle(d)
    return d

def card_str(c):
    return f"{c['rank']}{c['suit']}"

def load_data():
    if not os.path.exists(CARD_GAMES_FILE):
        return {"message_id": None}
    try:
        with open(CARD_GAMES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"message_id": None}

def save_data(data):
    os.makedirs(os.path.dirname(CARD_GAMES_FILE), exist_ok=True)
    with open(CARD_GAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ═══════════════════════════════════════════════════════════
#  8 AMÉRICAIN (CRAZY 8) ENGINE
# ═══════════════════════════════════════════════════════════

class Crazy8Engine:
    def __init__(self, bot, channel, host):
        self.bot = bot
        self.channel = channel
        self.host = host
        self.players = [host]
        self.state = "LOBBY" # LOBBY, PLAYING, ENDED
        self.deck = []
        self.discard = []
        self.hands = {} # user_id -> list of cards
        self.turn_idx = 0
        self.direction = 1 # 1 or -1
        self.penalties = 0 # Cumulative +2
        self.current_suit = None # For 8 wild card
        self.last_action_time = 0
        self.message = None
        self.lock = asyncio.Lock()
        self.winners = [] # List of members who finished
        self.auto_task = None
        self._auto_drawn_this_turn = False

    async def add_player(self, user):
        if user.id not in [p.id for p in self.players] and len(self.players) < 6:
            self.players.append(user)
            return True
        return False

    async def remove_player(self, user_id):
        player = next((p for p in self.players if p.id == user_id), None)
        if player:
            self.players.remove(player)
            if self.state == "PLAYING":
                # Reset game if someone leaves mid-manche
                await self.channel.send(f"⚠️ **{player.display_name}** a quitté la partie. La manche est annulée et les cartes sont redistribuées !")
                await self.start_game()
            return True
        return False

    def get_current_player(self):
        return self.players[self.turn_idx]

    async def start_game(self):
        self.state = "PLAYING"
        self.deck = make_deck()
        self.discard = []
        self.hands = {p.id: [] for p in self.players}
        self.turn_idx = 0
        self.direction = 1
        self.penalties = 0
        self.winners = []
        
        # Distribute 7 cards
        for _ in range(7):
            for p in self.players:
                self.hands[p.id].append(self.deck.pop())
        
        # Rule of the starting player (Dame of Hearts, Diamonds, Spades, Clubs)
        start_player_idx = None
        for r_s in [("Q", "♥️"), ("Q", "♦️"), ("Q", "♠️"), ("Q", "♣️")]:
            for i, p in enumerate(self.players):
                # Search for the card in hand
                found_idx = None
                for ci, c in enumerate(self.hands[p.id]):
                    if c["rank"] == r_s[0] and c["suit"] == r_s[1]:
                        found_idx = ci
                        break
                if found_idx is not None:
                    # HE PLAYS IT IMMEDIATELY as requested
                    self.discard.append(self.hands[p.id].pop(found_idx))
                    start_player_idx = i
                    break
            if start_player_idx is not None: break
            
        if start_player_idx is None:
            start_player_idx = random.randint(0, len(self.players) - 1)
            self.discard.append(self.deck.pop())
            
        self.turn_idx = start_player_idx
        # Advance turn after the Queen play
        self.advance_turn()
        
        self.current_suit = self.discard[-1]["suit"]
        self.last_action_time = time.time()
        if self.auto_task: self.auto_task.cancel()
        self.auto_task = asyncio.create_task(self.auto_action_loop())
        await self.update_message()

    async def auto_action_loop(self):
        try:
            while self.state == "PLAYING":
                now = time.time()
                elapsed = now - self.last_action_time
                
                # Auto draw logic to mask "no playables"
                # "si un joueur ne peut pas jouer au bout de 3-6 secondes aléatoire automatiquement il piochera une carte"
                # "pour brouiller les pistes car il peut avoir une carte à poser mais piocher"
                
                # I'll implement a 3-6s random check
                if elapsed >= random.uniform(3, 6) and not getattr(self, "_auto_drawn_this_turn", False):
                    # Should he auto-draw? 
                    # If he has no playable card -> YES
                    # If he HAS playable card -> Maybe (to mask)
                    current_p = self.get_current_player()
                    should_draw = False
                    if not self.has_playable_card(current_p.id):
                        should_draw = True
                    else:
                        # 30% chance to draw even with card to "brouiller les pistes"
                        if random.random() < 0.3: should_draw = True
                    
                    if should_draw:
                        async with self.lock:
                            if self.state == "PLAYING" and self.get_current_player().id == current_p.id:
                                await self.process_draw(current_p.id, auto=True)
                                self._auto_drawn_this_turn = True
                                continue
                
                if elapsed >= 30:
                    current_p = self.get_current_player()
                    async with self.lock:
                        if self.state == "PLAYING" and self.get_current_player().id == current_p.id:
                            await self.process_draw(current_p.id, timeout=True)
                            continue
                            
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def has_playable_card(self, user_id):
        hand = self.hands.get(user_id, [])
        top = self.discard[-1]
        
        # If penalty is active, can only play A or 8
        if self.penalties > 0:
            return any(c["rank"] in ["A", "8"] for c in hand)
            
        for c in hand:
            if c["rank"] == "8": return True # Wild
            if c["rank"] == top["rank"] or c["suit"] == self.current_suit:
                return True
        return False

    async def process_play(self, user_id, card_indices):
        async with self.lock:
            if self.state != "PLAYING": return False
            cp = self.get_current_player()
            if cp.id != user_id: return False
            
            hand = self.hands[user_id]
            cards_to_play = [hand[i] for i in card_indices]
            
            # Check if all cards have the same rank (if multi-play)
            if len(cards_to_play) > 1:
                if not all(c["rank"] == cards_to_play[0]["rank"] for c in cards_to_play):
                    return False
            
            first_card = cards_to_play[0]
            top = self.discard[-1]
            
            # Rules for playing
            # If penalty active, must play A or 8
            if self.penalties > 0:
                if first_card["rank"] not in ["A", "8"]:
                    return False
            else:
                if first_card["rank"] != "8" and first_card["rank"] != top["rank"] and first_card["suit"] != self.current_suit:
                    return False
            
            # Handle 8 ending restriction
            if len(hand) == len(cards_to_play) and first_card["rank"] == "8":
                return "finish_on_8" # Special case error

            # All good, process play
            for i in sorted(card_indices, reverse=True):
                hand.pop(i)
                
            self.discard.extend(cards_to_play)
            last_card = cards_to_play[-1]
            self.current_suit = last_card["suit"]
            
            # Special effects
            skip = False
            replay = False
            
            if last_card["rank"] == "7":
                skip = True
            elif last_card["rank"] == "8":
                # Cancel penalty
                self.penalties = 0
                # Note: Suit change handled by a follow-up interaction or default to 8's suit?
                # User says: "tu peux choisir le symbole pour le prochain joueur"
                # I'll need a "Choice" state.
                self.state = "CHOOSING_SUIT"
                await self.update_message()
                return True
            elif last_card["rank"] == "10":
                replay = True
            elif last_card["rank"] == "J":
                if len(self.players) == 2:
                    replay = True
                else:
                    self.direction *= -1
            elif last_card["rank"] == "A":
                self.penalties += 2 * len(cards_to_play)

            # Check for win
            if not hand:
                self.winners.append(cp)
                if len(self.players) <= 1: # Should not happen mid-play
                    self.state = "ENDED"
                    await self.update_message()
                    return True
                # If player finished, remove from rotation?
                # Usually in 8-Américain, the game continues until one left or first one wins.
                # User says: "Le joueur qui a finit ses cartes le premier... est le président" (for Président)
                # For 8-Américain: "TU NE PEUX PAS FINIR SUR UN 8 SINON TU FINIS DERNIER"
                # I'll end the game when someone finishes? Or continue?
                # Let's assume the game ends when one player has 0 cards.
                self.state = "ENDED"
                await self.update_message()
                return True

            if not replay:
                self.advance_turn(skip=skip)
                
            self.last_action_time = time.time()
            self._auto_drawn_this_turn = False
            await self.update_message()
            return True

    def advance_turn(self, skip=False):
        steps = 2 if skip else 1
        self.turn_idx = (self.turn_idx + steps * self.direction) % len(self.players)

    async def process_draw(self, user_id, auto=False, timeout=False):
        if self.state != "PLAYING": return False
        cp = self.get_current_player()
        if cp.id != user_id: return False
        
        # If penalty + No A/8
        if self.penalties > 0:
            count = self.penalties
            for _ in range(count):
                if not self.deck: self.shuffle_discard()
                if self.deck: self.hands[user_id].append(self.deck.pop())
            self.penalties = 0
        else:
            if not self.deck: self.shuffle_discard()
            if self.deck: self.hands[user_id].append(self.deck.pop())
            
        self.advance_turn()
        self.last_action_time = time.time()
        self._auto_drawn_this_turn = False
        await self.update_message()
        return True

    def shuffle_discard(self):
        if len(self.discard) < 2: return
        top = self.discard.pop()
        self.deck = self.discard
        random.shuffle(self.deck)
        self.discard = [top]

    async def update_message(self):
        embed = self.create_embed()
        view = Crazy8View(self)
        if self.message:
            try:
                await self.message.edit(embed=embed, view=view)
            except Exception:
                self.message = await self.channel.send(embed=embed, view=view)
        else:
            self.message = await self.channel.send(embed=embed, view=view)

    def create_embed(self):
        embed = discord.Embed(title="8️⃣ 8 AMÉRICAIN", color=discord.Color.blue())
        if self.state == "LOBBY":
            embed.description = "En attente de joueurs (2-6)..."
            embed.add_field(name="Joueurs", value="\n".join([p.display_name for p in self.players]) or "Aucun")
        elif self.state == "PLAYING":
            cp = self.get_current_player()
            top = self.discard[-1]
            embed.description = f"Tour de **{cp.display_name}**"
            embed.add_field(name="Carte au milieu", value=f"**{card_str(top)}**" + (f" (Symbole demandé: {self.current_suit})" if top["rank"] == "8" else ""), inline=True)
            embed.add_field(name="Pioche", value=f"{len(self.deck)} cartes restantes", inline=True)
            
            p_list = []
            for i, p in enumerate(self.players):
                marker = "👉 " if i == self.turn_idx else ""
                p_list.append(f"{marker}{p.display_name} : {len(self.hands[p.id])} cartes")
            embed.add_field(name="Joueurs", value="\n".join(p_list), inline=False)
            
            if self.penalties > 0:
                embed.add_field(name="⚠️ Pénalité", value=f"Le prochain joueur piochera **{self.penalties}** cartes s'il ne pose pas un As ou un 8 !")
                
            rem = int(30 - (time.time() - self.last_action_time))
            embed.set_footer(text=f"Temps restant : {max(0, rem)}s")
            
        elif self.state == "CHOOSING_SUIT":
            cp = self.get_current_player()
            embed.description = f"🌈 **{cp.display_name}** doit choisir le nouveau symbole !"
            embed.color = discord.Color.orange()
            
        elif self.state == "ENDED":
            winner = self.winners[0] if self.winners else "Personne"
            embed.description = f"🎉 **{winner.display_name}** a gagné la partie !"
            embed.color = discord.Color.gold()
        return embed

# ═══════════════════════════════════════════════════════════
#  VIEWS
# ═══════════════════════════════════════════════════════════

class Crazy8View(discord.ui.View):
    def __init__(self, engine):
        super().__init__(timeout=None)
        self.engine = engine
        
        if engine.state == "LOBBY":
            self.add_lobby_buttons()
        elif engine.state == "PLAYING":
            self.add_game_buttons()
        elif engine.state == "CHOOSING_SUIT":
            self.add_suit_buttons()
        elif engine.state == "ENDED":
            self.add_item(discord.ui.Button(label="Nouvelle Partie", style=discord.ButtonStyle.success, custom_id="c8_restart"))

    def add_lobby_buttons(self):
        btn_join = discord.ui.Button(label="Rejoindre", style=discord.ButtonStyle.success, emoji="✅")
        btn_join.callback = self.join_callback
        self.add_item(btn_join)
        
        btn_start = discord.ui.Button(label="Lancer", style=discord.ButtonStyle.primary, emoji="🚀")
        btn_start.callback = self.start_callback
        self.add_item(btn_start)

    async def join_callback(self, interaction):
        if await self.engine.add_player(interaction.user):
            await self.engine.update_message()
            await interaction.response.defer()
        else:
            await interaction.response.send_message("Tu es déjà dans la partie ou elle est complète !", ephemeral=True)

    async def start_callback(self, interaction):
        if interaction.user.id != self.engine.host.id:
            return await interaction.response.send_message("Seul l'hôte peut lancer la partie !", ephemeral=True)
        if len(self.engine.players) < 2:
            return await interaction.response.send_message("Il faut au moins 2 joueurs !", ephemeral=True)
        await self.engine.start_game()
        await interaction.response.defer()

    def add_game_buttons(self):
        # View Cards Button (Ephemeral)
        btn_cards = discord.ui.Button(label="Mes Cartes", style=discord.ButtonStyle.secondary, emoji="🃏")
        btn_cards.callback = self.view_cards_callback
        self.add_item(btn_cards)
        
        # Draw Button
        btn_draw = discord.ui.Button(label="Piocher / Passer", style=discord.ButtonStyle.danger, emoji="📥")
        btn_draw.callback = self.draw_callback
        self.add_item(btn_draw)

    async def view_cards_callback(self, interaction):
        engine = self.engine
        if interaction.user.id not in engine.hands:
            return await interaction.response.send_message("Tu ne joues pas !", ephemeral=True)
        
        hand = engine.hands[interaction.user.id]
        cp = engine.get_current_player()
        is_turn = (cp.id == interaction.user.id)
        
        if not is_turn:
            msg = "Tes cartes : " + " ".join([card_str(c) for c in hand])
            return await interaction.response.send_message(msg, ephemeral=True)
            
        # If it's the user's turn, show play buttons in a new view (ephemeral)
        await interaction.response.send_message("Choisis tes cartes à jouer :", view=Crazy8PlayView(engine, interaction.user.id), ephemeral=True)

    async def draw_callback(self, interaction):
        if interaction.user.id != self.engine.get_current_player().id:
            return await interaction.response.send_message("Ce n'est pas ton tour !", ephemeral=True)
        await self.engine.process_draw(interaction.user.id)
        await interaction.response.defer()

    def add_suit_buttons(self):
        for suit in SUITS:
            btn = discord.ui.Button(label=suit, style=discord.ButtonStyle.secondary)
            btn.callback = self.make_suit_callback(suit)
            self.add_item(btn)

    def make_suit_callback(self, suit):
        async def callback(interaction):
            if interaction.user.id != self.engine.get_current_player().id:
                return await interaction.response.send_message("Ce n'est pas ton tour !", ephemeral=True)
            self.engine.current_suit = suit
            self.engine.state = "PLAYING"
            self.engine.advance_turn()
            self.engine.last_action_time = time.time()
            await self.engine.update_message()
            await interaction.response.defer()
        return callback

class Crazy8PlayView(discord.ui.View):
    def __init__(self, engine, user_id):
        super().__init__(timeout=60)
        self.engine = engine
        self.user_id = user_id
        self.selected_indices = []
        
        hand = engine.hands[user_id]
        # Multi-select or buttons? Let's use a Select menu for multi-choice if rank is same
        # Actually, let's just use buttons for each card, but highlighted if selected.
        # Max 25 items in view. Hand might be large.
        
        # We'll use a Select for the first card, then handle multi-play if possible
        options = []
        top = engine.discard[-1]
        
        for i, c in enumerate(hand):
            playable = False
            if engine.penalties > 0:
                if c["rank"] in ["A", "8"]: playable = True
            else:
                if c["rank"] == "8" or c["rank"] == top["rank"] or c["suit"] == engine.current_suit:
                    playable = True
            
            label = card_str(c)
            if not playable: label = f"❌ {label}"
            
            options.append(discord.SelectOption(label=label, value=str(i), description="Jouer cette carte"))

        if not options:
            self.add_item(discord.ui.Button(label="Aucune carte jouable", disabled=True))
        else:
            # We allow multi-select if they are the same rank
            select = discord.ui.Select(placeholder="Choisis une ou plusieurs cartes (même chiffre)...", options=options, min_values=1, max_values=min(len(options), 4))
            select.callback = self.select_callback
            self.add_item(select)

    async def select_callback(self, interaction):
        indices = [int(v) for v in interaction.data["values"]]
        res = await self.engine.process_play(self.user_id, indices)
        if res == "finish_on_8":
            await interaction.response.send_message("⚠️ Tu ne peux pas terminer la partie sur un 8 !", ephemeral=True)
        elif res:
            await interaction.edit_original_response(content="Carte jouée !", view=None)
        else:
            await interaction.response.send_message("Mise non valide (les cartes doivent avoir le même chiffre) !", ephemeral=True)

# ═══════════════════════════════════════════════════════════
#  PRÉSIDENT (TRASH/KING) ENGINE
# ═══════════════════════════════════════════════════════════

class PresidentEngine:
    def __init__(self, bot, channel, host):
        self.bot = bot
        self.channel = channel
        self.host = host
        self.players = [host]
        self.state = "LOBBY" # LOBBY, EXCHANGING, PLAYING, ROUND_ENDED
        self.hands = {} # user_id -> list of cards
        self.deck = []
        self.pile = [] # Cards currently in the middle (the trick)
        self.last_cards = [] # The last cards played in this trick
        self.turn_idx = 0
        self.disqualified = [] # Players who passed or finished in this trick
        self.roles = {} # user_id -> role string
        self.finished_order = [] # Order in which players finished their hands
        self.message = None
        self.lock = asyncio.Lock()
        self.last_action_time = 0

    async def add_player(self, user):
        if user.id not in [p.id for p in self.players] and len(self.players) < 8:
            self.players.append(user)
            return True
        return False

    async def remove_player(self, user_id):
        player = next((p for p in self.players if p.id == user_id), None)
        if player:
            self.players.remove(player)
            if self.state != "LOBBY":
                await self.channel.send(f"⚠️ **{player.display_name}** a quitté la partie. La manche est annulée et les rôles sont réinitialisés.")
                self.roles = {}
                await self.start_game()
            return True
        return False

    def get_current_player(self):
        return self.players[self.turn_idx]

    def get_rank_value(self, rank):
        order = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
        return order.index(rank)

    async def start_game(self):
        self.state = "PLAYING"
        self.deck = make_deck()
        self.hands = {p.id: [] for p in self.players}
        self.pile = []
        self.last_cards = []
        self.disqualified = []
        self.finished_order = []
        
        while self.deck:
            for p in self.players:
                if self.deck: self.hands[p.id].append(self.deck.pop())
        
        for h in self.hands.values():
            h.sort(key=lambda c: self.get_rank_value(c["rank"]))

        if not self.roles:
            self.turn_idx = random.randint(0, len(self.players) - 1)
        else:
            self.state = "EXCHANGING"
            self.exchanges_done = 0
            # Identify roles for exchange
            # President/Trash: 2 cards
            # VP/VT: 1 card
            await self.update_message()
            
        self.last_action_time = time.time()
        await self.update_message()

    async def process_exchange(self, user_id, card_indices):
        async with self.lock:
            if self.state != "EXCHANGING": return False
            role = self.roles.get(user_id)
            if not role: return False
            
            # President gives to Trash (2 cards)
            # VP gives to Vice-Trash (1 card)
            # Trash/Vice-Trash give their BEST cards (automatic)
            
            # Find target
            target_role = ""
            count = 0
            if role == "Président": target_role = "Trou du Cul"; count = 2
            elif role == "Vice-Président": target_role = "Vice-Trou du Cul"; count = 1
            else: return False
            
            if len(card_indices) != count: return False
            
            target_p = next((p for p in self.players if self.roles.get(p.id) == target_role), None)
            if not target_p:
                return False
            
            hand = self.hands[user_id]
            target_hand = self.hands[target_p.id]
            
            # Exchange
            for i in sorted(card_indices, reverse=True):
                target_hand.append(hand.pop(i))
            
            # Target (Trash/VT) gives best cards
            trash_count = count
            for _ in range(trash_count):
                best_idx = len(target_hand) - 1 # Deck is sorted, but wait, target_hand might not be
                target_hand.sort(key=lambda c: self.get_rank_value(c["rank"]))
                # The Trash gives the BEST cards (last ones in sorted hand)
                # But wait, we need to GIVE to the user_id
                hand.append(target_hand.pop())
            
            # Re-sort hands
            hand.sort(key=lambda c: self.get_rank_value(c["rank"]))
            target_hand.sort(key=lambda c: self.get_rank_value(c["rank"]))
            
            self.exchanges_done += count
            
            # Check if all exchanges done
            required = 0
            n = len(self.players)
            if n >= 2: required += 2 # Prez/Trash
            if n >= 4: required += 1 # VP/VT
            
            if self.exchanges_done >= required:
                self.state = "PLAYING"
                # Trou du cul starts
                self.turn_idx = next((i for i, p in enumerate(self.players) if self.roles.get(p.id) == "Trou du Cul"), 0)
                
            await self.update_message()
            return True

    async def process_play(self, user_id, card_indices):
        async with self.lock:
            if self.state != "PLAYING": return False
            cp = self.get_current_player()
            if cp.id != user_id: return False
            
            hand = self.hands[user_id]
            cards_to_play = [hand[i] for i in card_indices]
            
            if not all(c["rank"] == cards_to_play[0]["rank"] for c in cards_to_play): return False
            
            if self.last_cards:
                if len(cards_to_play) != len(self.last_cards): return False
                if self.get_rank_value(cards_to_play[0]["rank"]) < self.get_rank_value(self.last_cards[0]["rank"]): return False
            
            for i in sorted(card_indices, reverse=True): hand.pop(i)
            self.last_cards = cards_to_play; self.pile.extend(cards_to_play)
            
            closed = cards_to_play[0]["rank"] == "2"
            if not hand:
                if cards_to_play[0]["rank"] == "2":
                    await self.channel.send(f"🤣 **{cp.display_name}** a fini avec un 2... D'office **Trou du Cul** !")
                self.finished_order.append(cp)
                if len(self.finished_order) == len(self.players) - 1:
                    last_p = next((p for p in self.players if self.hands.get(p.id)), None)
                    if last_p:
                        self.finished_order.append(last_p)
                    self.state = "ROUND_ENDED"
                    await self.assign_roles(cp if cards_to_play[0]["rank"] == "2" else None)
                    await self.update_message()
                    return True
            
            if closed: self.last_cards = []; self.disqualified = []
            else: self.advance_turn()
            
            self.last_action_time = time.time()
            await self.update_message()
            return True

    async def assign_roles(self, penalty_player=None):
        order = self.finished_order[:]
        if penalty_player:
            # Move penalty_player to the end of order (Trou du Cul)
            if penalty_player in order:
                order.remove(penalty_player)
                order.append(penalty_player)

        n = len(order)
        self.roles = {}
        if n == 2: self.roles[order[0].id], self.roles[order[1].id] = "Président", "Trou du Cul"
        elif n == 3: self.roles[order[0].id], self.roles[order[1].id], self.roles[order[2].id] = "Président", "Civil", "Trou du Cul"
        elif n == 4: self.roles[order[0].id], self.roles[order[1].id], self.roles[order[2].id], self.roles[order[3].id] = "Président", "Vice-Président", "Vice-Trou du Cul", "Trou du Cul"
        else:
            self.roles[order[0].id], self.roles[order[1].id] = "Président", "Vice-Président"
            for i in range(2, n - 2): self.roles[order[i].id] = "Civil"
            self.roles[order[n-2].id], self.roles[order[n-1].id] = "Vice-Trou du Cul", "Trou du Cul"

    async def process_pass(self, user_id):
        async with self.lock:
            if self.state != "PLAYING": return False
            if self.get_current_player().id != user_id: return False
            self.disqualified.append(user_id)
            self.advance_turn()
            active_ids = [p.id for p in self.players if p.id not in self.disqualified and self.hands[p.id]]
            if len(active_ids) == 0:
                self.last_cards = []
                self.disqualified = []
            self.last_action_time = time.time()
            await self.update_message()
            return True

    def advance_turn(self):
        count = 0
        while count < len(self.players):
            self.turn_idx = (self.turn_idx + 1) % len(self.players)
            p = self.players[self.turn_idx]
            if p.id not in self.disqualified and self.hands[p.id]: break
            count += 1

    async def update_message(self):
        embed = self.create_embed(); view = PresidentView(self)
        if self.message:
            try: await self.message.edit(embed=embed, view=view)
            except Exception: self.message = await self.channel.send(embed=embed, view=view)
        else: self.message = await self.channel.send(embed=embed, view=view)

    def create_embed(self):
        embed = discord.Embed(title="👑 PRÉSIDENT", color=discord.Color.purple())
        if self.state == "LOBBY":
            embed.description = "En attente de joueurs (2-8)..."
            embed.add_field(name="Joueurs", value="\n".join([p.display_name for p in self.players]) or "Aucun")
        elif self.state == "PLAYING":
            cp, pile_str = self.get_current_player(), " ".join([card_str(c) for c in self.last_cards]) or "Vide"
            embed.description = f"Tour de **{cp.display_name}**"
            embed.add_field(name="Pile", value=f"**{pile_str}**", inline=True)
            p_list = []
            for i, p in enumerate(self.players):
                marker = "👉 " if i == self.turn_idx else ""
                role = self.roles.get(p.id, "Civil")
                p_list.append(f"{marker}{p.display_name} ({role}) : {len(self.hands[p.id])} cartes" + (" (🚫 Pass)" if p.id in self.disqualified else ""))
            embed.add_field(name="Joueurs", value="\n".join(p_list), inline=False)
            rem = int(30 - (time.time() - self.last_action_time))
            embed.set_footer(text=f"Temps restant : {max(0, rem)}s")
        elif self.state == "ROUND_ENDED":
            embed.description = "🏁 **Fin de la manche !**\n" + "\n".join([f"{i+1}. {p.display_name} ({self.roles[p.id]})" for i, p in enumerate(self.finished_order)])
        return embed

class PresidentView(discord.ui.View):
    def __init__(self, engine):
        super().__init__(timeout=None); self.engine = engine
        if engine.state == "LOBBY":
            bj = discord.ui.Button(label="Rejoindre", style=discord.ButtonStyle.success, emoji="✅")
            bl = discord.ui.Button(label="Lancer", style=discord.ButtonStyle.primary, emoji="🚀")
            bj.callback, bl.callback = self.join_callback, self.start_callback
            self.add_item(bj); self.add_item(bl)
        elif engine.state == "EXCHANGING":
            role = engine.roles.get(engine.host.id) # Just a placeholder
            be = discord.ui.Button(label="Donner Cartes", style=discord.ButtonStyle.primary, emoji="🎁")
            be.callback = self.exchange_callback
            self.add_item(be)
        elif engine.state == "PLAYING":
            bc = discord.ui.Button(label="Mes Cartes", style=discord.ButtonStyle.secondary, emoji="🃏")
            bp = discord.ui.Button(label="Passer / Fermer", style=discord.ButtonStyle.danger, emoji="⏭️")
            bc.callback, bp.callback = self.view_cards_callback, self.pass_callback
            self.add_item(bc); self.add_item(bp)
        elif engine.state == "ROUND_ENDED":
            br = discord.ui.Button(label="Prochaine Manche", style=discord.ButtonStyle.success, emoji="🔄")
            br.callback = self.start_callback
            self.add_item(br)

    async def join_callback(self, it):
        if await self.engine.add_player(it.user): await self.engine.update_message(); await it.response.defer()
        else: await it.response.send_message("Déjà dedans ou complet !", ephemeral=True)
    async def start_callback(self, it):
        if it.user.id != self.engine.host.id: return await it.response.send_message("Host uniquement !", ephemeral=True)
        await self.engine.start_game(); await it.response.defer()
    async def pass_callback(self, it):
        if it.user.id != self.engine.get_current_player().id: return await it.response.send_message("Pas ton tour !", ephemeral=True)
        await self.engine.process_pass(it.user.id); await it.response.defer()
    async def view_cards_callback(self, it):
        if it.user.id not in self.engine.hands: return await it.response.send_message("Pas de jeu !", ephemeral=True)
        if self.engine.get_current_player().id != it.user.id:
            h = self.engine.hands[it.user.id]
            return await it.response.send_message("Tes cartes : " + " ".join([card_str(c) for c in h]), ephemeral=True)
        await it.response.send_message("Joue :", view=PresidentPlayView(self.engine, it.user.id), ephemeral=True)

    async def exchange_callback(self, it):
        role = self.engine.roles.get(it.user.id)
        if role not in ["Président", "Vice-Président"]:
            return await it.response.send_message("Tu n'as pas à choisir de cartes, tes meilleures sont données automatiquement !", ephemeral=True)
        await it.response.send_message("Choisis les cartes à donner :", view=PresidentExchangeView(self.engine, it.user.id), ephemeral=True)

class PresidentExchangeView(discord.ui.View):
    def __init__(self, engine, uid):
        super().__init__(timeout=60); self.engine, self.uid = engine, uid
        role = engine.roles.get(uid)
        count = 2 if role == "Président" else 1
        options = [discord.SelectOption(label=card_str(c), value=str(i)) for i, c in enumerate(engine.hands[uid])]
        sel = discord.ui.Select(placeholder=f"Donne-lui {count} cartes...", options=options[:25], min_values=count, max_values=count)
        sel.callback = self.exchange_callback; self.add_item(sel)
    async def exchange_callback(self, it):
        indices = [int(v) for v in it.data["values"]]
        if await self.engine.process_exchange(self.uid, indices):
            await it.edit_original_response(content="Cartes données !", view=None)
        else: await it.response.send_message("Erreur lors de l'échange !", ephemeral=True)

class PresidentPlayView(discord.ui.View):
    def __init__(self, engine, uid):
        super().__init__(timeout=60); self.engine, self.uid = engine, uid
        options = []
        for i, c in enumerate(engine.hands[uid]):
            playable = True
            if engine.last_cards:
                if engine.get_rank_value(c["rank"]) < engine.get_rank_value(engine.last_cards[0]["rank"]): playable = False
            label = card_str(c); options.append(discord.SelectOption(label=label if playable else f"❌ {label}", value=str(i)))
        if not options: self.add_item(discord.ui.Button(label="Rien", disabled=True))
        else:
            sel = discord.ui.Select(placeholder="Cartes...", options=options[:25], min_values=1, max_values=4)
            sel.callback = self.play_callback; self.add_item(sel)
    async def play_callback(self, it):
        indices = [int(v) for v in it.data["values"]]
        if await self.engine.process_play(self.uid, indices): await it.edit_original_response(content="Joué !", view=None)
        else: await it.response.send_message("Invalide !", ephemeral=True)

# ═══════════════════════════════════════════════════════════
#  HUB & COG
# ═══════════════════════════════════════════════════════════

class CardGameHubView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.selected_game = "8_americain"

    @discord.ui.select(placeholder="🎮 Choisis ton jeu de cartes...", options=[
        discord.SelectOption(label="8 Américain", value="8_americain", emoji="8️⃣", description="2-6 joueurs, cartes spéciales et fun !"),
        discord.SelectOption(label="Président", value="president", emoji="🃏", description="2-8 joueurs, deviens le parrain de la table !")
    ], custom_id="card_game_select")
    async def select_game(self, interaction, select):
        self.selected_game = select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label="Lancer 🚀", style=discord.ButtonStyle.primary, custom_id="card_hub_start")
    async def start_btn(self, interaction, button):
        if self.selected_game == "8_americain":
            engine = Crazy8Engine(self.bot, interaction.channel, interaction.user)
            await engine.update_message()
            await interaction.response.send_message("Lobby 8 Américain créé !", ephemeral=True)
        else:
            engine = PresidentEngine(self.bot, interaction.channel, interaction.user)
            await engine.update_message()
            await interaction.response.send_message("Lobby Président créé !", ephemeral=True)

class CardGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    async def cog_load(self):
        self.setup_task.start()

    @tasks.loop(count=1)
    async def setup_task(self):
        await self.bot.wait_until_ready()
        await self._update_hub()

    async def _update_hub(self):
        channel = self.bot.get_channel(CARD_GAMES_CHANNEL_ID)
        if not channel: return
        
        data = load_data()
        msg_id = data.get("message_id")
        
        embed = discord.Embed(
            title="🃏 SALON DES JEUX DE CARTES 🃏",
            description=(
                "Bienvenue dans l'espace dédié aux amateurs de cartes !\n\n"
                "### 🎲 Jeux Disponibles :\n"
                "• **8 Américain** (8️⃣) : Débarrasse-toi de tes cartes en premier. Attention aux As et aux 8 !\n"
                "• **Président** (👑) : Gravis l'échelle sociale pour devenir le Président et faire la loi.\n\n"
                "--- \n"
                "Choisis ton jeu dans le menu ci-dessous et clique sur **Lancer** pour ouvrir un lobby."
            ),
            color=discord.Color.gold()
        )
        view = CardGameHubView(self.bot)
        
        if msg_id:
            try:
                msg = await channel.fetch_message(msg_id)
                await msg.edit(embed=embed, view=view)
                return
            except Exception: pass
            
        msg = await channel.send(embed=embed, view=view)
        data["message_id"] = msg.id
        save_data(data)

async def setup(bot):
    await bot.add_cog(CardGames(bot))
