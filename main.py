from flask import Flask, request, jsonify
import telebot
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os. getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os. getenv('BALE_TOKEN')
TELEGRAM_CHAT_ID = os. getenv('TELEGRAM_CHAT_ID')
BALE_CHAT_ID = os. getenv('BALE_CHAT_ID')

telegram_bot = telebot. TeleBot(TELEGRAM_TOKEN)

@app. route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telebot. types. Update. de_json(request. stream. read(). decode('utf-8'))
        telegram_bot. process_new_updates([update])
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({'ok': True})

def send_to_bale(file_content, file_name, file_type, text):
    data = {'chat_id': BALE_CHAT_ID}
    if text:
        data['caption'] = text
    
    try:
        if file_type == "photo":
            files = {'photo': (file_name, file_content)}
            r = requests. post(
                f"https://tapi. bale. ai/bot{BALE_TOKEN}/sendPhoto",
                data=data,
                files=files
            )
        elif file_type == "video":
            files = {'video': (file_name, file_content)}
            r = requests. post(
                f"https://tapi. bale. ai/bot{BALE_TOKEN}/sendVideo",
                data=data,
                files=files
            )
        elif file_type == "audio" or file_type == "voice":
            files = {'audio': (file_name, file_content)}
            r = requests. post(
                f"https://tapi. bale. ai/bot{BALE_TOKEN}/sendAudio",
                data=data,
                files=files
            )
            if r. status_code != 200:
                files = {'document': (file_name, file_content)}
                r = requests. post(
                    f"https://tapi. bale. ai/bot{BALE_TOKEN}/sendDocument",
                    data=data,
                    files=files
                )
        else:
            files = {'document': (file_name, file_content)}
            r = requests. post(
                f"https://tapi. bale. ai/bot{BALE_TOKEN}/sendDocument",
                data=data,
                files=files
            )
        return r
    except Exception as e:
        return None

@telegram_bot.message_handler(content_types=['photo', 'document', 'audio', 'video', 'voice'])
def handle_media(message):
    try:
        print(f"=== MEDIA HANDLER START ===")
        print(f"Message type: {message.content_type}")
        
        file_id = None
        file_type = None
        file_name = "file"
        
        if message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
            print("Type: photo")
        elif message.document:
            file_id = message.document.file_id
            file_type = "document"
            file_name = message.document.file_name or "file"
            print(f"Type: document, name: {file_name}")
        elif message.audio:
            file_id = message.audio.file_id
            file_type = "audio"
            file_name = message.audio.file_name or "audio.mp3"
            print("Type: audio")
        elif message.voice:
            file_id = message.voice.file_id
            file_type = "voice"
            file_name = "voice.ogg"
            print("Type: voice")
        elif message.video:
            file_id = message.video.file_id
            file_type = "video"
            file_name = message.video.file_name or "video.mp4"
            print("Type: video")
        
        if file_id:
            print(f"File ID: {file_id}")
            
            text = message.caption or message.text or ""
            print(f"Caption/Text: {text}")
            
            file_info = telegram_bot.get_file(file_id)
            file_size = file_info.file_size
            print(f"File size from Telegram: {file_size} bytes")
            
            if file_size > 20 * 1024 * 1024:
                telegram_bot.reply_to(message, f"❌ فایل خیلی بزرگه! حداکثر حجم: 20MB\n📁 حجم فایل: {file_size/(1024*1024):.1f} MB")
                return
            
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
            print(f"Downloading from: {file_url}")
            file_content = requests.get(file_url).content
            print(f"Downloaded size: {len(file_content)} bytes")
            
            print(f"Sending to Bale: chat_id={BALE_CHAT_ID}, type={file_type}, name={file_name}")
            r = send_to_bale(file_content, file_name, file_type, text)
            print(f"Bale response: {r}")
            
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024*1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
            
            if r and r.status_code == 200:
                telegram_bot.reply_to(message, f"✅ فایل به Bale ارسال شد!\n📁 حجم: {size_str}")
            else:
                error_msg = r.text if r else "خطای ناشناخته"
                print(f"ERROR: {error_msg}")
                telegram_bot.reply_to(message, f"❌ خطا: {error_msg}\n📁 حجم: {size_str}")
        else:
            print("No file_id found!")
        print(f"=== MEDIA HANDLER END ===")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        telegram_bot.reply_to(message, f"❌ خطا: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
