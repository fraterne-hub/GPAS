from django.contrib import admin
from .models import EventCategory, Event, Speaker, EventRegistration


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ('title', 'event_type', 'start_date', 'is_online', 'is_published', 'registration_count')
    list_filter   = ('event_type', 'is_online', 'is_free', 'is_published')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'registered_at')
    list_filter  = ('status',)
