"""
GARL Research Center Views
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone

from .models import ResearchPaper, ResearchProject, ResearchCategory, ResearchDataset, ResearchTopic
from core.utils import track_activity, paginate_queryset, log_action
from core.decorators import publisher_required


def research_home(request):
    categories      = ResearchCategory.objects.filter(is_active=True, parent=None)
    latest_papers   = ResearchPaper.objects.filter(status='published').order_by('-published_at')[:8]
    active_projects = ResearchProject.objects.filter(status='ongoing', is_public=True).order_by('-created_at')[:6]
    topics          = ResearchTopic.objects.order_by('-paper_count')[:20]
    return render(request, 'research/home.html', {
        'categories':       categories,
        'latest_papers':    latest_papers,
        'active_projects':  active_projects,
        'topics':           topics,
    })


def paper_list(request):
    papers = ResearchPaper.objects.filter(status='published')

    q = request.GET.get('q', '')
    if q:
        papers = papers.filter(
            Q(title__icontains=q) | Q(abstract__icontains=q) | Q(keywords__icontains=q)
        )

    category_id = request.GET.get('category')
    if category_id:
        papers = papers.filter(categories__id=category_id)

    year = request.GET.get('year')
    if year:
        papers = papers.filter(publication_year=year)

    papers   = papers.select_related('created_by').order_by('-published_at')
    page_obj = paginate_queryset(papers, request, 15)
    categories = ResearchCategory.objects.filter(is_active=True)

    return render(request, 'research/paper_list.html', {
        'page_obj':   page_obj,
        'categories': categories,
        'q':          q,
    })


def paper_detail(request, slug):
    paper = get_object_or_404(ResearchPaper, slug=slug, status='published')
    ResearchPaper.objects.filter(pk=paper.pk).update(view_count=paper.view_count + 1)
    track_activity(request.user, 'paper', paper.pk, paper.title)

    # Related papers by category
    related = ResearchPaper.objects.filter(
        categories__in=paper.categories.all(), status='published'
    ).exclude(pk=paper.pk).distinct()[:4]

    return render(request, 'research/paper_detail.html', {
        'paper':   paper,
        'related': related,
    })


@login_required
def paper_download(request, pk):
    paper = get_object_or_404(ResearchPaper, pk=pk, status='published')
    if not paper.file:
        messages.error(request, 'No file available for download.')
        return redirect('research:paper_detail', slug=paper.slug)

    ResearchPaper.objects.filter(pk=pk).update(download_count=paper.download_count + 1)
    log_action(request, 'download', ResearchPaper, paper.pk, paper.title, 'Paper downloaded')

    from django.http import FileResponse
    return FileResponse(paper.file.open(), as_attachment=True, filename=paper.file.name.split('/')[-1])


def project_list(request):
    projects = ResearchProject.objects.filter(is_public=True)
    q = request.GET.get('q', '')
    if q:
        projects = projects.filter(Q(title__icontains=q) | Q(description__icontains=q))
    projects = projects.select_related('lead_researcher').order_by('-created_at')
    page_obj = paginate_queryset(projects, request, 12)
    return render(request, 'research/project_list.html', {'page_obj': page_obj, 'q': q})


def project_detail(request, slug):
    project = get_object_or_404(ResearchProject, slug=slug, is_public=True)
    track_activity(request.user, 'project', project.pk, project.title)
    return render(request, 'research/project_detail.html', {'project': project})


@login_required
@publisher_required
def submit_paper(request):
    from .forms import ResearchPaperForm
    if request.method == 'POST':
        form = ResearchPaperForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.created_by = request.user
            paper.status = 'submitted'
            paper.save()
            form.save_m2m()
            log_action(request, 'create', ResearchPaper, paper.pk, paper.title, 'Paper submitted')
            messages.success(request, 'Research paper submitted successfully.')
            return redirect('research:paper_detail', slug=paper.slug)
    else:
        form = ResearchPaperForm()
    return render(request, 'research/submit_paper.html', {'form': form})
