import telebot
import os
from bale_sender import send_to_bale

TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_LIST = [os.getenv("USER_1"), os.getenv("USER_2")]
DEST_MAP = {os.getenv("USER_1"): os.getenv("DEST_1"), os.getenv("USER_2"): os.getenv("DEST_2")}

bot = telebot.TeleBot(TOKEN, threaded=True)

def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_telegram_to_bale(message):
    user_id = str(message.from_user.id)
    if user_id not in USER_LIST:
        return

    dest_id = DEST_MAP.get(user_id)
    
    try:
        if message.content_type == 'text':
            send_to_bale(dest_id, text=message.text)
        else:
            # محاسبه حجم فایل
            file_id = None
            file_size = 0
            if message.content_type == 'photo':
                file_id = message.photo[-1].file_id
                file_size = message.photo[-1].file_size
            elif message.content_type == 'video':
                file_id = message.video.file_id
                file_size = message.video.file_size
            elif message.content_type == 'document':
                file_id = message.document.file_id
                file_size = message.document.file_size
            else:
                file_obj = getattr(message, message.content_type)
                file_id = file_obj.file_id
                file_size = file_obj.file_size

            readable_size = get_size_format(file_size)
            
            try:
                file_info = bot.get_file(file_id)
                downloaded = bot.download_file(file_info.file_path)
                caption = f"{message.caption or ''}\n📦 حجم: {readable_size}"
                send_to_bale(dest_id, file_data=downloaded, filename="file", caption=caption, file_type=message.content_type)
            except Exception as e:
                # اگر در دانلود یا ارسال خطا داد، فقط حجم را بفرست
                send_to_bale(dest_id, text=f"❌ خطا در انتقال فایل!\n📊 حجم فایل: {readable_size}\nنوع: {message.content_type}")

    except Exception as e:
        print(f"General Error: {e}")

print("🚀 انتقال‌دهنده تلگرام به بله فعال شد...")
bot.polling(none_stop=True)
