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
    profile,
    profile_assignment,
    profile_check,
)

from states.enum import State
from database.connection import get_connection

def get_conversation():

    entry_points = [
        CommandHandler(
            "profile_delete",
            admin(profile_delete_start),
        )
    ]

    states = {
        State.PROFILE_DELETE_SELECT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_delete_select),
            )
        ],
        State.PROFILE_DELETE_CONFIRM: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_delete_confirm),
            )
        ],
    }

    return (
        entry_points,
        states,
    )


async def profile_delete_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "Masukkan nama profile yang ingin dihapus.\n\n"
        "Anda dapat mengetik sebagian nama.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.PROFILE_DELETE_SELECT


async def profile_delete_select(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if "profile_mapping" not in context.user_data:

        profiles = profile.search(text)

        if not profiles:

            await update.message.reply_text(
                "Profile tidak ditemukan.\n\n"
                "Silakan masukkan nama profile lagi."
            )

            return State.PROFILE_DELETE_SELECT

        if len(profiles) == 1:
            selected = profiles[0]

        else:

            keyboard = []
            mapping = {}

            for row in profiles:

                keyboard.append([row["name"]])

                mapping[row["name"]] = row["id"]

            context.user_data["profile_mapping"] = mapping

            await update.message.reply_text(
                "Ditemukan beberapa profile.\n"
                "Silakan pilih salah satu.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True,
                    one_time_keyboard=True,
                ),
            )

            return State.PROFILE_DELETE_SELECT

    else:

        mapping = context.user_data["profile_mapping"]

        if text not in mapping:

            await update.message.reply_text(
                "Silakan pilih profile dari keyboard."
            )

            return State.PROFILE_DELETE_SELECT

        selected = profile.get(
            mapping[text]
        )

    context.user_data.pop(
        "profile_mapping",
        None,
    )

    context.user_data["profile_id"] = selected["id"]

    keyboard = [
        ["Ya"],
        ["Tidak"],
    ]

    await update.message.reply_text(
        f"Yakin ingin menghapus profile:\n\n"
        f"{selected['name']} ?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    return State.PROFILE_DELETE_CONFIRM


async def profile_delete_confirm(
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

        return State.PROFILE_DELETE_CONFIRM

    conn = get_connection()

    try:

        deleted = profile.delete(
            conn=conn,
            profile_id=context.user_data["profile_id"],
        )

        if deleted:

            profile_assignment.rebuild(conn)
            profile_check.rebuild(conn)

        conn.commit()

    except Exception:

        conn.rollback()

        await update.message.reply_text(
            "❌ Gagal menghapus profile.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    finally:

        conn.close()

    context.user_data.clear()

    if deleted:

        await update.message.reply_text(
            "✅ Profile berhasil dihapus.",
            reply_markup=ReplyKeyboardRemove(),
        )

    else:

        await update.message.reply_text(
            "Profile tidak ditemukan.",
            reply_markup=ReplyKeyboardRemove(),
        )

    return ConversationHandler.END