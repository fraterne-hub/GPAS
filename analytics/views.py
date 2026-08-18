"""
GARL Analytics Views — admin-only analytics dashboard
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from core.decorators import admin_required
from accounts.models import User
from publishing.models import Publication
from research.models import ResearchPaper
from learning.models import Course, Enrollment
from innovation.models import InnovationProject
from events.models import Event
from support.models import SupportTicket
from community.models import Institution
from .models import DailyStats


@login_required
@admin_required
def analytics_dashboard(request):
    today    = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago= today - timedelta(days=30)

    stats = {
        'total_users':         User.objects.filter(is_active=True).count(),
        'new_users_week':      User.objects.filter(date_joined__date__gte=week_ago).count(),
        'total_publications':  Publication.objects.filter(status='published').count(),
        'total_papers':        ResearchPaper.objects.filter(status='published').count(),
        'total_courses':       Course.objects.filter(is_published=True).count(),
        'total_enrollments':   Enrollment.objects.count(),
        'total_projects':      InnovationProject.objects.filter(status='published').count(),
        'total_events':        Event.objects.filter(is_published=True).count(),
        'open_tickets':        SupportTicket.objects.filter(status='open').count(),
        'total_institutions':  Institution.objects.filter(is_published=True).count(),
        'pending_publications':Publication.objects.filter(
            status__in=['submitted', 'screening', 'under_review', 'revision_req']
        ).count(),
        'pending_projects':    InnovationProject.objects.filter(
            status__in=['submitted', 'pending']
        ).count(),
    }

    # Users by role
    from django.db.models import Count
    users_by_role = (
        User.objects.values('role')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Daily stats last 14 days
    daily = DailyStats.objects.filter(
        date__gte=today - timedelta(days=14)
    ).order_by('date')

    # Recent audit logs
    from accounts.models import AuditLog
    recent_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:20]

    return render(request, 'analytics/dashboard.html', {
        'stats':         stats,
        'users_by_role': users_by_role,
        'daily':         daily,
        'recent_logs':   recent_logs,
    })
