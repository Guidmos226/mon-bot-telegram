"""
╔══════════════════════════════════════════════════════════════════╗
║  SCRIPT D'AUTHENTIFICATION — à exécuter UNE SEULE FOIS          ║
║                                                                  ║
║  Ce script génère votre SESSION_STRING Telethon.                ║
║  Lancez-le dans le Shell Replit :                                ║
║      python auth_setup.py                                        ║
║                                                                  ║
║  Copiez la chaîne affichée et enregistrez-la dans               ║
║  Replit Secrets sous le nom SESSION_STRING.                      ║
╚══════════════════════════════════════════════════════════════════╝
"""
import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

print("=" * 60)
print("  Génération de la session Telethon")
print("=" * 60)

# Lecture des identifiants
api_id_raw = os.environ.get("API_ID") or input("API_ID (entier) : ").strip()
api_hash_raw = os.environ.get("API_HASH") or input("API_HASH : ").strip()

API_ID = int(api_id_raw)
API_HASH = api_hash_raw


async def generate_session() -> None:
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        session_string = client.session.save()

    print("\n" + "=" * 60)
    print("✅  SESSION_STRING générée avec succès :\n")
    print(session_string)
    print("\n" + "=" * 60)
    print("👉  Copiez cette chaîne et ajoutez-la dans :")
    print("    Replit Secrets  →  clé : SESSION_STRING")
    print("=" * 60)


asyncio.run(generate_session())
