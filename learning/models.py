"""
GARL Learning Center Models
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from core.models import Subject, Tag


class CourseCategory(models.Model):
    name        = models.CharField(max_length=200, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=100, blank=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Course Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    class LevelChoice(models.TextChoices):
        BEGINNER     = 'beginner',     _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED     = 'advanced',     _('Advanced')

    title           = models.CharField(max_length=400)
    slug            = models.SlugField(max_length=420, unique=True, blank=True)
    description     = models.TextField()
    objectives      = models.TextField(blank=True)
    requirements    = models.TextField(blank=True)
    cover_image     = models.ImageField(upload_to='courses/covers/', null=True, blank=True)
    category        = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    subjects        = models.ManyToManyField(Subject, blank=True)
    tags            = models.ManyToManyField(Tag, blank=True)
    instructor      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='taught_courses'
    )
    level           = models.CharField(max_length=15, choices=LevelChoice.choices, default=LevelChoice.BEGINNER)
    language        = models.CharField(max_length=50, default='English')
    duration_hours  = models.FloatField(null=True, blank=True)
    is_published    = models.BooleanField(default=False, db_index=True)
    is_featured     = models.BooleanField(default=False)
    is_free         = models.BooleanField(default=True)
    has_certificate = models.BooleanField(default=False)
    enrollment_count= models.PositiveIntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['is_published', '-created_at'])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:400]
        super().save(*args, **kwargs)


class Lesson(models.Model):
    class ContentType(models.TextChoices):
        VIDEO    = 'video',    _('Video')
        TEXT     = 'text',     _('Text / Article')
        PDF      = 'pdf',      _('PDF Document')
        QUIZ     = 'quiz',     _('Quiz')
        LAB      = 'lab',      _('Virtual Lab')
        EXTERNAL = 'external', _('External Link')

    course          = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title           = models.CharField(max_length=300)
    content_type    = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.TEXT)
    content         = models.TextField(blank=True)
    video_url       = models.URLField(blank=True)
    file            = models.FileField(upload_to='learning/lessons/', null=True, blank=True)
    external_url    = models.URLField(blank=True)
    duration_minutes= models.PositiveSmallIntegerField(null=True, blank=True)
    order           = models.PositiveSmallIntegerField(default=1)
    is_preview      = models.BooleanField(default=False)
    is_published    = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering        = ['order']
        unique_together = ('course', 'order')

    def __str__(self):
        return f'{self.course.title} — {self.title}'


class Enrollment(models.Model):
    class StatusChoice(models.TextChoices):
        ACTIVE      = 'active',    _('Active')
        COMPLETED   = 'completed', _('Completed')
        DROPPED     = 'dropped',   _('Dropped')

    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status      = models.CharField(max_length=15, choices=StatusChoice.choices, default=StatusChoice.ACTIVE)
    progress    = models.PositiveSmallIntegerField(default=0)  # percentage 0–100
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at= models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering        = ['-enrolled_at']

    def __str__(self):
        return f'{self.student.username} enrolled in {self.course.title[:60]}'


class LessonProgress(models.Model):
    enrollment  = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson      = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    completed_at= models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f'{self.enrollment} — {self.lesson.title}'


class Quiz(models.Model):
    lesson          = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz', null=True, blank=True)
    course          = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title           = models.CharField(max_length=300)
    description     = models.TextField(blank=True)
    pass_percentage = models.PositiveSmallIntegerField(default=70)
    time_limit_mins = models.PositiveSmallIntegerField(null=True, blank=True)
    is_published    = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.course.title} — {self.title}'


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = 'mcq',       _('Multiple Choice')
        TRUE_FALSE      = 'tf',        _('True / False')
        SHORT_ANSWER    = 'short',     _('Short Answer')

    quiz        = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text        = models.TextField()
    q_type      = models.CharField(max_length=10, choices=QuestionType.choices, default=QuestionType.MULTIPLE_CHOICE)
    order       = models.PositiveSmallIntegerField(default=1)
    points      = models.PositiveSmallIntegerField(default=1)
    explanation = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:100]


class Answer(models.Model):
    question    = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text        = models.CharField(max_length=500)
    is_correct  = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.text[:80]} ({"correct" if self.is_correct else "wrong"})'


class QuizAttempt(models.Model):
    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz        = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score       = models.FloatField(default=0)
    max_score   = models.FloatField(default=0)
    passed      = models.BooleanField(default=False)
    started_at  = models.DateTimeField(auto_now_add=True)
    completed_at= models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.student.username} — {self.quiz.title} ({self.score}/{self.max_score})'


class Certificate(models.Model):
    student         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course          = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    enrollment      = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=100, unique=True)
    issued_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f'Certificate: {self.student.username} — {self.course.title[:60]}'
