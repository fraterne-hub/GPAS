"""
GARL global template context processor.
Makes platform info, site settings and common data available in all templates.
"""

from django.conf import settings
from notifications.models import Notification


def garl_context(request):
    ctx = {
        'GARL_SITE_NAME': settings.GARL_SITE_NAME,
        'GARL_VERSION':   settings.GARL_VERSION,
    }

    # Site settings (singleton — hero banner, logos, social links, etc.)
    try:
        from core.models import SiteSettings
        ctx['site_settings'] = SiteSettings.get()
    except Exception:
        ctx['site_settings'] = None

    if request.user.is_authenticated:
        # Unread notification count
        try:
            ctx['unread_notification_count'] = Notification.objects.filter(
                recipient=request.user, is_read=False
            ).count()
        except Exception:
            ctx['unread_notification_count'] = 0

        # User theme preference
        try:
            ctx['user_theme'] = request.user.preferences.theme
        except Exception:
            ctx['user_theme'] = 'light'
    else:
        ctx['unread_notification_count'] = 0
        ctx['user_theme'] = 'light'

    return ctx
