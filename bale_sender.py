import requests
import os

BALE_TOKEN = os.getenv("BALE_TOKEN")
BASE_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"

def send_to_bale(target_id, text=None, file_path=None, file_type=None):
    try:
        if not file_path:
            response = requests.post(f"{BASE_URL}/sendMessage", 
                                    data={'chat_id': target_id, 'text': text})
            return response.status_code == 200
        
        # انتخاب متد بر اساس نوع فایل
        method = "sendPhoto" if file_type == 'photo' else "sendDocument"
        field = "photo" if file_type == 'photo' else "document"

        with open(file_path, 'rb') as f:
            response = requests.post(f"{BASE_URL}/{method}", 
                                    data={'chat_id': target_id, 'caption': text}, 
                                    files={field: f})
            return response.status_code == 200
    except Exception as e:
        print(f"Error in bale_sender: {e}")
        return False
