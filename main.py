from flask import Flask, request, jsonify
import telebot
import requests
import os
from bale_sender import send_to_bale 

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تابع کمکی برای محاسبه حجم فایل
def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G"]:
        if b < factor:
            return f"{b:.2f} {unit}{suffix}"
        b /= factor

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        telegram_bot.process_new_updates([update])
        return ''
    return jsonify({'ok': False}), 403

# ۱. مدیریت پیام‌های متنی ساده
@telegram_bot.message_handler(content_types=['text'])
def handle_text(message):
    r = send_to_bale(None, None, "text", message.text)
    if r and r.status_code == 200:
        telegram_bot.reply_to(message, "✅ متن ارسال شد")
    else:
        telegram_bot.reply_to(message, "❌ خطا در ارسال متن")

# ۲. مدیریت انواع فایل (عکس، فیلم، صدا، داکیومنت)
@telegram_bot.message_handler(content_types=['photo', 'document', 'audio', 'video', 'voice'])
def handle_media(message):
    try:
        file_id = None
        file_name = "file"
        file_type = "document"

        if message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
            file_name = "image.jpg"
        elif message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
        elif message.video:
            file_id = message.video.file_id
            file_type = "video"
            file_name = "video.mp4"
        elif message.audio or message.voice:
            file_id = (message.audio or message.voice).file_id
            file_type = "audio"
            file_name = "audio.mp3" if message.audio else "voice.ogg"

        if file_id:
            file_info = telegram_bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
            response = requests.get(file_url)
            file_content = response.content
            
            # محاسبه حجم
            size_str = get_size_format(len(file_content))
            caption = message.caption or ""
            
            r = send_to_bale(file_content, file_name, file_type, caption)
            
            if r and r.status_code == 200:
                telegram_bot.reply_to(message, f"✅ ارسال شد\n⚖️ حجم: {size_str}")
            else:
                msg = f"❌ خطا در بله\n⚖️ حجم فایل: {size_str}"
                telegram_bot.reply_to(message, msg)
                
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ خطای سیستم: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
