"""
GARL Core Utilities — shared helpers used across modules
"""

from accounts.models import AuditLog


def get_client_ip(request):
    """Extract the real client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, model_class, object_id, object_repr, description='', extra_data=None):
    """Create an AuditLog entry."""
    user       = request.user if request.user.is_authenticated else None
    ip         = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    AuditLog.objects.create(
        user        = user,
        action      = action,
        model_name  = model_class.__name__ if model_class else '',
        object_id   = str(object_id),
        object_repr = str(object_repr)[:500],
        description = description,
        ip_address  = ip,
        user_agent  = user_agent,
        extra_data  = extra_data,
    )


def track_activity(user, content_type, object_id, object_title=''):
    """Record that a user accessed a resource."""
    from core.models import ActivityHistory
    if user and user.is_authenticated:
        ActivityHistory.objects.update_or_create(
            user=user, content_type=content_type, object_id=object_id,
            defaults={'object_title': object_title}
        )


def add_bookmark(user, content_type, object_id, note=''):
    """Toggle a bookmark for a user."""
    from core.models import Bookmark
    obj, created = Bookmark.objects.get_or_create(
        user=user, content_type=content_type, object_id=object_id,
        defaults={'note': note}
    )
    if not created:
        obj.delete()
        return False  # removed
    return True  # added


def paginate_queryset(queryset, request, page_size=20):
    """Return a paginator page for the given queryset."""
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(queryset, page_size)
    page      = request.GET.get('page', 1)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
