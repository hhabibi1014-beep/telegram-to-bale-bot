from flask import Flask, request, jsonify
import telebot
import requests
import io
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os.getenv('BALE_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BALE_CHAT_ID = os.getenv('BALE_CHAT_ID')

telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        telegram_bot.process_new_updates([update])
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({'ok': True})

@telegram_bot.message_handler(content_types=['photo', 'document', 'audio', 'video'])
def handle_media(message):
    try:
        file_id = None
        file_type = None
        file_name = "file"
        
        if message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
        elif message.document:
            file_id = message.document.file_id
            file_type = "document"
            file_name = message.document.file_name or "file"
        elif message.audio:
            file_id = message.audio.file_id
            file_type = "document"
            file_name = message.audio.file_name or "audio.mp3"
        elif message.video:
            file_id = message.video.file_id
            file_type = "video"
        
        if file_id:
            # دانلود فایل از تلگرام
            file_info = telegram_bot.get_file(file_id)
            downloaded_file = telegram_bot.download_file(file_info.file_path)
            file_obj = io.BytesIO(downloaded_file)
            file_obj.name = file_name
            
            # ارسال پیام متنی
            text = message.caption or message.text or ""
            requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage",
                json={'chat_id': BALE_CHAT_ID, 'text': f'پیام از تلگرام:\n{text}'}
            )
            
            # ارسال فایل به Bale
            files = {'file': (file_name, file_obj)}
            
            if file_type == "photo":
                r = requests.post(
                    f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendPhoto",
                    data={'chat_id': BALE_CHAT_ID},
                    files=files
                )
            else:
                r = requests.post(
                    f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendDocument",
                    data={'chat_id': BALE_CHAT_ID},
                    files=files
                )
            
            print(f"Bale response: {r.status_code} - {r.text}")
            
            if r.status_code == 200:
                telegram_bot.reply_to(message, "✅ فایل به Bale ارسال شد!")
            else:
                telegram_bot.reply_to(message, f"❌ خطا: {r.text}")
    except Exception as e:
        print(f"Error: {e}")
        telegram_bot.reply_to(message, f"❌ خطا: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
