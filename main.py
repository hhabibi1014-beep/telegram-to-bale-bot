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

# --- مسیر ۱: تلگرام به بله (با حفظ کپشن اصلی) ---
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
                
                # ارسال گزارش حجم به صورت جداگانه (بدون دستکاری کپشن)
                bot_tele.reply_to(message, f"📊 حجم فایل: {size_str}")
                send_to_bale(dest, text=f"📂 فایل جدید\n📊 حجم: {size_str}")

                if f_size > 20 * 1024 * 1024: return

                f_info = bot_tele.get_file(obj.file_id)
                downloaded = bot_tele.download_file(f_info.file_path)
                f_type = 'photo' if message.content_type == 'photo' else ('video' if message.content_type in ['video', 'video_note'] else message.content_type)
                
                # کپشن بدون تغییر فرستاده می‌شود
                send_to_bale(dest, file_data=downloaded, filename="file", caption=message.caption, file_type=f_type)
            except Exception as e: print(f"Tele to Bale Error: {e}")

# --- مسیر ۲: بله به تلگرام (با قابلیت دانلود فایل از بله) ---
def run_bale_manual():
    offset = 0
    while True:
        try:
            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates?offset={offset}&timeout=20"
            res = requests.get(url, timeout=25).json()
            if res.get("ok") and res.get("result"):
                for up in res["result"]:
                    offset = up["update_id"] + 1
                    msg = up.get("message")
                    if not msg: continue
                    
                    try:
                        # ۱. پیام متنی
                        if msg.get("text"):
                            bot_tele.send_message(USER_1, msg['text'])
                        
                        # ۲. مدیریت فایل‌ها (دانلود از بله و آپلود در تلگرام)
                        elif any(k in msg for k in ['photo', 'video', 'document', 'voice', 'audio']):
                            content_type = next(k for k in ['photo', 'video', 'document', 'voice', 'audio'] if k in msg)
                            f_id = msg[content_type][-1]['file_id'] if content_type == 'photo' else msg[content_type]['file_id']
                            caption = msg.get("caption")

                            # گرفتن لینک دانلود از بله
                            file_info = requests.get(f"https://tapi.bale.ai/bot{BALE_TOKEN}/getFile?file_id={f_id}").json()
                            if file_info.get("ok"):
                                file_path = file_info['result']['file_path']
                                file_url = f"https://tapi.bale.ai/file/bot{BALE_TOKEN}/{file_path}"
                                file_data = requests.get(file_url).content
                                
                                # ارسال به تلگرام بر اساس نوع
                                if content_type == 'photo': bot_tele.send_photo(USER_1, file_data, caption=caption)
                                elif content_type == 'video': bot_tele.send_video(USER_1, file_data, caption=caption)
                                else: bot_tele.send_document(USER_1, file_data, visible_file_name="file", caption=caption)
                    except Exception as e: print(f"Bale to Tele Error: {e}")
        except: time.sleep(2)

if __name__ == "__main__":
    # حذف وب‌هوک برای رفع خطای Conflict
    requests.get(f"https://tapi.bale.ai/bot{BALE_TOKEN}/deleteWebhook")
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")
    
    threading.Thread(target=run_bale_manual, daemon=True).start()
    
    while True:
        try:
            bot_tele.polling(none_stop=True, interval=3)
        except:
            time.sleep(10)
