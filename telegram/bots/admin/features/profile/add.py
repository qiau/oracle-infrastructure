from datetime import datetime
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from database.repositories import (
    profile,
    profile_type,
    profile_assignment,
    profile_check,
)

from bots.admin.auth import admin
from database.connection import get_connection
from states.enum import State


def get_conversation():

    entry_points = [
        CommandHandler(
            "profile_add",
            admin(profile_add_start),
        )
    ]

    states = {
        State.PROFILE_ADD_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_add_name),
            )
        ],
        State.PROFILE_ADD_TYPE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_add_type),
            )
        ],
        State.PROFILE_ADD_GENERATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_add_generation),
            )
        ],
        State.PROFILE_ADD_BIRTH_DATE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_add_birth_date),
            )
        ],
        State.PROFILE_ADD_X_USERNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_add_x_username),
            )
        ],
        State.PROFILE_ADD_INSTAGRAM_USERNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_add_instagram_username),
            )
        ],
        State.PROFILE_ADD_INSTAGRAM_USER_ID: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_add_instagram_user_id),
            )
        ],
        State.PROFILE_ADD_TIKTOK_USERNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                admin(profile_add_tiktok_username),
            )
        ],
    }

    return (
        entry_points,
        states,
    )

async def profile_add_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "Masukkan nama profile.\n\n"
        "Contoh:\n"
        "Freya",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.PROFILE_ADD_NAME


async def profile_add_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text(
            "Nama profile tidak boleh kosong."
        )
        return State.PROFILE_ADD_NAME

    context.user_data["name"] = name

    profile_types = profile_type.get_all()

    keyboard = []
    mapping = {}

    for row in profile_types:

        label = row["name"].replace("_", " ").title()

        keyboard.append([label])

        mapping[label] = row["id"]

    context.user_data["profile_type_mapping"] = mapping

    await update.message.reply_text(
        "Pilih Profile Type.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    return State.PROFILE_ADD_TYPE

async def profile_add_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    mapping = context.user_data["profile_type_mapping"]

    profile_type_name = update.message.text.strip()

    if profile_type_name not in mapping:
        await update.message.reply_text(
            "Profile Type tidak valid. Silakan pilih dari tombol yang tersedia."
        )
        return State.PROFILE_ADD_TYPE

    context.user_data["profile_type_id"] = mapping[profile_type_name]

    await update.message.reply_text(
        "Masukkan Generation.\n\n"
        "Ketik - jika kosong.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.PROFILE_ADD_GENERATION


async def profile_add_generation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    value = update.message.text.strip()

    if value == "-":
        context.user_data["generation"] = None

    else:
        try:
            context.user_data["generation"] = int(value)
        except ValueError:
            await update.message.reply_text(
                "Generation harus berupa angka atau -."
            )
            return State.PROFILE_ADD_GENERATION

    await update.message.reply_text(
        "Masukkan Birth Date.\n\n"
        "Format: YYYY-MM-DD\n"
        "Ketik - jika kosong."
    )

    return State.PROFILE_ADD_BIRTH_DATE


async def profile_add_birth_date(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    value = update.message.text.strip()

    if value == "-":
        context.user_data["birth_date"] = None

    else:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            await update.message.reply_text(
                "Format Birth Date tidak valid.\n"
                "Gunakan YYYY-MM-DD."
            )
            return State.PROFILE_ADD_BIRTH_DATE

        context.user_data["birth_date"] = value

    await update.message.reply_text(
        "Masukkan X Username.\n\n"
        "Ketik - jika kosong."
    )

    return State.PROFILE_ADD_X_USERNAME


async def profile_add_x_username(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    value = update.message.text.strip()

    context.user_data["x_username"] = (
        None
        if value == "-"
        else value
    )

    await update.message.reply_text(
        "Masukkan Instagram Username.\n\n"
        "Ketik - jika kosong."
    )

    return State.PROFILE_ADD_INSTAGRAM_USERNAME


async def profile_add_instagram_username(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    value = update.message.text.strip()

    context.user_data["instagram_username"] = (
        None
        if value == "-"
        else value
    )

    await update.message.reply_text(
        "Masukkan Instagram User ID.\n\n"
        "Ketik - jika kosong."
    )

    return State.PROFILE_ADD_INSTAGRAM_USER_ID


async def profile_add_instagram_user_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    value = update.message.text.strip()

    context.user_data["instagram_user_id"] = (
        None
        if value == "-"
        else value
    )

    await update.message.reply_text(
        "Masukkan TikTok Username.\n\n"
        "Ketik - jika kosong."
    )

    return State.PROFILE_ADD_TIKTOK_USERNAME



async def profile_add_tiktok_username(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    value = update.message.text.strip()

    context.user_data["tiktok_username"] = (
        None
        if value == "-"
        else value
    )

    conn = get_connection()

    try:

        profile_id = profile.add(
            conn=conn,
            name=context.user_data["name"],
            profile_type_id=context.user_data["profile_type_id"],
            generation=context.user_data["generation"],
            birth_date=context.user_data["birth_date"],
            x_username=context.user_data["x_username"],
            instagram_username=context.user_data["instagram_username"],
            instagram_user_id=context.user_data["instagram_user_id"],
            tiktok_username=context.user_data["tiktok_username"],
        )

        profile_assignment.rebuild(conn)
        profile_check.rebuild(conn)

        conn.commit()

    except Exception:

        conn.rollback()

        await update.message.reply_text(
            "❌ Gagal menambahkan profile.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    finally:

        conn.close()

    context.user_data.clear()

    await update.message.reply_text(
        f"✅ Profile berhasil ditambahkan.\n\n"
        f"ID: {profile_id}",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END