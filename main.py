import telebot
import os
import google.generativeai as genai
from bale_sender import send_to_bale

# تنظیمات متغیرها از پنل Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
USER_LIST = [os.getenv("USER_1"), os.getenv("USER_2")]
DEST_MAP = {os.getenv("USER_1"): os.getenv("DEST_1"), os.getenv("USER_2"): os.getenv("DEST_2")}

# پیکربندی اولیه جمنای
genai.configure(api_key=GEMINI_KEY)

def get_ai_response(prompt):
    # لیست مدل‌های پایدار برای جلوگیری از خطای 404
    for model_name in ['gemini-pro', 'gemini-1.0-pro', 'models/gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"تلاش با {model_name} ناموفق بود: {e}")
            continue
    return "هوش مصنوعی موقتاً پاسخگو نیست، اما انتقال پیام شما انجام شد."

# راه‌اندازی ربات تلگرام
bot = telebot.TeleBot(TOKEN, threaded=False)

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_messages(message):
    user_id = str(message.from_user.id)
    
    # پاسخ هوش مصنوعی در تلگرام
    if message.content_type == 'text':
        bot.send_chat_action(message.chat.id, 'typing')
        answer = get_ai_response(message.text)
        bot.reply_to(message, answer)

    # فرآیند انتقال به بله برای یوزرهای خاص
    if user_id in USER_LIST:
        dest_id = DEST_MAP.get(user_id)
        
        if message.content_type == 'text':
            send_to_bale(dest_id, text=message.text)
        else:
            try:
                # تشخیص فایل
                if message.content_type == 'photo': file_id = message.photo[-1].file_id
                elif message.content_type == 'video': file_id = message.video.file_id
                elif message.content_type == 'document': file_id = message.document.file_id
                else: file_id = message.voice.file_id if message.content_type == 'voice' else message.audio.file_id

                # دانلود از تلگرام و ارسال به بله
                file_info = bot.get_file(file_id)
                downloaded = bot.download_file(file_info.file_path)
                send_to_bale(dest_id, file_data=downloaded, filename="file", caption=message.caption, file_type=message.content_type)
            except Exception as e:
                print(f"خطا در انتقال فایل: {e}")

print("🚀 ربات تلگرام با موفقیت استارت شد...")
bot.polling(none_stop=True, skip_pending=True)
