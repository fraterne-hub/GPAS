"""
GARL Accounts Forms — Registration, Login, Profile, Password
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserPreference, RoleType


# ──────────────────────────────────────────────────────────────────────────────
# Registration form
# ──────────────────────────────────────────────────────────────────────────────
class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        min_length=8,
    )
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    role = forms.ChoiceField(
        label=_('I am a'),
        choices=[
            (RoleType.STUDENT,    _('Student')),
            (RoleType.RESEARCHER, _('Researcher')),
            (RoleType.AUTHOR,     _('Author')),
            (RoleType.INSTRUCTOR, _('Instructor / Lecturer')),
            (RoleType.GENERAL_USER, _('General User')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial=RoleType.STUDENT,
    )
    agree_terms = forms.BooleanField(
        label=_('I agree to the Terms of Use and Privacy Policy'),
        required=True,
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('Passwords do not match.'))
        return p2

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('An account with this email already exists.'))
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_('This username is already taken.'))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


# ──────────────────────────────────────────────────────────────────────────────
# Login form
# ──────────────────────────────────────────────────────────────────────────────
class GARLLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_('Email Address'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autofocus': True}),
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    remember_me = forms.BooleanField(required=False, label=_('Remember me'))


# ──────────────────────────────────────────────────────────────────────────────
# Profile update form
# ──────────────────────────────────────────────────────────────────────────────
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'headline', 'website', 'phone',
            'country', 'city', 'institution', 'department',
            'field_of_study', 'orcid', 'linkedin', 'twitter',
            'researchgate', 'visibility',
        ]
        widgets = {
            'bio':            forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'headline':       forms.TextInput(attrs={'class': 'form-control'}),
            'website':        forms.URLInput(attrs={'class': 'form-control'}),
            'phone':          forms.TextInput(attrs={'class': 'form-control'}),
            'country':        forms.TextInput(attrs={'class': 'form-control'}),
            'city':           forms.TextInput(attrs={'class': 'form-control'}),
            'institution':    forms.TextInput(attrs={'class': 'form-control'}),
            'department':     forms.TextInput(attrs={'class': 'form-control'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'orcid':          forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin':       forms.URLInput(attrs={'class': 'form-control'}),
            'twitter':        forms.URLInput(attrs={'class': 'form-control'}),
            'researchgate':   forms.URLInput(attrs={'class': 'form-control'}),
            'visibility':     forms.Select(attrs={'class': 'form-select'}),
        }


# ──────────────────────────────────────────────────────────────────────────────
# User info form (name/username)
# ──────────────────────────────────────────────────────────────────────────────
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Preferences form
# ──────────────────────────────────────────────────────────────────────────────
class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = [
            'theme', 'language',
            'email_notifications', 'publication_notifications',
            'event_notifications', 'collaboration_notifications',
            'system_notifications', 'items_per_page',
        ]
        widgets = {
            'theme':    forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
        }


# ──────────────────────────────────────────────────────────────────────────────
# Password reset
# ──────────────────────────────────────────────────────────────────────────────
class GARLPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_('Email Address'),
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )


class GARLSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_('New Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label=_('Confirm New Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
