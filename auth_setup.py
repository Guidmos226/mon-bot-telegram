"""
Script d'authentification Telethon — à exécuter UNE SEULE FOIS dans le Shell.
Lance : python auth_setup.py
Il vous demandera votre numéro de téléphone et le code reçu par SMS.
Copiez ensuite la SESSION_STRING affichée dans Replit Secrets.
"""
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

print("=" * 60)
print("  Génération de la session Telethon")
print("=" * 60)
print()
print("Entrez vos identifiants Telegram (obtenus sur https://my.telegram.org).")
print()

api_id = int(input("API_ID (nombre entier) : ").strip())
api_hash = input("API_HASH (chaîne hexadécimale) : ").strip()


async def generate() -> None:
    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        session_string = client.session.save()

    print()
    print("=" * 60)
    print("✅  SESSION_STRING générée avec succès !")
    print()
    print(session_string)
    print()
    print("=" * 60)
    print("👉  Copiez la chaîne ci-dessus et ajoutez-la dans :")
    print("    Replit Secrets  →  clé : SESSION_STRING")
    print("=" * 60)


asyncio.run(generate())
