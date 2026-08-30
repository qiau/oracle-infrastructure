import os
import json
import asyncio
from pathlib import Path

from telethon import TelegramClient

from app.telegram_checker import check_channel


API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]


BASE_DIR = Path(__file__).resolve().parent.parent

SESSION_PATH = BASE_DIR / "sessions" / "telegram"
CHANNELS_FILE = BASE_DIR / "config" / "channels.json"
RESULT_FILE = BASE_DIR / "results" / "result.json"


async def main():

    # --------------------------------------------------------
    # Load channels
    # --------------------------------------------------------

    with open(
        CHANNELS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        channels = json.load(f)

    print(
        f"[INFO] Total channel: {len(channels)}"
    )

    # --------------------------------------------------------
    # Telegram
    # --------------------------------------------------------

    client = TelegramClient(
        str(SESSION_PATH),
        API_ID,
        API_HASH,
    )

    await client.connect()

    if not await client.is_user_authorized():

        print()
        print("=" * 60)
        print("[ERROR] Telegram session tidak valid!")
        print()
        print(
            "Silakan login dengan:"
        )
        print(
            "docker compose run --rm "
            "ocr-checker python -m app.login"
        )
        print("=" * 60)

        await client.disconnect()

        return 1

    # --------------------------------------------------------
    # Check channels
    # --------------------------------------------------------

    for channel in channels:

        result = await check_channel(
            client,
            channel["id"],
            channel["name"]
        )

        if result["found"]:

            output = {
                "channel": channel["name"],
                "channel_id": channel["id"],
                "message_id": result["message_id"],
                "date": result["date"],
            }

            RESULT_FILE.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(
                RESULT_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    output,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            print()
            print("[INFO] Raffz ditemukan.")
            print(
                f"[INFO] Hasil: {RESULT_FILE}"
            )

            await client.disconnect()

            return 0

    # --------------------------------------------------------
    # Tidak ditemukan
    # --------------------------------------------------------

    print()
    print("[INFO] Raffz tidak ditemukan di semua channel.")

    await client.disconnect()

    return 0


if __name__ == "__main__":

    raise SystemExit(
        asyncio.run(main())
    )