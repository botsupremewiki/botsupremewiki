import aiosqlite
import os
from datetime import datetime, timezone

DB_PATH = os.path.join("bot", "data", "rpg.db")


async def get_db():
    return await aiosqlite.connect(DB_PATH)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript("""
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS players (
                user_id     INTEGER PRIMARY KEY,
                class       TEXT    DEFAULT NULL,
                level       INTEGER DEFAULT 1,
                xp          INTEGER DEFAULT 0,
                gold        INTEGER DEFAULT 0,
                zone        INTEGER DEFAULT 1,
                stage       INTEGER DEFAULT 1,
                boss_stage  INTEGER DEFAULT 0,
                prestige_level INTEGER DEFAULT 0,
                current_hp  INTEGER DEFAULT NULL,
                energy      INTEGER DEFAULT 500,
                max_energy  INTEGER DEFAULT 2000,
                pvp_elo     INTEGER DEFAULT 1000,
                last_passive_regen TEXT DEFAULT NULL,
                last_daily  TEXT    DEFAULT NULL,
                daily_streak INTEGER DEFAULT 0,
                wb_weekly_dmg INTEGER DEFAULT 0,
                wb_weekly_attacks INTEGER DEFAULT 0,
                wb_week_start TEXT DEFAULT NULL,
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS hub_messages (
                hub_name    TEXT PRIMARY KEY,
                channel_id  INTEGER,
                message_id  INTEGER
            );

            CREATE TABLE IF NOT EXISTS inventory_equipment (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                item_id     TEXT    NOT NULL,
                slot_equipped TEXT  DEFAULT NULL,
                enhancement INTEGER DEFAULT 0,
                rarity      TEXT    DEFAULT 'commun',
                level       INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS inventory_materials (
                user_id     INTEGER NOT NULL,
                item_id     TEXT    NOT NULL,
                quantity    INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS inventory_consumables (
                user_id     INTEGER NOT NULL,
                item_id     TEXT    NOT NULL,
                quantity    INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS bank_equipment (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                item_id     TEXT    NOT NULL,
                enhancement INTEGER DEFAULT 0,
                rarity      TEXT    DEFAULT 'commun',
                level       INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS bank_materials (
                user_id     INTEGER NOT NULL,
                item_id     TEXT    NOT NULL,
                quantity    INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS bank_consumables (
                user_id     INTEGER NOT NULL,
                item_id     TEXT    NOT NULL,
                quantity    INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS bank_gold (
                user_id     INTEGER PRIMARY KEY,
                amount      INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS professions (
                user_id         INTEGER PRIMARY KEY,
                harvest_type    TEXT    DEFAULT NULL,
                harvest_level   INTEGER DEFAULT 0,
                harvest_xp      INTEGER DEFAULT 0,
                craft_type      TEXT    DEFAULT NULL,
                craft_level     INTEGER DEFAULT 0,
                craft_xp        INTEGER DEFAULT 0,
                conception_type TEXT    DEFAULT NULL,
                conception_level INTEGER DEFAULT 0,
                conception_xp   INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS market_listings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id   INTEGER NOT NULL,
                item_type   TEXT    NOT NULL,
                item_id     TEXT    NOT NULL,
                quantity    INTEGER DEFAULT 1,
                price       INTEGER NOT NULL,
                equipment_inv_id INTEGER DEFAULT NULL,
                equipment_enhancement INTEGER DEFAULT 0,
                equipment_rarity TEXT DEFAULT NULL,
                listed_at   TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (seller_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS active_trades (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                initiator_id INTEGER NOT NULL,
                target_id   INTEGER NOT NULL,
                channel_id  INTEGER,
                message_id  INTEGER,
                status      TEXT    DEFAULT 'pending',
                initiator_confirmed INTEGER DEFAULT 0,
                target_confirmed    INTEGER DEFAULT 0,
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS trade_items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id    INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                item_type   TEXT    NOT NULL,
                item_id     TEXT    NOT NULL,
                quantity    INTEGER DEFAULT 1,
                equipment_inv_id INTEGER DEFAULT NULL,
                gold        INTEGER DEFAULT 0,
                FOREIGN KEY (trade_id) REFERENCES active_trades(id)
            );

            CREATE TABLE IF NOT EXISTS player_titles (
                user_id     INTEGER NOT NULL,
                title_id    TEXT    NOT NULL,
                unlocked_at TEXT    DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, title_id)
            );

            CREATE TABLE IF NOT EXISTS title_progress (
                user_id     INTEGER NOT NULL,
                title_id    TEXT    NOT NULL,
                current_value INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, title_id)
            );

            CREATE TABLE IF NOT EXISTS relics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                relic_id    TEXT    NOT NULL,
                obtained_at TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS raids (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                boss_id     TEXT    NOT NULL,
                status      TEXT    DEFAULT 'waiting',
                leader_id   INTEGER,
                channel_id  INTEGER,
                message_id  INTEGER,
                created_at  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS raid_participants (
                raid_id     INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                joined_at   TEXT    DEFAULT (datetime('now')),
                PRIMARY KEY (raid_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS world_boss_weekly (
                user_id     INTEGER NOT NULL,
                week_start  TEXT    NOT NULL,
                damage      INTEGER DEFAULT 0,
                attacks     INTEGER DEFAULT 0,
                display_name TEXT   DEFAULT NULL,
                PRIMARY KEY (user_id, week_start)
            );

            CREATE TABLE IF NOT EXISTS player_quest_stats (
                user_id                  INTEGER PRIMARY KEY,
                world_boss_count         INTEGER DEFAULT 0,
                market_sells             INTEGER DEFAULT 0,
                market_buys              INTEGER DEFAULT 0,
                trade_count              INTEGER DEFAULT 0,
                dungeon_best_classique   INTEGER DEFAULT 0,
                dungeon_best_elite       INTEGER DEFAULT 0,
                dungeon_best_abyssal     INTEGER DEFAULT 0,
                raid_max_completed       INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS player_quest_claimed (
                user_id    INTEGER NOT NULL,
                quest_id   TEXT    NOT NULL,
                claimed_at TEXT    DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, quest_id)
            );
        """)
        await db.commit()
        # Migrations — colonnes ajoutées progressivement
        migrations = [
            "ALTER TABLE players ADD COLUMN display_name TEXT DEFAULT NULL",
            "ALTER TABLE players ADD COLUMN active_title TEXT DEFAULT NULL",
            "ALTER TABLE players ADD COLUMN pvp_wins INTEGER DEFAULT 0",
            "ALTER TABLE players ADD COLUMN pvp_losses INTEGER DEFAULT 0",
            "ALTER TABLE players ADD COLUMN zone INTEGER DEFAULT 1",
            "ALTER TABLE market_listings ADD COLUMN seller_name TEXT DEFAULT NULL",
            "ALTER TABLE active_trades ADD COLUMN gold_offered INTEGER DEFAULT 0",
            "ALTER TABLE active_trades ADD COLUMN gold_requested INTEGER DEFAULT 0",
            "ALTER TABLE world_boss_weekly ADD COLUMN display_name TEXT DEFAULT NULL",
            "UPDATE players SET max_energy=1000 WHERE max_energy=100",
            "UPDATE players SET energy=500 WHERE energy=100 AND max_energy=1000",
            # Migration MAX_ENERGY 1000 → 2000
            "UPDATE players SET max_energy=2000 WHERE max_energy=1000",
            # Niveau des items (refonte panoplies)
            "ALTER TABLE inventory_equipment ADD COLUMN level INTEGER DEFAULT 1",
            # Passif quête 1 : chance de gagner +1 énergie après combat gagné
            "ALTER TABLE players ADD COLUMN energy_on_win_chance REAL DEFAULT 0.0",
            # Pénalité de mort : blocage regen passive pendant 1h
            "ALTER TABLE players ADD COLUMN regen_blocked_until TEXT DEFAULT NULL",
            # Pénalité de mort : montants perdus (pour remboursement par potion)
            "ALTER TABLE players ADD COLUMN death_gold_lost INTEGER DEFAULT 0",
            "ALTER TABLE players ADD COLUMN death_energy_lost INTEGER DEFAULT 0",
            # Food buffs temporaires (JSON)
            "ALTER TABLE players ADD COLUMN food_buffs TEXT DEFAULT NULL",
            # Potions de combat pré-combat
            "ALTER TABLE players ADD COLUMN potion_revival_active INTEGER DEFAULT 0",
            "ALTER TABLE players ADD COLUMN potion_no_passive INTEGER DEFAULT 0",
            # World Boss personnel par joueur
            "ALTER TABLE players ADD COLUMN wb_personal_turn INTEGER DEFAULT 0",
            # PvP Classé — suivi des combats quotidiens
            "ALTER TABLE players ADD COLUMN pvp_ranked_today INTEGER DEFAULT 0",
            "ALTER TABLE players ADD COLUMN pvp_ranked_reset TEXT DEFAULT NULL",
            # PvP Classé — stats séparées
            "ALTER TABLE players ADD COLUMN pvp_ranked_wins INTEGER DEFAULT 0",
            "ALTER TABLE players ADD COLUMN pvp_ranked_losses INTEGER DEFAULT 0",
            # Runes appliquées sur équipements (JSON)
            "ALTER TABLE inventory_equipment ADD COLUMN rune_bonuses TEXT DEFAULT NULL",
            # World Boss — HP collectifs hebdomadaires
            """CREATE TABLE IF NOT EXISTS wb_weekly_config (
                week_start TEXT PRIMARY KEY,
                boss_hp    INTEGER NOT NULL
            )""",
            # Verrou combat global (1 seul combat à la fois par joueur)
            "ALTER TABLE players ADD COLUMN in_combat INTEGER DEFAULT 0",
            # Niveau des items en banque (préservation du niveau lors du dépôt)
            "ALTER TABLE bank_equipment ADD COLUMN level INTEGER DEFAULT 1",
            # Runes en banque
            "ALTER TABLE bank_equipment ADD COLUMN rune_bonuses TEXT DEFAULT NULL",
            # Niveau et runes dans le marché (hotel des ventes)
            "ALTER TABLE market_listings ADD COLUMN equipment_level INTEGER DEFAULT 1",
            "ALTER TABLE market_listings ADD COLUMN equipment_rune_bonuses TEXT DEFAULT NULL",
        ]
        for sql in migrations:
            try:
                await db.execute(sql)
            except Exception:
                pass  # colonne déjà existante
        await db.commit()


