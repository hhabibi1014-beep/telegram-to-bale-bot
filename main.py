import telebot
from telebot import apihelper # وارد کردن مستقیم برای حل خطا
import os
import threading
from bale_sender import send_to_bale

# --- تنظیمات از Railway ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")

# اطلاعات اکانت‌ها
USER_1 = os.getenv("USER_1") # آیدی تلگرام اکانت اول
DEST_1 = os.getenv("DEST_1") # آیدی بله مقصد اول

USER_2 = os.getenv("USER_2") # آیدی تلگرام اکانت دوم
DEST_2 = os.getenv("DEST_2") # آیدی بله مقصد دوم

USER_LIST = [USER_1, USER_2]
DEST_MAP = {USER_1: DEST_1, USER_2: DEST_2}

# --- حل خطای AttributeError ---
# به جای استفاده از bot.api_helper، مستقیماً از خود کتابخانه استفاده می‌کنیم
apihelper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

bot_tele = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)
bot_bale = telebot.TeleBot(BALE_TOKEN)

# --- تابع محاسبه حجم ---
def get_size(size_bytes):
    if size_bytes < 1024: return f"{size_bytes} B"
    elif size_bytes < 1048576: return f"{size_bytes/1024:.2f} KB"
    else: return f"{size_bytes/1048576:.2f} MB"

# --- بخش ۱: تلگرام به بله (مدیریت دو اکانت) ---
@bot_tele.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'video_note', 'sticker'])
def telegram_to_bale(message):
    uid = str(message.from_user.id)
    
    if uid in USER_LIST:
        dest = DEST_MAP.get(uid)
        
        if message.content_type == 'text':
            send_to_bale(dest, text=message.text)
        else:
            try:
                # تشخیص نوع فایل و استخراج اطلاعات
                if message.content_type == 'photo':
                    obj = message.photo[-1]
                    f_type = 'photo'
                elif message.content_type in ['video', 'video_note']:
                    obj = getattr(message, message.content_type)
                    f_type = 'video'
                else:
                    obj = getattr(message, message.content_type)
                    f_type = message.content_type
                
                f_id, f_size = obj.file_id, obj.file_size
                size_str = get_size(f_size)
                
                try:
                    f_info = bot_tele.get_file(f_id)
                    downloaded = bot_tele.download_file(f_info.file_path)
                    caption = f"{message.caption or ''}\n\n📊 حجم: {size_str}"
                    send_to_bale(dest, file_data=downloaded, filename="file", caption=caption, file_type=f_type)
                except:
                    # اگر دانلود نشد فقط حجم را بفرست
                    send_to_bale(dest, text=f"⚠️ فایل منتقل نشد!\n📊 حجم: {size_str}\nنوع: {message.content_type}")
            except Exception as e:
                print(f"Transfer Error: {e}")

# --- بخش ۲: بله به تلگرام (ارسال به اکانت اصلی شما) ---
@bot_bale.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document'])
def bale_to_telegram(message):
    try:
        # پیام‌هایی که در بله می‌آیند به اکانت شماره ۱ شما در تلگرام فرستاده می‌شوند
        if message.content_type == 'text':
            bot_tele.send_message(USER_1, f"📥 از بله:\n\n{message.text}")
        elif message.content_type == 'photo':
            bot_tele.send_photo(USER_1, message.photo[-1].file_id, caption="🖼 عکس از بله")
        else:
            f_id = getattr(message, message.content_type).file_id
            bot_tele.send_document(USER_1, f_id, caption=f"📁 فایل {message.content_type} از بله")
    except Exception as e:
        print(f"Bale to Tele Error: {e}")

# --- اجرای موازی ---
def run_tele():
    bot_tele.polling(none_stop=True)

def run_bale():
    bot_bale.polling(none_stop=True)

if __name__ == "__main__":
    print("🚀 ربات با مدیریت دو اکانت روشن شد...")
    threading.Thread(target=run_tele).start()
    threading.Thread(target=run_bale).start()
