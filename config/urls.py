"""
GARL - Global Academic Research Library
Root URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Django admin — primary URL
    path('django-admin/', admin.site.urls),

    # /admin/ redirects to /django-admin/ (familiar URL alias)
    path('admin/', RedirectView.as_view(url='/django-admin/', permanent=False)),
    path('admin', RedirectView.as_view(url='/django-admin/', permanent=False)),

    # i18n
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # Core / homepage
    path('', include('core.urls', namespace='core')),

    # Authentication
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Dashboard (role-based)
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),

    # Research Center
    path('research/', include('research.urls', namespace='research')),

    # Publishing Center
    path('publishing/', include('publishing.urls', namespace='publishing')),

    # Innovation Hub
    path('innovation/', include('innovation.urls', namespace='innovation')),

    # Learning Center
    path('learning/', include('learning.urls', namespace='learning')),

    # Health Science Hub
    path('health/', include('health_science.urls', namespace='health_science')),

    # Library
    path('library/', include('library.urls', namespace='library')),

    # Events
    path('events/', include('events.urls', namespace='events')),

    # Community & Directory
    path('community/', include('community.urls', namespace='community')),

    # Support Center
    path('support/', include('support.urls', namespace='support')),

    # Notifications
    path('notifications/', include('notifications.urls', namespace='notifications')),

    # Global Search
    path('search/', include('search.urls', namespace='search')),

    # AI Support Assistant
    path('ai-support/', include('ai_support.urls', namespace='ai_support')),

    # Payments & Revenue
    path('payments/', include('payments.urls', namespace='payments')),

    # Analytics
    path('analytics/', include('analytics.urls', namespace='analytics')),

    prefix_default_language=False,
)

# Error handlers
handler400 = 'core.views.error_400'
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
