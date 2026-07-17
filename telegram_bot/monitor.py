"""
Surveillance du canal Telegram avec Telethon (client utilisateur).

Logique :
  - Ignore les messages de prédiction (sans ligne └).
  - Traite uniquement les messages de résultat (avec └♠♣♦♥…).
  - Suit les absences de ♠ dans les résultats.
  - Alerte dès que ♠ apparaît après N absences consécutives.
"""
import asyncio
import logging
from datetime import datetime

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from telegram_bot import database as db
from telegram_bot.analyzer import (
    extract_result_cards,
    extract_game_number,
    has_spade,
    is_result_message,
    cards_to_str,
)
from telegram_bot.config import API_ID, API_HASH, SESSION_STRING, CHANNEL_USERNAME

logger = logging.getLogger(__name__)


async def _build_alert(
    cards: list[str],
    game_number: str | None,
    absence_count_before: int,
    timestamp: str,
) -> str:
    """Construit le message d'alerte Telegram quand ♠ est détecté."""
    cards_str = cards_to_str(cards)
    game_info = f"Jeu #{game_number}" if game_number else "Jeu inconnu"

    if absence_count_before > 0:
        return (
            "🔔 <b>Pique détecté !</b>\n\n"
            f"♠ est apparu après <b>{absence_count_before}</b> résultat(s) sans pique.\n\n"
            f"🎮 {game_info}\n"
            f"🃏 Cartes sorties : <code>{cards_str}</code>\n"
            f"🕐 Heure : {timestamp}"
        )
    else:
        return (
            "✅ <b>Pique détecté !</b>\n\n"
            f"🎮 {game_info}\n"
            f"🃏 Cartes sorties : <code>{cards_str}</code>\n"
            f"🕐 Heure : {timestamp}"
        )


async def process_result(
    bot, my_chat_id: int, message_text: str, timestamp: str
) -> None:
    """
    Traite un message de résultat (ligne └ présente).
    Met à jour le compteur et envoie une alerte si ♠ est sorti.
    """
    cards = extract_result_cards(message_text)
    game_number = extract_game_number(message_text)
    cards_str = cards_to_str(cards)
    spade_present = has_spade(cards)
    current_count = db.get_absence_count()

    # Sauvegarder le résultat
    db.save_signal(cards_str, spade_present, current_count)

    if spade_present:
        alert = await _build_alert(cards, game_number, current_count, timestamp)
        db.set_absence_count(0)
        logger.info(
            "♠ détecté (jeu #%s) après %d absence(s). Alerte envoyée.",
            game_number,
            current_count,
        )
        await bot.send_message(my_chat_id, alert, parse_mode="HTML")
    else:
        new_count = current_count + 1
        db.set_absence_count(new_count)
        logger.info(
            "Résultat sans ♠ (jeu #%s) : %s | Compteur : %d",
            game_number,
            cards_str,
            new_count,
        )


async def start_monitor(bot, my_chat_id: int) -> None:
    """
    Démarre le client Telethon et écoute les nouveaux messages du canal.
    Reconnexion automatique en cas de déconnexion.
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
                "✅ Telethon connecté — surveillance de : %s", CHANNEL_USERNAME
            )

            @client.on(events.NewMessage(chats=CHANNEL_USERNAME))
            async def handler(event):
                text: str = event.message.message or ""

                # Ignorer les messages sans ligne de résultat (prédictions en cours)
                if not is_result_message(text):
                    logger.debug(
                        "Message ignoré (pas de résultat └) : %.40s", text[:40]
                    )
                    return

                timestamp = datetime.now().strftime("%H:%M:%S")
                logger.info(
                    "📩 Résultat reçu (jeu #%s)", extract_game_number(text) or "?"
                )
                try:
                    await process_result(bot, my_chat_id, text, timestamp)
                except Exception as exc:
                    logger.error("Erreur traitement résultat : %s", exc)

            await client.run_until_disconnected()

        except Exception as exc:
            logger.error(
                "Connexion Telethon perdue : %s — reconnexion dans 30 s…", exc
            )
            await asyncio.sleep(30)
