import telebot
import os
from groq import Groq
from telebot import types
from bale_sender import send_to_bale

# تنظیمات
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")
USER_LIST = [os.getenv("USER_1"), os.getenv("USER_2")]
DEST_MAP = {os.getenv("USER_1"): os.getenv("DEST_1"), os.getenv("USER_2"): os.getenv("DEST_2")}

# استفاده از مدل Instant برای سرعت فوق‌العاده
client = Groq(api_key=GROQ_KEY)
AI_MODEL = "llama-3.1-8b-instant"

def get_ai_response(prompt):
    try:
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "پاسخ‌ها را بسیار کوتاه، سریع و به فارسی بده."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500 # محدود کردن برای سرعت بیشتر
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "⚠️ مشکلی در پاسخگویی پیش آمد."

bot = telebot.TeleBot(TOKEN, threaded=True) # فعال کردن پردازش موازی برای سرعت

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🤖 گفتگو با هوش مصنوعی"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام حسن جان! سیستم آماده است.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_messages(message):
    user_id = str(message.from_user.id)
    
    # ۱. مدیریت دکمه و هوش مصنوعی
    if message.content_type == 'text':
        if message.text == "🤖 گفتگو با هوش مصنوعی":
            bot.reply_to(message, "✅ هوش مصنوعی آماده است. سوالت را بپرس:")
            return
        
        # اگر پیام متنی بود، اول جواب هوش مصنوعی را بده (اولویت اول)
        bot.send_chat_action(message.chat.id, 'typing')
        answer = get_ai_response(message.text)
        bot.reply_to(message, answer)

    # ۲. انتقال پیام/فایل به بله (در پس‌زمینه انجام می‌شود)
    if user_id in USER_LIST:
        dest_id = DEST_MAP.get(user_id)
        try:
            if message.content_type == 'text':
                send_to_bale(dest_id, text=message.text)
            else:
                # منطق دانلود و ارسال فایل
                if message.content_type == 'photo': file_id = message.photo[-1].file_id
                elif message.content_type == 'video': file_id = message.video.file_id
                elif message.content_type == 'document': file_id = message.document.file_id
                else: file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id

                file_info = bot.get_file(file_id)
                downloaded = bot.download_file(file_info.file_path)
                send_to_bale(dest_id, file_data=downloaded, filename="file", caption=message.caption, file_type=message.content_type)
        except Exception as e:
            print(f"Transfer Error: {e}")

bot.polling(none_stop=True)
