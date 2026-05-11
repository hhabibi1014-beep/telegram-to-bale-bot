from flask import Flask, request, jsonify
import telebot
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os.getenv('BALE_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BALE_CHAT_ID = os.getenv('BALE_CHAT_ID')

telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        telegram_bot.process_new_updates([update])
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({'ok': True})

@telegram_bot.message_handler(content_types=['photo', 'document', 'audio', 'video'])
def handle_media(message):
    try:
        file_id = None
        file_name = None
        
        if message.photo:
            file_id = message.photo[-1].file_id
            file_name = "photo.jpg"
        elif message.document:
            file_id = message.document.file_id
            file_name = message.document.file_name or "file"
        elif message.audio:
            file_id = message.audio.file_id
            file_name = message.audio.file_name or "audio"
        elif message.video:
            file_id = message.video.file_id
            file_name = "video.mp4"
        
        if file_id:
            file_info = telegram_bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
            
            response = requests.get(file_url)
            
            requests.post(
                f"https://api.bale.ai/bot{BALE_TOKEN}/sendMessage",
                json={'chat_id': BALE_CHAT_ID, 'text': f'پیام از تلگرام:\n{message.text or ""}'}
            )
            
            files = {'file': (file_name, response.content)}
            requests.post(
                f"https://api.bale.ai/bot{BALE_TOKEN}/sendDocument",
                json={'chat_id': BALE_CHAT_ID},
                files=files
            )
            
            telegram_bot.reply_to(message, "✅ فایل به Bale ارسال شد!")
    except Exception as e:
        print(f"Error: {e}")
        telegram_bot.reply_to(message, f"❌ خطا: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
