import os
import requests
from flask import Flask, request, jsonify
import telebot
from Bale import BaleBot

app = Flask(__name__)

# تنظیمات
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os.getenv('BALE_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BALE_CHAT_ID = os.getenv('BALE_CHAT_ID')

# ایجاد بات‌ها
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)
bale_bot = BaleBot(BALE_TOKEN)

def get_file_url(file_id, bot, chat_id):
    """دریافت لینک دانلود فایل"""
    try:
        file = bot.get_file(file_id)
        return f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path}"
    except Exception as e:
        print(f"Error getting file URL: {e}")
        return None

def forward_to_bale(message, file_url=None):
    """ارسال به بله"""
    try:
        if message.text:
            bale_bot.send_message(BALE_CHAT_ID, message.text)
        elif message.photo:
            file_id = message.photo[-1].file_id
            if file_url:
                bale_bot.send_photo(BALE_CHAT_ID, file_url, caption=message.caption or "")
        elif message.video:
            if file_url:
                bale_bot.send_video(BALE_CHAT_ID, file_url, caption=message.caption or "")
        elif message.document:
            if file_url:
                bale_bot.send_document(BALE_CHAT_ID, file_url, caption=message.caption or "")
        elif message.voice:
            if file_url:
                bale_bot.send_voice(BALE_CHAT_ID, file_url)
        elif message.audio:
            if file_url:
                bale_bot.send_audio(BALE_CHAT_ID, file_url)
    except Exception as e:
        print(f"Error forwarding to Bale: {e}")

def forward_to_telegram(message, file_url=None):
    """ارسال به تلگرام"""
    try:
        if message.text:
            telegram_bot.send_message(TELEGRAM_CHAT_ID, message.text)
        elif message.photo:
            if file_url:
                telegram_bot.send_photo(TELEGRAM_CHAT_ID, file_url, caption=message.caption or "")
        elif message.video:
            if file_url:
                telegram_bot.send_video(TELEGRAM_CHAT_ID, file_url, caption=message.caption or "")
        elif message.document:
            if file_url:
                telegram_bot.send_document(TELEGRAM_CHAT_ID, file_url, caption=message.caption or "")
        elif message.voice:
            if file_url:
                telegram_bot.send_voice(TELEGRAM_CHAT_ID, file_url)
        elif message.audio:
            if file_url:
                telegram_bot.send_audio(TELEGRAM_CHAT_ID, file_url)
    except Exception as e:
        print(f"Error forwarding to Telegram: {e}")

# وب‌هوک تلگرام
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    try:
        update = telebot.types.Update.de_json(request.get_json(force=True))
        message = update.message
        
        if message and str(message.chat.id) == str(TELEGRAM_CHAT_ID):
            file_url = None
            if message.photo:
                file_url = get_file_url(message.photo[-1].file_id, telegram_bot, TELEGRAM_CHAT_ID)
            elif message.video:
                file_url = get_file_url(message.video.file_id, telegram_bot, TELEGRAM_CHAT_ID)
            elif message.document:
                file_url = get_file_url(message.document.file_id, telegram_bot, TELEGRAM_CHAT_ID)
            elif message.voice:
                file_url = get_file_url(message.voice.file_id, telegram_bot, TELEGRAM_CHAT_ID)
            elif message.audio:
                file_url = get_file_url(message.audio.file_id, telegram_bot, TELEGRAM_CHAT_ID)
            
            forward_to_bale(message, file_url)
        
        return jsonify({'ok': True})
    except Exception as e:
        print(f"Telegram webhook error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

# وب‌هوک بله
@app.route(f'/bale_webhook_{BALE_TOKEN}', methods=['POST'])
def bale_webhook():
    try:
        data = req…
