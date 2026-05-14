import telebot
import os
import google.generativeai as genai
from telebot import types

# تنظیمات
BALE_TOKEN = os.getenv("BALE_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# آیدی‌های مدیر (فقط تو و همسرت)
ADMIN_IDS = [os.getenv("DEST_1"), os.getenv("DEST_2")]

# راه‌اندازی Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# راه‌اندازی ربات بله
bot = telebot.TeleBot(BALE_TOKEN, threaded=False)
bot.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

def get_main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🤖 گپ با هوش مصنوعی"))
    # دکمه فوروارد فقط برای مدیرها ظاهر می‌شود
    if str(user_id) in ADMIN_IDS:
        markup.add(types.KeyboardButton("🔄 بازبینی پیام‌های شخصی (فقط مدیر)"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    welcome_text = "سلام! من دستیار هوشمند شما هستم. چطور می‌توانم کمکتان کنم؟"
    bot.send_message(user_id, welcome_text, reply_markup=get_main_keyboard(user_id))

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    user_id = str(message.chat.id)
    text = message.text

    # ۱. بخش اختصاصی: فوروارد پیام‌ها (فقط برای ادمین)
    if text == "🔄 بازبینی پیام‌های شخصی (فقط مدیر)":
        if user_id in ADMIN_IDS:
            if os.path.exists(f"history_{user_id}.txt"):
                with open(f"history_{user_id}.txt", "r") as f:
                    history = f.read().splitlines()
                
                bot.send_message(user_id, "⏳ در حال بازنشر ۵ پیام آخر شما...")
                for msg_id in history[-5:]:
                    try:
                        bot.forward_message(user_id, user_id, msg_id)
                    except: pass
            else:
                bot.reply_to(message, "تاریخچه‌ای برای شما یافت نشد.")
        else:
            bot.reply_to(message, "❌ شما دسترسی به این بخش را ندارید.")

    # ۲. بخش عمومی: گپ با جمنای
    elif text == "🤖 گپ با هوش مصنوعی":
        bot.reply_to(message, "هر سوالی دارید بپرسید، من آماده پاسخگویی هستم!")

    else:
        # پاسخ عمومی جمنای به همه کاربران
        try:
            bot.send_chat_action(user_id, 'typing')
            response = model.generate_content(text)
            bot.reply_to(message, response.text)
        except Exception as e:
            print(f"Gemini Error: {e}")
            bot.reply_to(message, "کمی گیج شدم! دوباره بپرس.")

if __name__ == "__main__":
    print("🚀 ربات ترکیبی (عمومی/خصوصی) بله روشن شد...")
    bot.polling(none_stop=True)
