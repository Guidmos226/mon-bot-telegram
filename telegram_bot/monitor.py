"""
Surveillance du canal avec la logique de paires (impair + pair).

Signal = deux jeux consécutifs (N impair + N+1 pair).
  → Si le JOUEUR a ♠ dans au moins un des deux → signal "avec pique"
  → Sinon → signal "sans pique" (compteur +1)

Alerte : dès que ♠ apparaît dans un signal après ≥1 signal sans pique.
"""
import asyncio
import logging
from datetime import datetime

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from telegram_bot import database as db
from telegram_bot.analyzer import (
    parse_game_message,
    player_has_spade,
    is_odd_game,
    cards_to_str,
)
from telegram_bot.config import API_ID, API_HASH, SESSION_STRING, CHANNEL_USERNAME

logger = logging.getLogger(__name__)


async def _process_pair(
    bot,
    my_chat_id: int,
    game_odd: int,
    cards_odd: list[str],
    game_even: int,
    cards_even: list[str],
) -> None:
    """Traite une paire complète de jeux et envoie les notifications."""
    spade_odd  = player_has_spade(cards_odd)
    spade_even = player_has_spade(cards_even)
    pair_has_spade = spade_odd or spade_even

    cards_odd_str  = cards_to_str(cards_odd)
    cards_even_str = cards_to_str(cards_even)
    absence_before = db.get_absence_count()
    timestamp = datetime.now().strftime("%H:%M:%S")

    db.save_signal(
        game_odd, game_even,
        cards_odd_str, cards_even_str,
        pair_has_spade, absence_before,
    )

    if pair_has_spade:
        db.set_absence_count(0)
        logger.info(
            "✅ Signal #%d-#%d avec ♠ (absences avant : %d)",
            game_odd, game_even, absence_before,
        )
        if absence_before >= 1:
            # Alerte : ♠ est apparu après des absences
            msg = (
                f"🔔 <b>Pique apparu !</b>\n\n"
                f"♠ est sorti dans le signal <b>#{game_odd}-#{game_even}</b>\n"
                f"après <b>{absence_before}</b> signal(s) consécutif(s) sans pique.\n\n"
                f"🃏 Jeu #{game_odd} (joueur) : <code>{cards_odd_str}</code> "
                f"{'♠' if spade_odd else ''}\n"
                f"🃏 Jeu #{game_even} (joueur) : <code>{cards_even_str}</code> "
                f"{'♠' if spade_even else ''}\n"
                f"🕐 {timestamp}"
            )
            await bot.send_message(my_chat_id, msg, parse_mode="HTML")
        # Si absence_before == 0 : ♠ présent dès le départ, pas d'alerte
    else:
        new_count = absence_before + 1
        db.set_absence_count(new_count)
        logger.info(
            "⏳ Signal #%d-#%d sans ♠ → compteur : %d",
            game_odd, game_even, new_count,
        )
        msg = (
            f"⏳ <b>Signal sans pique</b>\n\n"
            f"Signal : <b>#{game_odd}-#{game_even}</b>\n"
            f"🃏 Jeu #{game_odd} (joueur) : <code>{cards_odd_str}</code>\n"
            f"🃏 Jeu #{game_even} (joueur) : <code>{cards_even_str}</code>\n"
            f"📊 Signaux sans ♠ : <b>{new_count}</b>\n"
            f"🕐 {timestamp}"
        )
        await bot.send_message(my_chat_id, msg, parse_mode="HTML")


async def start_monitor(bot, my_chat_id: int) -> None:
    """Démarre Telethon et écoute les nouveaux messages du canal."""
    while True:
        try:
            client = TelegramClient(
                StringSession(SESSION_STRING), API_ID, API_HASH
            )
            await client.start()
            logger.info("✅ Telethon connecté — surveillance : %s", CHANNEL_USERNAME)

            @client.on(events.NewMessage(chats=CHANNEL_USERNAME))
            async def handler(event):
                text: str = event.message.message or ""
                result = parse_game_message(text)
                if result is None:
                    logger.debug("Message ignoré (format inconnu) : %.60s", text[:60])
                    return

                game_number, cards = result
                logger.info(
                    "📩 Jeu #%d reçu — joueur : %s | ♠ : %s",
                    game_number, cards_to_str(cards), player_has_spade(cards),
                )

                if is_odd_game(game_number):
                    # Début d'un nouveau signal : on stocke le jeu impair
                    db.set_pending_odd(game_number, cards_to_str(cards), player_has_spade(cards))
                    logger.info("Jeu impair #%d stocké, attente du pair.", game_number)
                else:
                    # Jeu pair : on récupère le jeu impair en attente
                    pending = db.get_pending_odd()
                    if pending is None:
                        logger.warning(
                            "Jeu pair #%d reçu sans jeu impair en attente — ignoré.", game_number
                        )
                        return

                    odd_num, odd_cards_str, _ = pending
                    # Reconstruire la liste de cartes depuis la chaîne
                    odd_cards = list(odd_cards_str) if odd_cards_str else []

                    db.clear_pending_odd()
                    try:
                        await _process_pair(
                            bot, my_chat_id,
                            odd_num, odd_cards,
                            game_number, cards,
                        )
                    except Exception as exc:
                        logger.error("Erreur traitement paire #%d-#%d : %s", odd_num, game_number, exc)

            await client.run_until_disconnected()

        except Exception as exc:
            logger.error("Connexion Telethon perdue : %s — reconnexion dans 30 s…", exc)
            await asyncio.sleep(30)
