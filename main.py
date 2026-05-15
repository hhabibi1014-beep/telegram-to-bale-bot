import telebot
import os
import google.generativeai as genai
from bale_sender import send_to_bale

# تنظیمات محیطی
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
USER_LIST = [os.getenv("USER_1"), os.getenv("USER_2")]
DEST_MAP = {os.getenv("USER_1"): os.getenv("DEST_1"), os.getenv("USER_2"): os.getenv("DEST_2")}

# تنظیم هوش مصنوعی Gemini (مدل جدید و پایدار)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN, threaded=False)

def save_to_history(dest_id, msg_id):
    file_path = f"history_{dest_id}.txt"
    history = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            history = f.read().splitlines()
    
    history.append(str(msg_id))
    if len(history) > 50:
        history = history[-50:]
    
    with open(file_path, "w") as f:
        f.write("\n".join(history))

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def process_messages(message):
    user_id = str(message.from_user.id)
    
    # پاسخ هوشمند Gemini برای همه در تلگرام
    if message.content_type == 'text':
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except Exception as e:
            print(f"Gemini Error: {e}")

    # انتقال اختصاصی به بله برای شما و همسر
    if user_id in USER_LIST:
        dest_id = DEST_MAP.get(user_id)
        
        if message.content_type == 'text':
            res = send_to_bale(dest_id, text=message.text)
            if res and res.get("ok"):
                save_to_history(dest_id, res.get("result", {}).get("message_id"))
        else:
            file_type = message.content_type
            if file_type == 'photo': file_id = message.photo[-1].file_id
            elif file_type == 'video': file_id = message.video.file_id
            elif file_type == 'document': file_id = message.document.file_id
            elif file_type == 'audio': file_id = message.audio.file_id
            else: file_id = message.voice.file_id

            try:
                file_info = bot.get_file(file_id)
                downloaded = bot.download_file(file_info.file_path)
                res = send_to_bale(dest_id, file_data=downloaded, filename="file", caption=message.caption, file_type=file_type)
                if res and res.get("ok"):
                    save_to_history(dest_id, res.get("result", {}).get("message_id"))
            except Exception as e:
                print(f"Transfer Error: {e}")

print("🚀 ربات تلگرام روشن شد...")
bot.polling(none_stop=True, skip_pending=True)
