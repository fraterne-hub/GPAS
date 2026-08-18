from django.contrib import admin
from .models import CourseCategory, Course, Lesson, Enrollment, Quiz, Question, Answer, Certificate


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'level', 'is_published', 'is_featured', 'enrollment_count')
    list_filter  = ('level', 'is_published', 'is_free', 'has_certificate')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'content_type', 'order', 'is_published')
    list_filter  = ('content_type', 'is_published')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress', 'enrolled_at')
    list_filter  = ('status',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'pass_percentage', 'is_published')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'certificate_number', 'issued_at')
    search_fields = ('certificate_number', 'student__email')
