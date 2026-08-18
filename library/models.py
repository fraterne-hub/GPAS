"""
GARL Library Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.models import Subject


class LibraryCollection(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LibraryResource(models.Model):
    class ResourceType(models.TextChoices):
        BOOK        = 'book',       _('Book')
        JOURNAL     = 'journal',    _('Journal')
        THESIS      = 'thesis',     _('Thesis')
        DISSERTATION= 'dissertation', _('Dissertation')
        REPORT      = 'report',     _('Report')
        DATASET     = 'dataset',    _('Dataset')
        MULTIMEDIA  = 'multimedia', _('Multimedia')
        OTHER       = 'other',      _('Other')

    class AccessLevel(models.TextChoices):
        OPEN        = 'open',       _('Open Access')
        REGISTERED  = 'registered', _('Registered Users')
        RESTRICTED  = 'restricted', _('Restricted')

    title           = models.CharField(max_length=400)
    description     = models.TextField(blank=True)
    resource_type   = models.CharField(max_length=20, choices=ResourceType.choices, db_index=True)
    collection      = models.ForeignKey(LibraryCollection, on_delete=models.SET_NULL, null=True, blank=True)
    subjects        = models.ManyToManyField(Subject, blank=True)
    file            = models.FileField(upload_to='library/resources/', null=True, blank=True)
    external_url    = models.URLField(blank=True)
    isbn            = models.CharField(max_length=30, blank=True)
    issn            = models.CharField(max_length=20, blank=True)
    doi             = models.CharField(max_length=200, blank=True)
    author          = models.CharField(max_length=400, blank=True)
    publisher       = models.CharField(max_length=300, blank=True)
    year            = models.PositiveSmallIntegerField(null=True, blank=True)
    language        = models.CharField(max_length=50, default='English')
    access_level    = models.CharField(max_length=15, choices=AccessLevel.choices, default=AccessLevel.OPEN)
    is_published    = models.BooleanField(default=True, db_index=True)
    download_count  = models.PositiveIntegerField(default=0)
    view_count      = models.PositiveIntegerField(default=0)
    added_by        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Download(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='downloads')
    resource    = models.ForeignKey(LibraryResource, on_delete=models.CASCADE, related_name='downloads')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-downloaded_at']
