import telebot
import os
import threading
from bale_sender import send_to_bale

# --- تنظیمات توکن‌ها و آیدی‌ها ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")
USER_1 = os.getenv("USER_1")
USER_2 = os.getenv("USER_2")
DEST_1 = os.getenv("DEST_1")
DEST_2 = os.getenv("DEST_2")

USER_LIST = [USER_1, USER_2]
DEST_MAP = {USER_1: DEST_1, USER_2: DEST_2}

# --- تعریف ربات‌ها ---
bot_tele = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)
bot_bale = telebot.TeleBot(BALE_TOKEN)
bot_bale.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

# --- تابع محاسبه حجم فایل ---
def get_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    elif size_bytes < 1048576: return f"{size_bytes/1024:.2f} KB"
    else: return f"{size_bytes/1048576:.2f} MB"

# --- بخش ۱: از تلگرام به بله ---
@bot_tele.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'video_note', 'sticker'])
def telegram_to_bale(message):
    uid = str(message.from_user.id)
    if uid in USER_LIST:
        dest = DEST_MAP.get(uid)
        if message.content_type == 'text':
            send_to_bale(dest, text=message.text)
        else:
            try:
                # تشخیص فایل و حجم
                obj = message.photo[-1] if message.content_type == 'photo' else getattr(message, message.content_type)
                f_id, f_size = obj.file_id, obj.file_size
                f_type = 'photo' if message.content_type == 'photo' else ('video' if message.content_type in ['video', 'video_note'] else message.content_type)
                
                size_str = get_size(f_size)
                try:
                    f_info = bot_tele.get_file(f_id)
                    downloaded = bot_tele.download_file(f_info.file_path)
                    caption = f"{message.caption or ''}\n\n📊 حجم: {size_str}"
                    send_to_bale(dest, file_data=downloaded, filename="file", caption=caption, file_type=f_type)
                except:
                    send_to_bale(dest, text=f"⚠️ خطا در ارسال فایل سنگین!\n📊 حجم: {size_str}\nنوع: {message.content_type}")
            except Exception as e: print(f"Tele Error: {e}")

# --- بخش ۲: از بله به تلگرام ---
@bot_bale.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def bale_to_telegram(message):
    try:
        # پیام‌ها از بله مستقیم به USER_1 (خودت) در تلگرام برود
        if message.content_type == 'text':
            bot_tele.send_message(USER_1, f"📥 از بله:\n\n{message.text}")
        elif message.content_type == 'photo':
            bot_tele.send_photo(USER_1, message.photo[-1].file_id, caption="🖼 عکس از بله")
        else:
            f_id = getattr(message, message.content_type).file_id
            bot_tele.send_document(USER_1, f_id, caption=f"📁 فایل {message.content_type} از بله")
    except Exception as e: print(f"Bale Error: {e}")

# --- اجرای همزمان هر دو ربات ---
def run_tele():
    print("📡 تلگرام فعال شد...")
    bot_tele.polling(none_stop=True)

def run_bale():
    print("📡 بله فعال شد...")
    bot_bale.polling(none_stop=True)

if __name__ == "__main__":
    t1 = threading.Thread(target=run_tele)
    t2 = threading.Thread(target=run_bale)
    t1.start()
    t2.start()
