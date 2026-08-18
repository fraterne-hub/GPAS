from django.contrib import admin
from .models import DailyStats, ResourceView


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'new_users', 'active_users', 'new_publications',
                    'new_courses', 'downloads', 'searches')
    ordering = ('-date',)


@admin.register(ResourceView)
class ResourceViewAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'object_title', 'viewed_at')
    list_filter  = ('content_type',)
