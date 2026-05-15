import telebot
import os
import google.generativeai as genai
from bale_sender import send_to_bale

# تنظیمات اصلی از متغیرهای Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
USER_LIST = [os.getenv("USER_1"), os.getenv("USER_2")]
DEST_MAP = {os.getenv("USER_1"): os.getenv("DEST_1"), os.getenv("USER_2"): os.getenv("DEST_2")}

# پیکربندی هوش مصنوعی با مدل سریع و پایدار 8b
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-8b')

# راه‌اندازی ربات تلگرام (حالت threaded=False برای پایداری در سرور)
bot = telebot.TeleBot(TOKEN, threaded=False)

def get_ai_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return "هوش مصنوعی موقتاً در دسترس نیست، اما انتقال فایل انجام می‌شود."

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_messages(message):
    user_id = str(message.from_user.id)
    
    # ۱. پاسخ هوشمند Gemini در تلگرام
    if message.content_type == 'text':
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            answer = get_ai_response(message.text)
            bot.reply_to(message, answer)
        except:
            pass

    # ۲. انتقال پیام و فایل به بله (فقط برای شما و همسر)
    if user_id in USER_LIST:
        dest_id = DEST_MAP.get(user_id)
        
        if message.content_type == 'text':
            send_to_bale(dest_id, text=message.text)
        else:
            try:
                # تشخیص نوع فایل
                if message.content_type == 'photo': file_id = message.photo[-1].file_id
                elif message.content_type == 'video': file_id = message.video.file_id
                elif message.content_type == 'document': file_id = message.document.file_id
                else: file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id

                # دانلود و ارسال
                file_info = bot.get_file(file_id)
                downloaded = bot.download_file(file_info.file_path)
                send_to_bale(dest_id, file_data=downloaded, filename="file", caption=message.caption, file_type=message.content_type)
            except Exception as e:
                print(f"Transfer Error: {e}")

print("🚀 ربات تلگرام (ویرجینیا) روشن شد...")
bot.polling(none_stop=True, skip_pending=True)
