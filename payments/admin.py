from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ContentPrice, Purchase, AccessGrant,
    PublisherEarnings, PlatformRevenue, Payout
)


@admin.register(ContentPrice)
class ContentPriceAdmin(admin.ModelAdmin):
    list_display  = ('content_type', 'object_id', 'owner', 'price_display', 'currency', 'is_free', 'is_active')
    list_filter   = ('content_type', 'is_free', 'is_active', 'currency')
    search_fields = ('owner__email', 'owner__username')
    list_editable = ('is_free', 'is_active')

    def price_display(self, obj):
        if obj.is_free:
            return format_html('<span style="color:green;font-weight:600;">FREE</span>')
        return format_html('<strong>{} {}</strong>', obj.currency, obj.price)
    price_display.short_description = 'Price'


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display  = ('transaction_id', 'buyer', 'content_preview', 'amount_display',
                     'platform_amount', 'publisher_amount', 'status', 'created_at')
    list_filter   = ('status', 'currency', 'content_price__content_type')
    search_fields = ('transaction_id', 'buyer__email', 'buyer__username')
    readonly_fields = ('transaction_id', 'platform_amount', 'publisher_amount',
                       'buyer_notified', 'publisher_notified', 'owner_notified')

    def content_preview(self, obj):
        return f'{obj.content_price.get_content_type_display()} #{obj.content_price.object_id}'
    content_preview.short_description = 'Content'

    def amount_display(self, obj):
        return f'{obj.currency} {obj.amount}'
    amount_display.short_description = 'Total'


@admin.register(AccessGrant)
class AccessGrantAdmin(admin.ModelAdmin):
    list_display  = ('buyer', 'content_type', 'object_id', 'granted_at')
    list_filter   = ('content_type',)
    search_fields = ('buyer__email', 'buyer__username')


@admin.register(PublisherEarnings)
class PublisherEarningsAdmin(admin.ModelAdmin):
    list_display  = ('publisher', 'total_sales', 'total_revenue_display',
                     'publisher_paid_display', 'pending_payout_display', 'updated_at')
    search_fields = ('publisher__email', 'publisher__username')
    readonly_fields = ('publisher', 'total_sales', 'total_revenue', 'platform_paid',
                       'publisher_paid', 'pending_payout', 'total_paid_out', 'updated_at')

    def total_revenue_display(self, obj):
        return f'USD {obj.total_revenue}'
    total_revenue_display.short_description = 'Total Gross'

    def publisher_paid_display(self, obj):
        return format_html('<strong style="color:#198754;">USD {}</strong>', obj.publisher_paid)
    publisher_paid_display.short_description = 'Publisher Share (60%)'

    def pending_payout_display(self, obj):
        if obj.pending_payout > 0:
            return format_html('<strong style="color:#c9a227;">USD {}</strong>', obj.pending_payout)
        return 'USD 0.00'
    pending_payout_display.short_description = 'Pending Payout'


@admin.register(PlatformRevenue)
class PlatformRevenueAdmin(admin.ModelAdmin):
    list_display = ('total_transactions', 'total_gross', 'platform_share_display',
                    'total_publisher_cut', 'updated_at')
    readonly_fields = ('total_transactions', 'total_gross', 'total_platform_cut',
                       'total_publisher_cut', 'updated_at')

    def platform_share_display(self, obj):
        return format_html('<strong style="color:#c9a227;">USD {}</strong>', obj.total_platform_cut)
    platform_share_display.short_description = 'Platform Revenue (40%)'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display  = ('publisher', 'amount', 'currency', 'status', 'requested_at', 'processed_at')
    list_filter   = ('status', 'currency')
    search_fields = ('publisher__email', 'publisher__username')
    readonly_fields = ('requested_at',)
    actions = ['mark_paid']

    def mark_paid(self, request, queryset):
        from django.utils import timezone
        queryset.update(
            status='paid',
            processed_at=timezone.now(),
            processed_by=request.user
        )
    mark_paid.short_description = 'Mark selected payouts as Paid'
