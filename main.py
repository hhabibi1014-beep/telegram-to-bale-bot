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

# راه‌اندازی Groq
client = Groq(api_key=GROQ_KEY)

def get_ai_response(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "⚠️ هوش مصنوعی موقتاً قطع است، اما انتقال پیام انجام می‌شود."

bot = telebot.TeleBot(TOKEN, threaded=False)

# ساخت منوی دکمه‌دار
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_ai = types.KeyboardButton("🤖 گفتگو با هوش مصنوعی")
    markup.add(btn_ai)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام حسن جان! به ربات مدیریت پیام خوش آمدی.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_all(message):
    user_id = str(message.from_user.id)
    
    # مدیریت دکمه و هوش مصنوعی
    if message.text == "🤖 گفتگو با هوش مصنوعی":
        bot.reply_to(message, "هر سوالی داری بپرس، من آماده‌ام!")
        return

    if message.content_type == 'text':
        # اگر پیام دستور نبود، به هوش مصنوعی بفرست
        bot.send_chat_action(message.chat.id, 'typing')
        answer = get_ai_response(message.text)
        bot.reply_to(message, answer)

    # انتقال به بله (همان منطق قبلی)
    if user_id in USER_LIST:
        dest_id = DEST_MAP.get(user_id)
        if message.content_type == 'text':
            send_to_bale(dest_id, text=message.text)
        else:
            try:
                file_id = None
                if message.content_type == 'photo': file_id = message.photo[-1].file_id
                elif message.content_type == 'video': file_id = message.video.file_id
                elif message.content_type == 'document': file_id = message.document.file_id
                else: file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id

                file_info = bot.get_file(file_id)
                downloaded = bot.download_file(file_info.file_path)
                send_to_bale(dest_id, file_data=downloaded, filename="file", caption=message.caption, file_type=message.content_type)
            except: pass

bot.polling(none_stop=True, skip_pending=True)
