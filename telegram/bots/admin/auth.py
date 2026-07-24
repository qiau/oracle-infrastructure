from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import ADMIN_ID


def admin(handler):

    @wraps(handler)
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        user = update.effective_user

        if user is None:
            return

        if user.id not in ADMIN_ID:
            return

        return await handler(update, context)

    return wrapper