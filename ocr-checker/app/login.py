import os
from pathlib import Path

from telethon import TelegramClient


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

BASE_DIR = Path(__file__).resolve().parent.parent
SESSION_DIR = BASE_DIR / "sessions"

SESSION_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SESSION_PATH = SESSION_DIR / "telegram"

client = TelegramClient(
    str(SESSION_PATH),
    API_ID,
    API_HASH,
)


async def main():
    await client.start()

    me = await client.get_me()

    print()
    print("=" * 50)
    print("LOGIN BERHASIL")
    print("=" * 50)
    print(f"Nama     : {me.first_name}")
    print(f"Username : @{me.username}")
    print(f"User ID  : {me.id}")
    print(f"Session  : {SESSION_PATH}.session")
    print("=" * 50)


with client:
    client.loop.run_until_complete(main())