from django.contrib import admin
from .models import LibraryCollection, LibraryResource, Download


@admin.register(LibraryCollection)
class LibraryCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')


@admin.register(LibraryResource)
class LibraryResourceAdmin(admin.ModelAdmin):
    list_display  = ('title', 'resource_type', 'access_level', 'is_published', 'download_count')
    list_filter   = ('resource_type', 'access_level', 'is_published')
    search_fields = ('title', 'author', 'isbn')
