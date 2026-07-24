from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bots.admin.auth import admin

from database.repositories import scraper

from states.enum import State

PLATFORMS = {
    "Instagram": "instagram",
    "X": "x",
    "TikTok": "tiktok",
    "All": "all",
}


def get_conversation():

    entry_points = [
        CommandHandler(
            "scraper_start",
            admin(scraper_start),
        )
    ]

    states = {
        State.SCRAPER_START: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(scraper_start_platform),
            )
        ],
    }

    return (
        entry_points,
        states,
    )


async def scraper_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    keyboard = [
        ["Instagram"],
        ["X"],
        ["TikTok"],
        ["All"],
    ]

    await update.message.reply_text(
        "Pilih scraper yang ingin dijalankan.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    return State.SCRAPER_START


async def scraper_start_platform(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if text not in PLATFORMS:

        await update.message.reply_text(
            "Silakan pilih scraper dari keyboard."
        )

        return State.SCRAPER_START

    platform = PLATFORMS[text]

    if platform == "all":

        for name in (
            "instagram",
            "x",
            "tiktok",
        ):
            scraper.set_running(
                name,
                True,
            )

        message = "✅ Semua scraper berhasil dijalankan."

    else:

        scraper.set_running(
            platform,
            True,
        )

        message = (
            f"✅ Scraper {text} berhasil dijalankan."
        )

    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END