"""
Couche base de données SQLite.
Stocke les signaux analysés et l'état courant (compteur d'absences).
"""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("data/bot_data.db")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crée les tables si elles n'existent pas encore."""
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS signals (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp            TEXT    NOT NULL,
                cards                TEXT    NOT NULL,
                has_spade            INTEGER NOT NULL,
                absence_count_before INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS state (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            INSERT OR IGNORE INTO state (key, value) VALUES ('absence_count', '0');
        """)
    logger.info("Base de données initialisée : %s", DB_PATH)


# ── Compteur d'absences ─────────────────────────────────────────────────────

def get_absence_count() -> int:
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM state WHERE key = 'absence_count'"
        ).fetchone()
    return int(row["value"]) if row else 0


def set_absence_count(count: int) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO state (key, value) VALUES ('absence_count', ?)",
            (str(count),)
        )


def reset_absence_count() -> None:
    set_absence_count(0)
    logger.info("Compteur d'absences remis à zéro.")


# ── Signaux ─────────────────────────────────────────────────────────────────

def save_signal(cards: str, has_spade: bool, absence_count_before: int) -> None:
    with _connect() as conn:
        conn.execute(
            """INSERT INTO signals (timestamp, cards, has_spade, absence_count_before)
               VALUES (?, ?, ?, ?)""",
            (datetime.now().isoformat(timespec="seconds"), cards, int(has_spade), absence_count_before)
        )
    logger.debug("Signal sauvegardé : cards=%s has_spade=%s", cards, has_spade)


def get_history(limit: int = 10) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """SELECT timestamp, cards, has_spade, absence_count_before
               FROM signals ORDER BY id DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_total_signals() -> int:
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM signals").fetchone()
    return row["n"] if row else 0
