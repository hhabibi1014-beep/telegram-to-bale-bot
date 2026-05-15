import telebot
import os
import google.generativeai as genai

BALE_TOKEN = os.getenv("BALE_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-8b')

bot = telebot.TeleBot(BALE_TOKEN, threaded=False)
bot.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

@bot.message_handler(func=lambda m: True)
def handle_bale(message):
    # پاسخ هوشمند در بله
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "در حال حاضر سیستم هوش مصنوعی پاسخگو نیست.")

print("🚀 ربات بله روشن شد...")
bot.polling(none_stop=True, skip_pending=True)
