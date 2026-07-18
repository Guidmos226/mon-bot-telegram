"""Commandes Telegram : /start /status /reset /history"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot import database as db

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 <b>Bot Baccarat actif !</b>\n\n"
        "Je surveille les signaux par paires de jeux (impair + pair).\n"
        "J'envoie une alerte dès que ♠ apparaît après des signaux sans pique.\n\n"
        "Commandes :\n"
        "/status — compteur actuel\n"
        "/history — 10 derniers signaux\n"
        "/reset — remettre le compteur à zéro",
        parse_mode="HTML",
    )


@router.message(Command("status"))
async def cmd_status(message: Message):
    count = db.get_absence_count()
    pending = db.get_pending_odd()
    pending_info = (
        f"\n⏳ Jeu impair <b>#{pending[0]}</b> en attente de son pair."
        if pending else ""
    )
    logger.info("/status reçu de %s", message.from_user.id)
    await message.answer(
        f"📊 <b>Statut actuel</b>\n\n"
        f"Signaux consécutifs sans ♠ : <b>{count}</b>"
        f"{pending_info}",
        parse_mode="HTML",
    )


@router.message(Command("reset"))
async def cmd_reset(message: Message):
    db.reset_absence_count()
    db.clear_pending_odd()
    logger.info("/reset reçu de %s", message.from_user.id)
    await message.answer("✅ Compteur remis à zéro et jeu en attente effacé.")


@router.message(Command("history"))
async def cmd_history(message: Message):
    records = db.get_history(10)
    if not records:
        await message.answer("Aucun signal enregistré pour l'instant.")
        return

    lines = ["📋 <b>10 derniers signaux :</b>\n"]
    for r in records:
        spade_icon = "✅ ♠" if r["had_spade"] else "⏳"
        lines.append(
            f"{spade_icon} <b>#{r['game_odd']}-#{r['game_even']}</b> "
            f"| Joueur : <code>{r['cards_odd']}</code> / <code>{r['cards_even']}</code> "
            f"| Absences : {r['absence_count']}"
        )

    await message.answer("\n".join(lines), parse_mode="HTML")
