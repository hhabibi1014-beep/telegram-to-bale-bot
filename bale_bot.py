import telebot
import os
import google.generativeai as genai
from telebot import types

BALE_TOKEN = os.getenv("BALE_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_IDS = [os.getenv("DEST_1"), os.getenv("DEST_2")]

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(BALE_TOKEN, threaded=False)
bot.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

def get_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🤖 گپ با هوش مصنوعی"))
    if str(chat_id) in ADMIN_IDS:
        markup.add(types.KeyboardButton("🔄 بازبینی ۵۰ پیام اخیر (فقط مدیر)"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "سلام! چطور می‌تونم کمکت کنم؟", reply_markup=get_keyboard(message.chat.id))

@bot.message_handler(func=lambda m: True)
def handle_bale(message):
    user_id = str(message.chat.id)
    
    if message.text == "🔄 بازبینی ۵۰ پیام اخیر (فقط مدیر)":
        if user_id in ADMIN_IDS:
            file_path = f"history_{user_id}.txt"
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    history = f.read().splitlines()
                bot.send_message(user_id, f"⏳ در حال بازنشر {len(history)} پیام اخیر...")
                for msg_id in history:
                    try:
                        bot.forward_message(user_id, user_id, msg_id)
                    except: pass
            else:
                bot.send_message(user_id, "آرشیوی موجود نیست.")
        else:
            bot.send_message(user_id, "❌ دسترسی شما محدود است.")
            
    elif message.text == "🤖 گپ با هوش مصنوعی":
        bot.reply_to(message, "حالت هوش مصنوعی فعال شد. بپرس!")
        
    else:
        # پاسخ عمومی Gemini به همه
        try:
            bot.send_chat_action(user_id, 'typing')
            response = model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except:
            bot.reply_to(message, "مشکلی در پاسخگویی پیش آمد.")

bot.polling(none_stop=True)