# ─── Players ───────────────────────────────────────────────────────────────

async def get_player(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM players WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def create_player(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO players (user_id, energy, max_energy) VALUES (?,500,2000)", (user_id,))
        await db.execute("INSERT OR IGNORE INTO professions (user_id) VALUES (?)", (user_id,))
        await db.execute("INSERT OR IGNORE INTO bank_gold (user_id, amount) VALUES (?, 0)", (user_id,))
        await db.commit()
    return await get_player(user_id)


async def update_player(user_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)
        await db.commit()


async def get_or_create_player(user_id: int, display_name: str = None) -> dict:
    p = await get_player(user_id)
    if p is None:
        p = await create_player(user_id)
    if display_name:
        await update_player(user_id, display_name=display_name)
        p = dict(p)
        p["display_name"] = display_name
    return p


async def reset_all_in_combat():
    """Remet in_combat=0 pour tous les joueurs (appelé au démarrage du bot)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE players SET in_combat=0")
        await db.commit()


async def delete_player(user_id: int):
    """Supprime toutes les données RPG d'un joueur."""
    tables = [
        "players", "professions", "inventory_equipment", "inventory_materials",
        "inventory_consumables", "bank_equipment", "bank_materials",
        "bank_consumables", "bank_gold", "player_titles", "title_progress",
        "relics", "raid_participants", "world_boss_weekly",
        "market_listings", "active_trades", "trade_items",
    ]
    async with aiosqlite.connect(DB_PATH) as db:
        for table in tables:
            col = "user_id" if table not in ("market_listings",) else "seller_id"
            if table == "active_trades":
                await db.execute(
                    "DELETE FROM trade_items WHERE trade_id IN "
                    "(SELECT id FROM active_trades WHERE initiator_id=? OR target_id=?)",
                    (user_id, user_id)
                )
                await db.execute(
                    "DELETE FROM active_trades WHERE initiator_id=? OR target_id=?",
                    (user_id, user_id)
                )
                continue
            if table == "trade_items":
                continue  # déjà géré avec active_trades
            try:
                await db.execute(f"DELETE FROM {table} WHERE {col}=?", (user_id,))
            except Exception:
                pass
        await db.commit()


# ─── Hub Messages ──────────────────────────────────────────────────────────

async def get_hub_message(hub_name: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM hub_messages WHERE hub_name=?", (hub_name,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def set_hub_message(hub_name: str, channel_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO hub_messages (hub_name, channel_id, message_id) VALUES (?,?,?)",
            (hub_name, channel_id, message_id)
        )
        await db.commit()


# ─── Inventory Equipment ───────────────────────────────────────────────────

async def get_equipment(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM inventory_equipment WHERE user_id=? ORDER BY slot_equipped IS NULL, slot_equipped, id",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def add_equipment(user_id: int, item_id: str, rarity: str = "commun",
                        enhancement: int = 0, level: int = 1, rune_bonuses: str | None = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO inventory_equipment (user_id, item_id, rarity, enhancement, level, rune_bonuses) VALUES (?,?,?,?,?,?)",
            (user_id, item_id, rarity, enhancement, level, rune_bonuses)
        )
        await db.commit()
        return cur.lastrowid


async def equip_item(user_id: int, inv_id: int, slot: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE inventory_equipment SET slot_equipped=NULL WHERE user_id=? AND slot_equipped=?",
            (user_id, slot)
        )
        await db.execute(
            "UPDATE inventory_equipment SET slot_equipped=? WHERE id=? AND user_id=?",
            (slot, inv_id, user_id)
        )
        await db.commit()


async def unequip_item(user_id: int, inv_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE inventory_equipment SET slot_equipped=NULL WHERE id=? AND user_id=?",
            (inv_id, user_id)
        )
        await db.commit()


async def remove_equipment(user_id: int, inv_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM inventory_equipment WHERE id=? AND user_id=?", (inv_id, user_id))
        await db.commit()


async def add_rune_to_equipment(user_id: int, inv_id: int, effect: str, value: int):
    """Accumule le bonus d'une rune sur un équipement (JSON dans rune_bonuses)."""
    import json
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT rune_bonuses FROM inventory_equipment WHERE id=? AND user_id=?", (inv_id, user_id)
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return
        existing = json.loads(row["rune_bonuses"] or "{}")
        existing[effect] = existing.get(effect, 0) + value
        await db.execute(
            "UPDATE inventory_equipment SET rune_bonuses=? WHERE id=? AND user_id=?",
            (json.dumps(existing), inv_id, user_id),
        )
        await db.commit()


async def remove_rune_from_equipment(user_id: int, inv_id: int):
    """Retire la rune d'un équipement (remet rune_bonuses à NULL)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE inventory_equipment SET rune_bonuses=NULL WHERE id=? AND user_id=?",
            (inv_id, user_id),
        )
        await db.commit()


async def enhance_equipment(user_id: int, inv_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT enhancement FROM inventory_equipment WHERE id=? AND user_id=?", (inv_id, user_id)) as cur:
            row = await cur.fetchone()
        if not row or row["enhancement"] >= 10:
            return -1
        new_enh = row["enhancement"] + 1
        await db.execute("UPDATE inventory_equipment SET enhancement=? WHERE id=? AND user_id=?", (new_enh, inv_id, user_id))
        await db.commit()
        return new_enh


# ─── Inventory Materials ───────────────────────────────────────────────────

async def get_materials(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM inventory_materials WHERE user_id=? AND quantity>0 ORDER BY item_id",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def add_material(user_id: int, item_id: str, quantity: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO inventory_materials (user_id, item_id, quantity) VALUES (?,?,?) "
            "ON CONFLICT(user_id, item_id) DO UPDATE SET quantity=quantity+?",
            (user_id, item_id, quantity, quantity)
        )
        await db.commit()


async def get_material_qty(user_id: int, item_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT quantity FROM inventory_materials WHERE user_id=? AND item_id=?",
            (user_id, item_id)
        ) as cur:
            row = await cur.fetchone()
    return row[0] if row else 0


async def remove_material(user_id: int, item_id: str, quantity: int = 1) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT quantity FROM inventory_materials WHERE user_id=? AND item_id=?", (user_id, item_id)) as cur:
            row = await cur.fetchone()
        if not row or row["quantity"] < quantity:
            return False
        await db.execute(
            "UPDATE inventory_materials SET quantity=quantity-? WHERE user_id=? AND item_id=?",
            (quantity, user_id, item_id)
        )
        await db.commit()
        return True


# ─── Inventory Consumables ─────────────────────────────────────────────────

async def get_consumables(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM inventory_consumables WHERE user_id=? AND quantity>0 ORDER BY item_id",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def add_consumable(user_id: int, item_id: str, quantity: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO inventory_consumables (user_id, item_id, quantity) VALUES (?,?,?) "
            "ON CONFLICT(user_id, item_id) DO UPDATE SET quantity=quantity+?",
            (user_id, item_id, quantity, quantity)
        )
        await db.commit()


async def remove_consumable(user_id: int, item_id: str, quantity: int = 1) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT quantity FROM inventory_consumables WHERE user_id=? AND item_id=?", (user_id, item_id)) as cur:
            row = await cur.fetchone()
        if not row or row["quantity"] < quantity:
            return False
        await db.execute(
            "UPDATE inventory_consumables SET quantity=quantity-? WHERE user_id=? AND item_id=?",
            (quantity, user_id, item_id)
        )
        await db.commit()
        return True


# ─── Bank ──────────────────────────────────────────────────────────────────

async def get_bank_gold(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT amount FROM bank_gold WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row["amount"] if row else 0


async def add_bank_gold(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bank_gold (user_id, amount) VALUES (?,?) ON CONFLICT(user_id) DO UPDATE SET amount=amount+?",
            (user_id, amount, amount)
        )
        await db.commit()


async def remove_bank_gold(user_id: int, amount: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT amount FROM bank_gold WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row or row["amount"] < amount:
            return False
        await db.execute("UPDATE bank_gold SET amount=amount-? WHERE user_id=?", (amount, user_id))
        await db.commit()
        return True


async def get_bank_equipment(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM bank_equipment WHERE user_id=? ORDER BY id", (user_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def deposit_bank_equipment(user_id: int, item_id: str, rarity: str, enhancement: int, level: int = 1, rune_bonuses: str | None = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO bank_equipment (user_id, item_id, rarity, enhancement, level, rune_bonuses) VALUES (?,?,?,?,?,?)",
            (user_id, item_id, rarity, enhancement, level, rune_bonuses)
        )
        await db.commit()
        return cur.lastrowid


async def withdraw_bank_equipment(user_id: int, bank_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM bank_equipment WHERE id=? AND user_id=?", (bank_id, user_id)) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        await db.execute("DELETE FROM bank_equipment WHERE id=?", (bank_id,))
        await db.commit()
        return dict(row)


async def get_bank_materials(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM bank_materials WHERE user_id=? AND quantity>0", (user_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def deposit_bank_material(user_id: int, item_id: str, quantity: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bank_materials (user_id, item_id, quantity) VALUES (?,?,?) "
            "ON CONFLICT(user_id, item_id) DO UPDATE SET quantity=quantity+?",
            (user_id, item_id, quantity, quantity)
        )
        await db.commit()


async def withdraw_bank_material(user_id: int, item_id: str, quantity: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT quantity FROM bank_materials WHERE user_id=? AND item_id=?", (user_id, item_id)) as cur:
            row = await cur.fetchone()
        if not row or row["quantity"] < quantity:
            return False
        await db.execute("UPDATE bank_materials SET quantity=quantity-? WHERE user_id=? AND item_id=?", (quantity, user_id, item_id))
        await db.commit()
        return True


async def get_bank_consumables(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM bank_consumables WHERE user_id=? AND quantity>0", (user_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def deposit_bank_consumable(user_id: int, item_id: str, quantity: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bank_consumables (user_id, item_id, quantity) VALUES (?,?,?) "
            "ON CONFLICT(user_id, item_id) DO UPDATE SET quantity=quantity+?",
            (user_id, item_id, quantity, quantity)
        )
        await db.commit()


async def withdraw_bank_consumable(user_id: int, item_id: str, quantity: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT quantity FROM bank_consumables WHERE user_id=? AND item_id=?", (user_id, item_id)) as cur:
            row = await cur.fetchone()
        if not row or row["quantity"] < quantity:
            return False
        await db.execute("UPDATE bank_consumables SET quantity=quantity-? WHERE user_id=? AND item_id=?", (quantity, user_id, item_id))
        await db.commit()
        return True


# ─── Professions ───────────────────────────────────────────────────────────

async def get_professions(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM professions WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def update_professions(user_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE professions SET {sets} WHERE user_id=?", vals)
        await db.commit()


async def add_profession_xp(user_id: int, profession_type: str, xp_gain: int) -> tuple[int, int, bool]:
    """Returns (new_xp, new_level, leveled_up)"""
    prof = await get_professions(user_id)
    if not prof:
        return (0, 0, False)
    xp_col = f"{profession_type}_xp"
    lvl_col = f"{profession_type}_level"
    current_xp = prof[xp_col] + xp_gain
    current_level = prof[lvl_col]
    leveled_up = False
    while True:
        needed = xp_for_prof_level(current_level + 1)
        if current_xp >= needed and current_level < 100:
            current_xp -= needed
            current_level += 1
            leveled_up = True
        else:
            break
    await update_professions(user_id, **{xp_col: current_xp, lvl_col: current_level})
    return (current_xp, current_level, leveled_up)


def xp_for_prof_level(level: int) -> int:
    """XP requis pour passer au niveau suivant. Linéaire : profession niv 10 ≈ zone 1000."""
    return int(1000 * level)


# ─── Quêtes ────────────────────────────────────────────────────────────────

async def get_quest_stats(user_id: int) -> dict:
    """Retourne les compteurs de quêtes du joueur (crée la ligne si absente)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            "INSERT OR IGNORE INTO player_quest_stats (user_id) VALUES (?)", (user_id,)
        )
        await db.commit()
        cur = await db.execute(
            "SELECT * FROM player_quest_stats WHERE user_id = ?", (user_id,)
        )
        row = await cur.fetchone()
        return dict(row) if row else {}


async def increment_quest_stat(user_id: int, stat: str, amount: int = 1) -> None:
    """Incrémente un compteur de quête."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO player_quest_stats (user_id) VALUES (?)", (user_id,)
        )
        await db.execute(
            f"UPDATE player_quest_stats SET {stat} = {stat} + ? WHERE user_id = ?",
            (amount, user_id),
        )
        await db.commit()


async def update_dungeon_best(user_id: int, difficulty: str, level: int) -> None:
    """Met à jour le meilleur niveau de donjon complété si supérieur."""
    col = f"dungeon_best_{difficulty}"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO player_quest_stats (user_id) VALUES (?)", (user_id,)
        )
        await db.execute(
            f"UPDATE player_quest_stats SET {col} = MAX({col}, ?) WHERE user_id = ?",
            (level, user_id),
        )
        await db.commit()


async def update_raid_max(user_id: int, raid_level: int) -> None:
    """Met à jour le niveau de raid maximum complété si supérieur."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO player_quest_stats (user_id) VALUES (?)", (user_id,)
        )
        await db.execute(
            "UPDATE player_quest_stats SET raid_max_completed = MAX(raid_max_completed, ?) WHERE user_id = ?",
            (raid_level, user_id),
        )
        await db.commit()


async def get_claimed_quests(user_id: int) -> set:
    """Retourne l'ensemble des IDs de quêtes réclamées."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT quest_id FROM player_quest_claimed WHERE user_id = ?", (user_id,)
        )
        rows = await cur.fetchall()
        return {r[0] for r in rows}


async def claim_quest(user_id: int, quest_id: str) -> bool:
    """Marque une quête comme réclamée. Retourne False si déjà réclamée."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO player_quest_claimed (user_id, quest_id) VALUES (?, ?)",
                (user_id, quest_id),
            )
            await db.commit()
            return True
        except Exception:
            return False


