"""
Base de données SQLite pour le bot.
Stocke : compteur d'absences, jeu impair en attente, historique des signaux.
"""
import sqlite3
import logging
from pathlib import Path

DB_PATH = "data/bot_data.db"
logger = logging.getLogger(__name__)


def init_db() -> None:
    Path("data").mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS state (
                key   TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS signals (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                game_odd      INTEGER,
                game_even     INTEGER,
                cards_odd     TEXT,
                cards_even    TEXT,
                had_spade     INTEGER,
                absence_count INTEGER,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
    logger.info("Base de données initialisée : %s", DB_PATH)


# ── helpers state ────────────────────────────────────────────────────────────

def _get(key: str, default: str = "") -> str:
    with sqlite3.connect(DB_PATH) as con:
        row = con.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


def _set(key: str, value: str) -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO state(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )


# ── absence counter ──────────────────────────────────────────────────────────

def get_absence_count() -> int:
    return int(_get("absence_count", "0"))


def set_absence_count(n: int) -> None:
    _set("absence_count", str(n))


def reset_absence_count() -> None:
    set_absence_count(0)


# ── pending odd game ─────────────────────────────────────────────────────────

def get_pending_odd() -> tuple[int, str, bool] | None:
    """Retourne (game_number, cards_str, has_spade) ou None."""
    num = _get("pending_odd_num", "")
    if not num:
        return None
    cards = _get("pending_odd_cards", "")
    spade = _get("pending_odd_spade", "0") == "1"
    return int(num), cards, spade


def set_pending_odd(game_number: int, cards_str: str, has_spade: bool) -> None:
    _set("pending_odd_num", str(game_number))
    _set("pending_odd_cards", cards_str)
    _set("pending_odd_spade", "1" if has_spade else "0")


def clear_pending_odd() -> None:
    _set("pending_odd_num", "")
    _set("pending_odd_cards", "")
    _set("pending_odd_spade", "0")


# ── signal history ────────────────────────────────────────────────────────────

def save_signal(
    game_odd: int,
    game_even: int,
    cards_odd: str,
    cards_even: str,
    had_spade: bool,
    absence_count: int,
) -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO signals"
            "(game_odd,game_even,cards_odd,cards_even,had_spade,absence_count)"
            " VALUES(?,?,?,?,?,?)",
            (game_odd, game_even, cards_odd, cards_even, int(had_spade), absence_count),
        )


def get_history(limit: int = 10) -> list[dict]:
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute(
            "SELECT game_odd,game_even,cards_odd,cards_even,had_spade,absence_count,created_at"
            " FROM signals ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {
            "game_odd": r[0], "game_even": r[1],
            "cards_odd": r[2], "cards_even": r[3],
            "had_spade": bool(r[4]), "absence_count": r[5], "created_at": r[6],
        }
        for r in rows
    ]
