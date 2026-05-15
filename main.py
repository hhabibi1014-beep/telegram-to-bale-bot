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

bot_tele = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)

# --- تابع محاسبه حجم ---
def get_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    elif size_bytes < 1048576: return f"{size_bytes/1024:.2f} KB"
    else: return f"{size_bytes/1048576:.2f} MB"

# --- بخش ۱: تلگرام به بله (با گزارش به مبدأ) ---
@bot_tele.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'video_note', 'sticker'])
def telegram_to_bale(message):
    uid = str(message.from_user.id)
    if uid in USER_LIST:
        dest = DEST_MAP.get(uid)
        
        if message.content_type == 'text':
            send_to_bale(dest, text=message.text)
        else:
            try:
                # ۱. استخراج اطلاعات فایل
                if message.content_type == 'photo':
                    obj = message.photo[-1]
                elif message.content_type in ['video', 'video_note', 'document', 'audio', 'voice', 'sticker']:
                    obj = getattr(message, message.content_type)
                
                f_id, f_size = obj.file_id, obj.file_size
                size_str = get_size(f_size)
                
                # ۲. گزارش آنی حجم به خودت در تلگرام
                report_msg = bot_tele.reply_to(message, f"📊 گزارش فایل:\nنوع: {message.content_type}\nحجم: {size_str}\n⏳ در حال انتقال به بله...")

                # ۳. بررسی محدودیت ۲۰ مگابایت تلگرام برای دانلود ربات
                if f_size > 20 * 1024 * 1024:
                    bot_tele.edit_message_text(f"⚠️ فایل بسیار بزرگ است ({size_str})!\nتلگرام اجازه دانلود مستقیم به ربات را نمی‌دهد.\nفقط گزارش حجم به بله فرستاده شد.", chat_id=message.chat.id, message_id=report_msg.message_id)
                    send_to_bale(dest, text=f"📂 یک فایل سنگین فرستاده شد:\nنوع: {message.content_type}\nحجم: {size_str}\n❌ به دلیل محدودیت حجم منتقل نشد.")
                    return

                # ۴. تلاش برای دانلود و ارسال
                try:
                    f_info = bot_tele.get_file(f_id)
                    downloaded = bot_tele.download_file(f_info.file_path)
                    
                    f_type = 'photo' if message.content_type == 'photo' else ('video' if message.content_type in ['video', 'video_note'] else message.content_type)
                    
                    caption = f"{message.caption or ''}\n\n📊 حجم: {size_str}"
                    send_to_bale(dest, file_data=downloaded, filename="file", caption=caption, file_type=f_type)
                    
                    # تایید نهایی در تلگرام
                    bot_tele.edit_message_text(f"✅ با موفقیت منتقل شد.\n📊 حجم: {size_str}", chat_id=message.chat.id, message_id=report_msg.message_id)
                
                except Exception as e:
                    bot_tele.edit_message_text(f"❌ خطا در انتقال فایل!\nحجم: {size_str}\nاحتمالاً سرور بله یا تلگرام پاسخگو نیست.", chat_id=message.chat.id, message_id=report_msg.message_id)
                    send_to_bale(dest, text=f"⚠️ خطا در دریافت فایل از تلگرام!\nحجم: {size_str}")

            except Exception as e:
                print(f"Tele Error: {e}")

# --- بخش ۲: بله به تلگرام (بدون تغییر) ---
def run_bale_manual():
    import requests
    import time
    offset = 0
    while True:
        try:
            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates?offset={offset}"
            response = requests.get(url, timeout=10).json()
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

if __name__ == "__main__":
    print("🚀 سیستم پل دوطرفه با گزارش هوشمند فعال شد...")
    threading.Thread(target=run_bale_manual, daemon=True).start()
    bot_tele.polling(none_stop=True)
