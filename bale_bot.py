import telebot
import os
from groq import Groq
from telebot import types

BALE_TOKEN = os.getenv("BALE_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_KEY)
bot = telebot.TeleBot(BALE_TOKEN, threaded=False)
bot.api_helper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"

def get_ai_response(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except:
        return "مشکلی در اتصال به هوش مصنوعی رخ داد."

@bot.message_handler(func=lambda m: True)
def handle_bale(message):
    if message.text == "🤖 گفتگو با هوش مصنوعی":
        bot.reply_to(message, "در خدمتم! سوالت چیست؟")
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        answer = get_ai_response(message.text)
        bot.reply_to(message, answer)

bot.polling(none_stop=True, skip_pending=True)
