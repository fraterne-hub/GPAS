from django.contrib import admin
from .models import ResearchCategory, ResearchPaper, ResearchProject, ResearchDataset, ResearchTopic, Citation


@admin.register(ResearchCategory)
class ResearchCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ResearchPaper)
class ResearchPaperAdmin(admin.ModelAdmin):
    list_display  = ('title', 'status', 'publication_year', 'download_count', 'created_at')
    list_filter   = ('status', 'language')
    search_fields = ('title', 'abstract', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display  = ('title', 'status', 'lead_researcher', 'start_date')
    list_filter   = ('status', 'is_public')
    search_fields = ('title', 'description')


@admin.register(ResearchDataset)
class ResearchDatasetAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_format', 'is_public', 'download_count', 'created_at')


@admin.register(ResearchTopic)
class ResearchTopicAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'paper_count')
    prepopulated_fields = {'slug': ('name',)}
