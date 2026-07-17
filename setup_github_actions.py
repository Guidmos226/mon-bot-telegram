"""
Script to set up GitHub Actions secrets and make repo public.
"""
import os
import sys
import json
import base64
import requests
from nacl import encoding, public

TOKEN = os.environ["GITHUB_TOKEN"]
OWNER = "Guidmos226"
REPO = "mon-bot-telegram"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

SECRETS = {
    "API_ID": os.environ.get("API_ID", ""),
    "API_HASH": os.environ.get("API_HASH", ""),
    "BOT_TOKEN": os.environ.get("BOT_TOKEN", ""),
    "MY_CHAT_ID": os.environ.get("MY_CHAT_ID", ""),
    "SESSION_STRING": os.environ.get("SESSION_STRING", ""),
    "CHANNEL_USERNAME": os.environ.get("CHANNEL_USERNAME", ""),
}

def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    pk = public.PublicKey(public_key_b64.encode(), encoding.Base64Encoder())
    box = public.SealedBox(pk)
    encrypted = box.encrypt(secret_value.encode())
    return base64.b64encode(encrypted).decode()

# 1. Make repo public
print("1. Rendre le dépôt public...")
r = requests.patch(
    f"https://api.github.com/repos/{OWNER}/{REPO}",
    headers=HEADERS,
    json={"private": False},
)
print(f"   Status: {r.status_code} {'✅' if r.status_code == 200 else '❌'}")

# 2. Get public key for secrets encryption
print("2. Récupération de la clé publique GitHub Actions...")
r = requests.get(
    f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/public-key",
    headers=HEADERS,
)
key_data = r.json()
key_id = key_data["key_id"]
key_b64 = key_data["key"]
print(f"   Key ID: {key_id} ✅")

# 3. Upload each secret
print("3. Envoi des secrets...")
for name, value in SECRETS.items():
    if not value:
        print(f"   ⚠️  {name} vide, ignoré")
        continue
    encrypted = encrypt_secret(key_b64, value)
    r = requests.put(
        f"https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/{name}",
        headers=HEADERS,
        json={"encrypted_value": encrypted, "key_id": key_id},
    )
    status = "✅" if r.status_code in (201, 204) else f"❌ ({r.status_code})"
    print(f"   {name}: {status}")

print("\nTerminé !")
