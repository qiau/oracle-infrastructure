import os
from telethon import TelegramClient

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

SESSION_PATH = "/app/sessions/telegram"

client = TelegramClient(
    SESSION_PATH,
    API_ID,
    API_HASH,
)


async def main():
    await client.start()

    me = await client.get_me()

    print()
    print("Login berhasil!")
    print(f"Account: {me.first_name}")
    print(f"Username: @{me.username}")
    print(f"Session: {SESSION_PATH}.session")

    await client.disconnect()


with client:
    client.loop.run_until_complete(main())