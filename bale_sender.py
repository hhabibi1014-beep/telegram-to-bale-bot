import requests
import os

def send_to_bale(dest_id, text=None, file_data=None, filename=None, caption=None):
    token = os.getenv("BALE_TOKEN")
    
    # ارسال فایل (اگر داده فایل وجود داشته باشد)
    if file_data:
        url = f"https://tapi.bale.ai/bot{token}/sendDocument"
        files = {'document': (filename, file_data)}
        data = {'chat_id': dest_id, 'caption': caption}
        try:
            response = requests.post(url, files=files, data=data)
            return response.json()
        except Exception as e:
            print(f"Error sending file to Bale: {e}")
            return None
    
    # ارسال متن
    elif text:
        url = f"https://tapi.bale.ai/bot{token}/sendMessage"
        data = {'chat_id': dest_id, 'text': text}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print(f"Error sending text to Bale: {e}")
            return None
