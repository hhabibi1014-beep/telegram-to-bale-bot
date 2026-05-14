import telebot
import os
import google.generativeai as genai
from telebot import types

BALE_TOKEN = os.getenv("BALE_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ALLOWED_BALE_IDS = [os.getenv("DEST_1"), os.getenv("DEST_2")]

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BALE_TOKEN, threaded=False)
bot.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

# تابع کمکی برای خواندن آخرین پیام‌های ذخیره شده
def get_history(chat_id):
    file_name = f"history_{chat_id}.txt"
    if not os.path.exists(file_name):
        return []
    with open(file_name, "r") as f:
        return f.read().splitlines()

@bot.message_handler(commands=['start'])
def start(message):
    if str(message.chat.id) in ALLOWED_BALE_IDS:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🤖 گپ با هوش مصنوعی"))
        markup.add(types.KeyboardButton("🔄 بازبینی پیام‌های اخیر"))
        bot.send_message(message.chat.id, "خوش آمدی حسن جان. چه کمکی از دستم برمی‌آید؟", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_bale(message):
    chat_id = str(message.chat.id)
    if chat_id not in ALLOWED_BALE_IDS: return

    if message.text == "🔄 بازبینی پیام‌های اخیر":
        history = get_history(chat_id)
        if not history:
            bot.reply_to(message, "هنوز پیامی در تاریخچه ذخیره نشده است.")
            return
        
        bot.send_message(chat_id, "⏳ در حال بازنشر ۵ پیام آخر...")
        # ۵ پیام آخر را بدون آپلود مجدد، فوروارد می‌کند
        for msg_id in history[-5:]:
            try:
                bot.forward_message(chat_id, chat_id, msg_id)
            except:
                pass
    
    elif message.text == "🤖 گپ با هوش مصنوعی":
        bot.reply_to(message, "حالت هوش مصنوعی فعال است. سوال خود را بپرسید:")
    
    else:
        # اگر دکمه نبود، به عنوان سوال از Gemini فرض می‌شود
        try:
            bot.send_chat_action(chat_id, 'typing')
            response = model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except:
            bot.reply_to(message, "خطا در پاسخگویی هوش مصنوعی.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
