from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

from .models import HealthCategory, HealthResource
from core.utils import paginate_queryset, log_action, track_activity


DISCIPLINES = HealthCategory.DisciplineChoice


def health_home(request):
    disciplines = [
        {'key': d.value, 'label': d.label} for d in DISCIPLINES
    ]
    categories  = HealthCategory.objects.filter(is_active=True, parent=None)
    recent      = HealthResource.objects.filter(is_published=True).order_by('-created_at')[:8]
    return render(request, 'health_science/home.html', {
        'disciplines': disciplines,
        'categories':  categories,
        'recent':      recent,
    })


def discipline_view(request, discipline):
    disc_choices = {d.value: d.label for d in DISCIPLINES}
    if discipline not in disc_choices:
        from django.http import Http404
        raise Http404

    categories = HealthCategory.objects.filter(discipline=discipline, is_active=True, parent=None)
    resources  = HealthResource.objects.filter(
        category__discipline=discipline, is_published=True
    ).order_by('-created_at')

    q = request.GET.get('q', '')
    if q:
        resources = resources.filter(Q(title__icontains=q) | Q(description__icontains=q))

    page_obj = paginate_queryset(resources, request, 15)
    return render(request, 'health_science/discipline.html', {
        'discipline':    discipline,
        'disc_label':    disc_choices[discipline],
        'categories':    categories,
        'disciplines_all': [(d.value, d.label) for d in DISCIPLINES],
        'page_obj':      page_obj,
        'q':             q,
    })


def resource_list(request):
    resources = HealthResource.objects.filter(is_published=True)
    q = request.GET.get('q', '')
    category  = request.GET.get('category')
    disc      = request.GET.get('discipline')
    rtype     = request.GET.get('type')

    if q:
        resources = resources.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category:
        resources = resources.filter(category_id=category)
    if disc:
        resources = resources.filter(category__discipline=disc)
    if rtype:
        resources = resources.filter(resource_type=rtype)

    resources  = resources.select_related('category').order_by('-created_at')
    page_obj   = paginate_queryset(resources, request, 15)
    categories = HealthCategory.objects.filter(is_active=True)

    return render(request, 'health_science/resource_list.html', {
        'page_obj':    page_obj,
        'categories':  categories,
        'disciplines': [(d.value, d.label) for d in DISCIPLINES],
        'types':       HealthResource.ResourceType.choices,
        'q':           q,
    })


def resource_detail(request, slug):
    resource = get_object_or_404(HealthResource, slug=slug, is_published=True)
    HealthResource.objects.filter(pk=resource.pk).update(view_count=resource.view_count + 1)
    track_activity(request.user, 'health', resource.pk, resource.title)
    related  = HealthResource.objects.filter(
        category=resource.category, is_published=True
    ).exclude(pk=resource.pk)[:4]
    return render(request, 'health_science/resource_detail.html', {
        'resource': resource,
        'related':  related,
    })


@login_required
def resource_download(request, pk):
    resource = get_object_or_404(HealthResource, pk=pk, is_published=True)
    if not resource.file:
        messages.error(request, 'No file available for download.')
        return redirect('health_science:resource_detail', slug=resource.slug)
    HealthResource.objects.filter(pk=pk).update(download_count=resource.download_count + 1)
    log_action(request, 'download', HealthResource, resource.pk, resource.title, 'Health resource downloaded')
    from django.http import FileResponse
    return FileResponse(resource.file.open(), as_attachment=True, filename=resource.file.name.split('/')[-1])
