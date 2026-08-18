"""
GARL Innovation Hub Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from core.models import Subject, Tag


class ProjectCategory(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=100, blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Project Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class InnovationProject(models.Model):
    class StatusChoice(models.TextChoices):
        DRAFT     = 'draft',     _('Draft')
        SUBMITTED = 'submitted', _('Submitted')
        PENDING   = 'pending',   _('Pending Moderation')
        APPROVED  = 'approved',  _('Approved')
        PUBLISHED = 'published', _('Published')
        REJECTED  = 'rejected',  _('Rejected')

    class ProjectType(models.TextChoices):
        STUDENT     = 'student',     _('Student Project')
        UNIVERSITY  = 'university',  _('University Project')
        INSTITUTION = 'institution', _('Institution Project')
        COMPANY     = 'company',     _('Company Product')
        PROTOTYPE   = 'prototype',   _('Prototype')
        STARTUP     = 'startup',     _('Startup')
        RESEARCH    = 'research',    _('Research Innovation')
        PATENT      = 'patent',      _('Patent')
        CHALLENGE   = 'challenge',   _('Innovation Challenge')

    title           = models.CharField(max_length=400)
    slug            = models.SlugField(max_length=420, unique=True, blank=True)
    description     = models.TextField()
    problem_solved  = models.TextField(blank=True)
    technologies    = models.CharField(max_length=500, blank=True)
    project_type    = models.CharField(max_length=20, choices=ProjectType.choices, db_index=True)
    categories      = models.ManyToManyField(ProjectCategory, blank=True)
    subjects        = models.ManyToManyField(Subject, blank=True)
    tags            = models.ManyToManyField(Tag, blank=True)
    cover_image     = models.ImageField(upload_to='innovation/covers/', null=True, blank=True)
    document        = models.FileField(upload_to='innovation/documents/', null=True, blank=True)
    demo_url        = models.URLField(blank=True)
    repository_url  = models.URLField(blank=True)
    status          = models.CharField(
        max_length=20, choices=StatusChoice.choices, default=StatusChoice.DRAFT, db_index=True
    )
    is_featured     = models.BooleanField(default=False)
    like_count      = models.PositiveIntegerField(default=0)
    view_count      = models.PositiveIntegerField(default=0)
    submitted_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='innovation_projects'
    )
    institution     = models.CharField(max_length=300, blank=True)
    rejection_reason= models.TextField(blank=True)
    moderated_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='moderated_projects'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    published_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['project_type', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:400]
        super().save(*args, **kwargs)


class ProjectMember(models.Model):
    project = models.ForeignKey(InnovationProject, on_delete=models.CASCADE, related_name='members')
    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    name    = models.CharField(max_length=200)
    role    = models.CharField(max_length=200, blank=True)
    is_lead = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} — {self.project.title[:60]}'


class ProjectLike(models.Model):
    project     = models.ForeignKey(InnovationProject, on_delete=models.CASCADE, related_name='likes')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')


class ProjectComment(models.Model):
    project     = models.ForeignKey(InnovationProject, on_delete=models.CASCADE, related_name='comments')
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content     = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.project.title[:40]}'
