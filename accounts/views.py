"""
GARL Accounts Views — Registration, Login, Logout, Profile, Password
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView, PasswordChangeDoneView,
)
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.http import JsonResponse

from .models import User, UserProfile, UserPreference
from .forms import (
    RegistrationForm, GARLLoginForm,
    ProfileUpdateForm, UserUpdateForm,
    UserPreferenceForm, GARLPasswordResetForm, GARLSetPasswordForm
)
from core.utils import log_action, get_client_ip


# ──────────────────────────────────────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────────────────────────────────────
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            log_action(request, 'create', User, user.pk, str(user), 'User registered')
            messages.success(request, _('Welcome to GARL! Your account has been created.'))
            return redirect('dashboard:home')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# ──────────────────────────────────────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────────────────────────────────────
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = GARLLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            remember = form.cleaned_data.get('remember_me')
            if not remember:
                request.session.set_expiry(0)
            # Update last login IP
            ip = get_client_ip(request)
            User.objects.filter(pk=user.pk).update(last_login_ip=ip)
            login(request, user)
            log_action(request, 'login', User, user.pk, str(user), 'User logged in')
            messages.success(request, _(f'Welcome back, {user.get_short_name()}!'))
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        else:
            messages.error(request, _('Invalid email or password.'))
    else:
        form = GARLLoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


# ──────────────────────────────────────────────────────────────────────────────
# Logout
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def user_logout(request):
    log_action(request, 'logout', User, request.user.pk, str(request.user), 'User logged out')
    logout(request)
    messages.info(request, _('You have been logged out.'))
    return redirect('core:home')


# ──────────────────────────────────────────────────────────────────────────────
# Profile
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {
        'profile': profile_obj,
        'user': request.user,
    })


@login_required
def edit_profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # ── Process user fields (first_name, last_name, username) ──────────
        user_errors = {}
        new_username = request.POST.get('username', '').strip()
        new_first    = request.POST.get('first_name', '').strip()
        new_last     = request.POST.get('last_name', '').strip()

        if not new_first:
            user_errors['first_name'] = _('First name is required.')
        if not new_last:
            user_errors['last_name'] = _('Last name is required.')
        if not new_username:
            user_errors['username'] = _('Username is required.')
        elif (User.objects
              .filter(username__iexact=new_username)
              .exclude(pk=request.user.pk)
              .exists()):
            user_errors['username'] = _('This username is already taken.')

        # ── Process profile fields ──────────────────────────────────────────
        profile_errors = {}
        website = request.POST.get('website', '').strip()
        if website and not website.startswith(('http://', 'https://')):
            profile_errors['website'] = _('Enter a valid URL starting with http:// or https://')

        if not user_errors and not profile_errors:
            # Save user fields
            request.user.first_name = new_first
            request.user.last_name  = new_last
            request.user.username   = new_username
            request.user.save(update_fields=['first_name', 'last_name', 'username'])

            # Save profile fields
            profile_obj.bio           = request.POST.get('bio', '').strip()
            profile_obj.headline      = request.POST.get('headline', '').strip()
            profile_obj.website       = website
            profile_obj.phone         = request.POST.get('phone', '').strip()
            profile_obj.country       = request.POST.get('country', '').strip()
            profile_obj.city          = request.POST.get('city', '').strip()
            profile_obj.institution   = request.POST.get('institution', '').strip()
            profile_obj.department    = request.POST.get('department', '').strip()
            profile_obj.field_of_study= request.POST.get('field_of_study', '').strip()
            profile_obj.orcid         = request.POST.get('orcid', '').strip()
            profile_obj.linkedin      = request.POST.get('linkedin', '').strip()
            profile_obj.twitter       = request.POST.get('twitter', '').strip()
            profile_obj.researchgate  = request.POST.get('researchgate', '').strip()
            profile_obj.visibility    = request.POST.get('visibility', 'public')

            # Handle avatar upload
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                # Validate file type
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if avatar_file.content_type in allowed_types:
                    profile_obj.avatar = avatar_file
                else:
                    profile_errors['avatar'] = _('Avatar must be a JPG, PNG, GIF or WebP image.')

            if not profile_errors:
                profile_obj.save()
                log_action(request, 'update', UserProfile, profile_obj.pk,
                           str(request.user), 'Profile updated')
                messages.success(request, _('Profile updated successfully.'))
                return redirect('accounts:profile')

        # Re-render with errors
        from .forms import UserUpdateForm, ProfileUpdateForm
        user_form    = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
        # Inject manual errors so template can display them
        for field, msg in user_errors.items():
            user_form.add_error(field, msg)
        for field, msg in profile_errors.items():
            profile_form.add_error(field, msg)

        return render(request, 'accounts/edit_profile.html', {
            'user_form':    user_form,
            'profile_form': profile_form,
        })

    # GET request
    from .forms import UserUpdateForm, ProfileUpdateForm
    user_form    = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=profile_obj)

    return render(request, 'accounts/edit_profile.html', {
        'user_form':    user_form,
        'profile_form': profile_form,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Preferences
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def preferences(request):
    pref_obj, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=pref_obj)
        if form.is_valid():
            form.save()
            messages.success(request, _('Preferences saved.'))
            return redirect('accounts:preferences')
    else:
        form = UserPreferenceForm(instance=pref_obj)

    return render(request, 'accounts/preferences.html', {'form': form})


# ──────────────────────────────────────────────────────────────────────────────
# Theme toggle (AJAX)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def toggle_theme(request):
    pref, _ = UserPreference.objects.get_or_create(user=request.user)
    pref.theme = 'dark' if pref.theme == 'light' else 'light'
    pref.save(update_fields=['theme'])
    return JsonResponse({'theme': pref.theme})


# ──────────────────────────────────────────────────────────────────────────────
# Public user profile
# ──────────────────────────────────────────────────────────────────────────────
def public_profile(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    profile_obj = get_object_or_404(UserProfile, user=user)

    # Respect visibility settings
    if profile_obj.visibility == 'private':
        if request.user != user:
            return render(request, 'accounts/profile_private.html', {'profile_user': user})

    return render(request, 'accounts/public_profile.html', {
        'profile_user': user,
        'profile': profile_obj,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Password change
# ──────────────────────────────────────────────────────────────────────────────
class GARLPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url   = reverse_lazy('accounts:password_change_done')


class GARLPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'


# ──────────────────────────────────────────────────────────────────────────────
# Password reset
# ──────────────────────────────────────────────────────────────────────────────
class GARLPasswordResetView(PasswordResetView):
    template_name       = 'accounts/password_reset.html'
    email_template_name = 'accounts/email/password_reset_email.html'
    subject_template_name = 'accounts/email/password_reset_subject.txt'
    form_class          = GARLPasswordResetForm
    success_url         = reverse_lazy('accounts:password_reset_done')


class GARLPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class GARLPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class    = GARLSetPasswordForm
    success_url   = reverse_lazy('accounts:password_reset_complete')


class GARLPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
