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
            "cookie_add",
            admin(cookie_add_start),
        )
    ]

    states = {
        State.COOKIE_ADD_WORKER: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_add_worker),
            )
        ],
        State.COOKIE_ADD_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_add_name),
            )
        ],
        State.COOKIE_ADD_CONTENT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(cookie_add_content),
            )
        ],
    }

    return (
        entry_points,
        states,
    )


async def cookie_add_start(
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

    return State.COOKIE_ADD_WORKER


async def cookie_add_worker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    mapping = context.user_data["worker_mapping"]

    if text not in mapping:

        await update.message.reply_text(
            "Silakan pilih worker dari keyboard."
        )

        return State.COOKIE_ADD_WORKER

    context.user_data["worker_id"] = mapping[text]

    await update.message.reply_text(
        "Masukkan nama cookie.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.COOKIE_ADD_NAME


async def cookie_add_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    name = update.message.text.strip()

    if not name:

        await update.message.reply_text(
            "Nama cookie tidak boleh kosong."
        )

        return State.COOKIE_ADD_NAME

    if cookie.exists(
        context.user_data["worker_id"],
        name,
    ):

        await update.message.reply_text(
            "Nama cookie sudah digunakan pada worker tersebut.\n"
            "Silakan gunakan nama lain."
        )

        return State.COOKIE_ADD_NAME

    context.user_data["name"] = name

    await update.message.reply_text(
        "Silakan paste cookie content."
    )

    return State.COOKIE_ADD_CONTENT


async def cookie_add_content(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    content = update.message.text.strip()

    if not content:

        await update.message.reply_text(
            "Cookie content tidak boleh kosong."
        )

        return State.COOKIE_ADD_CONTENT

    try:

        normalized_content, _ = parse_netscape_cookie(
            content
        )

    except ValueError as e:

        await update.message.reply_text(
            str(e)
        )

        return State.COOKIE_ADD_CONTENT

    cookie_id = cookie.add(
        worker_id=context.user_data["worker_id"],
        name=context.user_data["name"],
        content=normalized_content,
    )

    context.user_data.clear()

    await update.message.reply_text(
        f"✅ Cookie berhasil ditambahkan.\n\n"
        f"ID: {cookie_id}",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END