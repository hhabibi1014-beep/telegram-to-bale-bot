import requests

def send_to_bale(file_content, file_name, file_type, text, token, chat_id):
    base_url = f"https://tapi.bale.ai/bot{token}"
    data = {'chat_id': chat_id}
    
    try:
        if file_type == "text":
            return requests.post(f"{base_url}/sendMessage", data={'chat_id': chat_id, 'text': text})

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

        return requests.post(endpoint, data=data, files=files)
    except:
        return None
