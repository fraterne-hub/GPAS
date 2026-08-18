from django.contrib import admin
from .models import AIChatSession, AIChatMessage, AIChatFeedback


class AIChatMessageInline(admin.TabularInline):
    model       = AIChatMessage
    extra       = 0
    readonly_fields = ('role', 'content', 'confidence', 'enhanced', 'timestamp')
    can_delete  = False


@admin.register(AIChatSession)
class AIChatSessionAdmin(admin.ModelAdmin):
    list_display    = ('session_key', 'user', 'message_count', 'started_at', 'last_active')
    list_filter     = ('last_active',)
    search_fields   = ('session_key', 'user__email', 'user__username')
    readonly_fields = ('session_key', 'started_at', 'last_active')
    inlines         = [AIChatMessageInline]


@admin.register(AIChatMessage)
class AIChatMessageAdmin(admin.ModelAdmin):
    list_display    = ('session', 'role', 'content_preview', 'confidence', 'enhanced', 'timestamp')
    list_filter     = ('role', 'confidence', 'enhanced')
    search_fields   = ('content',)
    readonly_fields = ('session', 'role', 'content', 'sources', 'intents', 'confidence', 'enhanced', 'timestamp')

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = 'Content'


@admin.register(AIChatFeedback)
class AIChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ('message', 'rating', 'comment', 'submitted_at')
    list_filter  = ('rating',)
