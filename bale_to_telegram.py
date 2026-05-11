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
        elif file_type == "video":
            files = {'video': (file_name, file_content)}
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                data=data,
                files=files
            )
        elif file_type == "audio" or file_type == "voice":
            files = {'audio': (file_name, file_content)}
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendAudio",
                data=data,
                files=files
            )
            # اگه صدا نبود، داکیومنت بفرست
            if r.status_code != 200:
                files = {'document': (file_name, file_content)}
                r = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                    data=data,
                    files=files
                )
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
            chat_id = msg['chat']['id']
            
            # مدیریت عکس
            if 'photo' in msg:
                file_id = msg['photo'][-1]['file_id']
                file_info = requests.get(
                    f"https://tapi.bale.ai/bot{BALE_TOKEN}/getFile?file_id={file_id}"
                ).json()
                file_path = file_info['result']['file_path']
                file_url = f"https://tapi.bale.ai/file/bot{BALE_TOKEN}/{file_path}"
                file_content = requests.get(file_url).content
                
                caption = msg.get('caption', '')
                r = send_to_telegram(file_content, "photo.jpg", "photo", caption)
                
                print(f"Telegram response: {r.status_code if r else 'None'}")
            
            # مدیریت ویدیو
            elif 'video' in msg:
                file_id = msg['video']['file_id']
                file_info = requests.get(
                    f"https://tapi.bale.ai/bot{BALE_TOKEN}/getFile?file_id={file_id}"
                ).json()
                file_path = file_info['result']['file_path']
                file_url = f"https://tapi.bale.ai/file/bot{BALE_TOKEN}/{file_path}"
                file_content = requests.get(file_url).content
                
                caption = msg.get('caption', '')
                r = send_to_telegram(file_content, "video.mp4", "video", caption)
                
                print(f"Telegram response: {r.status_code if r else 'None'}")
            
            # مدیریت صدا / ویس
            elif 'voice' in msg:
                file_id = msg['voice']['file_id']
                file_info = requests.get(
                    f"https://tapi.bale.ai/bot{BALE_TOKEN}/getFile?file_id={file_id}"
                ).json()
                file_path = file_info['result']['file_path']
                file_url = f"https://tapi.bale.ai/file/bot{BALE_TOKEN}/{file_path}"
                file_content = requests.get(file_url).content
                
                r = s…
