from flask import request, jsonify
import telebot
import requests
import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os.getenv('BALE_TOKEN')
BALE_CHAT_ID = os.getenv('BALE_CHAT_ID')

telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_to_bale(file_content, file_name, file_type, text):
    data = {'chat_id': BALE_CHAT_ID}
    if text:
        data['caption'] = text
    
    try:
        if file_type == "photo":
            files = {'photo': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendPhoto",
                data=data,
                files=files
            )
        elif file_type == "video":
            files = {'video': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendVideo",
                data=data,
                files=files
            )
        elif file_type == "audio" or file_type == "voice":
            files = {'audio': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendAudio",
                data=data,
                files=files
            )
        else:
            files = {'document': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendDocument",
                data=data,
                files=files
            )
        return r
    except Exception as e:
        print(f"Error: {e}")
        return None

@telegram_bot.message_handler(content_types=['photo', 'document', 'audio', 'video', 'voice'])
def handle_media(message):
    # ... همون کد قبلی تو

def handle_telegram_message(request):
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        telegram_bot.process_new_updates([update])
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({'ok': True})
