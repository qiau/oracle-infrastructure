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
            "scraper_stop",
            admin(scraper_stop),
        )
    ]

    states = {
        State.SCRAPER_STOP: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(scraper_stop_platform),
            )
        ],
    }

    return (
        entry_points,
        states,
    )


async def scraper_stop(
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
        "Pilih scraper yang ingin dihentikan.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    return State.SCRAPER_STOP


async def scraper_stop_platform(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if text not in PLATFORMS:

        await update.message.reply_text(
            "Silakan pilih scraper dari keyboard."
        )

        return State.SCRAPER_STOP

    platform = PLATFORMS[text]

    if platform == "all":

        for name in (
            "instagram",
            "x",
            "tiktok",
        ):
            scraper.set_running(
                name,
                False,
            )

        message = "✅ Semua scraper berhasil dihentikan."

    else:

        scraper.set_running(
            platform,
            False,
        )

        message = (
            f"✅ Scraper {text} berhasil dihentikan."
        )

    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END