# ─── Market ────────────────────────────────────────────────────────────────

async def add_market_listing(seller_id: int, seller_name: str, item_type: str, item_id: str,
                              rarity: str = "commun", enhancement: int = 0,
                              quantity: int = 1, price: int = 0,
                              level: int = 1, rune_bonuses: str | None = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO market_listings (seller_id, seller_name, item_type, item_id, quantity, price, "
            "equipment_rarity, equipment_enhancement, equipment_level, equipment_rune_bonuses) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (seller_id, seller_name, item_type, item_id, quantity, price, rarity, enhancement, level, rune_bonuses)
        )
        await db.commit()
        return cur.lastrowid


async def get_market_listings(item_type: str = None, exclude_user: int = None,
                               seller_id: int = None, limit: int = 100, offset: int = 0) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        conditions = []
        params = []
        if item_type:
            conditions.append("item_type=?")
            params.append(item_type)
        if exclude_user:
            conditions.append("seller_id!=?")
            params.append(exclude_user)
        if seller_id is not None:
            conditions.append("seller_id=?")
            params.append(seller_id)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.extend([limit, offset])
        async with db.execute(
            f"SELECT *, equipment_rarity AS rarity, equipment_enhancement AS enhancement, "
            f"equipment_level AS level, equipment_rune_bonuses AS rune_bonuses "
            f"FROM market_listings {where} ORDER BY listed_at DESC LIMIT ? OFFSET ?",
            params
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_my_market_listings(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM market_listings WHERE seller_id=? ORDER BY listed_at DESC", (user_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def remove_market_listing(listing_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM market_listings WHERE id=?", (listing_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return None
        await db.execute("DELETE FROM market_listings WHERE id=?", (listing_id,))
        await db.commit()
        return dict(row)


async def count_market_listings(item_type: str = None, exclude_user: int = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        conditions = []
        params = []
        if item_type:
            conditions.append("item_type=?")
            params.append(item_type)
        if exclude_user:
            conditions.append("seller_id!=?")
            params.append(exclude_user)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        async with db.execute(f"SELECT COUNT(*) FROM market_listings {where}", params) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ─── Titles ────────────────────────────────────────────────────────────────

async def get_title_bonuses(user_id: int) -> dict:
    """Agrège tous les bonus passifs des titres débloqués du joueur.

    Retourne un dict avec les clés :
      xp_pct, prestige_bonus_pct, gold_pct, monde_loot_pct,
      djc_stats_pct, dje_stats_pct, dja_stats_pct,
      raid_stats_pct, wb_stats_pct,
      harvest_xp_pct, craft_xp_pct, conception_xp_pct,
      hdv_discount_pct  (réduction en points de %, min 0)
    """
    from bot.cogs.rpg.models import TITLES
    unlocked = await get_player_titles(user_id)
    unlocked_ids = {t["title_id"] for t in unlocked}

    bonuses: dict = {
        "xp_pct":               0,
        "prestige_bonus_pct":   0,
        "gold_pct":             0,
        "monde_loot_pct":       0,
        "djc_stats_pct":        0,
        "dje_stats_pct":        0,
        "dja_stats_pct":        0,
        "raid_stats_pct":       0,
        "wb_stats_pct":         0,
        "harvest_xp_pct":       0,
        "craft_xp_pct":         0,
        "conception_xp_pct":    0,
        "hdv_discount_pct":     0.0,
    }
    for tid in unlocked_ids:
        title = TITLES.get(tid)
        if not title:
            continue
        bt = title.get("bonus_type")
        bv = title.get("bonus_value", 0)
        if bt and bv and bt in bonuses:
            bonuses[bt] += bv
    return bonuses


async def get_player_titles(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT title_id, unlocked_at FROM player_titles WHERE user_id=?", (user_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def unlock_title(user_id: int, title_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM player_titles WHERE user_id=? AND title_id=?", (user_id, title_id)) as cur:
            exists = await cur.fetchone()
        if exists:
            return False
        await db.execute("INSERT INTO player_titles (user_id, title_id) VALUES (?,?)", (user_id, title_id))
        await db.commit()
        return True


async def get_title_progress(user_id: int, title_id: str = None):
    """Returns int if title_id given, else list[dict] of all progress."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if title_id is not None:
            async with db.execute("SELECT current_value FROM title_progress WHERE user_id=? AND title_id=?", (user_id, title_id)) as cur:
                row = await cur.fetchone()
                return row[0] if row else 0
        else:
            async with db.execute("SELECT title_id, current_value AS count FROM title_progress WHERE user_id=?", (user_id,)) as cur:
                return [dict(r) for r in await cur.fetchall()]


async def update_title_progress(user_id: int, title_id: str, value: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO title_progress (user_id, title_id, current_value) VALUES (?,?,?) "
            "ON CONFLICT(user_id, title_id) DO UPDATE SET current_value=?",
            (user_id, title_id, value, value)
        )
        await db.commit()
        return value


async def increment_title_progress(user_id: int, title_id: str, amount: int = 1) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO title_progress (user_id, title_id, current_value) VALUES (?,?,?) "
            "ON CONFLICT(user_id, title_id) DO UPDATE SET current_value=current_value+?",
            (user_id, title_id, amount, amount)
        )
        async with db.execute("SELECT current_value FROM title_progress WHERE user_id=? AND title_id=?", (user_id, title_id)) as cur:
            row = await cur.fetchone()
        await db.commit()
        return row[0] if row else amount


# ─── Relics ────────────────────────────────────────────────────────────────

async def get_relics(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM relics WHERE user_id=? ORDER BY obtained_at", (user_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def add_relic(user_id: int, relic_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO relics (user_id, relic_id) VALUES (?,?)", (user_id, relic_id))
        await db.commit()


# ─── Raids ─────────────────────────────────────────────────────────────────

async def create_raid(boss_id: str, leader_id: int, channel_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO raids (boss_id, leader_id, channel_id, status) VALUES (?,?,?,'waiting')",
            (boss_id, leader_id, channel_id)
        )
        await db.execute("INSERT INTO raid_participants (raid_id, user_id) VALUES (?,?)", (cur.lastrowid, leader_id))
        await db.commit()
        return cur.lastrowid


async def get_raid(raid_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM raids WHERE id=?", (raid_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_raid_participants(raid_id: int) -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM raid_participants WHERE raid_id=?", (raid_id,)) as cur:
            return [r[0] for r in await cur.fetchall()]


async def join_raid(raid_id: int, user_id: int) -> bool:
    participants = await get_raid_participants(raid_id)
    if user_id in participants or len(participants) >= 5:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO raid_participants (raid_id, user_id) VALUES (?,?)", (raid_id, user_id))
        await db.commit()
    return True


async def update_raid(raid_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [raid_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE raids SET {sets} WHERE id=?", vals)
        await db.commit()


# ─── World Boss Weekly ─────────────────────────────────────────────────────

def current_week_start() -> str:
    now = datetime.now(timezone.utc)
    monday = now - __import__('datetime').timedelta(days=now.weekday())
    return monday.strftime("%Y-%m-%d")


async def add_wb_damage(user_id: int, display_name: str, damage: int):
    week = current_week_start()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO world_boss_weekly (user_id, week_start, damage, attacks, display_name) VALUES (?,?,?,1,?) "
            "ON CONFLICT(user_id, week_start) DO UPDATE SET damage=damage+?, attacks=attacks+1, display_name=?",
            (user_id, week, damage, display_name, damage, display_name)
        )
        await db.commit()


async def get_wb_server_stats() -> dict:
    """Retourne le nombre de joueurs actifs et leur niveau moyen (avec une classe)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) as cnt, AVG(level) as avg_level, AVG(prestige_level) as avg_prestige "
            "FROM players WHERE class IS NOT NULL"
        ) as cur:
            row = await cur.fetchone()
            return {
                "num_players":   row[0] or 0,
                "avg_level":     row[1] or 1,
                "avg_prestige":  row[2] or 0,
            }


async def get_or_create_wb_weekly_hp(week: str, boss_hp: int) -> int:
    """Récupère ou initialise les HP du boss de la semaine."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT boss_hp FROM wb_weekly_config WHERE week_start=?", (week,)) as cur:
            row = await cur.fetchone()
        if row:
            return row[0]
        await db.execute(
            "INSERT INTO wb_weekly_config (week_start, boss_hp) VALUES (?,?)",
            (week, boss_hp)
        )
        await db.commit()
        return boss_hp


async def get_wb_total_weekly_damage(week: str = None) -> int:
    """Total des dégâts infligés au boss cette semaine par tous les joueurs."""
    if week is None:
        week = current_week_start()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COALESCE(SUM(damage), 0) FROM world_boss_weekly WHERE week_start=?", (week,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def get_wb_leaderboard(week: str = None) -> list[dict]:
    if week is None:
        week = current_week_start()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT w.user_id, w.damage, w.attacks, w.display_name, p.active_title "
            "FROM world_boss_weekly w LEFT JOIN players p ON w.user_id = p.user_id "
            "WHERE w.week_start=? ORDER BY w.damage DESC LIMIT 100",
            (week,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_wb_weekly_attacks(user_id: int) -> int:
    week = current_week_start()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT attacks FROM world_boss_weekly WHERE user_id=? AND week_start=?",
            (user_id, week)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ─── Leaderboards ──────────────────────────────────────────────────────────

async def get_global_leaderboard(limit: int = 50) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT user_id, prestige_level, level, xp, zone, stage, display_name, active_title, class FROM players "
            "WHERE class IS NOT NULL ORDER BY prestige_level DESC, level DESC, zone DESC LIMIT ?",
            (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_pvp_leaderboard(limit: int = 50) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT user_id, pvp_elo, pvp_ranked_wins AS pvp_wins, pvp_ranked_losses AS pvp_losses, "
            "level, display_name, active_title FROM players "
            "WHERE class IS NOT NULL ORDER BY pvp_elo DESC LIMIT ?",
            (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_prestige_leaderboard(limit: int = 50) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT user_id, prestige_level, level, zone, display_name FROM players "
            "WHERE class IS NOT NULL AND prestige_level > 0 ORDER BY prestige_level DESC, zone DESC LIMIT ?",
            (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


# ─── Trades ────────────────────────────────────────────────────────────────

async def create_trade(initiator_id: int, target_id: int, gold_offered: int = 0,
                        gold_requested: int = 0, channel_id: int = 0) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO active_trades (initiator_id, target_id, channel_id, gold_offered, gold_requested) "
            "VALUES (?,?,?,?,?)",
            (initiator_id, target_id, channel_id, gold_offered, gold_requested)
        )
        await db.commit()
        return cur.lastrowid


async def get_trade(trade_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM active_trades WHERE id=?", (trade_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def update_trade(trade_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [trade_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE active_trades SET {sets} WHERE id=?", vals)
        await db.commit()


async def delete_trade(trade_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM trade_items WHERE trade_id=?", (trade_id,))
        await db.execute("DELETE FROM active_trades WHERE id=?", (trade_id,))
        await db.commit()


async def add_trade_item(trade_id: int, side: str, item_type: str, item_id,
                          quantity: int = 1, equipment_inv_id: int = None, gold: int = 0):
    """side = 'initiator' or 'target'; item_id can be str or int."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO trade_items (trade_id, user_id, item_type, item_id, quantity, equipment_inv_id, gold) "
            "VALUES (?,?,?,?,?,?,?)",
            (trade_id, side, item_type, str(item_id), quantity, equipment_inv_id, gold)
        )
        await db.commit()


async def cancel_trade(trade_id: int):
    await delete_trade(trade_id)


async def complete_trade(trade_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE active_trades SET status='completed' WHERE id=?", (trade_id,))
        await db.commit()


async def get_active_trades(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM active_trades WHERE (initiator_id=? OR target_id=?) AND status='pending'",
            (user_id, user_id)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_equipment_by_id(eq_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM inventory_equipment WHERE id=?", (eq_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_trade_items(trade_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT *, user_id AS side FROM trade_items WHERE trade_id=?", (trade_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def clear_trade_items(trade_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM trade_items WHERE trade_id=? AND user_id=?", (trade_id, user_id))
        await db.commit()
