import telebot
import requests
import os

# فراخوانی ۵ متغیر از ری‌لوی
TELE_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")
DEST_1 = os.getenv("DESTINATION_ID_1")
DEST_2 = os.getenv("DESTINATION_ID_2")
MY_ID = os.getenv("USER_ID") # آیدی تلگرام خودت برای امنیت

bot = telebot.TeleBot(TELE_TOKEN)

@bot.message_handler(func=lambda message: True)
def forward_to_bale(message):
    # چک کن که فقط خودت داری پیام می‌فرستی (اختیاری ولی امن)
    if str(message.from_user.id) == MY_ID:
        text = message.text or message.caption or "فایل یا عکس"
        
        # آدرس API بله
        url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
        
        # ارسال همزمان به هر دو مقصد در بله
        requests.post(url, data={'chat_id': DEST_1, 'text': text})
        requests.post(url, data={'chat_id': DEST_2, 'text': text})
        
        print(f"پیام به هر دو مقصد ارسال شد: {text[:20]}...")

print("ربات با سیستم جدید Polling روشن شد. منتظر پیام...")
bot.infinity_polling()
