"""
GARL Core Views — Homepage, Error pages, Bookmarks
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone

from .models import Announcement, Bookmark
from .utils import add_bookmark


# ──────────────────────────────────────────────────────────────────────────────
# Homepage
# ──────────────────────────────────────────────────────────────────────────────
def home(request):
    from publishing.models import Publication
    from events.models import Event
    from research.models import ResearchPaper
    from learning.models import Course
    from innovation.models import InnovationProject

    announcements = Announcement.objects.filter(
        is_active=True
    ).order_by('-is_pinned', '-created_at')[:5]

    latest_publications = Publication.objects.filter(
        status='published'
    ).select_related('created_by').order_by('-published_at')[:8]

    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now(), is_published=True
    ).order_by('start_date')[:6]

    latest_papers = ResearchPaper.objects.filter(
        status='published'
    ).order_by('-created_at')[:6]

    featured_courses = Course.objects.filter(
        is_published=True, is_featured=True
    ).order_by('-created_at')[:4]

    featured_innovations = InnovationProject.objects.filter(
        status='published', is_featured=True
    ).order_by('-created_at')[:4]

    # Platform stats
    from accounts.models import User
    stats = {
        'users':        User.objects.filter(is_active=True).count(),
        'publications': Publication.objects.filter(status='published').count(),
        'courses':      Course.objects.filter(is_published=True).count(),
        'papers':       ResearchPaper.objects.filter(status='published').count(),
    }

    ctx = {
        'announcements':        announcements,
        'latest_publications':  latest_publications,
        'upcoming_events':      upcoming_events,
        'latest_papers':        latest_papers,
        'featured_courses':     featured_courses,
        'featured_innovations': featured_innovations,
        'stats':                stats,
        'search_types': [
            ('publications', 'Publications'),
            ('papers',       'Research Papers'),
            ('books',        'Books'),
            ('courses',      'Courses'),
            ('innovations',  'Innovations'),
            ('events',       'Events'),
            ('researchers',  'Researchers'),
            ('health',       'Health Resources'),
        ],
    }
    return render(request, 'core/home.html', ctx)


# ──────────────────────────────────────────────────────────────────────────────
# Bookmark toggle (AJAX)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def toggle_bookmark(request):
    content_type = request.POST.get('content_type')
    object_id    = request.POST.get('object_id')

    if not content_type or not object_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    try:
        object_id = int(object_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid object_id'}, status=400)

    added = add_bookmark(request.user, content_type, object_id)
    return JsonResponse({'bookmarked': added})


# ──────────────────────────────────────────────────────────────────────────────
# Error pages
# ──────────────────────────────────────────────────────────────────────────────
def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)


# ──────────────────────────────────────────────────────────────────────────────
# Newsletter Subscribe (AJAX POST)
# ──────────────────────────────────────────────────────────────────────────────
@require_POST
def newsletter_subscribe(request):
    """
    AJAX endpoint — saves a newsletter subscriber email.
    Returns JSON so the frontend can show a success/error message
    without a page reload.
    """
    import json
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    from .models import NewsletterSubscriber

    try:
        data  = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except (json.JSONDecodeError, AttributeError):
        # Also accept regular form POST
        email = request.POST.get('email', '').strip().lower()

    if not email:
        return JsonResponse({'ok': False, 'error': 'Please enter your email address.'}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'ok': False, 'error': 'Please enter a valid email address.'}, status=400)

    ip = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR', ''))

    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={
            'ip_address': ip,
            'is_active':  True,
        }
    )

    if not created:
        if subscriber.is_active:
            return JsonResponse({'ok': True, 'message': "You're already subscribed. Thank you!"})
        else:
            # Re-subscribe
            subscriber.is_active       = True
            subscriber.unsubscribed_at = None
            subscriber.save(update_fields=['is_active', 'unsubscribed_at'])
            return JsonResponse({'ok': True, 'message': 'Welcome back! You have been re-subscribed.'})

    # Send a welcome email
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        site_name = getattr(settings, 'GARL_SITE_NAME', 'GARL')
        send_mail(
            subject=f'Welcome to {site_name} Newsletter!',
            message=(
                f'Hi,\n\nThank you for subscribing to the {site_name} newsletter.\n\n'
                'You will receive updates about new research, courses, publications and events.\n\n'
                f'— The {site_name} Team'
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@garl.edu>'),
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        pass

    return JsonResponse({'ok': True, 'message': f"You've been subscribed! Check your email for confirmation."})
