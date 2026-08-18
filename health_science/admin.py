from django.contrib import admin
from .models import HealthCategory, HealthResource


@admin.register(HealthCategory)
class HealthCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'discipline', 'is_active', 'order')
    list_filter  = ('discipline', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(HealthResource)
class HealthResourceAdmin(admin.ModelAdmin):
    list_display  = ('title', 'resource_type', 'category', 'is_published', 'download_count')
    list_filter   = ('resource_type', 'is_published', 'language')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
