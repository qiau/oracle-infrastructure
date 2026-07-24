from telegram import Update
from telegram.ext import ContextTypes

from database.repositories import scraper


PLATFORM_NAMES = {
    "instagram": "Instagram",
    "x": "X",
    "tiktok": "TikTok",
}


async def scraper_status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    scrapers = scraper.get_all()

    if not scrapers:
        await update.message.reply_text(
            "Belum ada scraper."
        )
        return

    text = "🛰️ Scraper Status\n\n"

    for row in scrapers:

        platform = PLATFORM_NAMES.get(
            row["platform"],
            row["platform"],
        )

        status = (
            "🟢 Running"
            if row["is_running"]
            else "🔴 Stopped"
        )

        updated_at = row["updated_at"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        text += (
            f"{platform}\n"
            f"Status : {status}\n"
            f"Updated: {updated_at}\n"
        )

        if row["last_error_message"]:
            text += (
                f"Error  : {row['last_error_message']}\n"
            )

        text += "\n"

    await update.message.reply_text(
        text.rstrip()
    )