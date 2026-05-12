# bale_api.py
from bale import Bot
import os
import requests

BALE_BOT_TOKEN = os.environ.get('BALE_TOKEN')

class BaleBot:
    def __init__(self, token):
        self.bot = Bot(token)
    
    def send_message(self, chat_id, text):
        try:
            self.bot.sendMessage(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def send_file(self, chat_id, file_url, file_type='photo', caption=None):
        try:
            if file_type == 'photo':
                self.bot.sendPhoto(chat_id=chat_id, photo=file_url, caption=caption)
            elif file_type == 'document':
                self.bot.sendDocument(chat_id=chat_id, document=file_url, caption=caption)
            elif file_type == 'video':
                self.bot.sendVideo(chat_id=chat_id, video=file_url, caption=caption)
            return True
        except Exception as e:
            print(f"Error sending file: {e}")
            return False

bale_bot = BaleBot(BALE_BOT_TOKEN)
