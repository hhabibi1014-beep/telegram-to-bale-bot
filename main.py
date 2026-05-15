import telebot
import os
import google.generativeai as genai
from bale_sender import send_to_bale

TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
USER_LIST = [os.getenv("USER_1"), os.getenv("USER_2")]
DEST_MAP = {os.getenv("USER_1"): os.getenv("DEST_1"), os.getenv("USER_2"): os.getenv("DEST_2")}

genai.configure(api_key=GEMINI_KEY)

# تابعی برای گرفتن پاسخ از هر مدلی که در دسترس بود
def get_ai_response(prompt):
    # لیست مدل‌هایی که شانس کار کردن دارند
    model_names = ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-1.5-flash-latest']
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = model.generate_content(prompt)
            return response.text
        except:
            continue
    return "هوش مصنوعی موقتاً در دسترس نیست، اما انتقال فایل انجام می‌شود."

bot = telebot.TeleBot(TOKEN, threaded=False)

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_messages(message):
    user_id = str(message.from_user.id)
    
    if message.content_type == 'text':
        bot.send_chat_action(message.chat.id, 'typing')
        answer = get_ai_response(message.text)
        bot.reply_to(message, answer)

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
