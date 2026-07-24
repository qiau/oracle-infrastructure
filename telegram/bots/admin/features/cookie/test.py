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

from database.repositories import (
    cookie,
    worker,
)

from utils.cookies_checker import check_instagram_cookie

from states.enum import State


def get_conversation():

    entry_points = [
        CommandHandler(
            "cookie_test",
            admin(cookie_test_start),
        )
    ]

    states = {
        State.COOKIE_TEST_WORKER: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_test_worker),
            )
        ],
        State.COOKIE_TEST_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_test_name),
            )
        ],
    }

    return (
        entry_points,
        states,
    )


async def cookie_test_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    workers = worker.get_all()

    keyboard = []
    mapping = {}

    for row in workers:

        keyboard.append([row["name"]])

        mapping[row["name"]] = row["id"]

    context.user_data["worker_mapping"] = mapping

    await update.message.reply_text(
        "Pilih worker.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    return State.COOKIE_TEST_WORKER


async def cookie_test_worker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    mapping = context.user_data["worker_mapping"]

    if text not in mapping:

        await update.message.reply_text(
            "Silakan pilih worker dari keyboard."
        )

        return State.COOKIE_TEST_WORKER

    context.user_data["worker_id"] = mapping[text]

    await update.message.reply_text(
        "Masukkan nama cookie.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.COOKIE_TEST_NAME


async def cookie_test_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    name = update.message.text.strip()

    cookie_data = cookie.get_by_worker_and_name(
        context.user_data["worker_id"],
        name,
    )

    if cookie_data is None:

        await update.message.reply_text(
            "Cookie tidak ditemukan."
        )

        return State.COOKIE_TEST_NAME

    is_valid, message = check_instagram_cookie(
        cookie_data["content"]
    )

    updated = cookie.update_validation(
        cookie_data["id"],
        is_valid,
    )

    if not updated:
        await update.message.reply_text(
            "Status cookie gagal diperbarui.",
            reply_markup=ReplyKeyboardRemove(),
        )

        context.user_data.clear()

        return ConversationHandler.END

    context.user_data.clear()

    status = (
        "✅ Valid"
        if is_valid
        else "❌ Invalid"
    )

    await update.message.reply_text(
        f"{status}\n\n"
        f"{message}",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END