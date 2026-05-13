import telebot
import os
from bale_sender import send_to_bale

TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_LIST = [os.getenv("USER_1"), os.getenv("USER_2")]
DEST_MAP = {os.getenv("USER_1"): os.getenv("DEST_1"), os.getenv("USER_2"): os.getenv("DEST_2")}

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_messages(message):
    user_id = str(message.from_user.id)
    if user_id not in USER_LIST:
        return

    dest_id = DEST_MAP.get(user_id)
    
    if message.content_type == 'text':
        send_to_bale(dest_id, text=message.text)
        bot.reply_to(message, "✅ متن به بله ارسال شد.")
    
    else:
        # استخراج اطلاعات فایل
        file_type = message.content_type
        if file_type == 'photo':
            file_id = message.photo[-1].file_id
            f_name = "image.jpg"
            f_size = message.photo[-1].file_size
        elif file_type == 'video':
            file_id = message.video.file_id
            f_name = message.video.file_name or "video.mp4"
            f_size = message.video.file_size
        elif file_type == 'document':
            file_id = message.document.file_id
            f_name = message.document.file_name
            f_size = message.document.file_size
        elif file_type == 'audio':
            file_id = message.audio.file_id
            f_name = message.audio.file_name or "audio.mp3"
            f_size = message.audio.file_size
        else: # voice
            file_id = message.voice.file_id
            f_name = "voice.ogg"
            f_size = message.voice.file_size

        size_mb = round(f_size / (1024 * 1024), 2)
        
        # ارسال گزارش به تلگرام (مبدأ)
        report = bot.reply_to(message, f"📥 فایل: {f_name}\n⚖️ حجم: {size_mb} MB\n⏳ در حال انتقال...")

        if size_mb > 20:
            bot.edit_message_text(f"❌ خطا: حجم ({size_mb}MB) از محدودیت ۲۰ مگابایت تلگرام بیشتر است.", chat_id=message.chat.id, message_id=report.message_id)
            return

        try:
            file_info = bot.get_file(file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            # ارسال به بله با فرمت خودش
            res = send_to_bale(dest_id, file_data=downloaded, filename=f_name, caption=message.caption, file_type=file_type)
            
            if res and res.get("ok"):
                bot.edit_message_text("✅ با موفقیت در بله آپلود شد.", chat_id=message.chat.id, message_id=report.message_id)
            else:
                bot.edit_message_text("⚠️ فایل دریافت شد اما بله خطا داد.", chat_id=message.chat.id, message_id=report.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ خطای سیستم: {str(e)}", chat_id=message.chat.id, message_id=report.message_id)

print("🚀 ربات هوشمند فعال شد...")
bot.polling(none_stop=True)
