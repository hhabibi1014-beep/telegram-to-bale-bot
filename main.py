import os
import requests
from flask import Flask, request, jsonify
import telebot

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os.getenv('BALE_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BALE_CHAT_ID = os.getenv('BALE_CHAT_ID')

telegram_bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_to_bale(text, file_url=None, file_type=None, caption=""):
    url = "https://tapi.bale.ai/sendMessage"
    headers = {'Authorization': f'Bearer {BALE_TOKEN}', 'Content-Type': 'application/json'}
    
    if file_url:
        if file_type == 'photo':
            payload = {'chat_id': BALE_CHAT_ID, 'photo': file_url, 'caption': caption}
        elif file_type == 'video':
            payload = {'chat_id': BALE_CHAT_ID, 'video': file_url, 'caption': caption}
        elif file_type == 'document':
            payload = {'chat_id': BALE_CHAT_ID, 'document': file_url, 'caption': caption}
        elif file_type == 'voice':
            payload = {'chat_id': BALE_CHAT_ID, 'voice': file_url}
        elif file_type == 'audio':
            payload = {'chat_id': BALE_CHAT_ID, 'audio': file_url}
    else:
        payload = {'chat_id': BALE_CHAT_ID, 'text': text}
    
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Error: {e}")

def get_file_url(file_id):
    try:
        file = telegram_bot.get_file(file_id)
        return f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path}"
    except:
        return None

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def telegram_webhook():
    try:
        update = telebot.types.Update.de_json(request.get_json(force=True))
        message = update.message
        
        if message and str(message.chat.id) == str(TELEGRAM_CHAT_ID):
            file_url = None
            file_type = None
            caption = message.caption or ""
            
            if message.photo:
                file_type = 'photo'
                file_url = get_file_url(message.photo[-1].file_id)
            elif message.video:
                file_type = 'video'
                file_url = get_file_url(message.video.file_id)
            elif message.document:
                file_type = 'document'
                file_url = get_file_url(message.document.file_id)
            elif message.voice:
                file_type = 'voice'
                file_url = get_file_url(message.voice.file_id)
            elif message.audio:
                file_type = 'audio'
                file_url = get_file_url(message.audio.file_id)
            
            if file_url:
                send_to_bale("", file_url, file_type, caption)
            elif message.text:
                send_to_bale(message.text)
        
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route(f'/bale_webhook_{BALE_TOKEN}', methods=['POST'])
def bale_webhook():
    try:
        data = request.get_json()
        if data and 'message' in data:
            msg = data['message']
            chat_id = msg.get('chat', {}).get('id')
            if str(chat_id) == str(BALE_CHAT_ID):
                text = msg.get('text', '')
                if text:
                    telegram_bot.send_message(TELEGRAM_CHAT_ID, text)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/')
def index():
    return 'Bot is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
