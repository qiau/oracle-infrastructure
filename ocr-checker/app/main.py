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

    if not CHANNELS_FILE.exists():

        print(
            f"[ERROR] File channel tidak ditemukan: "
            f"{CHANNELS_FILE}"
        )

        return 1

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
    # Hasil semua channel
    # --------------------------------------------------------

    results = []

    total = len(channels)

    # --------------------------------------------------------
    # Check channels satu per satu
    # --------------------------------------------------------

    for index, channel in enumerate(
        channels,
        start=1
    ):

        print()
        print("-" * 60)

        print(
            f"[CHANNEL {index}/{total}] "
            f"{channel['name']}"
        )

        print("-" * 60)

        result = await check_channel(
            client,
            channel["id"],
            channel["name"]
        )

        # ----------------------------------------------------
        # Raffz ditemukan
        # ----------------------------------------------------

        if result["found"]:

            output = {
                "channel": channel["name"],
                "channel_id": channel["id"],
                "message_id": result["message_id"],
                "date": result["date"],
            }

            results.append(output)

            print(
                f"[INFO] Raffz ditemukan di "
                f"{channel['name']}"
            )

        # ----------------------------------------------------
        # Raffz tidak ditemukan
        # ----------------------------------------------------

        else:

            print(
                f"[INFO] Raffz tidak ditemukan di "
                f"{channel['name']}"
            )

        # ----------------------------------------------------
        # PENTING:
        #
        # Jangan return di sini.
        #
        # Setelah satu channel selesai, loop akan otomatis
        # melanjutkan ke channel berikutnya.
        # ----------------------------------------------------

    # --------------------------------------------------------
    # Simpan hasil setelah SEMUA channel selesai
    # --------------------------------------------------------

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
            results,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------------
    # Selesai
    # --------------------------------------------------------

    print()
    print("=" * 60)

    print(
        "[INFO] Semua channel selesai diperiksa."
    )

    print(
        f"[INFO] Total channel: {total}"
    )

    print(
        f"[INFO] Raffz ditemukan: {len(results)}"
    )

    print(
        f"[INFO] Hasil: {RESULT_FILE}"
    )

    print("=" * 60)

    await client.disconnect()

    return 0


if __name__ == "__main__":

    raise SystemExit(
        asyncio.run(main())
    )