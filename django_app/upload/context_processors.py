from django.conf import settings


def site_context(request):
    return {
        'SITE_URL': getattr(settings, 'SITE_URL', ''),
        'PLAUSIBLE_DOMAIN': getattr(settings, 'PLAUSIBLE_DOMAIN', ''),
    }
