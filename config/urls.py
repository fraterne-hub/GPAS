"""
GARL - Global Academic Research Library
Root URL Configuration
"""

import os
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import JsonResponse
from core.views import newsletter_subscribe


# ──────────────────────────────────────────────────────────────────────────────
# Diagnostic endpoint — remove after confirming Cloudinary works
# ──────────────────────────────────────────────────────────────────────────────
def _storage_check(request):
    return JsonResponse({
        'DEFAULT_FILE_STORAGE': getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET'),
        'CLOUD_NAME_env': os.environ.get('CLOUDINARY_CLOUD_NAME', 'NOT SET'),
        'API_KEY_env': (os.environ.get('CLOUDINARY_API_KEY') or 'NOT SET')[:6] + '...',
        'API_SECRET_env': 'SET' if os.environ.get('CLOUDINARY_API_SECRET') else 'NOT SET',
        'CLOUDINARY_URL_built': (os.environ.get('CLOUDINARY_URL') or 'NOT SET')[:25] + '...',
        'MEDIA_URL': settings.MEDIA_URL,
        'DEBUG': settings.DEBUG,
    })


urlpatterns = [
    # Diagnostic — remove once Cloudinary is confirmed working
    path('_storage-check/', _storage_check),

    # Django admin
    path('django-admin/', admin.site.urls),
    path('admin/', RedirectView.as_view(url='/django-admin/', permanent=False)),
    path('admin', RedirectView.as_view(url='/django-admin/', permanent=False)),

    # i18n language switcher — outside i18n_patterns
    path('i18n/', include('django.conf.urls.i18n')),

    # Newsletter subscribe — global, no language prefix needed
    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
]

urlpatterns += i18n_patterns(
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('research/', include('research.urls', namespace='research')),
    path('publishing/', include('publishing.urls', namespace='publishing')),
    path('innovation/', include('innovation.urls', namespace='innovation')),
    path('learning/', include('learning.urls', namespace='learning')),
    path('health/', include('health_science.urls', namespace='health_science')),
    path('library/', include('library.urls', namespace='library')),
    path('events/', include('events.urls', namespace='events')),
    path('community/', include('community.urls', namespace='community')),
    path('support/', include('support.urls', namespace='support')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('search/', include('search.urls', namespace='search')),
    path('ai-support/', include('ai_support.urls', namespace='ai_support')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    prefix_default_language=False,
)

# Error handlers
handler400 = 'core.views.error_400'
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

# ──────────────────────────────────────────────────────────────────────────────
# Serve /media/ locally ONLY when Cloudinary is NOT active.
# We check the SAME flag that settings.py uses, so they can never disagree.
# ──────────────────────────────────────────────────────────────────────────────
_using_cloudinary = getattr(settings, 'DEFAULT_FILE_STORAGE', '').startswith('cloudinary')

if not _using_cloudinary and settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in development (WhiteNoise handles this in production)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)