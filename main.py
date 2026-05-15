import telebot
import os
from bale_sender import send_to_bale

# تنظیمات از Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_LIST = [os.getenv("USER_1"), os.getenv("USER_2")]
DEST_MAP = {os.getenv("USER_1"): os.getenv("DEST_1"), os.getenv("USER_2"): os.getenv("DEST_2")}

bot = telebot.TeleBot(TOKEN, threaded=True)

# تابع کمکی برای تبدیل بایت به حجم قابل خواندن
def get_readable_size(size_in_bytes):
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"

# اضافه کردن تمام تایپ‌ها از جمله ویدیو نوت و استیکر
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'video_note', 'sticker'])
def handle_telegram_to_bale(message):
    user_id = str(message.from_user.id)
    
    # بررسی دسترسی کاربر
    if user_id in USER_LIST:
        dest_id = DEST_MAP.get(user_id)
        
        # ۱. مدیریت پیام‌های متنی
        if message.content_type == 'text':
            send_to_bale(dest_id, text=message.text)
        
        # ۲. مدیریت انواع فایل‌ها
        else:
            try:
                file_id = None
                file_size = 0
                file_type = 'document' # پیش‌فرض
                
                # تشخیص نوع و استخراج اطلاعات
                if message.content_type == 'photo':
                    file_id = message.photo[-1].file_id
                    file_size = message.photo[-1].file_size
                    file_type = 'photo'
                elif message.content_type == 'video':
                    file_id = message.video.file_id
                    file_size = message.video.file_size
                    file_type = 'video'
                elif message.content_type == 'video_note': # ویدیوهای دایره‌ای
                    file_id = message.video_note.file_id
                    file_size = message.video_note.file_size
                    file_type = 'video' # در بله به عنوان ویدیو ارسال شود
                elif message.content_type == 'document':
                    file_id = message.document.file_id
                    file_size = message.document.file_size
                    file_type = 'document'
                elif message.content_type == 'audio':
                    file_id = message.audio.file_id
                    file_size = message.audio.file_size
                    file_type = 'audio'
                elif message.content_type == 'voice':
                    file_id = message.voice.file_id
                    file_size = message.voice.file_size
                    file_type = 'voice'
                elif message.content_type == 'sticker':
                    file_id = message.sticker.file_id
                    file_size = message.sticker.file_size
                    file_type = 'document'

                readable_size = get_readable_size(file_size)
                
                try:
                    # دانلود فایل از تلگرام
                    file_info = bot.get_file(file_id)
                    downloaded = bot.download_file(file_info.file_path)
                    
                    # تهیه کپشن همراه با حجم
                    caption_text = f"{message.caption or ''}\n\n📊 حجم: {readable_size}"
                    
                    # ارسال به بله با استفاده از فایل bale_sender شما
                    send_to_bale(
                        dest_id=dest_id, 
                        file_data=downloaded, 
                        filename=f"file_{file_id[:5]}", 
                        caption=caption_text, 
                        file_type=file_type
                    )
                
                except Exception as download_error:
                    # در صورت خطای دانلود (مثلاً فایل بالای ۲۰ مگابایت)
                    error_msg = f"⚠️ فایل منتقل نشد (احتمالاً به دلیل محدودیت حجم)\n📊 حجم: {readable_size}\nنوع: {message.content_type}"
                    send_to_bale(dest_id, text=error_msg)

            except Exception as e:
                print(f"خطای کلی در پردازش فایل: {e}")

print("🚀 ربات پل ارتباطی با پشتیبانی از Video Note فعال شد...")
bot.polling(none_stop=True)
