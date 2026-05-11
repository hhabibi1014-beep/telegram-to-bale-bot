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

@def send_to_bale(file_content, file_name, file_type, text):
    data = {chat_id: BALE_CHAT_ID }
    if text:
        data['caption'] = text
    
    try:
        if file_type == "photo":
            files = {'photo': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendPhoto",
                data=data,
                files=files
            )
        elif file_type == "video":
            files = {'video': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendVideo",
                data=data,
                files=files
            )
        elif file_type == "audio" or file_type == "voice":
            files = {'audio': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendAudio",
                data=data,
                files=files
            )
            if r.status_code != 200:
                files = {'document': (file_name, file_content)}
                r = requests.post(
                    f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendDocument",
                    data=data,
                    files=files
                )
        else:
            files = {'document': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendDocument",
                data=data,
                files=files
            )
        return r
    except Exception as e:
        return None
@telegram_bot.message_handler(content_types=['photo', 'document', 'audio', 'video', 'voice'])
def handle_media(message):
    try:
        file_id = None
        file_type = None
        file_name = "file"
        
        if message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
        elif message.document:
            file_id = message.document.file_id
            file_type = "document"
            file_name = message.document.file_name or "file"
        elif message.audio:
            file_id = message.audio.file_id
            file_type = "audio"
            file_name = message.audio.file_name or "audio.mp3"
        elif message.voice:
            file_id = message.voice.file_id
            file_type = "voice"
            file_name = "voice.ogg"
        elif message.video:
            file_id = message.video.file_id
            file_type = "video"
            file_name = message.video.file_name or "video.mp4"
        
        if file_id:
            text = message.caption or message.text or ""
            
            file_info = telegram_bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
            file_content = requests.get(file_url).content
            
            r = send_to_bale(file_content, file_name, file_type, text)
            
            print(f"Bale response: {r.status_org} - {r.text}")
            
            if r and r.status_code == 200:
                telegram_bot.reply_to(message, "∮یام از Bale9i��")
            else:
                telegram_bot.reply_to(message, f"⌮ۘ� السالایام ثجيب!")
      except Exception as e:
        print(f"Error: {e}")
        telegram_bot.reply_to(message, f"」رالسالایام ثجيب!: {e}")