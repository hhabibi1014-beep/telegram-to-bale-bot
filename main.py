#!/usr/bin/env python3
import os
import requests
import telebot
from flask import Flask, request, jsonify

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

@app.route('/bale_webhook', methods=['POST'])
def bale_webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': True})
        
        message = data.get('message', {})
        chat = message.get('chat', {})
        
        if str(chat.get('id')) != str(BALE_CHAT_ID):
            return jsonify({'ok': True})
        
        text = message.get('text', '')
        caption = message.get('caption', '')
        
        file_id = None
        file_type = None
        file_name = "file"
        
        if 'photo' in message:
            photo = message['photo'][-1]
            file_id = photo.get('file_id')
            file_type = "photo"
        elif 'document' in message:
            doc = message['document']
            file_id = doc.get('file_id')
            file_type = "document"
            file_name = doc.get('file_name', 'file')
        elif 'audio' in message:
            audio = message['audio']
            file_id = audio.get('file_id')
            file_type = "audio"
            file_name = audio.get('file_name', 'audio.mp3')
        elif 'voice' in message:
            voice = message['voice']
            file_id = voice.get('file_id')
            file_type = "voice"
            file_name = "voice.ogg"
        elif 'video' in message:
            video = message['video']
            file_id = video.get('file_id')
            file_type = "video"
            file_name = video.get('file_name', 'video.mp4')
        
        msg_text = text or caption or ""
        
        if file_id:
            file_url = f"https://tapi.bale.ai/file/bot{BALE_TOKEN}/{file_id}"
            file_content = requests.get(file_url).content
            
            if file_type == "photo":
                telegram_bot.send_photo(TELEGRAM_CHAT_ID, file_content, caption=msg_text)
            elif file_type == "video":
                telegram_bot.send_video(TELEGRAM_CHAT_ID, file_content, caption=msg_text)
            elif file_type == "audio" or file_type == "voice":
                telegram_bot.send_audio(TELEGRAM_CHAT_ID, file_content, caption=msg_text)
            else:
                telegram_bot.send_document(TELEGRAM_CHAT_ID, file_content, caption=msg_text)
        else:
            telegram_bot.send_message(TELEGRAM_CHAT_ID, f"Message from Bale: {msg_text}")
        
    except Exception as e:
        print("Bale webhook error: " + str(e))
    
    return jsonify({'ok': True})

def send_to_bale(file_content, file_name, file_type, text):
    data = {chat_id: BALE_CHAT_ID}
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
            r…
