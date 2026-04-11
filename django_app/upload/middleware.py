import threading

TRACKED_PATHS = {
    '/', '/services/', '/skills/', '/work/',
    '/team/', '/culture/', '/careers/', '/blogs/', '/contact/',
}

# Common bot identifiers — skip tracking these
BOT_KEYWORDS = ('bot', 'crawl', 'spider', 'slurp', 'mediapartners', 'facebookexternalhit', 'curl', 'wget')


def _anonymize_ip(ip):
    """Zero out last octet (IPv4) or last 80 bits (IPv6) for privacy."""
    try:
        if ':' in ip:
            parts = ip.split(':')
            return ':'.join(parts[:3] + ['0', '0', '0', '0', '0'])
        parts = ip.split('.')
        return '.'.join(parts[:3] + ['0'])
    except Exception:
        return None


def _log_visit_async(path, referrer, ua, raw_ip):
    """Run in a background thread — does geo lookup, writes PageVisit, updates IPRecord."""
    try:
        from upload.models import PageVisit
        from upload.utils import get_ip_location, update_ip_record

        geo = get_ip_location(raw_ip)
        PageVisit.objects.create(
            path=path,
            referrer=referrer,
            user_agent=ua,
            ip_address=_anonymize_ip(raw_ip),
            city=geo.get('city', ''),
            region=geo.get('regionName', ''),
            country=geo.get('country', ''),
            isp=geo.get('isp', ''),
        )
        update_ip_record(raw_ip, path=path, geo=geo)
    except Exception:
        pass  # Never let tracking break anything


class PageVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.method == 'GET'
                and request.path in TRACKED_PATHS
                and response.status_code == 200):
            ua = request.META.get('HTTP_USER_AGENT', '').lower()
            if not any(kw in ua for kw in BOT_KEYWORDS):
                raw_ip = (
                    request.META.get('HTTP_X_FORWARDED_FOR', '')
                    .split(',')[0].strip()
                    or request.META.get('REMOTE_ADDR', '')
                )
                threading.Thread(
                    target=_log_visit_async,
                    args=(
                        request.path,
                        request.META.get('HTTP_REFERER', '')[:2000],
                        request.META.get('HTTP_USER_AGENT', '')[:500],
                        raw_ip,
                    ),
                    daemon=True,
                ).start()

        return response
