import telebot
import os

# توکن‌ها را از متغیرهای Railway می‌گیرد
BALE_TOKEN = os.getenv("BALE_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# آیدی تلگرام شما (USER_1) که پیام‌ها باید به آن تحویل داده شود
MY_TELEGRAM_ID = os.getenv("USER_1") 

# تعریف ربات بله (برای گوش دادن به پیام‌های بله)
bot_bale = telebot.TeleBot(BALE_TOKEN)
bot_bale.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

# تعریف ربات تلگرام (فقط برای فرستادن پیام به شما)
bot_tele = telebot.TeleBot(TELEGRAM_TOKEN)

@bot_bale.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_bale_to_telegram(message):
    try:
        # ۱. اگر متن بود
        if message.content_type == 'text':
            bot_tele.send_message(MY_TELEGRAM_ID, f"📥 پیام جدید از بله:\n\n{message.text}")
        
        # ۲. اگر عکس بود
        elif message.content_type == 'photo':
            bot_tele.send_photo(MY_TELEGRAM_ID, message.photo[-1].file_id, caption=f"🖼 تصویر از بله\n{message.caption or ''}")
            
        # ۳. سایر فایل‌ها (ویدیو، داکیومنت و غیره)
        else:
            file_id = getattr(message, message.content_type).file_id
            bot_tele.send_document(MY_TELEGRAM_ID, file_id, caption=f"📁 فایل ({message.content_type}) از بله")
            
    except Exception as e:
        print(f"خطا در انتقال از بله به تلگرام: {e}")

print("🚀 شنونده بله فعال شد (ارسال به تلگرام)...")
bot_bale.polling(none_stop=True)
