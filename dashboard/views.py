"""
GARL Role-Based Dashboard Views
Each role sees a tailored dashboard.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from accounts.models import User, UserProfile, AuditLog, RoleType
from core.models import Bookmark, ActivityHistory
from notifications.models import Notification
from core.decorators import admin_required, super_admin_required


# ──────────────────────────────────────────────────────────────────────────────
# Main dashboard router — directs each role to the correct dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def home(request):
    role = request.user.role

    if role in (RoleType.SUPER_ADMIN, RoleType.SYSTEM_ADMIN, RoleType.CONTENT_ADMIN):
        return redirect('dashboard:admin_dashboard')
    elif role == RoleType.EDITOR:
        return redirect('dashboard:editor_dashboard')
    elif role == RoleType.REVIEWER:
        return redirect('dashboard:reviewer_dashboard')
    elif role == RoleType.RESEARCHER:
        return redirect('dashboard:researcher_dashboard')
    elif role == RoleType.AUTHOR:
        return redirect('dashboard:author_dashboard')
    elif role == RoleType.INSTRUCTOR:
        return redirect('dashboard:instructor_dashboard')
    elif role == RoleType.INSTITUTION_ADMIN:
        return redirect('dashboard:institution_dashboard')
    elif role == RoleType.LIBRARY_ADMIN:
        return redirect('dashboard:library_dashboard')
    else:
        return redirect('dashboard:user_dashboard')


# ──────────────────────────────────────────────────────────────────────────────
# General user dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def user_dashboard(request):
    from learning.models import Enrollment
    from events.models import EventRegistration
    from publishing.models import Publication

    profile, _    = UserProfile.objects.get_or_create(user=request.user)
    enrollments   = Enrollment.objects.filter(
        student=request.user, status='active'
    ).select_related('course').order_by('-enrolled_at')[:5]

    my_pubs       = Publication.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:5]

    upcoming_events = EventRegistration.objects.filter(
        user=request.user,
        event__start_date__gte=timezone.now()
    ).select_related('event').order_by('event__start_date')[:5]

    notifications  = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).order_by('-created_at')[:10]

    recent_activity = ActivityHistory.objects.filter(
        user=request.user
    ).order_by('-accessed_at')[:8]

    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')[:8]

    return render(request, 'dashboard/user.html', {
        'profile':          profile,
        'enrollments':      enrollments,
        'my_pubs':          my_pubs,
        'upcoming_events':  upcoming_events,
        'notifications':    notifications,
        'recent_activity':  recent_activity,
        'bookmarks':        bookmarks,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Researcher dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def researcher_dashboard(request):
    from research.models import ResearchPaper, ResearchProject
    from publishing.models import Publication

    papers    = ResearchPaper.objects.filter(
        authors=request.user
    ).order_by('-created_at')[:6]

    projects  = ResearchProject.objects.filter(
        Q(lead_researcher=request.user) | Q(team_members=request.user)
    ).distinct().order_by('-created_at')[:6]

    pubs      = Publication.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:6]

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    return render(request, 'dashboard/researcher.html', {
        'papers':   papers,
        'projects': projects,
        'pubs':     pubs,
        'profile':  profile,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Author dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def author_dashboard(request):
    from publishing.models import Publication

    pubs_by_status = {}
    for status, label in Publication.StatusChoice.choices:
        pubs_by_status[status] = Publication.objects.filter(
            created_by=request.user, status=status
        ).count()

    recent_pubs = Publication.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:10]

    return render(request, 'dashboard/author.html', {
        'pubs_by_status': pubs_by_status,
        'recent_pubs':    recent_pubs,
        'status_choices': Publication.StatusChoice.choices,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Instructor dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def instructor_dashboard(request):
    from learning.models import Course, Enrollment

    courses     = Course.objects.filter(instructor=request.user).order_by('-created_at')
    course_ids  = courses.values_list('id', flat=True)
    enrollments = Enrollment.objects.filter(
        course_id__in=course_ids
    ).select_related('student', 'course').order_by('-enrolled_at')[:10]

    total_students = Enrollment.objects.filter(course_id__in=course_ids).count()

    return render(request, 'dashboard/instructor.html', {
        'courses':        courses,
        'enrollments':    enrollments,
        'total_students': total_students,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Reviewer dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def reviewer_dashboard(request):
    from publishing.models import Review

    pending   = Review.objects.filter(
        reviewer=request.user, is_completed=False
    ).select_related('submission__publication').order_by('due_date')

    completed = Review.objects.filter(
        reviewer=request.user, is_completed=True
    ).select_related('submission__publication').order_by('-submitted_at')[:10]

    return render(request, 'dashboard/reviewer.html', {
        'pending_reviews':   pending,
        'completed_reviews': completed,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Editor dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def editor_dashboard(request):
    if not (request.user.is_editor() or request.user.is_any_admin()):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    from publishing.models import Submission, Publication
    pending_subs = Submission.objects.filter(
        publication__status__in=['submitted', 'screening', 'under_review', 'revision_req']
    ).select_related('publication', 'submitted_by').order_by('-submitted_at')[:20]

    stats = {
        'submitted':    Publication.objects.filter(status='submitted').count(),
        'under_review': Publication.objects.filter(status='under_review').count(),
        'approved':     Publication.objects.filter(status='approved').count(),
        'published':    Publication.objects.filter(status='published').count(),
    }

    return render(request, 'dashboard/editor.html', {
        'pending_subs': pending_subs,
        'stats':        stats,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Institution admin dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def institution_dashboard(request):
    from community.models import Institution, InstitutionMember

    institution = Institution.objects.filter(admin_user=request.user).first()
    if not institution:
        messages.warning(request, 'No institution is linked to your account.')
        return redirect('dashboard:user_dashboard')

    members  = InstitutionMember.objects.filter(
        institution=institution, is_active=True
    ).select_related('user').order_by('role')[:20]

    return render(request, 'dashboard/institution.html', {
        'institution': institution,
        'members':     members,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Library admin dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def library_dashboard(request):
    from library.models import LibraryResource, Download
    resources = LibraryResource.objects.order_by('-created_at')[:20]
    recent_downloads = Download.objects.select_related('user', 'resource').order_by('-downloaded_at')[:20]
    total_resources  = LibraryResource.objects.count()
    total_downloads  = Download.objects.count()
    return render(request, 'dashboard/library.html', {
        'resources':         resources,
        'recent_downloads':  recent_downloads,
        'total_resources':   total_resources,
        'total_downloads':   total_downloads,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Admin dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@admin_required
def admin_dashboard(request):
    from publishing.models import Publication, Submission
    from research.models import ResearchPaper
    from learning.models import Course, Enrollment
    from innovation.models import InnovationProject
    from events.models import Event
    from support.models import SupportTicket
    from community.models import Institution

    stats = {
        'total_users':         User.objects.filter(is_active=True).count(),
        'new_users_today':     User.objects.filter(
            date_joined__date=timezone.now().date()
        ).count(),
        'total_publications':  Publication.objects.filter(status='published').count(),
        'pending_review':      Publication.objects.filter(
            status__in=['submitted', 'screening', 'under_review']
        ).count(),
        'total_papers':        ResearchPaper.objects.filter(status='published').count(),
        'total_courses':       Course.objects.filter(is_published=True).count(),
        'total_enrollments':   Enrollment.objects.count(),
        'total_projects':      InnovationProject.objects.filter(status='published').count(),
        'pending_projects':    InnovationProject.objects.filter(
            status__in=['submitted', 'pending']
        ).count(),
        'total_institutions':  Institution.objects.filter(is_published=True).count(),
        'open_tickets':        SupportTicket.objects.filter(status='open').count(),
        'in_progress_tickets': SupportTicket.objects.filter(status='in_progress').count(),
    }

    # Users by role
    users_by_role = list(
        User.objects.values('role').annotate(count=Count('id')).order_by('-count')
    )

    # Recent registrations
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:10]

    # Pending submissions
    pending_subs = Submission.objects.filter(
        publication__status__in=['submitted', 'screening']
    ).select_related('publication', 'submitted_by').order_by('-submitted_at')[:10]

    # Open tickets
    open_tickets = SupportTicket.objects.filter(
        status='open'
    ).select_related('created_by').order_by('-created_at')[:10]

    # Recent audit logs
    recent_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:15]

    return render(request, 'dashboard/admin.html', {
        'stats':          stats,
        'users_by_role':  users_by_role,
        'recent_users':   recent_users,
        'pending_subs':   pending_subs,
        'open_tickets':   open_tickets,
        'recent_logs':    recent_logs,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Admin: User management
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@admin_required
def manage_users(request):
    users = User.objects.select_related('profile').order_by('-date_joined')
    q     = request.GET.get('q', '')
    role  = request.GET.get('role', '')
    if q:
        users = users.filter(
            Q(email__icontains=q) | Q(first_name__icontains=q) |
            Q(last_name__icontains=q) | Q(username__icontains=q)
        )
    if role:
        users = users.filter(role=role)

    from core.utils import paginate_queryset
    page_obj = paginate_queryset(users, request, 25)

    return render(request, 'dashboard/manage_users.html', {
        'page_obj':     page_obj,
        'roles':        RoleType.choices,
        'q':            q,
        'role_filter':  role,
    })


@login_required
@admin_required
def toggle_user_active(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'You cannot deactivate your own account.')
            return redirect('dashboard:manage_users')
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        action = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.email} has been {action}.')
        from core.utils import log_action
        log_action(request, 'update', User, user.pk, str(user), f'User {action}')
    return redirect('dashboard:manage_users')


@login_required
@super_admin_required
def change_user_role(request, pk):
    if request.method == 'POST':
        user     = get_object_or_404(User, pk=pk)
        new_role = request.POST.get('role')
        if new_role in dict(RoleType.choices):
            old_role  = user.role
            user.role = new_role
            user.save(update_fields=['role'])
            messages.success(request, f'Role changed from {old_role} to {new_role}.')
            from core.utils import log_action
            log_action(request, 'update', User, user.pk, str(user),
                       f'Role changed: {old_role} → {new_role}')
        else:
            messages.error(request, 'Invalid role.')
    return redirect('dashboard:manage_users')
