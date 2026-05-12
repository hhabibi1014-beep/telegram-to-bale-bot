from flask import Flask, request, jsonify
import telebot
import requests
import os
from bale_sender import send_to_bale 

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os.getenv('BALE_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تابع تبدیل واحد حجم برای نمایش بهتر
def get_size_format(b):
    for unit in ["", "K", "M", "G"]:
        if b < 1024: return f"{b:.2f} {unit}B"
        b /= 1024
    return f"{b:.2f} GB"

# نقشه اتصال اکانت‌های تلگرام به چت‌آیدی‌های بله
USER_MAPPING = {
    int(os.getenv('MY_TELEGRAM_ID_1')): os.getenv('BALE_CHAT_ID_1'),
    int(os.getenv('MY_TELEGRAM_ID_2')): os.getenv('BALE_CHAT_ID_2')
}

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return jsonify({'ok': False}), 403

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'document', 'audio', 'video', 'voice'])
def handle_all_messages(message):
    user_id = message.from_user.id
    target_chat_id = USER_MAPPING.get(user_id)
    
    # اگر کاربر در لیست نبود، پیام را نادیده بگیر یا اخطار بده
    if not target_chat_id:
        bot.reply_to(message, "⚠️ شما اجازه استفاده از این پل ارتباطی را ندارید.")
        return

    try:
        size_str = ""
        if message.content_type == 'text':
            r = send_to_bale(None, None, "text", message.text, BALE_TOKEN, target_chat_id)
        else:
            file_id = None
            file_type = "document"
            file_name = "file"
            raw_size = 0
            
            if message.photo:
                file_id, file_type, file_name = message.photo[-1].file_id, "photo", "image.jpg"
                raw_size = message.photo[-1].file_size
            elif message.document:
                file_id, file_type, file_name = message.document.file_id, "document", message.document.file_name
                raw_size = message.document.file_size
            elif message.video:
                file_id, file_type, file_name = message.video.file_id, "video", "video.mp4"
                raw_size = message.video.file_size
            elif message.audio or message.voice:
                media = message.audio or message.voice
                file_id, file_type, file_name = media.file_id, "audio", ("audio.mp3" if message.audio else "voice.ogg")
                raw_size = media.file_size

            size_str = get_size_format(raw_size)

            # محدودیت ۲۰ مگابایت تلگرام
            if raw_size > 20 * 1024 * 1024:
                bot.reply_to(message, f"❌ خطا: حجم فایل ({size_str}) بیشتر از ۲۰ مگابایت است.")
                return

            file_info = bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
            file_content = requests.get(file_url).content
            r = send_to_bale(file_content, file_name, file_type, message.caption or "", BALE_TOKEN, target_chat_id)

        if r and r.status_code == 200:
            bot.reply_to(message, f"✅ با موفقیت به بله منتقل شد.\n⚖️ حجم فایل: {size_str}" if size_str else "✅ متن ارسال شد.")
        else:
            bot.reply_to(message, "❌ خطا در برقراری ارتباط با بله.")

    except Exception as e:
        bot.reply_to(message, f"❌ خطای سیستمی: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
