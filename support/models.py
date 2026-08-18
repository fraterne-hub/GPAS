"""
GARL Support Center Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class FAQCategory(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'FAQ Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class FAQ(models.Model):
    category    = models.ForeignKey(FAQCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='faqs')
    question    = models.CharField(max_length=500)
    answer      = models.TextField()
    is_published= models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__order', 'order']

    def __str__(self):
        return self.question[:100]


class SupportTicket(models.Model):
    class StatusChoice(models.TextChoices):
        OPEN            = 'open',         _('Open')
        ASSIGNED        = 'assigned',     _('Assigned')
        IN_PROGRESS     = 'in_progress',  _('In Progress')
        WAITING         = 'waiting',      _('Waiting for User')
        RESOLVED        = 'resolved',     _('Resolved')
        CLOSED          = 'closed',       _('Closed')

    class PriorityChoice(models.TextChoices):
        LOW     = 'low',    _('Low')
        MEDIUM  = 'medium', _('Medium')
        HIGH    = 'high',   _('High')
        URGENT  = 'urgent', _('Urgent')

    class CategoryChoice(models.TextChoices):
        ACCOUNT     = 'account',     _('Account')
        TECHNICAL   = 'technical',   _('Technical Support')
        PUBLISHING  = 'publishing',  _('Publishing')
        RESEARCH    = 'research',    _('Research Assistance')
        BILLING     = 'billing',     _('Billing')
        OTHER       = 'other',       _('Other')

    ticket_number   = models.CharField(max_length=20, unique=True)
    subject         = models.CharField(max_length=400)
    description     = models.TextField()
    category        = models.CharField(max_length=20, choices=CategoryChoice.choices, default=CategoryChoice.OTHER)
    priority        = models.CharField(max_length=10, choices=PriorityChoice.choices, default=PriorityChoice.MEDIUM)
    status          = models.CharField(max_length=15, choices=StatusChoice.choices, default=StatusChoice.OPEN, db_index=True)
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets'
    )
    assigned_to     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tickets'
    )
    attachment      = models.FileField(upload_to='support/attachments/', null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    resolved_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['status', '-created_at'])]

    def __str__(self):
        return f'[{self.ticket_number}] {self.subject}'

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import uuid
            self.ticket_number = f'TKT-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)


class TicketMessage(models.Model):
    ticket      = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message     = models.TextField()
    is_staff    = models.BooleanField(default=False)
    attachment  = models.FileField(upload_to='support/messages/', null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message on {self.ticket.ticket_number} by {self.author.username}'
