from telegram import Update
from telegram.ext import ContextTypes


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🤖 Oshinesia Admin Bot\n\n"

        "👤 Profile\n"
        "/profile_list - Tampilkan semua profile\n"
        "/profile_add - Tambah profile baru\n"
        "/profile_edit - Edit profile\n"
        "/profile_delete - Hapus profile\n\n"

        "🍪 Cookie\n"
        "/cookie_list - Tampilkan semua cookie\n"
        "/cookie_add - Tambah cookie\n"
        "/cookie_edit - Edit cookie\n"
        "/cookie_delete - Hapus cookie\n"
        "/cookie_test - Uji validitas cookie\n\n"

        "🛰️ Scraper\n"
        "/scraper_start - Jalankan scraper\n"
        "/scraper_stop - Hentikan scraper\n"
        "/scraper_status - Lihat status scraper"
    )