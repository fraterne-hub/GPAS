"""
GARL RBAC decorators — enforce role-based access at the view level.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from accounts.models import RoleType


def role_required(*roles):
    """Restrict view to users with any of the given roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f'/accounts/login/?next={request.path}')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, _('You do not have permission to access this page.'))
                return redirect('dashboard:home')
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def admin_required(view_func):
    """Restrict view to any admin role."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.is_any_admin() and not request.user.is_superuser:
            messages.error(request, _('Administrator access required.'))
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapped


def super_admin_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if request.user.role != RoleType.SUPER_ADMIN and not request.user.is_superuser:
            messages.error(request, _('Super Administrator access required.'))
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapped


def publisher_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.can_publish():
            messages.error(request, _('Publishing permission required.'))
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapped


def reviewer_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.can_review():
            messages.error(request, _('Reviewer access required.'))
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapped
