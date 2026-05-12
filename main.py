from flask import Flask, request, jsonify
import telebot
import requests
import os
from bale_sender import send_to_bale 

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تابع تبدیل حجم فایل به فرمت خوانا
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

# مدیریت پیام‌های متنی
@telegram_bot.message_handler(content_types=['text'])
def handle_text(message):
    r = send_to_bale(None, None, "text", message.text)
    if r and r.status_code == 200:
        telegram_bot.reply_to(message, "✅ متن با موفقیت ارسال شد")
    else:
        telegram_bot.reply_to(message, "❌ خطا در ارسال متن به بله")

# مدیریت انواع فایل و رسانه
@telegram_bot.message_handler(content_types=['photo', 'document', 'audio', 'video', 'voice'])
def handle_media(message):
    try:
        file_id = None
        file_name = "file"
        file_type = "document"

        # تشخیص نوع رسانه
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
            # تلاش برای گرفتن اطلاعات فایل از تلگرام
            file_info = telegram_bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
            
            # دانلود فایل
            response = requests.get(file_url)
            file_content = response.content
            
            # محاسبه حجم و ارسال
            size_str = get_size_format(len(file_content))
            caption = message.caption or ""
            
            r = send_to_bale(file_content, file_name, file_type, caption)
            
            if r and r.status_code == 200:
                telegram_bot.reply_to(message, f"✅ فایل ارسال شد\n⚖️ حجم: {size_str}")
            else:
                telegram_bot.reply_to(message, f"❌ خطا در بله\n⚖️ حجم فایل: {size_str}")
                
    except Exception as e:
        error_text = str(e)
        # نمایش پیام فارسی برای فایل‌های حجیم
        if "file is too big" in error_text:
            telegram_bot.reply_to(message, "⚠️ این فایل از حد مجاز تلگرام (۲۰ مگابایت) بزرگ‌تر است و امکان انتقال آن وجود ندارد.")
        else:
            telegram_bot.reply_to(message, f"❌ خطای سیستم: {error_text}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
