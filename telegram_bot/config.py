"""
Configuration — chargée depuis les variables d'environnement Replit.
Tous les secrets sont définis dans Replit Secrets (onglet 🔒 Secrets).
"""
import os

def _require(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise EnvironmentError(
            f"Variable manquante : {key}\n"
            "Configurez-la dans Replit Secrets (onglet 🔒 Secrets)."
        )
    return val

# ── Télégram API (my.telegram.org) ─────────────────────────────────────────
API_ID: int = int(_require("API_ID"))
API_HASH: str = _require("API_HASH")

# ── Session Telethon (générée par auth_setup.py) ────────────────────────────
SESSION_STRING: str = _require("SESSION_STRING")

# ── Bot Token (BotFather) ───────────────────────────────────────────────────
BOT_TOKEN: str = _require("BOT_TOKEN")

# ── Votre chat ID Telegram (pour recevoir les alertes) ─────────────────────
MY_CHAT_ID: int = int(_require("MY_CHAT_ID"))

# ── Canal à surveiller (ex: "@mon_canal" ou un ID numérique) ───────────────
CHANNEL_USERNAME: str = _require("CHANNEL_USERNAME")

# ── Nombre de signaux d'historique affiché par /history ─────────────────────
HISTORY_LIMIT: int = int(os.environ.get("HISTORY_LIMIT", "10"))
