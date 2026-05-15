import telebot
from telebot import apihelper
import os
import threading
import time
import requests
from bale_sender import send_to_bale

# --- تنظیمات ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")
USER_1 = os.getenv("USER_1")
DEST_1 = os.getenv("DEST_1")
USER_2 = os.getenv("USER_2")
DEST_2 = os.getenv("DEST_2")

USER_LIST = [USER_1, USER_2]
DEST_MAP = {USER_1: DEST_1, USER_2: DEST_2}

bot_tele = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)

def get_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    elif size_bytes < 1048576: return f"{size_bytes/1024:.2f} KB"
    else: return f"{size_bytes/1048576:.2f} MB"

# --- تلگرام به بله (گزارش به هر دو طرف) ---
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
                size_str = get_size(f_size)
                
                # گزارش به تلگرام
                report = bot_tele.reply_to(message, f"📊 حجم فایل: {size_str}\n⏳ در حال ارسال به بله...")
                
                # گزارش به بله (قبل از ارسال فایل)
                send_to_bale(dest, text=f"📂 در حال دریافت فایل از تلگرام...\n📊 حجم: {size_str}\nنوع: {message.content_type}")

                if f_size > 20 * 1024 * 1024:
                    bot_tele.edit_message_text(f"⚠️ سنگین ({size_str})! فقط گزارش به بله رفت.", message.chat.id, report.message_id)
                    return

                f_info = bot_tele.get_file(f_id)
                downloaded = bot_tele.download_file(f_info.file_path)
                f_type = 'photo' if message.content_type == 'photo' else ('video' if message.content_type in ['video', 'video_note'] else message.content_type)
                
                send_to_bale(dest, file_data=downloaded, filename="file", caption=f"📊 حجم: {size_str}", file_type=f_type)
                bot_tele.edit_message_text(f"✅ ارسال شد. ({size_str})", message.chat.id, report.message_id)
            except Exception as e:
                print(f"Error: {e}")

# --- بله به تلگرام (پشتیبانی از متن و فایل) ---
def run_bale_manual():
    offset = 0
    while True:
        try:
            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates?offset={offset}&timeout=30"
            res = requests.get(url, timeout=35).json()
            if res.get("ok") and res.get("result"):
                for up in res["result"]:
                    m = up.get("message")
                    if m:
                        # ۱. متن
                        if m.get("text"):
                            bot_tele.send_message(USER_1, f"📥 بله (متن):\n\n{m['text']}")
                        # ۲. عکس
                        elif m.get("photo"):
                            bot_tele.send_photo(USER_1, m['photo'][-1]['file_id'], caption="🖼 عکس از بله")
                        # ۳. ویدیو
                        elif m.get("video"):
                            bot_tele.send_video(USER_1, m['video']['file_id'], caption="🎬 ویدیو از بله")
                        # ۴. داکیومنت و فایل
                        elif m.get("document"):
                            bot_tele.send_document(USER_1, m['document']['file_id'], caption="📁 فایل از بله")
                    offset = up["update_id"] + 1
        except: time.sleep(2)

if __name__ == "__main__":
    print("🚀 سیستم فعال شد. خطاها در حال مدیریت هستند...")
    # رفع خطای Conflict با کمی تاخیر در شروع
    time.sleep(5) 
    threading.Thread(target=run_bale_manual, daemon=True).start()
    
    # حلقه برای جلوگیری از توقف ربات در صورت خطای تلگرام
    while True:
        try:
            bot_tele.polling(none_stop=True, interval=2, timeout=20)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(10)
