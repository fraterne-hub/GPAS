"""
GARL Notifications Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        PUBLICATION_SUBMITTED   = 'pub_submitted',   _('Publication Submitted')
        REVIEW_ASSIGNED         = 'review_assigned', _('Review Assigned')
        REVISION_REQUESTED      = 'revision_req',    _('Revision Requested')
        PUBLICATION_APPROVED    = 'pub_approved',    _('Publication Approved')
        PUBLICATION_REJECTED    = 'pub_rejected',    _('Publication Rejected')
        COURSE_ENROLLED         = 'enrolled',        _('Course Enrollment')
        COURSE_COMPLETED        = 'completed',       _('Course Completed')
        CERTIFICATE_ISSUED      = 'certificate',     _('Certificate Issued')
        EVENT_REGISTERED        = 'event_reg',       _('Event Registration')
        SUPPORT_UPDATE          = 'support',         _('Support Ticket Update')
        COLLABORATION_REQUEST   = 'collab_req',      _('Collaboration Request')
        ANNOUNCEMENT            = 'announcement',    _('Announcement')
        SYSTEM                  = 'system',          _('System Notification')
        PROJECT_APPROVED        = 'proj_approved',   _('Project Approved')

    recipient   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    sender      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sent_notifications'
    )
    type        = models.CharField(max_length=30, choices=NotificationType.choices)
    title       = models.CharField(max_length=300)
    message     = models.TextField()
    link        = models.CharField(max_length=500, blank=True)
    is_read     = models.BooleanField(default=False, db_index=True)
    created_at  = models.DateTimeField(default=timezone.now, db_index=True)
    read_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['recipient', '-created_at']),
        ]

    def __str__(self):
        return f'[{self.type}] {self.title} → {self.recipient.username}'

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


def send_notification(recipient, notif_type, title, message, link='', sender=None):
    """Helper to create a notification record."""
    Notification.objects.create(
        recipient   = recipient,
        sender      = sender,
        type        = notif_type,
        title       = title,
        message     = message,
        link        = link,
    )
