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


_CACHE_MISS = object()  # Sentinel — never stored in cache, so acts as a reliable "not found" signal


def get_cached_abuse_score(ip: str):
    """
    Return the cached abuse score for an IP without hitting the API.
    Lookup order: Django cache → IPRecord DB row → None (unknown).
    Only caches when a real integer score exists — never caches None/unknown.
    """
    if not ip or ip in ('127.0.0.1', '::1', 'unknown'):
        return None
    from django.core.cache import cache
    cached = cache.get(f'abuse_{ip}', _CACHE_MISS)
    if cached is not _CACHE_MISS:
        return cached  # int (already looked up) — fast path
    try:
        from upload.models import IPRecord
        record = IPRecord.objects.filter(ip_address=ip).only('abuse_score').first()
        if record is not None and record.abuse_score is not None:
            cache.set(f'abuse_{ip}', record.abuse_score, timeout=86400)  # 24 h
            return record.abuse_score
    except Exception:
        pass
    return None


def get_reverse_dns(ip):
    """Return the PTR (reverse DNS) hostname for an IP, or '' if none exists."""
    import socket
    try:
        hostname = socket.getfqdn(ip)
        return hostname if hostname != ip else ''
    except Exception:
        return ''


def get_abuse_score(ip):
    """
    Query AbuseIPDB for a confidence score (0–100) and total report count.
    Returns (None, None) if the API key is missing, invalid, or the call fails —
    the rest of the app continues working normally.
    """
    from django.conf import settings
    api_key = getattr(settings, 'ABUSEIPDB_API_KEY', '')
    if not api_key:
        return None, None
    try:
        resp = requests.get(
            'https://api.abuseipdb.com/api/v2/check',
            headers={'Key': api_key, 'Accept': 'application/json'},
            params={'ipAddress': ip, 'maxAgeInDays': 90},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json().get('data', {})
            return data.get('abuseConfidenceScore'), data.get('totalReports')
        # 401 = invalid key, 429 = rate limit, etc. — all handled silently
        return None, None
    except Exception:
        return None, None


def update_ip_record(ip, path=None, geo=None, form_submitted=False, is_bot=False,
                     hostname=None, abuse_score=None, abuse_total_reports=None):
    """
    Upsert IPRecord for the given IP address.
    - path: page path hit (increments visit_count and pages_hit[path])
    - form_submitted: increments form_submission_count
    - is_bot: increments bot_submission_count instead
    """
    if not ip or ip in ('127.0.0.1', '::1', 'unknown'):
        return
    try:
        from upload.models import IPRecord
        from django.db.models import F
        from django.utils import timezone

        geo = geo or {}
        geo_defaults = {
            'city': geo.get('city', ''),
            'region': geo.get('regionName', ''),
            'country': geo.get('country', ''),
            'isp': geo.get('isp', ''),
        }

        record, created = IPRecord.objects.get_or_create(
            ip_address=ip,
            defaults=geo_defaults,
        )

        if created:
            # New IP — run enrichment (use pre-fetched values if caller already has them)
            _hostname = hostname if hostname is not None else get_reverse_dns(ip)
            if abuse_score is None:
                _abuse_score, _abuse_reports = get_abuse_score(ip)
            else:
                _abuse_score, _abuse_reports = abuse_score, abuse_total_reports
            IPRecord.objects.filter(pk=record.pk).update(
                hostname=_hostname,
                abuse_score=_abuse_score,
                abuse_total_reports=_abuse_reports,
            )
            # Populate cache so the blocker middleware has it on the very next request
            if _abuse_score is not None:
                from django.core.cache import cache
                cache.set(f'abuse_{ip}', _abuse_score, timeout=86400)

        update = {'last_seen': timezone.now()}

        if geo and (not record.country or created):
            update.update(geo_defaults)
        if path:
            update['visit_count'] = F('visit_count') + 1
        if form_submitted:
            update['form_submission_count'] = F('form_submission_count') + 1
        if is_bot:
            update['bot_submission_count'] = F('bot_submission_count') + 1

        IPRecord.objects.filter(pk=record.pk).update(**update)

        # Update pages_hit JSON separately (JSONField can't use F() atomically)
        if path:
            record.refresh_from_db(fields=['pages_hit'])
            pages = record.pages_hit or {}
            pages[path] = pages.get(path, 0) + 1
            IPRecord.objects.filter(pk=record.pk).update(pages_hit=pages)

        return record

    except Exception:
        pass
    return None


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
