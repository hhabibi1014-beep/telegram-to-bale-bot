import telebot
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

# --- مسیر ۱: تلگرام به بله ---
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
                f_size = obj.file_size
                size_str = get_size(f_size)
                
                # گزارش به تلگرام و بله
                report = bot_tele.reply_to(message, f"📊 حجم: {size_str}\n⏳ ارسال به بله...")
                send_to_bale(dest, text=f"📂 فایل جدید در حال دریافت...\n📊 حجم: {size_str}")

                if f_size > 20 * 1024 * 1024:
                    bot_tele.edit_message_text(f"⚠️ سنگین ({size_str})! فقط گزارش فرستاده شد.", message.chat.id, report.message_id)
                    return

                f_info = bot_tele.get_file(obj.file_id)
                downloaded = bot_tele.download_file(f_info.file_path)
                f_type = 'photo' if message.content_type == 'photo' else ('video' if message.content_type in ['video', 'video_note'] else message.content_type)
                
                send_to_bale(dest, file_data=downloaded, filename="file", caption=f"📊 حجم: {size_str}", file_type=f_type)
                bot_tele.edit_message_text(f"✅ ارسال شد ({size_str})", message.chat.id, report.message_id)
            except Exception as e: print(f"Tele Error: {e}")

# --- مسیر ۲: بله به تلگرام (متن + فایل + ویس) ---
def run_bale_manual():
    offset = 0
    print("📡 موتور بله فعال شد...")
    while True:
        try:
            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates?offset={offset}&timeout=20"
            res = requests.get(url, timeout=25).json()
            if res.get("ok") and res.get("result"):
                for up in res["result"]:
                    offset = up["update_id"] + 1
                    msg = up.get("message")
                    if not msg: continue
                    
                    # تشخیص و ارسال انواع پیام به USER_1 در تلگرام
                    try:
                        if msg.get("text"):
                            bot_tele.send_message(USER_1, f"📥 بله:\n\n{msg['text']}")
                        elif msg.get("photo"):
                            bot_tele.send_photo(USER_1, msg['photo'][-1]['file_id'], caption="🖼 عکس از بله")
                        elif msg.get("video"):
                            bot_tele.send_video(USER_1, msg['video']['file_id'], caption="🎬 ویدیو از بله")
                        elif msg.get("voice"):
                            bot_tele.send_voice(USER_1, msg['voice']['file_id'], caption="🎤 ویس از بله")
                        elif msg.get("document"):
                            bot_tele.send_document(USER_1, msg['document']['file_id'], caption="📁 فایل از بله")
                    except Exception as e: print(f"Error sending to Tele: {e}")
        except: time.sleep(2)

# --- مدیریت اجرای ربات و رفع خطای Conflict ---
if __name__ == "__main__":
    # ۱. حذف وب‌هوک احتمالی برای بله و تلگرام
    requests.get(f"https://tapi.bale.ai/bot{BALE_TOKEN}/deleteWebhook")
    
    # ۲. شروع موتور بله در پس‌زمینه
    threading.Thread(target=run_bale_manual, daemon=True).start()
    
    # ۳. شروع موتور تلگرام با مدیریت خطا
    print("🚀 ربات با مدیریت خطاها روشن شد...")
    while True:
        try:
            bot_tele.polling(none_stop=True, interval=3, timeout=20)
        except Exception as e:
            if "409" in str(e):
                print("⚠️ خطای Conflict (ربات جای دیگری باز است). ۱۰ ثانیه صبر...")
                time.sleep(10)
            else:
                time.sleep(5)
