from django.contrib import admin
from .models import FAQCategory, FAQ, SupportTicket, TicketMessage


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display  = ('question', 'category', 'is_published', 'order')
    list_filter   = ('category', 'is_published')
    search_fields = ('question', 'answer')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display  = ('ticket_number', 'subject', 'status', 'priority', 'created_by', 'assigned_to', 'created_at')
    list_filter   = ('status', 'priority', 'category')
    search_fields = ('ticket_number', 'subject', 'created_by__email')
    readonly_fields = ('ticket_number',)


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_staff', 'created_at')
