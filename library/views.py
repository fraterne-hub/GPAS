from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import LibraryResource, LibraryCollection, Download
from core.utils import paginate_queryset, log_action, get_client_ip, track_activity


def library_home(request):
    collections = LibraryCollection.objects.filter(is_active=True)
    recent      = LibraryResource.objects.filter(is_published=True).order_by('-created_at')[:8]
    types       = LibraryResource.ResourceType.choices
    return render(request, 'library/home.html', {
        'collections': collections,
        'recent':      recent,
        'types':       types,
    })


def resource_list(request):
    resources = LibraryResource.objects.filter(is_published=True)

    q           = request.GET.get('q', '')
    rtype       = request.GET.get('type')
    collection  = request.GET.get('collection')

    if q:
        resources = resources.filter(
            Q(title__icontains=q) | Q(author__icontains=q) |
            Q(isbn__icontains=q) | Q(description__icontains=q)
        )
    if rtype:
        resources = resources.filter(resource_type=rtype)
    if collection:
        resources = resources.filter(collection_id=collection)

    resources   = resources.order_by('-created_at')
    page_obj    = paginate_queryset(resources, request, 20)
    collections = LibraryCollection.objects.filter(is_active=True)

    return render(request, 'library/resource_list.html', {
        'page_obj':    page_obj,
        'collections': collections,
        'types':       LibraryResource.ResourceType.choices,
        'q':           q,
    })


def resource_detail(request, pk):
    resource = get_object_or_404(LibraryResource, pk=pk, is_published=True)
    LibraryResource.objects.filter(pk=pk).update(view_count=resource.view_count + 1)
    track_activity(request.user, 'book', resource.pk, resource.title)
    return render(request, 'library/resource_detail.html', {'resource': resource})


@login_required
def resource_download(request, pk):
    resource = get_object_or_404(LibraryResource, pk=pk, is_published=True)

    if resource.access_level == 'restricted':
        messages.error(request, 'This resource is restricted.')
        return redirect('library:resource_detail', pk=pk)

    if not resource.file and not resource.external_url:
        messages.error(request, 'No file available.')
        return redirect('library:resource_detail', pk=pk)

    LibraryResource.objects.filter(pk=pk).update(download_count=resource.download_count + 1)
    Download.objects.create(user=request.user, resource=resource, ip_address=get_client_ip(request))
    log_action(request, 'download', LibraryResource, resource.pk, resource.title, 'Library resource downloaded')

    if resource.external_url:
        return redirect(resource.external_url)

    from django.http import FileResponse
    return FileResponse(resource.file.open(), as_attachment=True, filename=resource.file.name.split('/')[-1])
