"""
GARL Payments & Revenue Models
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Revenue split:
  Platform owner  → 40% of every sale
  Publisher/Author → 60% of every sale

Supported content types: Book, Publication (articles/journals/theses), Journal
"""

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


# ── Revenue split constants ───────────────────────────────────────────────────
PLATFORM_SHARE  = Decimal('0.40')   # 40% to GARL platform owner
PUBLISHER_SHARE = Decimal('0.60')   # 60% to publisher/author


# ── Content type choices (what is being sold) ─────────────────────────────────
class ContentType(models.TextChoices):
    BOOK        = 'book',        _('Book')
    PUBLICATION = 'publication', _('Publication / Article')
    JOURNAL     = 'journal',     _('Journal Issue')
    THESIS      = 'thesis',      _('Thesis / Dissertation')


# ──────────────────────────────────────────────────────────────────────────────
# ContentPrice — price entry for any content item
# ──────────────────────────────────────────────────────────────────────────────
class ContentPrice(models.Model):
    content_type    = models.CharField(max_length=20, choices=ContentType.choices, db_index=True)
    object_id       = models.PositiveIntegerField(db_index=True)
    # The owner/publisher of this content (gets 60%)
    owner           = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='content_prices'
    )
    price           = models.DecimalField(max_digits=10, decimal_places=2)
    currency        = models.CharField(max_length=3, default='USD')
    is_free         = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('content_type', 'object_id')
        verbose_name        = _('content price')
        verbose_name_plural = _('content prices')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.content_type}:{self.object_id} — {self.currency} {self.price}'

    @property
    def platform_cut(self):
        """Amount going to GARL (40%)."""
        return (self.price * PLATFORM_SHARE).quantize(Decimal('0.01'))

    @property
    def publisher_cut(self):
        """Amount going to publisher (60%)."""
        return (self.price * PUBLISHER_SHARE).quantize(Decimal('0.01'))


# ──────────────────────────────────────────────────────────────────────────────
# Purchase — one transaction (one user buys one content item)
# ──────────────────────────────────────────────────────────────────────────────
class Purchase(models.Model):
    class StatusChoice(models.TextChoices):
        PENDING   = 'pending',   _('Pending')
        COMPLETED = 'completed', _('Completed')
        FAILED    = 'failed',    _('Failed')
        REFUNDED  = 'refunded',  _('Refunded')

    transaction_id  = models.CharField(max_length=64, unique=True, editable=False)
    buyer           = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='purchases'
    )
    content_price   = models.ForeignKey(
        ContentPrice, on_delete=models.PROTECT, related_name='purchases'
    )
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    currency        = models.CharField(max_length=3, default='USD')
    platform_amount = models.DecimalField(max_digits=10, decimal_places=2)
    publisher_amount= models.DecimalField(max_digits=10, decimal_places=2)
    status          = models.CharField(
        max_length=12, choices=StatusChoice.choices, default=StatusChoice.PENDING
    )
    payment_method  = models.CharField(max_length=50, blank=True)  # 'card', 'mobile_money', etc.
    payment_ref     = models.CharField(max_length=200, blank=True)  # external payment reference
    buyer_email     = models.EmailField(blank=True)
    created_at      = models.DateTimeField(default=timezone.now, db_index=True)
    completed_at    = models.DateTimeField(null=True, blank=True)
    # Notification flags
    buyer_notified      = models.BooleanField(default=False)
    publisher_notified  = models.BooleanField(default=False)
    owner_notified      = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name        = _('purchase')
        verbose_name_plural = _('purchases')

    def __str__(self):
        return f'Purchase {self.transaction_id} — {self.buyer} — {self.currency} {self.amount}'

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f'GARL-{uuid.uuid4().hex[:16].upper()}'
        if not self.platform_amount:
            self.platform_amount = (self.amount * PLATFORM_SHARE).quantize(Decimal('0.01'))
        if not self.publisher_amount:
            self.publisher_amount = (self.amount * PUBLISHER_SHARE).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def complete(self):
        """Mark purchase as completed."""
        self.status       = self.StatusChoice.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
        # Create access grant
        AccessGrant.objects.get_or_create(
            buyer=self.buyer,
            content_type=self.content_price.content_type,
            object_id=self.content_price.object_id,
        )


