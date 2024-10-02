# utils.py or another appropriate file

import os
import requests
import aiohttp

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_KEY')


def send_telegram_message(CHAT_ID, message: str):
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

async def send_telegram_message_to_chat(chat_id: int, message: str):
    """
    Sends a message to a specific Telegram chat.
    
    :param chat_id: The chat ID to send the message to.
    :param message: The message content.
    :return: Response from the Telegram API.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'  # Optional: Use Markdown or HTML
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                if response.status == 200:
                    return {'status': 'success', 'result': result}
                else:
                    return {'status': 'error', 'result': result}
        except aiohttp.ClientError as e:
            return {'status': 'error', 'message': str(e)}