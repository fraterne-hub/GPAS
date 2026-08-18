"""
GARL Research Center Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from core.models import Subject, Tag


class ResearchCategory(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Research Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ResearchPaper(models.Model):
    class StatusChoice(models.TextChoices):
        DRAFT       = 'draft',     _('Draft')
        SUBMITTED   = 'submitted', _('Submitted')
        UNDER_REVIEW= 'under_review', _('Under Review')
        PUBLISHED   = 'published', _('Published')
        ARCHIVED    = 'archived',  _('Archived')

    title           = models.CharField(max_length=500)
    slug            = models.SlugField(max_length=520, unique=True, blank=True)
    abstract        = models.TextField()
    keywords        = models.CharField(max_length=500, blank=True)
    authors         = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='research_papers', blank=True
    )
    categories      = models.ManyToManyField(ResearchCategory, blank=True)
    tags            = models.ManyToManyField(Tag, blank=True)
    file            = models.FileField(upload_to='research/papers/', null=True, blank=True)
    doi             = models.CharField(max_length=200, blank=True)
    journal_name    = models.CharField(max_length=300, blank=True)
    publication_year= models.PositiveSmallIntegerField(null=True, blank=True)
    pages           = models.CharField(max_length=50, blank=True)
    language        = models.CharField(max_length=50, default='English')
    status          = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.DRAFT, db_index=True)
    download_count  = models.PositiveIntegerField(default=0)
    view_count      = models.PositiveIntegerField(default=0)
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_papers'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    published_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:500]
        super().save(*args, **kwargs)


class ResearchProject(models.Model):
    class StatusChoice(models.TextChoices):
        ONGOING     = 'ongoing',   _('Ongoing')
        COMPLETED   = 'completed', _('Completed')
        PAUSED      = 'paused',    _('Paused')

    title           = models.CharField(max_length=500)
    slug            = models.SlugField(max_length=520, unique=True, blank=True)
    description     = models.TextField()
    objectives      = models.TextField(blank=True)
    methodology     = models.TextField(blank=True)
    categories      = models.ManyToManyField(ResearchCategory, blank=True)
    lead_researcher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='led_projects'
    )
    team_members    = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='research_projects', blank=True
    )
    institution     = models.CharField(max_length=300, blank=True)
    start_date      = models.DateField(null=True, blank=True)
    end_date        = models.DateField(null=True, blank=True)
    status          = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.ONGOING)
    is_public       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:500]
        super().save(*args, **kwargs)


class ResearchDataset(models.Model):
    title           = models.CharField(max_length=400)
    description     = models.TextField()
    file            = models.FileField(upload_to='research/datasets/', null=True, blank=True)
    file_format     = models.CharField(max_length=50, blank=True)
    size_mb         = models.FloatField(null=True, blank=True)
    license         = models.CharField(max_length=200, blank=True)
    doi             = models.CharField(max_length=200, blank=True)
    uploaded_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='datasets'
    )
    project         = models.ForeignKey(
        ResearchProject, on_delete=models.SET_NULL, null=True, blank=True, related_name='datasets'
    )
    is_public       = models.BooleanField(default=True)
    download_count  = models.PositiveIntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ResearchTopic(models.Model):
    name            = models.CharField(max_length=300, unique=True)
    slug            = models.SlugField(unique=True, blank=True)
    description     = models.TextField(blank=True)
    category        = models.ForeignKey(ResearchCategory, on_delete=models.SET_NULL, null=True, blank=True)
    paper_count     = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Citation(models.Model):
    class StyleChoice(models.TextChoices):
        APA   = 'apa',    'APA'
        MLA   = 'mla',    'MLA'
        IEEE  = 'ieee',   'IEEE'
        AMA   = 'ama',    'AMA'
        CHICAGO='chicago','Chicago'
        HARVARD='harvard','Harvard'

    paper       = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE, related_name='citations')
    generated_by= models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    style       = models.CharField(max_length=20, choices=StyleChoice.choices, default=StyleChoice.APA)
    citation_text = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.style} citation for {self.paper.title[:60]}'
