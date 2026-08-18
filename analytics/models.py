"""
GARL Analytics Models — platform-wide statistics and activity tracking
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DailyStats(models.Model):
    """Aggregated daily statistics for the admin analytics dashboard."""
    date                = models.DateField(unique=True, db_index=True)
    new_users           = models.PositiveIntegerField(default=0)
    active_users        = models.PositiveIntegerField(default=0)
    new_publications    = models.PositiveIntegerField(default=0)
    new_papers          = models.PositiveIntegerField(default=0)
    new_courses         = models.PositiveIntegerField(default=0)
    new_enrollments     = models.PositiveIntegerField(default=0)
    new_projects        = models.PositiveIntegerField(default=0)
    downloads           = models.PositiveIntegerField(default=0)
    searches            = models.PositiveIntegerField(default=0)
    support_tickets     = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'Stats for {self.date}'


class ResourceView(models.Model):
    """Records individual resource views for analytics."""
    content_type    = models.CharField(max_length=30, db_index=True)
    object_id       = models.PositiveIntegerField()
    object_title    = models.CharField(max_length=400, blank=True)
    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    ip_address      = models.GenericIPAddressField(null=True, blank=True)
    viewed_at       = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-viewed_at']
        indexes  = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['-viewed_at']),
        ]

    def __str__(self):
        return f'{self.content_type}:{self.object_id} viewed at {self.viewed_at:%Y-%m-%d %H:%M}'
