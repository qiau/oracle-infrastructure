from telegram import (
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "✅ Proses berhasil dibatalkan.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END