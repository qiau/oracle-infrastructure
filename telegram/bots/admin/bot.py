from telegram.ext import ApplicationBuilder

from config.settings import ADMIN_BOT_TOKEN

from bots.admin.commands import register_commands


def create_app():
    app = (
        ApplicationBuilder()
        .token(ADMIN_BOT_TOKEN)
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