"""
GARL Core Models — Categories, Subjects, Announcements, Bookmarks, Favorites, SiteSettings
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


# ──────────────────────────────────────────────────────────────────────────────
# Subject / Category (reusable across all modules)
# ──────────────────────────────────────────────────────────────────────────────
class Subject(models.Model):
    name        = models.CharField(_('name'), max_length=200, unique=True)
    slug        = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=100, blank=True, help_text='Bootstrap icon class e.g. bi-book')
    color       = models.CharField(max_length=20, blank=True, help_text='CSS color hex')
    parent      = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children'
    )
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = _('subject')
        verbose_name_plural = _('subjects')
        ordering            = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# Tag
# ──────────────────────────────────────────────────────────────────────────────
class Tag(models.Model):
    name    = models.CharField(max_length=100, unique=True)
    slug    = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# Announcement
# ──────────────────────────────────────────────────────────────────────────────
class Announcement(models.Model):
    class AnnouncementType(models.TextChoices):
        GENERAL     = 'general',     _('General')
        MAINTENANCE = 'maintenance', _('Maintenance')
        NEW_FEATURE = 'feature',     _('New Feature')
        EVENT       = 'event',       _('Event')
        URGENT      = 'urgent',      _('Urgent')

    title       = models.CharField(max_length=300)
    content     = models.TextField()
    type        = models.CharField(max_length=20, choices=AnnouncementType.choices, default=AnnouncementType.GENERAL)
    is_active   = models.BooleanField(default=True)
    is_pinned   = models.BooleanField(default=False)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='announcements'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


# ──────────────────────────────────────────────────────────────────────────────
# Bookmark / Favorite (generic)
# ──────────────────────────────────────────────────────────────────────────────
class Bookmark(models.Model):
    class ContentType(models.TextChoices):
        BOOK          = 'book',          _('Book')
        PAPER         = 'paper',         _('Research Paper')
        JOURNAL       = 'journal',       _('Journal')
        COURSE        = 'course',        _('Course')
        PROJECT       = 'project',       _('Project')
        RESEARCHER    = 'researcher',    _('Researcher')
        INSTITUTION   = 'institution',   _('Institution')
        EVENT         = 'event',         _('Event')
        HEALTH        = 'health',        _('Health Resource')

    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks'
    )
    content_type    = models.CharField(max_length=20, choices=ContentType.choices)
    object_id       = models.PositiveIntegerField()
    note            = models.CharField(max_length=300, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        ordering        = ['-created_at']

    def __str__(self):
        return f'{self.user.username} bookmarked {self.content_type}:{self.object_id}'


# ──────────────────────────────────────────────────────────────────────────────
# Reading / Activity History
# ──────────────────────────────────────────────────────────────────────────────
class ActivityHistory(models.Model):
    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_history'
    )
    content_type    = models.CharField(max_length=20)
    object_id       = models.PositiveIntegerField()
    object_title    = models.CharField(max_length=300, blank=True)
    accessed_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-accessed_at']
        indexes  = [models.Index(fields=['user', '-accessed_at'])]

    def __str__(self):
        return f'{self.user.username} accessed {self.content_type}:{self.object_id}'


# ──────────────────────────────────────────────────────────────────────────────
# Platform Statistics (cached aggregate counts for homepage)
# ──────────────────────────────────────────────────────────────────────────────
class PlatformStatistic(models.Model):
    key         = models.CharField(max_length=100, unique=True)
    value       = models.BigIntegerField(default=0)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.key}: {self.value}'


# ──────────────────────────────────────────────────────────────────────────────
# Site Settings — Admin-managed images & branding
# ──────────────────────────────────────────────────────────────────────────────
class SiteSettings(models.Model):
    """
    Singleton model — only one row.  Admin can upload a hero banner image,
    logo, and other site-wide images directly from the Django admin panel.
    """
    # Hero / Banner
    hero_banner     = models.ImageField(
        upload_to='site/banners/',
        null=True, blank=True,
        help_text=_('Homepage hero background image (recommended: 1920×900 px, JPG/PNG).')
    )
    hero_title      = models.CharField(
        max_length=200, blank=True, default='',
        help_text=_('Override hero headline text. Leave blank to use the default.')
    )
    hero_subtitle   = models.CharField(
        max_length=300, blank=True, default='',
        help_text=_('Override hero sub-heading. Leave blank to use the default.')
    )

    # Site logo (overrides the icon-based logo)
    site_logo       = models.ImageField(
        upload_to='site/logos/',
        null=True, blank=True,
        help_text=_('Site logo image (recommended: transparent PNG, ~200×60 px).')
    )
    site_logo_white = models.ImageField(
        upload_to='site/logos/',
        null=True, blank=True,
        help_text=_('White/inverted logo for dark navbar backgrounds.')
    )
    favicon         = models.ImageField(
        upload_to='site/logos/',
        null=True, blank=True,
        help_text=_('Browser favicon (32×32 px ICO or PNG).')
    )

    # Promotional / Feature images
    promo_image_1   = models.ImageField(
        upload_to='site/promo/',
        null=True, blank=True,
        verbose_name=_('Promotional Image 1'),
        help_text=_('Shown in the homepage features / about section.')
    )
    promo_image_2   = models.ImageField(
        upload_to='site/promo/',
        null=True, blank=True,
        verbose_name=_('Promotional Image 2')
    )
    promo_image_3   = models.ImageField(
        upload_to='site/promo/',
        null=True, blank=True,
        verbose_name=_('Promotional Image 3')
    )

    # About section
    about_text      = models.TextField(
        blank=True, default='',
        help_text=_('Short about-us text shown on the homepage.')
    )

    # Social links (overrides footer hard-coded links)
    social_twitter  = models.URLField(blank=True, default='', verbose_name='Twitter / X URL')
    social_linkedin = models.URLField(blank=True, default='', verbose_name='LinkedIn URL')
    social_facebook = models.URLField(blank=True, default='', verbose_name='Facebook URL')
    social_youtube  = models.URLField(blank=True, default='', verbose_name='YouTube URL')

    # Metadata
    updated_at      = models.DateTimeField(auto_now=True)
    updated_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='site_settings_updates'
    )

    class Meta:
        verbose_name        = _('Site Settings')
        verbose_name_plural = _('Site Settings')

    def __str__(self):
        return 'GARL Site Settings'

    def save(self, *args, **kwargs):
        # Enforce singleton — always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        """Return the single SiteSettings object, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def delete(self, *args, **kwargs):
        # Prevent deletion of the singleton
        pass


# ──────────────────────────────────────────────────────────────────────────────
# Newsletter Subscriber
# ──────────────────────────────────────────────────────────────────────────────
class NewsletterSubscriber(models.Model):
    email           = models.EmailField(unique=True, db_index=True)
    name            = models.CharField(max_length=200, blank=True)
    is_active       = models.BooleanField(default=True)
    subscribed_at   = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    ip_address      = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name        = _('newsletter subscriber')
        verbose_name_plural = _('newsletter subscribers')
        ordering            = ['-subscribed_at']

    def __str__(self):
        return self.email
