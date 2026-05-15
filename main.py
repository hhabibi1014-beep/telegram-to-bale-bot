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
        
        # ۱. پیام متنی
        if message.content_type == 'text':
            try:
                send_to_bale(dest, text=message.text)
            except: pass
        
        # ۲. فایل‌ها
        else:
            try:
                obj = message.photo[-1] if message.content_type == 'photo' else getattr(message, message.content_type)
                f_size = obj.file_size
                size_str = get_size(f_size)
                
                # گزارش حجم به تلگرام
                bot_tele.reply_to(message, f"📊 حجم فایل: {size_str}")

                # تلاش برای ارسال گزارش به بله (ایمن شده)
                try:
                    send_to_bale(dest, text=f"📂 فایل جدید دریافت شد\n📊 حجم: {size_str}")
                except: pass

                if f_size > 20 * 1024 * 1024: return

                f_info = bot_tele.get_file(obj.file_id)
                downloaded = bot_tele.download_file(f_info.file_path)
                f_type = 'photo' if message.content_type == 'photo' else ('video' if message.content_type in ['video', 'video_note'] else message.content_type)
                
                # ارسال فایل با کپشن اصلی
                send_to_bale(dest, file_data=downloaded, filename="file", caption=message.caption, file_type=f_type)
            except Exception as e: print(f"Tele to Bale Error: {e}")

# --- مسیر ۲: بله به تلگرام (ایمن شده در برابر Timeout) ---
def run_bale_manual():
    offset = 0
    while True:
        try:
            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates?offset={offset}&timeout=10"
            res = requests.get(url, timeout=15).json()
            
            if res.get("ok") and res.get("result"):
                for up in res["result"]:
                    offset = up["update_id"] + 1
                    msg = up.get("message")
                    if not msg: continue
                    
                    try:
                        if msg.get("text"):
                            bot_tele.send_message(USER_1, msg['text'])
                        
                        elif any(k in msg for k in ['photo', 'video', 'document', 'voice', 'audio']):
                            content_type = next(k for k in ['photo', 'video', 'document', 'voice', 'audio'] if k in msg)
                            f_id = msg[content_type][-1]['file_id'] if content_type == 'photo' else msg[content_type]['file_id']
                            caption = msg.get("caption")

                            f_info_res = requests.get(f"https://tapi.bale.ai/bot{BALE_TOKEN}/getFile?file_id={f_id}", timeout=10).json()
                            if f_info_res.get("ok"):
                                f_path = f_info_res['result']['file_path']
                                f_url = f"https://tapi.bale.ai/file/bot{BALE_TOKEN}/{f_path}"
                                f_data = requests.get(f_url, timeout=20).content
                                
                                if content_type == 'photo': bot_tele.send_photo(USER_1, f_data, caption=caption)
                                elif content_type == 'video': bot_tele.send_video(USER_1, f_data, caption=caption)
                                else: bot_tele.send_document(USER_1, f_data, visible_file_name="file", caption=caption)
                    except Exception as e: print(f"Bale to Tele Error: {e}")
        except Exception as e:
            # در صورت Timeout فقط صبر می‌کنیم و دوباره تلاش می‌کنیم
            print(f"Bale connection waiting... {e}")
            time.sleep(5)
        time.sleep(1)

if __name__ == "__main__":
    print("🚀 ربات با سیستم ضد-Timeout روشن شد...")
    
    # حذف وب‌هوک‌ها به صورت ایمن
    try:
        requests.get(f"https://tapi.bale.ai/bot{BALE_TOKEN}/deleteWebhook", timeout=5)
    except: pass
    
    threading.Thread(target=run_bale_manual, daemon=True).start()
    
    while True:
        try:
            bot_tele.polling(none_stop=True, interval=3)
        except Exception as e:
            print(f"Tele Polling Error: {e}")
            time.sleep(10)
