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

from states.enum import State
from utils.cookies_parser import parse_netscape_cookie

def get_conversation():

    entry_points = [
        CommandHandler(
            "cookie_edit",
            admin(cookie_edit_start),
        )
    ]

    states = {
        State.COOKIE_EDIT_WORKER: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_edit_worker),
            )
        ],
        State.COOKIE_EDIT_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_edit_name),
            )
        ],
        State.COOKIE_EDIT_CONTENT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_edit_content),
            )
        ],
    }

    return (
        entry_points,
        states,
    )

async def cookie_edit_start(
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

    return State.COOKIE_EDIT_WORKER


async def cookie_edit_worker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    mapping = context.user_data["worker_mapping"]

    if text not in mapping:

        await update.message.reply_text(
            "Silakan pilih worker dari keyboard."
        )

        return State.COOKIE_EDIT_WORKER

    context.user_data["worker_id"] = mapping[text]

    await update.message.reply_text(
        "Masukkan nama cookie.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.COOKIE_EDIT_NAME


async def cookie_edit_name(
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

        return State.COOKIE_EDIT_NAME

    context.user_data["cookie_id"] = cookie_data["id"]

    await update.message.reply_text(
        "Silakan paste cookie content baru."
    )

    return State.COOKIE_EDIT_CONTENT


async def cookie_edit_content(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    content = update.message.text.strip()

    if not content:

        await update.message.reply_text(
            "Cookie content tidak boleh kosong."
        )

        return State.COOKIE_EDIT_CONTENT

    try:

        normalized_content, _ = parse_netscape_cookie(
            content
        )

    except ValueError as e:

        await update.message.reply_text(
            str(e)
        )

        return State.COOKIE_EDIT_CONTENT

    updated = cookie.update_content(
        context.user_data["cookie_id"],
        normalized_content,
    )

    context.user_data.clear()

    if updated:

        await update.message.reply_text(
            "✅ Cookie berhasil diperbarui.",
            reply_markup=ReplyKeyboardRemove(),
        )

    else:

        await update.message.reply_text(
            "Cookie gagal diperbarui.",
            reply_markup=ReplyKeyboardRemove(),
        )

    return ConversationHandler.END