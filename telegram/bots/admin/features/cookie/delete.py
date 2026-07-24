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

def get_conversation():

    entry_points = [
        CommandHandler(
            "cookie_delete",
            admin(cookie_delete_start),
        )
    ]

    states = {
        State.COOKIE_DELETE_WORKER: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_delete_worker),
            )
        ],
        State.COOKIE_DELETE_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_delete_name),
            )
        ],
        State.COOKIE_DELETE_CONFIRM: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_delete_confirm),
            )
        ],
    }

    return (
        entry_points,
        states,
    )

async def cookie_delete_start(
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

    return State.COOKIE_DELETE_WORKER


async def cookie_delete_worker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    mapping = context.user_data["worker_mapping"]

    if text not in mapping:

        await update.message.reply_text(
            "Silakan pilih worker dari keyboard."
        )

        return State.COOKIE_DELETE_WORKER

    context.user_data["worker_id"] = mapping[text]

    await update.message.reply_text(
        "Masukkan nama cookie.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.COOKIE_DELETE_NAME


async def cookie_delete_name(
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

        return State.COOKIE_DELETE_NAME

    context.user_data["cookie_id"] = cookie_data["id"]

    keyboard = [
        ["Ya"],
        ["Tidak"],
    ]

    await update.message.reply_text(
        f'Yakin ingin menghapus cookie "{name}"?',
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    return State.COOKIE_DELETE_CONFIRM


async def cookie_delete_confirm(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if text == "Tidak":

        context.user_data.clear()

        await update.message.reply_text(
            "Penghapusan dibatalkan.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    if text != "Ya":

        await update.message.reply_text(
            "Silakan pilih Ya atau Tidak."
        )

        return State.COOKIE_DELETE_CONFIRM

    deleted = cookie.delete(
        context.user_data["cookie_id"],
    )

    context.user_data.clear()

    if deleted:

        await update.message.reply_text(
            "✅ Cookie berhasil dihapus.",
            reply_markup=ReplyKeyboardRemove(),
        )

    else:

        await update.message.reply_text(
            "Cookie gagal dihapus.",
            reply_markup=ReplyKeyboardRemove(),
        )

    return ConversationHandler.END