import asyncio
from io import BytesIO
from zoneinfo import ZoneInfo

from telethon.errors import FloodWaitError

from app.ocr_detector import detect_raffz


async def download_image(client, message):
    """
    Download image langsung ke RAM.
    Jika Telegram memberikan FloodWait,
    tunggu sesuai waktu yang diberikan Telegram.
    """

    while True:

        try:

            return await client.download_media(
                message,
                file=BytesIO()
            )

        except FloodWaitError as e:

            print(
                f"    [FLOOD] Telegram meminta "
                f"menunggu {e.seconds} detik..."
            )

            await asyncio.sleep(e.seconds)

            print(
                "    [FLOOD] Melanjutkan download..."
            )


async def check_channel(
    client,
    channel_id,
    channel_name
):
    """
    Memeriksa satu channel dari pesan paling lama
    sampai terbaru.

    Jika Raffz ditemukan:
        langsung berhenti pada channel tersebut.

    Setelah fungsi selesai, main.py akan melanjutkan
    ke channel berikutnya.
    """

    print()
    print("=" * 60)
    print(f"[CHANNEL] {channel_name}")
    print("=" * 60)

    while True:

        try:

            # ------------------------------------------------
            # Oldest -> newest
            # ------------------------------------------------

            async for message in client.iter_messages(
                channel_id,
                reverse=True
            ):

                # Hanya image/photo
                if not message.photo:
                    continue

                print(
                    f"[MESSAGE] ID={message.id} "
                    f"DATE={message.date}"
                )

                # --------------------------------------------
                # Download image ke RAM
                # --------------------------------------------

                image_bytes = await download_image(
                    client,
                    message
                )

                if image_bytes is None:

                    print(
                        "    [WARN] Gagal download image"
                    )

                    continue

                # --------------------------------------------
                # Ambil bytes
                # --------------------------------------------

                image_bytes.seek(0)

                data = image_bytes.read()

                # --------------------------------------------
                # OCR
                # --------------------------------------------

                detected = detect_raffz(
                    data
                )

                # --------------------------------------------
                # Raffz ditemukan
                # --------------------------------------------

                if detected:

                    print()
                    print(
                        "    >>> RAFFZ DITEMUKAN <<<"
                    )

                    return {
                        "found": True,
                        "message_id": message.id,
                        "date": message.date.astimezone(
                            ZoneInfo("Asia/Jakarta")
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }

            # ------------------------------------------------
            # Seluruh history selesai
            # ------------------------------------------------

            return {
                "found": False
            }

        except FloodWaitError as e:

            print()
            print(
                f"[FLOOD] Telegram meminta "
                f"menunggu {e.seconds} detik..."
            )

            await asyncio.sleep(
                e.seconds
            )

            print(
                "[FLOOD] Melanjutkan pemeriksaan channel..."
            )