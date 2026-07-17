"""
Gestionnaires des commandes Telegram du bot.
/start   — présentation
/status  — état actuel (compteur, dernier signal)
/reset   — remet le compteur à zéro
/history — affiche les derniers signaux analysés
"""
import logging
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot import database as db
from telegram_bot.config import CHANNEL_USERNAME

logger = logging.getLogger(__name__)
router = Router()


# ── /start ──────────────────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    text = (
        "👋 <b>Bot de surveillance de signaux</b>\n\n"
        f"Je surveille le canal <code>{CHANNEL_USERNAME}</code> et je vous alerte "
        "dès que ♠ <b>(Pique)</b> apparaît dans un signal.\n\n"
        "<b>Commandes disponibles :</b>\n"
        "/status   — état actuel du compteur\n"
        "/history  — derniers signaux analysés\n"
        "/reset    — remettre le compteur à zéro\n"
    )
    await message.answer(text, parse_mode="HTML")
    logger.info("/start reçu de %s", message.from_user.id)


# ── /status ─────────────────────────────────────────────────────────────────

@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    count = db.get_absence_count()
    total = db.get_total_signals()
    history = db.get_history(1)

    if history:
        last = history[0]
        last_line = (
            f"<code>{last['cards'] or 'aucune carte'}</code> "
            f"({'♠ présent' if last['has_spade'] else 'sans ♠'}) "
            f"à {last['timestamp']}"
        )
    else:
        last_line = "Aucun signal analysé pour l'instant."

    text = (
        "📊 <b>État actuel</b>\n\n"
        f"🔢 Signaux consécutifs sans ♠ : <b>{count}</b>\n"
        f"📈 Total signaux analysés : <b>{total}</b>\n"
        f"📩 Dernier signal : {last_line}"
    )
    await message.answer(text, parse_mode="HTML")
    logger.info("/status reçu de %s", message.from_user.id)


# ── /reset ───────────────────────────────────────────────────────────────────

@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    db.reset_absence_count()
    await message.answer("✅ Compteur remis à zéro.")
    logger.info("/reset reçu de %s", message.from_user.id)


# ── /history ─────────────────────────────────────────────────────────────────

@router.message(Command("history"))
async def cmd_history(message: Message) -> None:
    from telegram_bot.config import HISTORY_LIMIT
    history = db.get_history(HISTORY_LIMIT)

    if not history:
        await message.answer("Aucun historique disponible pour l'instant.")
        return

    lines = [f"📜 <b>Derniers {len(history)} signaux analysés :</b>\n"]
    for entry in history:
        icon = "♠" if entry["has_spade"] else "—"
        cards = entry["cards"] or "aucune carte"
        ts = entry["timestamp"]
        lines.append(f"{icon} <code>{cards}</code>  {ts}")

    await message.answer("\n".join(lines), parse_mode="HTML")
    logger.info("/history reçu de %s", message.from_user.id)
