import os

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Bale API
BALE_BOT_TOKEN = os.environ.get('BALE_BOT_TOKEN')

# User mapping: telegram_chat_id -> bale_chat_id
USER_MAPPING = {
    "123456789": "bale_chat_id_1",
    "987654321": "bale_chat_id_2",
}
