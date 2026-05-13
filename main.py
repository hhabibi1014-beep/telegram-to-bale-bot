import telebot
import os
from bale_sender import send_to_bale

TOKEN = os.getenv("TELEGRAM_TOKEN")
# لیست آیدی‌های مجاز تلگرام (اطمینان از استرینگ بودن)
USER_1 = os.getenv("USER_1")
USER_2 = os.getenv("USER_2")
USER_LIST = [USER_1, USER_2]

# نقشه‌برداری تلگرام به بله
DEST_MAP = {
    USER_1: os.getenv("DEST_1"),
    USER_2: os.getenv("DEST_2")
}

bot = telebot.TeleBot(TOKEN)

def get_file_details(message):
    """استخراج اطلاعات فایل و حجم"""
    file_id = None
    file_name = "file"
    file_size = 0
    
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_name = "photo.jpg"
        file_size = message.photo[-1].file_size
    elif message.content_type == 'video':
        file_id = message.video.file_id
        file_name = message.video.file_name or "video.mp4"
        file_size = message.video.file_size
    elif message.content_type == 'document':
        file_id = message.document.id_size if hasattr(message.document, 'id_size') else message.document.file_size
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_size = message.document.file_size
    elif message.content_type == 'audio':
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio.mp3"
        file_size = message.audio.file_size
    elif message.content_type == 'voice':
        file_id = message.voice.file_id
        file_name = "voice.ogg"
        file_size = message.voice.file_size

    return file_id, file_name, file_size

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_messages(message):
    user_id = str(message.from_user.id)
    
    if user_id in USER_LIST:
        dest_id = DEST_MAP.get(user_id)
        
        # مدیریت متن
        if message.content_type == 'text':
            send_to_bale(dest_id, text=f"💬 متن جدید:\n\n{message.text}")
        
        # مدیریت فایل‌ها
        else:
            file_id, f_name, f_size = get_file_details(message)
            size_mb = round(f_size / (1024 * 1024), 2)
            
            # اطلاع‌رسانی اولیه به بله
            send_to_bale(dest_id, text=f"📂 فایل: {f_name}\n⚖️ حجم: {size_mb} MB\n⏳ در حال انتقال به بله...")

            # محدودیت ۲۰ مگابایت تلگرام
            if size_mb > 20:
                send_to_bale(dest_id, text=f"❌ خطا: حجم فایل ({size_mb}MB) بیشتر از حد مجاز تلگرام (20MB) است.")
                return

            try:
                file_info = bot.get_file(file_id)
                downloaded = bot.download_file(file_info.file_path)
                
                # ارسال فایل به بله همراه با کپشن اصلی
                caption = message.caption if message.caption else ""
                send_to_bale(dest_id, file_data=downloaded, filename=f_name, caption=caption)
                send_to_bale(dest_id, text="✅ فایل با موفقیت منتقل شد.")
            except Exception as e:
                send_to_bale(dest_id, text=f"❌ خطا در عملیات انتقال: {str(e)}")

print("🚀 ربات دوکاربره با مانیتورینگ حجم فعال شد...")
# استفاده از این متد برای پایداری بیشتر و رفع خودکار تداخل‌ها
bot.polling(none_stop=True, interval=0, timeout=20)
