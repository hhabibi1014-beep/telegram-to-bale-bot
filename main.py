import telebot
from telebot import apihelper
import os
import threading
from bale_sender import send_to_bale

# --- تنظیمات توکن‌ها ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")

USER_1 = os.getenv("USER_1")
DEST_1 = os.getenv("DEST_1")
USER_2 = os.getenv("USER_2")
DEST_2 = os.getenv("DEST_2")

USER_LIST = [USER_1, USER_2]
DEST_MAP = {USER_1: DEST_1, USER_2: DEST_2}

# --- راه‌اندازی ربات تلگرام (با آدرس پیش‌فرض تلگرام) ---
bot_tele = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)

# --- راه‌اندازی ربات بله (با آدرس اختصاصی بله) ---
# برای اینکه تداخل ایجاد نشود، یک کلاس جدا برای بله می‌سازیم
class BaleBot(telebot.TeleBot):
    def __init__(self, token, *args, **kwargs):
        super().__init__(token, *args, **kwargs)
    def get_me(self):
        # تغییر موقت آیدی برای بله
        original_url = apihelper.API_URL
        apihelper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"
        result = super().get_me()
        apihelper.API_URL = original_url
        return result

bot_bale = telebot.TeleBot(BALE_TOKEN)

# تابع کمکی برای ارسال پیام به بله با آدرس درست
def send_msg_bale_request(method, data):
    url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/{method}"
    import requests
    return requests.post(url, json=data)

# --- تابع محاسبه حجم ---
def get_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    elif size_bytes < 1048576: return f"{size_bytes/1024:.2f} KB"
    else: return f"{size_bytes/1048576:.2f} MB"

# --- بخش ۱: تلگرام به بله ---
@bot_tele.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'video_note', 'sticker'])
def telegram_to_bale(message):
    uid = str(message.from_user.id)
    if uid in USER_LIST:
        dest = DEST_MAP.get(uid)
        if message.content_type == 'text':
            send_to_bale(dest, text=message.text)
        else:
            try:
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
                    send_to_bale(dest, text=f"⚠️ فایل منتقل نشد!\n📊 حجم: {size_str}")
            except Exception as e: print(f"Tele Error: {e}")

# --- بخش ۲: بله به تلگرام ---
# از متد پولینگ دستی برای بله استفاده می‌کنیم تا با تلگرام قاطی نشود
def run_bale_manual():
    import requests
    import time
    offset = 0
    print("📡 موتور بله روشن شد...")
    while True:
        try:
            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates?offset={offset}"
            response = requests.get(url).json()
            if response.get("ok") and response.get("result"):
                for update in response["result"]:
                    msg = update.get("message")
                    if msg:
                        text = msg.get("text")
                        if text:
                            bot_tele.send_message(USER_1, f"📥 از بله:\n\n{text}")
                    offset = update["update_id"] + 1
        except: pass
        time.sleep(1)

# --- اجرای نهایی ---
if __name__ == "__main__":
    print("🚀 سیستم پل دوطرفه فعال شد...")
    # اجرای تلگرام در ترد اصلی
    threading.Thread(target=run_bale_manual, daemon=True).start()
    bot_tele.polling(none_stop=True)
