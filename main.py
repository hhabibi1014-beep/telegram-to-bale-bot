from flask import Flask, request, jsonify
import telebot
from telegram_to_bale import telegram_bot

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        telegram_bot.process_new_updates([update])
    except Exception as e:
        print(f"Error: {e}")
    return jsonify({'ok': True})

@app.route('/test', methods=['GET'])
def test():
    import requests
    from config import BALE_BOT_TOKEN
    url = f"https://api.bale.ai/v1/bots/{BALE_BOT_TOKEN}/getMe"
    response = requests.get(url)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
