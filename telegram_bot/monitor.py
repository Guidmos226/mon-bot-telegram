"""
Surveillance du canal Telegram avec Telethon (client utilisateur).
Détecte les nouveaux signaux et déclenche les alertes via le bot.
"""
import asyncio
import logging
from datetime import datetime

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from telegram_bot import database as db
from telegram_bot.analyzer import (
    extract_cards,
    has_spade,
    is_signal_message,
    cards_to_str,
)
from telegram_bot.config import API_ID, API_HASH, SESSION_STRING, CHANNEL_USERNAME

logger = logging.getLogger(__name__)


async def _build_alert(cards: list[str], absence_count_before: int, timestamp: str) -> str:
    """Construit le message d'alerte envoyé quand ♠ est détecté."""
    cards_str = cards_to_str(cards)
    if absence_count_before > 0:
        return (
            "🔔 <b>Pique détecté !</b>\n\n"
            f"♠ est apparu après <b>{absence_count_before}</b> signal(s) sans pique.\n"
            f"🃏 Cartes détectées : <code>{cards_str}</code>\n"
            f"🕐 Heure : {timestamp}"
        )
    else:
        return (
            "✅ <b>Pique détecté !</b>\n\n"
            f"🃏 Cartes détectées : <code>{cards_str}</code>\n"
            f"🕐 Heure : {timestamp}"
        )


async def process_signal(bot, my_chat_id: int, message_text: str, timestamp: str) -> None:
    """Analyse un signal et envoie une alerte si ♠ est détecté."""
    cards = extract_cards(message_text)
    cards_str = cards_to_str(cards)
    spade_present = has_spade(cards)
    current_count = db.get_absence_count()

    # Sauvegarder le signal
    db.save_signal(cards_str, spade_present, current_count)

    if spade_present:
        alert = await _build_alert(cards, current_count, timestamp)
        db.set_absence_count(0)
        logger.info("♠ détecté après %d absence(s). Envoi de l'alerte.", current_count)
        await bot.send_message(my_chat_id, alert, parse_mode="HTML")
    else:
        new_count = current_count + 1
        db.set_absence_count(new_count)
        logger.info(
            "Pas de ♠ dans ce signal. Cartes : %s | Compteur : %d",
            cards_str,
            new_count,
        )


async def start_monitor(bot, my_chat_id: int) -> None:
    """
    Démarre le client Telethon (utilisateur) et écoute les nouveaux messages
    du canal configuré. Tourne indéfiniment avec reconnexion automatique.
    """
    while True:
        try:
            client = TelegramClient(
                StringSession(SESSION_STRING),
                API_ID,
                API_HASH,
            )
            await client.start()
            logger.info(
                "✅ Client Telethon connecté — surveillance de : %s",
                CHANNEL_USERNAME,
            )

            @client.on(events.NewMessage(chats=CHANNEL_USERNAME))
            async def handler(event):
                text: str = event.message.message or ""
                if not is_signal_message(text):
                    return
                timestamp = datetime.now().strftime("%H:%M:%S")
                logger.info("📩 Nouveau signal reçu : %.60s", text)
                try:
                    await process_signal(bot, my_chat_id, text, timestamp)
                except Exception as exc:
                    logger.error("Erreur lors du traitement du signal : %s", exc)

            await client.run_until_disconnected()

        except Exception as exc:
            logger.error(
                "Connexion Telethon perdue : %s — reconnexion dans 30 s…", exc
            )
            await asyncio.sleep(30)