# ──────────────────────────────────────────────────────────────────────────────
# AccessGrant — records that a user has paid for and may access content
# ──────────────────────────────────────────────────────────────────────────────
class AccessGrant(models.Model):
    buyer           = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='access_grants'
    )
    content_type    = models.CharField(max_length=20, choices=ContentType.choices)
    object_id       = models.PositiveIntegerField()
    granted_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'content_type', 'object_id')
        verbose_name        = _('access grant')
        verbose_name_plural = _('access grants')

    def __str__(self):
        return f'{self.buyer.username} → {self.content_type}:{self.object_id}'


# ──────────────────────────────────────────────────────────────────────────────
# PublisherEarnings — aggregate earnings per publisher
# ──────────────────────────────────────────────────────────────────────────────
class PublisherEarnings(models.Model):
    publisher       = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='earnings'
    )
    total_sales     = models.PositiveIntegerField(default=0)
    total_revenue   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    platform_paid   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    publisher_paid  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pending_payout  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_paid_out  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _('publisher earnings')
        verbose_name_plural = _('publisher earnings')

    def __str__(self):
        return f'Earnings for {self.publisher.get_full_name()}: {self.publisher_paid}'

    def record_sale(self, publisher_amount: Decimal, total_amount: Decimal):
        """Update earnings after a completed sale."""
        self.total_sales    += 1
        self.total_revenue  += total_amount
        self.platform_paid  += (total_amount * PLATFORM_SHARE).quantize(Decimal('0.01'))
        self.publisher_paid += publisher_amount
        self.pending_payout += publisher_amount
        self.save()


# ──────────────────────────────────────────────────────────────────────────────
# Payout — when a publisher requests / receives their earnings
# ──────────────────────────────────────────────────────────────────────────────
class Payout(models.Model):
    class StatusChoice(models.TextChoices):
        REQUESTED  = 'requested',  _('Requested')
        PROCESSING = 'processing', _('Processing')
        PAID       = 'paid',       _('Paid')
        REJECTED   = 'rejected',   _('Rejected')

    publisher       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts'
    )
    amount          = models.DecimalField(max_digits=12, decimal_places=2)
    currency        = models.CharField(max_length=3, default='USD')
    status          = models.CharField(
        max_length=12, choices=StatusChoice.choices, default=StatusChoice.REQUESTED
    )
    payment_details = models.TextField(blank=True, help_text=_('Bank/mobile money details'))
    admin_note      = models.TextField(blank=True)
    requested_at    = models.DateTimeField(auto_now_add=True)
    processed_at    = models.DateTimeField(null=True, blank=True)
    processed_by    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='processed_payouts'
    )

    class Meta:
        ordering = ['-requested_at']
        verbose_name        = _('payout')
        verbose_name_plural = _('payouts')

    def __str__(self):
        return f'Payout {self.pk} — {self.publisher.get_full_name()} — {self.currency} {self.amount} ({self.status})'


# ──────────────────────────────────────────────────────────────────────────────
# PlatformRevenue — running totals for the system owner
# ──────────────────────────────────────────────────────────────────────────────
class PlatformRevenue(models.Model):
    """Singleton — one row tracks platform-wide totals."""
    total_transactions  = models.PositiveIntegerField(default=0)
    total_gross         = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_platform_cut  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_publisher_cut = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _('platform revenue')
        verbose_name_plural = _('platform revenue')

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def record_sale(self, gross: Decimal, platform_cut: Decimal, publisher_cut: Decimal):
        self.total_transactions  += 1
        self.total_gross         += gross
        self.total_platform_cut  += platform_cut
        self.total_publisher_cut += publisher_cut
        self.save()

    def __str__(self):
        return f'Platform Revenue: ${self.total_platform_cut} (40% of ${self.total_gross})'
