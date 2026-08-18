"""
GARL Accounts Models
Custom User, Roles, Profiles, Preferences, AuditLog
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ──────────────────────────────────────────────────────────────────────────────
# Role constants
# ──────────────────────────────────────────────────────────────────────────────
class RoleType(models.TextChoices):
    SUPER_ADMIN         = 'super_admin',         _('Super Administrator')
    SYSTEM_ADMIN        = 'system_admin',         _('System Administrator')
    CONTENT_ADMIN       = 'content_admin',        _('Content Administrator')
    EDITOR              = 'editor',               _('Editor / Publishing Admin')
    REVIEWER            = 'reviewer',             _('Reviewer')
    RESEARCHER          = 'researcher',           _('Researcher')
    AUTHOR              = 'author',               _('Author')
    STUDENT             = 'student',              _('Student')
    INSTRUCTOR          = 'instructor',           _('Instructor / Lecturer')
    INSTITUTION_ADMIN   = 'institution_admin',    _('Institution Administrator')
    LIBRARY_ADMIN       = 'library_admin',        _('Library Administrator')
    COMPANY_USER        = 'company_user',         _('Company / Organization User')
    GENERAL_USER        = 'general_user',         _('General User')


# ──────────────────────────────────────────────────────────────────────────────
# User manager
# ──────────────────────────────────────────────────────────────────────────────
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email address is required'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', RoleType.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)


# ──────────────────────────────────────────────────────────────────────────────
# Custom User
# ──────────────────────────────────────────────────────────────────────────────
class User(AbstractBaseUser, PermissionsMixin):
    email           = models.EmailField(_('email address'), unique=True, db_index=True)
    username        = models.CharField(_('username'), max_length=150, unique=True, db_index=True)
    first_name      = models.CharField(_('first name'), max_length=100)
    last_name       = models.CharField(_('last name'), max_length=100)
    role            = models.CharField(
        _('role'), max_length=50,
        choices=RoleType.choices, default=RoleType.GENERAL_USER,
        db_index=True
    )
    is_active       = models.BooleanField(_('active'), default=True)
    is_staff        = models.BooleanField(_('staff'), default=False)
    is_verified     = models.BooleanField(_('email verified'), default=False)
    date_joined     = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login_ip   = models.GenericIPAddressField(_('last login IP'), null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name        = _('user')
        verbose_name_plural = _('users')
        ordering            = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name

    # ── convenience role helpers ──────────────────────────────────────────────
    def is_super_admin(self):
        return self.role == RoleType.SUPER_ADMIN

    def is_any_admin(self):
        return self.role in (
            RoleType.SUPER_ADMIN, RoleType.SYSTEM_ADMIN, RoleType.CONTENT_ADMIN
        )

    def is_editor(self):
        return self.role == RoleType.EDITOR

    def is_reviewer(self):
        return self.role == RoleType.REVIEWER

    def is_researcher(self):
        return self.role == RoleType.RESEARCHER

    def is_author(self):
        return self.role in (RoleType.AUTHOR, RoleType.RESEARCHER)

    def is_student(self):
        return self.role == RoleType.STUDENT

    def is_instructor(self):
        return self.role == RoleType.INSTRUCTOR

    def is_institution_admin(self):
        return self.role == RoleType.INSTITUTION_ADMIN

    def is_library_admin(self):
        return self.role == RoleType.LIBRARY_ADMIN

    def can_publish(self):
        return self.role in (
            RoleType.SUPER_ADMIN, RoleType.SYSTEM_ADMIN,
            RoleType.CONTENT_ADMIN, RoleType.EDITOR,
            RoleType.RESEARCHER, RoleType.AUTHOR
        )

    def can_review(self):
        return self.role in (
            RoleType.SUPER_ADMIN, RoleType.EDITOR, RoleType.REVIEWER
        )

    def can_manage_content(self):
        return self.role in (
            RoleType.SUPER_ADMIN, RoleType.SYSTEM_ADMIN, RoleType.CONTENT_ADMIN
        )


# ──────────────────────────────────────────────────────────────────────────────
# User Profile
# ──────────────────────────────────────────────────────────────────────────────
class UserProfile(models.Model):
    class VisibilityChoice(models.TextChoices):
        PUBLIC          = 'public',       _('Public')
        RESEARCHERS     = 'researchers',  _('Researchers Only')
        INSTITUTION     = 'institution',  _('Institution Only')
        PRIVATE         = 'private',      _('Private')

    user            = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    avatar          = models.ImageField(
        _('avatar'), upload_to='avatars/', null=True, blank=True
    )
    bio             = models.TextField(_('biography'), blank=True)
    headline        = models.CharField(_('headline'), max_length=200, blank=True)
    website         = models.URLField(_('website'), blank=True)
    phone           = models.CharField(_('phone'), max_length=30, blank=True)
    country         = models.CharField(_('country'), max_length=100, blank=True)
    city            = models.CharField(_('city'), max_length=100, blank=True)
    institution     = models.CharField(_('institution'), max_length=200, blank=True)
    department      = models.CharField(_('department'), max_length=200, blank=True)
    field_of_study  = models.CharField(_('field of study'), max_length=200, blank=True)
    orcid           = models.CharField(_('ORCID'), max_length=50, blank=True)
    linkedin        = models.URLField(_('LinkedIn'), blank=True)
    twitter         = models.URLField(_('Twitter / X'), blank=True)
    researchgate    = models.URLField(_('ResearchGate'), blank=True)
    visibility      = models.CharField(
        _('profile visibility'), max_length=20,
        choices=VisibilityChoice.choices, default=VisibilityChoice.PUBLIC
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f'Profile of {self.user.get_full_name()}'

    def completion_percentage(self):
        """Calculate profile completion as a percentage."""
        fields = [
            self.avatar, self.bio, self.headline, self.website,
            self.phone, self.country, self.city, self.institution,
            self.department, self.field_of_study
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)


# ──────────────────────────────────────────────────────────────────────────────
# User Preferences
# ──────────────────────────────────────────────────────────────────────────────
class UserPreference(models.Model):
    class ThemeChoice(models.TextChoices):
        LIGHT = 'light', _('Light')
        DARK  = 'dark',  _('Dark')

    user                        = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='preferences'
    )
    theme                       = models.CharField(
        max_length=10, choices=ThemeChoice.choices, default=ThemeChoice.LIGHT
    )
    language                    = models.CharField(max_length=10, default='en')
    email_notifications         = models.BooleanField(default=True)
    publication_notifications   = models.BooleanField(default=True)
    event_notifications         = models.BooleanField(default=True)
    collaboration_notifications = models.BooleanField(default=True)
    system_notifications        = models.BooleanField(default=True)
    items_per_page              = models.PositiveSmallIntegerField(default=20)

    class Meta:
        verbose_name        = _('user preference')
        verbose_name_plural = _('user preferences')

    def __str__(self):
        return f'Preferences of {self.user.get_full_name()}'


# ──────────────────────────────────────────────────────────────────────────────
# Audit Log
# ──────────────────────────────────────────────────────────────────────────────
class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE  = 'create',  _('Create')
        READ    = 'read',    _('Read')
        UPDATE  = 'update',  _('Update')
        DELETE  = 'delete',  _('Delete')
        LOGIN   = 'login',   _('Login')
        LOGOUT  = 'logout',  _('Logout')
        APPROVE = 'approve', _('Approve')
        REJECT  = 'reject',  _('Reject')
        PUBLISH = 'publish', _('Publish')
        UPLOAD  = 'upload',  _('Upload')
        DOWNLOAD= 'download',_('Download')
        OTHER   = 'other',   _('Other')

    user            = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs'
    )
    action          = models.CharField(max_length=20, choices=ActionType.choices)
    model_name      = models.CharField(max_length=100, blank=True)
    object_id       = models.CharField(max_length=50, blank=True)
    object_repr     = models.CharField(max_length=500, blank=True)
    description     = models.TextField(blank=True)
    ip_address      = models.GenericIPAddressField(null=True, blank=True)
    user_agent      = models.CharField(max_length=500, blank=True)
    timestamp       = models.DateTimeField(default=timezone.now, db_index=True)
    extra_data      = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name        = _('audit log')
        verbose_name_plural = _('audit logs')
        ordering            = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]

    def __str__(self):
        user_str = self.user.get_full_name() if self.user else 'Anonymous'
        return f'{user_str} — {self.action} — {self.timestamp:%Y-%m-%d %H:%M}'
