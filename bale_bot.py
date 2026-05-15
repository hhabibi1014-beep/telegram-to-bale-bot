import telebot
import os
import google.generativeai as genai
from telebot import types

BALE_TOKEN = os.getenv("BALE_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

def get_ai_response(prompt):
    model_names = ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-1.5-flash-latest']
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = model.generate_content(prompt)
            return response.text
        except:
            continue
    return "متأسفانه در حال حاضر به هوش مصنوعی وصل نمی‌شوم."

bot = telebot.TeleBot(BALE_TOKEN, threaded=False)
bot.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

@bot.message_handler(func=lambda m: True)
def handle_bale(message):
    if message.text == "🤖 گپ با هوش مصنوعی":
        bot.reply_to(message, "هر سوالی داری بپرس!")
    elif "بازبینی" in message.text:
        bot.reply_to(message, "این بخش در حال بروزرسانی است.")
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        answer = get_ai_response(message.text)
        bot.reply_to(message, answer)

bot.polling(none_stop=True, skip_pending=True)
