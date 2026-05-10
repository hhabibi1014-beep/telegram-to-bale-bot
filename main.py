import os
import requests
from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters

# توکن‌ها
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8604521579:AAGaGnQAGAsUCwnglICGOF7tKP3SIpxDr40')
BALE_TOKEN = os.getenv('BALE_TOKEN', '1460285521:Mw1SZUhzaDW2wzu6QBKryMfO_SPYjvaxIvA')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '315946834')
BALE_CHAT_ID = os.getenv('BALE_CHAT_ID', '1511382713')

telegram_bot = Bot(token=TELEGRAM_TOKEN)

def send_to_bale(text):
    """ارسال پیام به بله"""
    url = "https://tapi.bale.ai/sendMessage"
    headers = {
        'Authorization': f'Bearer {BALE_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'chat_id': BALE_CHAT_ID,
        'text': text
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Bale: {response.status_code}")
        return response.ok
    except Exception as e:
        print(f"Error: {e}")
        return False

def send_to_telegram(text):
    """ارسال پیام به تلگرام"""
    try:
        telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def handle_telegram(update, context):
    """تلگرام → بله"""
    msg = update.message
    if not msg:
        return
    
    text = msg.text or msg.caption or "پیام جدید"
    send_to_bale(f"📱 از تلگرام:\n{text}")

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    updater.dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.video, handle_telegram))
    
    print("🤖 ربات شروع به کار کرد")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
