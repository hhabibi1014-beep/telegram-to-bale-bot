import telebot
import os
import google.generativeai as genai

BALE_TOKEN = os.getenv("BALE_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

def get_ai_response(prompt):
    # استفاده از مدل فوق پایدار pro
    for model_name in ['gemini-pro', 'gemini-1.0-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except:
            continue
    return "پاسخی از هوش مصنوعی دریافت نشد."

bot = telebot.TeleBot(BALE_TOKEN, threaded=False)
bot.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

@bot.message_handler(func=lambda m: True)
def handle_bale(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = get_ai_response(message.text)
    bot.reply_to(message, answer)

print("🚀 ربات بله با موفقیت استارت شد...")
bot.polling(none_stop=True, skip_pending=True)
