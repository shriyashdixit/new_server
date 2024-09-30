# utils.py or another appropriate file

import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_KEY')


def send_telegram_message(message: str, CHAT_ID):
    """
    Sends a message to a specific Telegram chat.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,  # Chat ID where the message should be sent
        'text': message
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad HTTP responses
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
