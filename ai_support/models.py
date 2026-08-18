"""
GARL AI Support — Chat session and message models
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class AIChatSession(models.Model):
    """One conversation thread per user (or anonymous session)."""
    session_key     = models.CharField(max_length=64, unique=True, db_index=True)
    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='ai_chat_sessions'
    )
    started_at      = models.DateTimeField(default=timezone.now)
    last_active     = models.DateTimeField(auto_now=True)
    message_count   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-last_active']

    def __str__(self):
        return f"Chat {self.session_key[:12]}… — {self.user or 'anonymous'}"

    @classmethod
    def get_or_create_for_request(cls, request):
        """Get or create a session for this request."""
        if request.user.is_authenticated:
            # Authenticated users get one session per user
            session_key = f'user_{request.user.pk}'
        else:
            # Guests use Django's session key
            if not request.session.session_key:
                request.session.create()
            session_key = f'anon_{request.session.session_key}'

        obj, _ = cls.objects.get_or_create(
            session_key=session_key,
            defaults={'user': request.user if request.user.is_authenticated else None}
        )
        return obj


class AIChatMessage(models.Model):
    """Single message in a chat session."""
    ROLE_USER      = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES   = [(ROLE_USER, 'User'), (ROLE_ASSISTANT, 'Assistant')]

    session     = models.ForeignKey(AIChatSession, on_delete=models.CASCADE, related_name='messages')
    role        = models.CharField(max_length=15, choices=ROLE_CHOICES)
    content     = models.TextField()
    sources     = models.JSONField(null=True, blank=True)   # list of {type,title,url} dicts
    confidence  = models.CharField(max_length=10, blank=True)  # high/medium/low
    intents     = models.JSONField(null=True, blank=True)
    enhanced    = models.BooleanField(default=False)  # True = LLM was used
    timestamp   = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'[{self.role}] {self.content[:60]}'


class AIChatFeedback(models.Model):
    """Thumbs up/down feedback on an AI response."""
    HELPFUL     = 'helpful'
    UNHELPFUL   = 'unhelpful'
    RATING_CHOICES = [(HELPFUL, 'Helpful'), (UNHELPFUL, 'Not Helpful')]

    message     = models.OneToOneField(AIChatMessage, on_delete=models.CASCADE, related_name='feedback')
    rating      = models.CharField(max_length=12, choices=RATING_CHOICES)
    comment     = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.rating} on message {self.message_id}'
