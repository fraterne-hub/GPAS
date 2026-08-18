"""
GARL Publishing Center Models
Full submission → review → revision → approval → publication workflow
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from core.models import Subject, Tag


class PublicationType(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Journal(models.Model):
    title           = models.CharField(max_length=400)
    slug            = models.SlugField(unique=True, blank=True)
    issn            = models.CharField(max_length=20, blank=True)
    e_issn          = models.CharField(max_length=20, blank=True)
    description     = models.TextField(blank=True)
    subjects        = models.ManyToManyField(Subject, blank=True)
    cover_image     = models.ImageField(upload_to='journals/covers/', null=True, blank=True)
    publisher       = models.CharField(max_length=300, blank=True)
    website         = models.URLField(blank=True)
    is_open_access  = models.BooleanField(default=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class JournalIssue(models.Model):
    journal     = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='issues')
    volume      = models.PositiveSmallIntegerField()
    issue       = models.PositiveSmallIntegerField()
    year        = models.PositiveSmallIntegerField()
    title       = models.CharField(max_length=300, blank=True)
    published_at= models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('journal', 'volume', 'issue')
        ordering        = ['-year', '-volume', '-issue']

    def __str__(self):
        return f'{self.journal.title} Vol.{self.volume} No.{self.issue} ({self.year})'


class Publication(models.Model):
    class StatusChoice(models.TextChoices):
        DRAFT           = 'draft',          _('Draft')
        SUBMITTED       = 'submitted',      _('Submitted')
        SCREENING       = 'screening',      _('Editorial Screening')
        UNDER_REVIEW    = 'under_review',   _('Under Review')
        REVISION_REQ    = 'revision_req',   _('Revision Required')
        FINAL_REVIEW    = 'final_review',   _('Final Review')
        APPROVED        = 'approved',       _('Approved')
        PUBLISHED       = 'published',      _('Published')
        REJECTED        = 'rejected',       _('Rejected')
        ARCHIVED        = 'archived',       _('Archived')

    title           = models.CharField(max_length=500)
    slug            = models.SlugField(max_length=520, unique=True, blank=True)
    abstract        = models.TextField()
    keywords        = models.CharField(max_length=500, blank=True)
    pub_type        = models.ForeignKey(PublicationType, on_delete=models.SET_NULL, null=True, blank=True)
    journal         = models.ForeignKey(Journal, on_delete=models.SET_NULL, null=True, blank=True, related_name='publications')
    journal_issue   = models.ForeignKey(JournalIssue, on_delete=models.SET_NULL, null=True, blank=True, related_name='publications')
    subjects        = models.ManyToManyField(Subject, blank=True)
    tags            = models.ManyToManyField(Tag, blank=True)
    manuscript      = models.FileField(upload_to='publishing/manuscripts/', null=True, blank=True)
    cover_image     = models.ImageField(upload_to='publishing/covers/', null=True, blank=True)
    doi             = models.CharField(max_length=200, blank=True)
    isbn            = models.CharField(max_length=30, blank=True)
    language        = models.CharField(max_length=50, default='English')
    pages           = models.CharField(max_length=50, blank=True)
    status          = models.CharField(
        max_length=20, choices=StatusChoice.choices, default=StatusChoice.DRAFT, db_index=True
    )
    is_open_access  = models.BooleanField(default=True)
    view_count      = models.PositiveIntegerField(default=0)
    download_count  = models.PositiveIntegerField(default=0)
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='publications'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    submitted_at    = models.DateTimeField(null=True, blank=True)
    published_at    = models.DateTimeField(null=True, blank=True)
    rejection_reason= models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:500]
        super().save(*args, **kwargs)


class PublicationAuthor(models.Model):
    """Links authors to a publication with ordering."""
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='publication_authors')
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    name        = models.CharField(max_length=300)   # in case author has no account
    email       = models.EmailField(blank=True)
    affiliation = models.CharField(max_length=300, blank=True)
    is_corresponding = models.BooleanField(default=False)
    order       = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering        = ['order']
        unique_together = ('publication', 'order')

    def __str__(self):
        return f'{self.name} — {self.publication.title[:60]}'


class Submission(models.Model):
    """Tracks the lifecycle of a single publication submission."""
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE, related_name='submission')
    submitted_by= models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='submissions'
    )
    assigned_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_submissions'
    )
    submitted_at    = models.DateTimeField(auto_now_add=True)
    screening_at    = models.DateTimeField(null=True, blank=True)
    decision_at     = models.DateTimeField(null=True, blank=True)
    notes           = models.TextField(blank=True)

    def __str__(self):
        return f'Submission: {self.publication.title[:80]}'


class Review(models.Model):
    class RecommendationChoice(models.TextChoices):
        ACCEPT          = 'accept',   _('Accept')
        MINOR_REVISION  = 'minor',    _('Minor Revision')
        MAJOR_REVISION  = 'major',    _('Major Revision')
        REJECT          = 'reject',   _('Reject')

    submission  = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='reviews')
    reviewer    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviews'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date    = models.DateField(null=True, blank=True)
    submitted_at= models.DateTimeField(null=True, blank=True)
    recommendation = models.CharField(
        max_length=10, choices=RecommendationChoice.choices, blank=True
    )
    comments_to_author  = models.TextField(blank=True)
    comments_to_editor  = models.TextField(blank=True)
    is_completed        = models.BooleanField(default=False)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f'Review by {self.reviewer} for {self.submission}'


class Revision(models.Model):
    submission      = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='revisions')
    requested_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='revision_requests'
    )
    requested_at    = models.DateTimeField(auto_now_add=True)
    deadline        = models.DateField(null=True, blank=True)
    instructions    = models.TextField()
    revised_file    = models.FileField(upload_to='publishing/revisions/', null=True, blank=True)
    author_response = models.TextField(blank=True)
    submitted_at    = models.DateTimeField(null=True, blank=True)
    is_complete     = models.BooleanField(default=False)

    def __str__(self):
        return f'Revision for {self.submission}'


class Book(models.Model):
    title       = models.CharField(max_length=400)
    slug        = models.SlugField(unique=True, blank=True)
    subtitle    = models.CharField(max_length=400, blank=True)
    description = models.TextField()
    cover       = models.ImageField(upload_to='books/covers/', null=True, blank=True)
    file        = models.FileField(upload_to='books/files/', null=True, blank=True)
    isbn        = models.CharField(max_length=30, blank=True)
    publisher   = models.CharField(max_length=300, blank=True)
    edition     = models.CharField(max_length=50, blank=True)
    year        = models.PositiveSmallIntegerField(null=True, blank=True)
    pages       = models.PositiveSmallIntegerField(null=True, blank=True)
    language    = models.CharField(max_length=50, default='English')
    subjects    = models.ManyToManyField(Subject, blank=True)
    tags        = models.ManyToManyField(Tag, blank=True)
    is_free     = models.BooleanField(default=True)
    is_published= models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    view_count  = models.PositiveIntegerField(default=0)
    added_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        indexes  = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
