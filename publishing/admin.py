from django.contrib import admin
from .models import PublicationType, Journal, JournalIssue, Publication, PublicationAuthor, Submission, Review, Revision, Book


@admin.register(PublicationType)
class PublicationTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ('title', 'issn', 'is_open_access', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'issn')


@admin.register(JournalIssue)
class JournalIssueAdmin(admin.ModelAdmin):
    list_display = ('journal', 'volume', 'issue', 'year')


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display  = ('title', 'status', 'pub_type', 'created_by', 'created_at', 'published_at')
    list_filter   = ('status', 'pub_type', 'is_open_access')
    search_fields = ('title', 'abstract')
    prepopulated_fields = {'slug': ('title',)}
    actions = ['approve_publications', 'reject_publications']

    def approve_publications(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='published', published_at=timezone.now())
    approve_publications.short_description = 'Approve and publish selected publications'

    def reject_publications(self, request, queryset):
        queryset.update(status='rejected')
    reject_publications.short_description = 'Reject selected publications'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('publication', 'submitted_by', 'assigned_editor', 'submitted_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'reviewer', 'recommendation', 'is_completed', 'assigned_at')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ('title', 'publisher', 'year', 'is_free', 'is_published', 'download_count')
    search_fields = ('title', 'isbn', 'publisher')
    prepopulated_fields = {'slug': ('title',)}
