"""
GARL Learning Center Views
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
import uuid

from .models import Course, Lesson, Enrollment, LessonProgress, Quiz, Certificate, CourseCategory
from core.utils import paginate_queryset, log_action, track_activity
from notifications.models import send_notification


def learning_home(request):
    categories = CourseCategory.objects.filter(is_active=True)
    featured   = Course.objects.filter(is_published=True, is_featured=True).order_by('-created_at')[:6]
    recent     = Course.objects.filter(is_published=True).order_by('-created_at')[:8]
    return render(request, 'learning/home.html', {
        'categories': categories,
        'featured':   featured,
        'recent':     recent,
    })


def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('instructor', 'category')

    q           = request.GET.get('q', '')
    category_id = request.GET.get('category')
    level       = request.GET.get('level')

    if q:
        courses = courses.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category_id:
        courses = courses.filter(category_id=category_id)
    if level:
        courses = courses.filter(level=level)

    courses    = courses.order_by('-created_at')
    page_obj   = paginate_queryset(courses, request, 12)
    categories = CourseCategory.objects.filter(is_active=True)

    return render(request, 'learning/course_list.html', {
        'page_obj':   page_obj,
        'categories': categories,
        'levels':     Course.LevelChoice.choices,
        'q':          q,
    })


def course_detail(request, slug):
    course  = get_object_or_404(Course, slug=slug, is_published=True)
    lessons = course.lessons.filter(is_published=True).order_by('order')
    track_activity(request.user, 'course', course.pk, course.title)

    is_enrolled = False
    enrollment  = None
    if request.user.is_authenticated:
        enrollment  = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None

    return render(request, 'learning/course_detail.html', {
        'course':      course,
        'lessons':     lessons,
        'is_enrolled': is_enrolled,
        'enrollment':  enrollment,
    })


@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course
    )
    if created:
        Course.objects.filter(pk=course.pk).update(enrollment_count=course.enrollment_count + 1)
        log_action(request, 'create', Enrollment, enrollment.pk, str(enrollment), 'Course enrollment')
        send_notification(
            request.user, 'enrolled',
            'Course Enrollment',
            f'You have successfully enrolled in "{course.title}".',
            link=f'/learning/courses/{course.slug}/'
        )
        messages.success(request, f'Successfully enrolled in {course.title}.')
    else:
        messages.info(request, 'You are already enrolled in this course.')
    return redirect('learning:lesson', course_slug=course.slug, lesson_order=1)


@login_required
def lesson_view(request, course_slug, lesson_order):
    course   = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson   = get_object_or_404(Lesson, course=course, order=lesson_order, is_published=True)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)

    # Mark lesson complete
    lp, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment, lesson=lesson,
        defaults={'is_complete': True, 'completed_at': timezone.now()}
    )
    if not lp.is_complete:
        lp.is_complete  = True
        lp.completed_at = timezone.now()
        lp.save()

    # Update course progress
    total   = course.lessons.filter(is_published=True).count()
    done    = enrollment.lesson_progress.filter(is_complete=True).count()
    progress = int((done / total) * 100) if total > 0 else 0
    Enrollment.objects.filter(pk=enrollment.pk).update(progress=progress)

    # Check completion
    if progress >= 100 and enrollment.status != 'completed':
        Enrollment.objects.filter(pk=enrollment.pk).update(status='completed', completed_at=timezone.now())
        # Issue certificate if course has it
        if course.has_certificate:
            cert_number = f'GARL-{course.pk}-{request.user.pk}-{uuid.uuid4().hex[:8].upper()}'
            Certificate.objects.get_or_create(
                student=request.user, course=course,
                defaults={'enrollment': enrollment, 'certificate_number': cert_number}
            )
            send_notification(
                request.user, 'certificate',
                'Certificate Issued',
                f'Congratulations! Your certificate for "{course.title}" is ready.',
                link='/dashboard/certificates/'
            )

    prev_lesson = Lesson.objects.filter(course=course, order__lt=lesson_order, is_published=True).order_by('-order').first()
    next_lesson = Lesson.objects.filter(course=course, order__gt=lesson_order, is_published=True).order_by('order').first()

    return render(request, 'learning/lesson.html', {
        'course':      course,
        'lesson':      lesson,
        'enrollment':  enrollment,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'progress':    progress,
    })


@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course').order_by('-enrolled_at')
    return render(request, 'learning/my_courses.html', {'enrollments': enrollments})


@login_required
def my_certificates(request):
    certificates = Certificate.objects.filter(student=request.user).select_related('course').order_by('-issued_at')
    return render(request, 'learning/certificates.html', {'certificates': certificates})
