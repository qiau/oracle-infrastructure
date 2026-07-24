from telegram import Message

from config.settings import TELEGRAM_MESSAGE_LIMIT


async def reply_long_text(
    message: Message,
    text: str,
):
    if len(text) <= TELEGRAM_MESSAGE_LIMIT:
        await message.reply_text(text)
        return

    start = 0

    while start < len(text):

        end = min(
            start + TELEGRAM_MESSAGE_LIMIT,
            len(text),
        )

        if end < len(text):

            newline = text.rfind(
                "\n",
                start,
                end,
            )

            if newline > start:
                end = newline

        await message.reply_text(
            text[start:end]
        )

        start = end

        while (
            start < len(text)
            and text[start] == "\n"
        ):
            start += 1