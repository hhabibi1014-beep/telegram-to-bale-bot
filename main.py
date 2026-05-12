from flask import Flask, request, jsonify
import telebot
import requests
import os
# اینجا به برنامه می‌گوییم از فایلی که در مرحله قبل ساختیم استفاده کن
from bale_sender import send_to_bale 

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        telegram_bot.process_new_updates([update])
    except:
        pass
    return jsonify({'ok': True})

@telegram_bot.message_handler(content_types=['photo', 'document', 'audio', 'video', 'voice'])
def handle_media(message):
    try:
        # پیدا کردن مشخصات فایل فرستاده شده در تلگرام
        file_id = None
        file_type = "document"
        file_name = "file"

        if message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
        elif message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name
        elif message.video:
            file_id = message.video.file_id
            file_type = "video"
        
        if file_id:
            # دانلود فایل از تلگرام
            file_info = telegram_bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
            file_content = requests.get(file_url).content
            
            # فرستادن فایل به فایل جانبی (bale_sender) برای ارسال به بله
            text = message.caption or ""
            r = send_to_bale(file_content, file_name, file_type, text)
            
            if r and r.status_code == 200:
                telegram_bot.reply_to(message, "✅ با موفقیت به بله فرستاده شد")
            else:
                telegram_bot.reply_to(message, "❌ خطا در ارسال")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
