from telegram import Update
from telegram.ext import ContextTypes

from database.repositories import cookie


async def cookie_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    cookies = cookie.get_all()

    if not cookies:
        await update.message.reply_text(
            "Belum ada cookie."
        )
        return

    valid_count = sum(
        1
        for row in cookies
        if row["is_valid"]
    )

    invalid_count = len(cookies) - valid_count

    text = (
        "🍪 Daftar Cookie\n"
        f"Total : {len(cookies)}\n"
        f"Valid : {valid_count}\n"
        f"Invalid: {invalid_count}\n\n"
    )

    for row in cookies:

        status = (
            "✅ Valid"
            if row["is_valid"]
            else "❌ Invalid"
        )

        worker = (
            row["worker_name"]
            if row["worker_name"]
            else "-"
        )

        last_checked = (
            row["last_checked_at"].strftime("%Y-%m-%d %H:%M:%S")
            if row["last_checked_at"]
            else "-"
        )

        text += (
            f"{row['id']}. {row['name']}\n"
            f"Worker : {worker}\n"
            f"Status : {status}\n"
            f"Checked: {last_checked}\n\n"
        )

    await update.message.reply_text(text)