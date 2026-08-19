from django.contrib import admin
from django.contrib import admin
from django.utils.html import format_html
from .models import Subject, Tag, Announcement, Bookmark, ActivityHistory, PlatformStatistic, SiteSettings, NewsletterSubscriber


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ('name', 'parent', 'is_active', 'order')
    list_filter   = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'is_active', 'is_pinned', 'created_at')
    list_filter  = ('type', 'is_active', 'is_pinned')
    search_fields = ('title', 'content')


@admin.register(PlatformStatistic)
class PlatformStatisticAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Singleton admin — edit the single GARL site settings record.
    Admins can upload: hero banner, logos, promo images, and update social links.
    """

    fieldsets = (
        ('🖼️  Hero Banner', {
            'description': 'Upload a background image for the homepage hero section.',
            'fields': ('hero_banner', 'hero_title', 'hero_subtitle'),
        }),
        ('🔰  Site Logo & Favicon', {
            'fields': ('site_logo', 'site_logo_white', 'favicon'),
        }),
        ('🖼️  Promotional Images', {
            'description': 'Optional images shown in the homepage about/features section.',
            'fields': ('promo_image_1', 'promo_image_2', 'promo_image_3'),
        }),
        ('📝  About Text', {
            'fields': ('about_text',),
        }),
        ('🔗  Social Media Links', {
            'fields': ('social_twitter', 'social_linkedin', 'social_facebook', 'social_youtube'),
        }),
        ('📋  Meta', {
            'classes': ('collapse',),
            'fields': ('updated_at', 'updated_by'),
        }),
    )

    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Only allow adding if no record exists yet
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion of singleton

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        """Redirect from list to the single edit page automatically."""
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(
            reverse('admin:core_sitesettings_change', args=[obj.pk])
        )

    def banner_preview(self, obj):
        if obj.hero_banner:
            return format_html(
                '<img src="{}" style="max-height:120px;max-width:400px;border-radius:6px;" />',
                obj.hero_banner.url
            )
        return '—'
    banner_preview.short_description = 'Banner Preview'

    def logo_preview(self, obj):
        if obj.site_logo:
            return format_html(
                '<img src="{}" style="max-height:60px;max-width:200px;" />',
                obj.site_logo.url
            )
        return '—'
    logo_preview.short_description = 'Logo Preview'


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display    = ('email', 'name', 'is_active', 'subscribed_at', 'ip_address')
    list_filter     = ('is_active',)
    search_fields   = ('email', 'name')
    readonly_fields = ('subscribed_at', 'ip_address')
    actions         = ['deactivate_selected', 'reactivate_selected']

    def deactivate_selected(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_active=False, unsubscribed_at=timezone.now())
    deactivate_selected.short_description = 'Deactivate selected subscribers'

    def reactivate_selected(self, request, queryset):
        queryset.update(is_active=True, unsubscribed_at=None)
    reactivate_selected.short_description = 'Re-activate selected subscribers'
