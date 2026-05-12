import requests
import os

BALE_TOKEN = os.getenv('BALE_TOKEN')
BALE_CHAT_ID = os.getenv('BALE_CHAT_ID')

def send_to_bale(file_content, file_name, file_type, text):
    base_url = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
    data = {'chat_id': BALE_CHAT_ID}
    
    try:
        # اگر فقط متن بود و فایلی در کار نبود
        if file_type == "text":
            return requests.post(f"{base_url}/sendMessage", data={'chat_id': BALE_CHAT_ID, 'text': text})

        # برای بقیه موارد (عکس، فیلم، صدا، فایل)
        if text:
            data['caption'] = text
            
        if file_type == "photo":
            endpoint = f"{base_url}/sendPhoto"
            files = {'photo': (file_name, file_content)}
        elif file_type == "video":
            endpoint = f"{base_url}/sendVideo"
            files = {'video': (file_name, file_content)}
        elif file_type in ["audio", "voice"]:
            endpoint = f"{base_url}/sendAudio"
            files = {'audio': (file_name, file_content)}
        else:
            endpoint = f"{base_url}/sendDocument"
            files = {'document': (file_name, file_content)}

        r = requests.post(endpoint, data=data, files=files)
        return r
    except:
        return None
