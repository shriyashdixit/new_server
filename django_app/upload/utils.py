# utils.py or another appropriate file

import os
import requests
import aiohttp
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_KEY')


def send_telegram_message(CHAT_ID, message: str):
    """
    Sends a message to a specific Telegram chat.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
    }

    try:
        response = requests.post(url, json=payload, timeout=8)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")


async def send_telegram_message_to_chat(chat_id: int, message: str):
    """
    Sends a message to a specific Telegram chat.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
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


def get_client_ip(request):
    """Extract real client IP, accounting for proxies."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def get_ip_location(ip: str) -> dict:
    """Look up approximate geo-location for an IP using ip-api.com (free, no key)."""
    if ip in ('127.0.0.1', 'unknown', '::1'):
        return {'city': 'localhost', 'country': 'local', 'regionName': '', 'isp': ''}
    try:
        resp = requests.get(
            f'http://ip-api.com/json/{ip}',
            params={'fields': 'status,city,regionName,country,isp,query'},
            timeout=5,
        )
        data = resp.json()
        if data.get('status') == 'success':
            return data
    except Exception:
        pass
    return {'city': '?', 'country': '?', 'regionName': '?', 'isp': '?'}


def notify_landing_page_visit(request):
    """Fire-and-forget Telegram notification for a homepage visit."""
    import threading
    from django.conf import settings

    chat_id = settings.TELEGRAM_CHAT_ID
    if not chat_id:
        return

    def _send():
        ip = get_client_ip(request)
        geo = get_ip_location(ip)
        ts = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')
        ua = request.META.get('HTTP_USER_AGENT', 'unknown')

        city = geo.get('city', '?')
        region = geo.get('regionName', '?')
        country = geo.get('country', '?')
        isp = geo.get('isp', '?')

        msg = (
            '🌐 <b>Landing Page Visit</b>\n\n'
            f'🕒 <b>Time:</b> {ts}\n'
            f'🌍 <b>IP:</b> {ip}\n'
            f'📍 <b>Location:</b> {city}, {region}, {country}\n'
            f'📡 <b>ISP:</b> {isp}\n'
            f'🖥️ <b>User-Agent:</b> {ua[:200]}'
        )
        send_telegram_message(chat_id, msg)

    threading.Thread(target=_send, daemon=True).start()
