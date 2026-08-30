import asyncio
import random
from io import BytesIO
from zoneinfo import ZoneInfo

from telethon.errors import FloodWaitError
from telethon.tl.types import InputMessagesFilterPhotos

from app.ocr_detector import detect_raffz


# ============================================================
# KONFIGURASI
# ============================================================

BATCH_SIZE = 20
BATCH_DELAY1 = 2
BATCH_DELAY2 = 4


# ============================================================
# DOWNLOAD IMAGE
# ============================================================

async def download_image(client, message):
    """
    Download image langsung ke RAM.

    Jika terkena FloodWait, tunggu sesuai instruksi
    Telegram lalu coba kembali.
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

            await asyncio.sleep(
                e.seconds
            )

            print(
                "    [FLOOD] Melanjutkan download..."
            )


# ============================================================
# PROCESS ONE IMAGE
# ============================================================

async def process_image(
    client,
    message
):
    """
    Download satu image ke RAM lalu jalankan OCR.

    Return:
        True  -> Raffz ditemukan
        False -> tidak ditemukan
        None  -> gagal download
    """

    print(
        f"[MESSAGE] ID={message.id} "
        f"DATE={message.date}"
    )

    # --------------------------------------------------------
    # Download image
    # --------------------------------------------------------

    image_bytes = await download_image(
        client,
        message
    )

    if image_bytes is None:

        print(
            "    [WARN] Gagal download image"
        )

        return None

    # --------------------------------------------------------
    # Bytes
    # --------------------------------------------------------

    image_bytes.seek(0)

    data = image_bytes.read()

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    detected = detect_raffz(
        data
    )

    return detected


# ============================================================
# CHECK CHANNEL
# ============================================================

async def check_channel(
    client,
    channel_id,
    channel_name
):
    """
    Memeriksa channel dari pesan paling lama
    sampai terbaru.

    Pemrosesan dilakukan dalam batch:

        100 image
        ↓
        OCR
        ↓
        sleep 3 detik
        ↓
        100 image berikutnya

    Jika Raffz ditemukan:
        langsung berhenti pada channel tersebut.

    Setelah itu main.py akan melanjutkan
    ke channel berikutnya.
    """

    print()
    print("=" * 60)
    print(f"[CHANNEL] {channel_name}")
    print("=" * 60)

    batch = []

    while True:

        try:

            # ------------------------------------------------
            # Ambil pesan photo
            # ------------------------------------------------

            async for message in client.iter_messages(
                channel_id,
                filter=InputMessagesFilterPhotos(),
                reverse=True
            ):

                batch.append(message)

                # ------------------------------------------------
                # Jika batch sudah 100
                # ------------------------------------------------

                if len(batch) >= BATCH_SIZE:

                    print()
                    print(
                        f"[BATCH] Memproses "
                        f"{len(batch)} image..."
                    )

                    # --------------------------------------------
                    # Process batch
                    # --------------------------------------------

                    for item in batch:

                        detected = await process_image(
                            client,
                            item
                        )

                        if detected:

                            print()
                            print(
                                "    >>> RAFFZ DITEMUKAN <<<"
                            )

                            return {
                                "found": True,
                                "message_id": item.id,
                                "date": item.date.astimezone(
                                    ZoneInfo("Asia/Jakarta")
                                ).strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            }

                    # --------------------------------------------
                    # Kosongkan batch
                    # --------------------------------------------

                    batch.clear()

                    # --------------------------------------------
                    # Jeda antar batch
                    # --------------------------------------------
                    delay = random.uniform(
                        BATCH_DELAY1,
                        BATCH_DELAY2
                    )

                    print(
                        f"[BATCH] Selesai. "
                        f"Menunggu {delay:.1f} detik..."
                    )

                    await asyncio.sleep(delay)

            # ------------------------------------------------
            # Proses sisa batch
            # ------------------------------------------------

            if batch:

                print()
                print(
                    f"[BATCH] Memproses sisa "
                    f"{len(batch)} image..."
                )

                for item in batch:

                    detected = await process_image(
                        client,
                        item
                    )

                    if detected:

                        print()
                        print(
                            "    >>> RAFFZ DITEMUKAN <<<"
                        )

                        return {
                            "found": True,
                            "message_id": item.id,
                            "date": item.date.astimezone(
                                ZoneInfo("Asia/Jakarta")
                            ).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }

                batch.clear()

            # ------------------------------------------------
            # Semua history selesai
            # ------------------------------------------------

            print(
                "[CHANNEL] Semua image selesai diperiksa."
            )

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
                "[FLOOD] Melanjutkan pemeriksaan..."
            )