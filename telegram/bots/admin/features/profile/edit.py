from datetime import datetime

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
from database.connection import get_connection

from database.repositories import (
    profile,
    profile_type,
    profile_check,
)

from states.enum import State

PROFILE_FIELDS = {
    "Name": "name",
    "Profile Type": "profile_type_id",
    "Generation": "generation",
    "Birth Date": "birth_date",
    "X Username": "x_username",
    "Instagram Username": "instagram_username",
    "Instagram User ID": "instagram_user_id",
    "TikTok Username": "tiktok_username",
}


def get_conversation():

    entry_points = [
        CommandHandler(
            "profile_edit",
            admin(profile_edit_start),
        )
    ]

    states = {
        State.PROFILE_EDIT_SELECT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_edit_select),
            )
        ],
        State.PROFILE_EDIT_FIELD: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_edit_field),
            )
        ],
        State.PROFILE_EDIT_VALUE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_edit_value),
            )
        ],
    }

    return (
        entry_points,
        states,
    )


async def profile_edit_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "Masukkan nama profile yang ingin diedit.\n\n"
        "Anda dapat mengetik sebagian nama.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.PROFILE_EDIT_SELECT


async def profile_edit_select(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    # Belum memilih profile, lakukan pencarian
    if "profile_mapping" not in context.user_data:

        profiles = profile.search(text)

        if not profiles:
            await update.message.reply_text(
                "Profile tidak ditemukan.\n\n"
                "Silakan masukkan nama profile lagi."
            )
            return State.PROFILE_EDIT_SELECT

        # Tepat satu hasil → langsung pilih
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

            return State.PROFILE_EDIT_SELECT

    # Sudah memilih profile dari keyboard
    else:

        mapping = context.user_data["profile_mapping"]

        if text not in mapping:

            await update.message.reply_text(
                "Silakan pilih profile dari keyboard."
            )

            return State.PROFILE_EDIT_SELECT

        selected = profile.get(
            mapping[text]
        )

    context.user_data.pop(
        "profile_mapping",
        None,
    )

    context.user_data["profile_id"] = selected["id"]

    keyboard = [
        ["Name"],
        ["Profile Type"],
        ["Generation"],
        ["Birth Date"],
        ["X Username"],
        ["Instagram Username"],
        ["Instagram User ID"],
        ["TikTok Username"],
    ]

    await update.message.reply_text(
        f"Profile: {selected['name']}\n\n"
        "Pilih field yang ingin diubah.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    return State.PROFILE_EDIT_FIELD

async def profile_edit_field(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if text not in PROFILE_FIELDS:
        await update.message.reply_text(
            "Silakan pilih field dari keyboard."
        )
        return State.PROFILE_EDIT_FIELD

    field = PROFILE_FIELDS[text]

    context.user_data["field"] = field

    profile_data = profile.get(
        context.user_data["profile_id"]
    )

    if field == "profile_type_id":

        profile_types = profile_type.get_all()

        keyboard = []
        mapping = {}

        current = None

        for row in profile_types:

            label = row["name"].replace("_", " ").title()

            keyboard.append([label])

            mapping[label] = row["id"]

            if row["id"] == profile_data["profile_type_id"]:
                current = label

        context.user_data["profile_type_mapping"] = mapping

        await update.message.reply_text(
            f"Profile Type saat ini:\n\n"
            f"{current}\n\n"
            "Pilih Profile Type baru.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )

    else:

        value = profile_data[field]

        if value is None:
            value = "-"

        await update.message.reply_text(
            f"Nilai saat ini:\n\n"
            f"{value}\n\n"
            "Masukkan nilai baru.\n"
            "Ketik - untuk mengosongkan.",
            reply_markup=ReplyKeyboardRemove(),
        )

    return State.PROFILE_EDIT_VALUE


async def profile_edit_value(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    field = context.user_data["field"]

    value = None if text == "-" else text

    if field == "profile_type_id":

        mapping = context.user_data["profile_type_mapping"]

        if text not in mapping:

            await update.message.reply_text(
                "Silakan pilih Profile Type dari keyboard."
            )

            return State.PROFILE_EDIT_VALUE

        value = mapping[text]

    elif field == "generation":

        if value is not None:

            try:
                value = int(value)

            except ValueError:

                await update.message.reply_text(
                    "Generation harus berupa angka."
                )

                return State.PROFILE_EDIT_VALUE

    elif field == "birth_date":

        if value is not None:

            try:
                datetime.strptime(
                    value,
                    "%Y-%m-%d",
                )

            except ValueError:

                await update.message.reply_text(
                    "Format Birth Date tidak valid.\n"
                    "Gunakan YYYY-MM-DD."
                )

                return State.PROFILE_EDIT_VALUE

    conn = get_connection()

    try:

        profile.update_field(
            conn=conn,
            profile_id=context.user_data["profile_id"],
            field=field,
            value=value,
        )

        profile_check.rebuild(conn)

        conn.commit()

    except Exception:

        conn.rollback()

        await update.message.reply_text(
            "❌ Gagal memperbarui profile.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    finally:

        conn.close()

    context.user_data.clear()

    await update.message.reply_text(
        "✅ Profile berhasil diperbarui.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END