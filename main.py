from flask import Flask, request, jsonify
import os
from telegram_to_bale import handle_telegram_message
from bale_to_telegram import handle_bale_message

app = Flask(__name__)

@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    """دریافت پیام از تلگرام و ارسال به بله"""
    return handle_telegram_message(request)

@app.route('/bale_webhook', methods=['POST'])
def bale_webhook():
    """دریافت پیام از بله و ارسال به تلگرام"""
    return handle_bale_message(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
