from flask import request, jsonify
import requests
import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BALE_TOKEN = os.getenv('BALE_TOKEN')
BALE_CHAT_ID = os.getenv('BALE_CHAT_ID')
def send_to_bale(file_content, file_name, file_type, text):
    data = {'chat_id': BALE_CHAT_ID}
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
        else:
            files = {'document': (file_name, file_content)}
            r = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendDocument",
                data=data,
                files=files
            )
        return r
    except Exception as e:
        print(f"Error: {e}")
        return None
def handle_telegram_message(req):
    try:
        data = req.get_json()
        
        if 'message' in data:
            msg = data['message']
            text = msg.get('text', '')
            
            if 'photo' in msg:
                file_id = msg['photo'][-1]['file_id']
                file_info = requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
                ).json()
                file_path = file_info['result']['file_path']
                file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
                file_content = requests.get(file_url).content
                caption = msg.get('caption', '')
                r = send_to_bale(file_content, "photo.jpg", "photo", caption)
                print(f"Bale response: {r.status_code if r else 'None'}")
            
            elif 'video' in msg:
                file_id = msg['video']['file_id']
                file_info = requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
                ).json()
                file_path = file_info['result']['file_path']
                file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
                file_content = requests.get(file_url).content
                caption = msg.get('caption', '')
                r = send_to_bale(file_content, "video.mp4", "video", caption)
                print(f"Bale response: {r.status_code if r else 'None'}")
                            elif 'document' in msg:
                file_id = msg['document']['file_id']
                file_name = msg['document'].get('file_name', 'file')
                file_info = requests.get(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
                ).json()
                file_path = file_info['result']['file_path']
                file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
                file_content = requests.get(file_url).content
                caption = msg.get('caption', '')
                r = send_to_bale(file_content, file_name, "document", caption)
                print(f"Bale response: {r.status_code if r else 'None'}")
            
            elif text:
                r = requests.post(
                    f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage",
                    json={'chat_id': BALE_CHAT_ID, 'text': text}
                )
                print(f"Bale response: {r.status_code if r else 'None'}")
                
    except Exception as e:
        print(f"Error: {e}")
    
    return jsonify({'ok': True})
