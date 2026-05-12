import requests
from telebot import TeleBot
from config import TELEGRAM_BOT_TOKEN, BALE_BOT_TOKEN, BALE_CHAT_ID

telegram_bot = TeleBot(TELEGRAM_BOT_TOKEN)

# ========== متن ==========
@telegram_bot.message_handler(commands=['start'])
def handle_start(message):
    telegram_bot.reply_to(message, "✅ ربات فعال شد!")

@telegram_bot.message_handler(func=lambda m: m.text and not m.text.startswith('/'))
def handle_text(message):
    url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/sendMessage"
    data = {"chat_id": BALE_CHAT_ID, "text": message.text}
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            telegram_bot.reply_to(message, "✅ متن به Bale ارسال شد!")
        else:
            telegram_bot.reply_to(message, f"❌ خطا: {response.status_code}")
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ خطا: {str(e)}")

# ========== عکس ==========
@telegram_bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_id = message.photo[-1].file_id
        file = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file.file_path}"
        
        bale_url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/sendPhoto"
        data = {"chat_id": BALE_CHAT_ID, "photo": file_url}
        
        response = requests.post(bale_url, json=data)
        if response.status_code == 200:
            telegram_bot.reply_to(message, "✅ عکس به Bale ارسال شد!")
        else:
            telegram_bot.reply_to(message, f"❌ خطا: {response.status_code}")
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ خطا: {str(e)}")

# ========== ویدیو ==========
@telegram_bot.message_handler(content_types=['video'])
def handle_video(message):
    try:
        file_id = message.video.file_id
        file = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file.file_path}"
        
        bale_url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/sendVideo"
        data = {"chat_id": BALE_CHAT_ID, "video": file_url}
        
        response = requests.post(bale_url, json=data)
        if response.status_code == 200:
            telegram_bot.reply_to(message, "✅ ویدیو به Bale ارسال شد!")
        else:
            telegram_bot.reply_to(message, f"❌ خطا: {response.status_code}")
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ خطا: {str(e)}")

# ========== صوت / ویس ==========
@telegram_bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_id = message.voice.file_id
        file = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file.file_path}"
        
        bale_url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/sendVoice"
        data = {"chat_id": BALE_CHAT_ID, "voice": file_url}
        
        response = requests.post(bale_url, json=data)
        if response.status_code == 200:
            telegram_bot.reply_to(message, "✅ ویس به Bale ارسال شد!")
        else:
            telegram_bot.reply_to(message, f"❌ خطا: {response.status_code}")
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ خطا: {str(e)}")

# ========== موزیک ==========
@telegram_bot.message_handler(content_types=['audio'])
def handle_audio(message):
    try:
        file_id = message.audio.file_id
        file = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file.file_path}"
        
        bale_url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/sendAudio"
        data = {"chat_id": BALE_CHAT_ID, "audio": file_url}
        
        response = requests.post(bale_url, json=data)
        if response.status_code == 200:
            telegram_bot.reply_to(message, "✅ موزیک به Bale ارسال شد!")
        else:
            telegram_bot.reply_to(message, f"❌ خطا: {response.status_code}")
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ خطا: {str(e)}")

# ========== سند / فایل ==========
@telegram_bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_id = message.document.file_id
        file = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file.file_path}"
        
        bale_url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/sendDocument"
        data = {"chat_id": BALE_CHAT_ID, "document": file_url}
        
        response = requests.post(bale_url, json=data)
        if response.status_code == 200:
            telegram_bot.reply_to(message, "✅ سند به Bale ارسال شد!")
        else:
            telegram_bot.reply_to(message, f"❌ خطا: {response.status_code}")
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ خطا: {str(e)}")

# ========== استیکر ==========
@telegram_bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    try:
        file_id = message.sticker.file_id
        file = telegram_bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file.file_path}"
        
        bale_url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/sendSticker"
        data = {"chat_id": BALE_CHAT_ID, "sticker": file_url}
        
        response = requests.post(bale_url, json=data)
        if response.status_code == 200:
            telegram_bot.reply_to(message, "✅ استیکر به Bale ارسال شد!")
        else:
            telegram_bot.reply_to(message, f"❌ خطا: {response.status_code}")
    except Exception as e:
        telegram_bot.reply_to(message, f"❌ خطا: {str(e)}")
