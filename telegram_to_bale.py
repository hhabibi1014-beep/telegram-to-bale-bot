import requests
from telebot import TeleBot

from config import TELEGRAM_BOT_TOKEN, BALE_BOT_TOKEN, BALE_CHAT_ID

telegram_robot = TeleBot(TELEGRAM_BOT_TOKEN)

@telegram_robot.message_handler(commands=['start'])
def handle_start(message):
    telegram_robot.reply_to(message, "✅ ربات فعال شد! پیام بفرستید.")

@telegram_robot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text
    
    url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/sendMessage"
    data = {"chat_id": BALE_CHAT_ID, "text": text}
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            telegram_robot.reply_to(message, "✅ به Bale ارسال شد!")
        else:
            telegram_robot.reply_to(message, f"❌ خطا: {response.text}")
    except Exception as e:
        telegram_robot.reply_to(message, f"❌ خطا: {str(e)}")
