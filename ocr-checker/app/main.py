import os
import sys
import asyncio
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import (
    AuthKeyUnregisteredError,
    SessionRevokedError,
)


# ============================================================
# CONFIG
# ============================================================

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]

BASE_DIR = Path(__file__).resolve().parent.parent

SESSION_PATH = BASE_DIR / "sessions" / "telegram"


# ============================================================
# MAIN
# ============================================================

async def main():

    client = TelegramClient(
        str(SESSION_PATH),
        API_ID,
        API_HASH,
    )

    try:

        print("[INFO] Menghubungkan ke Telegram...")

        await client.connect()

        # ----------------------------------------------------
        # Cek session
        # ----------------------------------------------------

        if not await client.is_user_authorized():

            print()
            print("=" * 60)
            print("[ERROR] Telegram session tidak valid!")
            print()
            print("Silakan login terlebih dahulu dengan:")
            print()
            print(
                "docker compose run --rm ocr-checker "
                "python -m app.login"
            )
            print()
            print("Setelah login berhasil, jalankan:")
            print()
            print("docker compose up -d")
            print("=" * 60)

            return 1

        # ----------------------------------------------------
        # Ambil informasi akun
        # ----------------------------------------------------

        me = await client.get_me()

        account_name = (
            me.username
            or me.first_name
            or str(me.id)
        )

        print(
            f"[INFO] Telegram login valid: {account_name}"
        )

        # ----------------------------------------------------
        # TODO:
        # Jalankan sistem checker di sini
        # ----------------------------------------------------

        print("[INFO] Telegram checker siap dijalankan.")

        return 0

    except (
        AuthKeyUnregisteredError,
        SessionRevokedError,
    ):

        print()
        print("=" * 60)
        print("[ERROR] Telegram session sudah tidak valid!")
        print()
        print("Silakan login ulang dengan:")
        print()
        print(
            "docker compose run --rm ocr-checker "
            "python -m app.login"
        )
        print()
        print("Setelah login berhasil, jalankan:")
        print()
        print("docker compose up -d")
        print("=" * 60)

        return 1

    except Exception as e:

        print()
        print("=" * 60)
        print("[ERROR] Gagal terhubung ke Telegram")
        print(f"[ERROR] {type(e).__name__}: {e}")
        print("=" * 60)

        return 1

    finally:

        await client.disconnect()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    exit_code = asyncio.run(main())

    sys.exit(exit_code)