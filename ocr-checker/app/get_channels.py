import os
import json
import asyncio
from pathlib import Path

from telethon import TelegramClient


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

BASE_DIR = Path(__file__).resolve().parent.parent

SESSION_PATH = BASE_DIR / "sessions" / "telegram"
CONFIG_DIR = BASE_DIR / "config"
CHANNELS_FILE = CONFIG_DIR / "channels.json"

CONFIG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


async def main():

    client = TelegramClient(
        str(SESSION_PATH),
        API_ID,
        API_HASH,
    )

    await client.connect()

    if not await client.is_user_authorized():

        print("[ERROR] Telegram session tidak valid.")
        print()
        print(
            "Jalankan terlebih dahulu:"
        )
        print(
            "docker compose run --rm ocr-checker "
            "python -m app.login"
        )

        await client.disconnect()
        return 1

    print("[INFO] Mengambil daftar channel...")

    channels = []

    async for dialog in client.iter_dialogs():

        entity = dialog.entity

        # Hanya channel Telegram
        if not getattr(entity, "broadcast", False):
            continue

        channels.append({
            "name": dialog.name,
            "id": entity.id,
            "username": getattr(
                entity,
                "username",
                None
            ),
        })

    with open(
        CHANNELS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            channels,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"[INFO] Ditemukan {len(channels)} channel."
    )

    print(
        f"[INFO] Disimpan ke: {CHANNELS_FILE}"
    )

    await client.disconnect()

    return 0


if __name__ == "__main__":

    exit_code = asyncio.run(main())

    raise SystemExit(exit_code)