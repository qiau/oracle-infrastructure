from os import getenv

DB_HOST = getenv("DB_HOST")
DB_PORT = int(getenv("DB_PORT", 5432))
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")

ADMIN_ID = {
    int(x.strip())
    for x in getenv("ADMIN_ID", "").split(",")
    if x.strip()
}
ADMIN_BOT_TOKEN = getenv("ADMIN_BOT_TOKEN")

TELEGRAM_MESSAGE_LIMIT = int(getenv("TELEGRAM_MESSAGE_LIMIT"))
