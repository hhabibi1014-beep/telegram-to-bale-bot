from flask import jsonify
import requests
import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os.getenv('BALE_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_to_telegram(file_content, file_name, file_type, text):
    data = {'chat_id': TELEGRAM_CHAT_ID}
    if text:
        data['caption'] = text
    
    try:
        if file_type == "photo":
            files = {'photo': (file_name, file_content)}
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                data=data,
                files=files
            )
        # ... بقیه مدیا مثل بالا
        else:
            files = {'document': (file_name, file_content)}
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                data=data,
                files=files
            )
        return r
    except Exception as e:
        print(f"Error: {e}")
        return None

def handle_bale_message(request):
    try:
        data = request.get_json()
        
        if 'message' in data:
            msg = data['message']
            text = msg.get('text', '')
            chat_id = msg['c…
