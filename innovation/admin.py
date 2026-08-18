from django.contrib import admin
from .models import ProjectCategory, InnovationProject, ProjectMember, ProjectLike, ProjectComment


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(InnovationProject)
class InnovationProjectAdmin(admin.ModelAdmin):
    list_display  = ('title', 'project_type', 'status', 'submitted_by', 'is_featured', 'created_at')
    list_filter   = ('status', 'project_type', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    actions       = ['publish_projects', 'reject_projects']

    def publish_projects(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='published', published_at=timezone.now())
    publish_projects.short_description = 'Publish selected projects'

    def reject_projects(self, request, queryset):
        queryset.update(status='rejected')
    reject_projects.short_description = 'Reject selected projects'
