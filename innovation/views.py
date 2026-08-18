"""
GARL Innovation Hub Views
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import InnovationProject, ProjectCategory, ProjectLike, ProjectComment
from core.utils import paginate_queryset, log_action, track_activity
from notifications.models import send_notification


def innovation_home(request):
    categories  = ProjectCategory.objects.filter(is_active=True)
    featured    = InnovationProject.objects.filter(status='published', is_featured=True).order_by('-published_at')[:6]
    recent      = InnovationProject.objects.filter(status='published').order_by('-published_at')[:12]
    project_types = InnovationProject.ProjectType.choices
    return render(request, 'innovation/home.html', {
        'categories':    categories,
        'featured':      featured,
        'recent':        recent,
        'project_types': project_types,
    })


def project_list(request):
    projects = InnovationProject.objects.filter(status='published')

    q            = request.GET.get('q', '')
    category_id  = request.GET.get('category')
    project_type = request.GET.get('type')

    if q:
        projects = projects.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(technologies__icontains=q)
        )
    if category_id:
        projects = projects.filter(categories__id=category_id)
    if project_type:
        projects = projects.filter(project_type=project_type)

    projects     = projects.select_related('submitted_by').order_by('-published_at')
    page_obj     = paginate_queryset(projects, request, 12)
    categories   = ProjectCategory.objects.filter(is_active=True)

    return render(request, 'innovation/project_list.html', {
        'page_obj':      page_obj,
        'categories':    categories,
        'project_types': InnovationProject.ProjectType.choices,
        'q':             q,
    })


def project_detail(request, slug):
    project  = get_object_or_404(InnovationProject, slug=slug, status='published')
    InnovationProject.objects.filter(pk=project.pk).update(view_count=project.view_count + 1)
    track_activity(request.user, 'project', project.pk, project.title)
    members  = project.members.all()
    comments = project.comments.filter(is_approved=True).select_related('author')

    user_liked = False
    if request.user.is_authenticated:
        user_liked = ProjectLike.objects.filter(project=project, user=request.user).exists()

    return render(request, 'innovation/project_detail.html', {
        'project':    project,
        'members':    members,
        'comments':   comments,
        'user_liked': user_liked,
    })


@login_required
def submit_project(request):
    from .forms import InnovationProjectForm
    if request.method == 'POST':
        form = InnovationProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.submitted_by = request.user
            project.status       = InnovationProject.StatusChoice.SUBMITTED
            project.save()
            form.save_m2m()
            log_action(request, 'create', InnovationProject, project.pk, project.title, 'Project submitted')
            messages.success(request, 'Project submitted for moderation.')
            return redirect('innovation:project_detail', slug=project.slug)
    else:
        form = InnovationProjectForm()
    return render(request, 'innovation/submit.html', {'form': form})


@login_required
@require_POST
def toggle_like(request, pk):
    project = get_object_or_404(InnovationProject, pk=pk, status='published')
    like, created = ProjectLike.objects.get_or_create(project=project, user=request.user)
    if not created:
        like.delete()
        InnovationProject.objects.filter(pk=pk).update(like_count=project.like_count - 1)
        liked = False
    else:
        InnovationProject.objects.filter(pk=pk).update(like_count=project.like_count + 1)
        liked = True
    project.refresh_from_db(fields=['like_count'])
    return JsonResponse({'liked': liked, 'count': project.like_count})


@login_required
def moderate_projects(request):
    if not request.user.is_any_admin():
        messages.error(request, 'Admin access required.')
        return redirect('dashboard:home')
    pending = InnovationProject.objects.filter(
        status__in=['submitted', 'pending']
    ).select_related('submitted_by').order_by('-created_at')
    return render(request, 'innovation/moderate.html', {'projects': pending})


@login_required
def approve_project(request, pk):
    if not request.user.is_any_admin():
        messages.error(request, 'Admin access required.')
        return redirect('dashboard:home')
    project = get_object_or_404(InnovationProject, pk=pk)
    project.status       = InnovationProject.StatusChoice.PUBLISHED
    project.published_at = timezone.now()
    project.moderated_by = request.user
    project.save(update_fields=['status', 'published_at', 'moderated_by'])
    log_action(request, 'approve', InnovationProject, project.pk, project.title, 'Project approved')
    if project.submitted_by:
        send_notification(
            project.submitted_by, 'proj_approved',
            'Project Approved',
            f'Your project "{project.title}" has been approved and published.',
            link=f'/innovation/projects/{project.slug}/'
        )
    messages.success(request, 'Project approved and published.')
    return redirect('innovation:moderate')
