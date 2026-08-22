from telegram.ext import ApplicationBuilder
from config.settings import ADMIN_BOT_TOKEN
from bots.admin.commands import register_commands


def create_app():
    app = (
        ApplicationBuilder()
        .token(ADMIN_BOT_TOKEN)
        .base_url("http://telegram-bot-api:8081/bot")
        .base_file_url("http://telegram-bot-api:8081/file/bot")
        .local_mode(True)
        .build()
    )
    register_commands(app)
    return app


def start():
    app = create_app()
    app.run_polling(
        allowed_updates=[
            "message",
            "callback_query",
        ]
    )