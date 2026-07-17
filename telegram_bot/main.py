"""
Point d'entrée principal du bot.
Lance simultanément :
  - le polling aiogram (commandes /start, /status, /reset, /history)
  - la surveillance Telethon du canal (détection des signaux)
"""
import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from telegram_bot import database as db
from telegram_bot.config import BOT_TOKEN, MY_CHAT_ID
from telegram_bot.handlers import router
from telegram_bot.monitor import start_monitor


# ── Logging ──────────────────────────────────────────────────────────────────

Path("data").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ── Démarrage ─────────────────────────────────────────────────────────────────

async def main() -> None:
    # Initialiser la base de données
    db.init_db()
    logger.info("🚀 Démarrage du bot…")

    # Créer le bot aiogram
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    # Démarrer en parallèle : polling bot + surveillance canal
    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=["message"]),
        start_monitor(bot, MY_CHAT_ID),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot arrêté manuellement.")
