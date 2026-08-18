from django.contrib import admin
from .models import InstitutionType, Institution, Department, InstitutionMember, ResearchNetwork, CollaborationRequest


@admin.register(InstitutionType)
class InstitutionTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display  = ('name', 'institution_type', 'country', 'is_verified', 'is_published')
    list_filter   = ('institution_type', 'is_verified', 'country')
    search_fields = ('name', 'city', 'country')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'institution')
    search_fields = ('name', 'institution__name')


@admin.register(ResearchNetwork)
class ResearchNetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
