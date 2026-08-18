"""
GARL Health Science Hub Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class HealthCategory(models.Model):
    class DisciplineChoice(models.TextChoices):
        NURSING         = 'nursing',        _('Nursing')
        MEDICINE        = 'medicine',       _('Medicine')
        MIDWIFERY       = 'midwifery',      _('Midwifery')
        PHARMACY        = 'pharmacy',       _('Pharmacy')
        DENTISTRY       = 'dentistry',      _('Dentistry')
        PUBLIC_HEALTH   = 'public_health',  _('Public Health')
        BIOMEDICAL      = 'biomedical',     _('Biomedical Science')
        ALLIED_HEALTH   = 'allied_health',  _('Allied Health Sciences')

    name        = models.CharField(max_length=200, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    discipline  = models.CharField(max_length=20, choices=DisciplineChoice.choices, db_index=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=100, blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Health Categories'
        ordering = ['discipline', 'order', 'name']

    def __str__(self):
        return f'{self.get_discipline_display()} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class HealthResource(models.Model):
    class ResourceType(models.TextChoices):
        TEXTBOOK    = 'textbook',    _('Textbook')
        PAPER       = 'paper',       _('Research Paper')
        GUIDELINE   = 'guideline',   _('Clinical Guideline')
        LECTURE     = 'lecture',     _('Lecture Notes')
        CASE_STUDY  = 'case_study',  _('Case Study')
        COURSE      = 'course',      _('Course Material')
        OTHER       = 'other',       _('Other')

    title           = models.CharField(max_length=400)
    slug            = models.SlugField(max_length=420, unique=True, blank=True)
    description     = models.TextField()
    resource_type   = models.CharField(max_length=20, choices=ResourceType.choices, db_index=True)
    category        = models.ForeignKey(HealthCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    file            = models.FileField(upload_to='health/resources/', null=True, blank=True)
    external_url    = models.URLField(blank=True)
    author          = models.CharField(max_length=300, blank=True)
    year            = models.PositiveSmallIntegerField(null=True, blank=True)
    language        = models.CharField(max_length=50, default='English')
    is_published    = models.BooleanField(default=True, db_index=True)
    download_count  = models.PositiveIntegerField(default=0)
    view_count      = models.PositiveIntegerField(default=0)
    added_by        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['category', 'is_published'])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:400]
        super().save(*args, **kwargs)
