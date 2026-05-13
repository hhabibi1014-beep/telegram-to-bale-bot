import requests
import os

def send_to_bale(dest_id, text=None, file_data=None, filename=None, caption=None, file_type='document'):
    token = os.getenv("BALE_TOKEN")
    
    if file_data:
        # تشخیص متد ارسال بر اساس نوع فایل
        methods = {
            'photo': 'sendPhoto',
            'video': 'sendVideo',
            'audio': 'sendAudio',
            'voice': 'sendVoice',
            'document': 'sendDocument'
        }
        method = methods.get(file_type, 'sendDocument')
        url = f"https://tapi.bale.ai/bot{token}/{method}"
        
        # در بله برای عکس 'photo' و برای بقیه 'document' یا نام خودشان استفاده می‌شود
        files = {file_type if file_type != 'document' else 'document': (filename, file_data)}
        data = {'chat_id': dest_id, 'caption': caption}
        
        try:
            response = requests.post(url, files=files, data=data)
            return response.json()
        except Exception as e:
            print(f"Error sending to Bale: {e}")
            return None
    
    elif text:
        url = f"https://tapi.bale.ai/bot{token}/sendMessage"
        data = {'chat_id': dest_id, 'text': text}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            return None
