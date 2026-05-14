import telebot
import os
import google.generativeai as genai
from telebot import types

# ۱. دریافت توکن‌ها و تنظیمات از محیط Railway
BALE_TOKEN = os.getenv("BALE_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# آیدی‌های شما و همسرت برای دسترسی به دکمه بازبینی
ADMIN_IDS = [os.getenv("DEST_1"), os.getenv("DEST_2")]

# ۲. تنظیم هوش مصنوعی Gemini (نسخه پایدار Pro)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# ۳. راه‌اندازی ربات بله (با استفاده از کتابخانه تلگرام و تغییر آدرس سرور)
bot = telebot.TeleBot(BALE_TOKEN, threaded=False)
bot.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

# تابع ساخت کیبورد (تفکیک مدیر و کاربر عادی)
def get_main_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🤖 گپ با هوش مصنوعی"))
    
    # دکمه بازبینی فقط برای شما و همسرت نمایش داده می‌شود
    if str(chat_id) in ADMIN_IDS:
        markup.add(types.KeyboardButton("🔄 بازبینی ۵۰ پیام اخیر (فقط مدیر)"))
    
    return markup

# مدیریت دستور شروع
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id, 
        "سلام! به دستیار هوشمند بله خوش آمدید.\nچطور می‌توانم کمکتان کنم؟", 
        reply_markup=get_main_keyboard(chat_id)
    )

# مدیریت پیام‌های ورودی
@bot.message_handler(func=lambda m: True)
def handle_bale_messages(message):
    chat_id = str(message.chat.id)
    text = message.text

    # الف) بخش اختصاصی مدیر: بازبینی تاریخچه
    if text == "🔄 بازبینی ۵۰ پیام اخیر (فقط مدیر)":
        if chat_id in ADMIN_IDS:
            file_path = f"history_{chat_id}.txt"
            
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    history = f.read().splitlines()
                
                if history:
                    bot.send_message(chat_id, f"⏳ در حال بازنشر {len(history)} پیام اخیر شما از آرشیو...")
                    # فوروارد کردن پیام‌ها بدون آپلود مجدد
                    for msg_id in history:
                        try:
                            bot.forward_message(chat_id, chat_id, msg_id)
                        except:
                            pass
                else:
                    bot.send_message(chat_id, "آرشیو شما خالی است.")
            else:
                bot.send_message(chat_id, "هنوز هیچ پیامی برای شما ثبت نشده است.")
        else:
            bot.reply_to(message, "❌ پوزش می‌طلبم، این بخش فقط برای مدیران در دسترس است.")

    # ب) بخش عمومی: گفتگو با هوش مصنوعی
    elif text == "🤖 گپ با هوش مصنوعی":
        bot.reply_to(message, "حالت هوش مصنوعی فعال شد. هر سوالی دارید بپرسید، من آماده‌ام!")

    else:
        # پاسخ هوشمند Gemini به هر پیامی که دکمه نباشد
        try:
            bot.send_chat_action(chat_id, 'typing')
            response = model.generate_content(text)
            bot.reply_to(message, response.text)
        except Exception as e:
            print(f"Bale Gemini Error: {e}")
            bot.reply_to(message, "کمی گیج شدم! لطفاً دوباره بپرسید.")

# اجرای ربات
if __name__ == "__main__":
    print("🚀 ربات ترکیبی (عمومی/خصوصی) بله روشن شد...")
    bot.polling(none_stop=True)
