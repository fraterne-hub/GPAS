"""
GARL Community & Directory Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class InstitutionType(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Institution(models.Model):
    name            = models.CharField(max_length=400, db_index=True)
    slug            = models.SlugField(max_length=420, unique=True, blank=True)
    institution_type = models.ForeignKey(InstitutionType, on_delete=models.SET_NULL, null=True, blank=True)
    description     = models.TextField(blank=True)
    logo            = models.ImageField(upload_to='institutions/logos/', null=True, blank=True)
    cover_image     = models.ImageField(upload_to='institutions/covers/', null=True, blank=True)
    website         = models.URLField(blank=True)
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=50, blank=True)
    address         = models.TextField(blank=True)
    city            = models.CharField(max_length=100, blank=True)
    country         = models.CharField(max_length=100, db_index=True)
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)
    is_verified     = models.BooleanField(default=False)
    is_published    = models.BooleanField(default=True)
    admin_user      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='administered_institutions'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes  = [models.Index(fields=['country', 'name'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:400]
        super().save(*args, **kwargs)


class Department(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='departments')
    name        = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('institution', 'name')
        ordering        = ['name']

    def __str__(self):
        return f'{self.institution.name} — {self.name}'


class InstitutionMember(models.Model):
    class RoleChoice(models.TextChoices):
        FACULTY     = 'faculty',     _('Faculty')
        RESEARCHER  = 'researcher',  _('Researcher')
        STUDENT     = 'student',     _('Student')
        STAFF       = 'staff',       _('Staff')
        ADMIN       = 'admin',       _('Administrator')

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='members')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='institution_memberships')
    department  = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role        = models.CharField(max_length=20, choices=RoleChoice.choices, default=RoleChoice.STUDENT)
    is_active   = models.BooleanField(default=True)
    joined_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('institution', 'user')

    def __str__(self):
        return f'{self.user.username} @ {self.institution.name}'


class ResearchNetwork(models.Model):
    name        = models.CharField(max_length=300, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    focus_areas = models.TextField(blank=True)
    founder     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='founded_networks')
    members     = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='research_networks', blank=True)
    is_public   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CollaborationRequest(models.Model):
    class StatusChoice(models.TextChoices):
        PENDING     = 'pending',  _('Pending')
        ACCEPTED    = 'accepted', _('Accepted')
        DECLINED    = 'declined', _('Declined')

    from_user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_collaborations')
    to_user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_collaborations')
    message     = models.TextField(blank=True)
    status      = models.CharField(max_length=15, choices=StatusChoice.choices, default=StatusChoice.PENDING)
    created_at  = models.DateTimeField(auto_now_add=True)
    responded_at= models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering        = ['-created_at']

    def __str__(self):
        return f'{self.from_user.username} → {self.to_user.username} ({self.status})'
