# telegram_to_bale.py
import telebot
from telebot import types
import os
import requests
from bale_api import bale_bot
from config import TELEGRAM_BOT_TOKEN

telegram_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@telegram_bot.message_handler(content_types=['text'])
def handle_text(message):
    text = f"✉️ پیام از Telegram:\n\n{message.text}"
    bale_bot.send_message(os.environ.get('BALE_CHAT_ID'), text)

@telegram_bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_id = message.photo[-1].file_id
        file_info = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
        
        caption = message.caption or ""
        caption = f"🖼 عکس از Telegram:\n\n{caption}"
        
        bale_bot.send_file(os.environ.get('BALE_CHAT_ID'), file_url, 'photo', caption)
    except Exception as e:
        print(f"Error: {e}")

@telegram_bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_id = message.document.file_id
        file_info = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
        
        caption = message.caption or ""
        caption = f"📎 فایل از Telegram:\n\n{caption}"
        
        bale_bot.send_file(os.environ.get('BALE_CHAT_ID'), file_url, 'document', caption)
    except Exception as e:
        print(f"Error: {e}")

@telegram_bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_id = message.video.file_id
        file_info = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
        
        caption = message.caption or ""
        caption = f"🎬 ویدیو از Telegram:\n\n{caption}"
        
        bale_bot.send_file(os.environ.get('BALE_CHAT_ID'), file_url, 'video', caption)
    except Exception as e:
        print(f"Error: {e}")
