from telegram import Update
from telegram.ext import ContextTypes

from database.repositories import profile
from utils.split_message import reply_long_text


async def profile_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    profiles = profile.get_all()

    if not profiles:
        await update.message.reply_text(
            "Belum ada profile."
        )
        return

    text = (
        "👤 Daftar Profile\n"
        f"Total: {len(profiles)}\n\n"
    )

    for index, row in enumerate(
        profiles,
        start=1,
    ):
        generation = (
            f"Gen {row['generation']}"
            if row["generation"] is not None
            else "-"
        )

        text += (
            f"{index}. "
            f"{row['name']} "
            f"({row['profile_type']}, {generation})\n"
        )

    await reply_long_text(
        update.message,
        text,
    )