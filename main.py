import telebot
import os
from bale_sender import send_to_bale

TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_MAPPING = {
    os.getenv("USER_1"): os.getenv("DEST_1"),
    os.getenv("USER_2"): os.getenv("DEST_2")
}

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo', 'document', 'video', 'audio', 'voice', 'video_note'])
def handle_files(message):
    user_id = str(message.from_user.id)
    if user_id not in USER_MAPPING:
        return

    target_bale_id = USER_MAPPING[user_id]
    
    try:
        # ۱. استخراج اطلاعات فایل بدون دانلود
        c_type = message.content_type
        if c_type == 'photo':
            file_id = message.photo[-1].file_id
            file_size = message.photo[-1].file_size
        else:
            file_obj = getattr(message, c_type)
            file_id = file_obj.file_id
            file_size = file_obj.file_size

        # ۲. محاسبه حجم به مگابایت
        file_size_mb = round(file_size / (1024 * 1024), 2)
        
        # ۳. چک کردن محدودیت حجم (مثلاً ۵۰ مگابایت)
        if file_size_mb > 50:
            error_text = f"❌ عدم امکان ارسال!\n\n📁 نوع فایل: {c_type}\n📦 حجم فایل: {file_size_mb} MB\n\n⚠️ پیام: حجم فایل بیش از حد مجاز (۵۰ مگابایت) است و امکان جابجایی وجود ندارد."
            send_to_bale(target_bale_id, text=error_text)
            print(f"فایل سنگین رد شد: {file_size_mb} MB")
            return

        # ۴. اگر حجم مجاز بود -> شروع دانلود و ارسال
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_filename = f"temp_{os.path.basename(file_info.file_path)}"
        
        with open(temp_filename, 'wb') as f:
            f.write(downloaded_file)
        
        caption = (message.caption or "") + f"\n\n📦 حجم: {file_size_mb} MB"
        success = send_to_bale(target_bale_id, text=caption, file_path=temp_filename, file_type=c_type)
        
        if not success:
            send_to_bale(target_bale_id, text=f"❌ خطای فنی در آپلود فایل {file_size_mb} مگابایتی به بله.")

        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    except Exception as e:
        print(f"Error: {e}")
        send_to_bale(target_bale_id, text="⚠️ خطا در دسترسی به فایل تلگرام.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = str(message.from_user.id)
    if user_id in USER_MAPPING:
        send_to_bale(USER_MAPPING[user_id], text=message.text)

print("ربات با مانیتورینگ حجم فایل (حتی فایل‌های سنگین) فعال شد...")
bot.infinity_polling()
