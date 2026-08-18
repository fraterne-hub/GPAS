"""
GARL Events Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class EventCategory(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Event Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    class EventType(models.TextChoices):
        CONFERENCE  = 'conference',  _('Conference')
        SEMINAR     = 'seminar',     _('Seminar')
        WORKSHOP    = 'workshop',    _('Workshop')
        WEBINAR     = 'webinar',     _('Webinar')
        MEETING     = 'meeting',     _('Academic Meeting')
        COMPETITION = 'competition', _('Innovation Competition')
        RESEARCH    = 'research',    _('Research Event')
        OTHER       = 'other',       _('Other')

    title           = models.CharField(max_length=400)
    slug            = models.SlugField(max_length=420, unique=True, blank=True)
    description     = models.TextField()
    event_type      = models.CharField(max_length=20, choices=EventType.choices, db_index=True)
    category        = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True)
    cover_image     = models.ImageField(upload_to='events/covers/', null=True, blank=True)
    start_date      = models.DateTimeField(db_index=True)
    end_date        = models.DateTimeField()
    location        = models.CharField(max_length=400, blank=True)
    online_link     = models.URLField(blank=True)
    is_online       = models.BooleanField(default=False)
    capacity        = models.PositiveIntegerField(null=True, blank=True)
    is_free         = models.BooleanField(default=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    is_published    = models.BooleanField(default=True, db_index=True)
    organizer       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='organized_events'
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']
        indexes  = [models.Index(fields=['start_date', 'is_published'])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:400]
        super().save(*args, **kwargs)

    @property
    def registration_count(self):
        return self.registrations.count()

    @property
    def is_full(self):
        if self.capacity:
            return self.registration_count >= self.capacity
        return False


class Speaker(models.Model):
    event           = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='speakers')
    name            = models.CharField(max_length=200)
    bio             = models.TextField(blank=True)
    photo           = models.ImageField(upload_to='events/speakers/', null=True, blank=True)
    affiliation     = models.CharField(max_length=300, blank=True)
    topic           = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f'{self.name} — {self.event.title[:60]}'


class EventRegistration(models.Model):
    class StatusChoice(models.TextChoices):
        REGISTERED  = 'registered',  _('Registered')
        CONFIRMED   = 'confirmed',   _('Confirmed')
        ATTENDED    = 'attended',    _('Attended')
        CANCELLED   = 'cancelled',   _('Cancelled')

    event       = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    status      = models.CharField(max_length=15, choices=StatusChoice.choices, default=StatusChoice.REGISTERED)
    registered_at = models.DateTimeField(auto_now_add=True)
    notes       = models.TextField(blank=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering        = ['-registered_at']

    def __str__(self):
        return f'{self.user.username} — {self.event.title[:60]}'
