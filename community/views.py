from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Institution, ResearchNetwork, CollaborationRequest
from accounts.models import User
from core.utils import paginate_queryset


def directory_home(request):
    institutions = Institution.objects.filter(is_published=True).order_by('name')[:8]
    researchers  = User.objects.filter(role='researcher', is_active=True).order_by('-date_joined')[:8]
    networks     = ResearchNetwork.objects.filter(is_public=True).order_by('name')[:6]
    return render(request, 'community/home.html', {
        'institutions': institutions,
        'researchers':  researchers,
        'networks':     networks,
    })


def institution_list(request):
    institutions = Institution.objects.filter(is_published=True)

    q           = request.GET.get('q', '')
    country     = request.GET.get('country')
    itype       = request.GET.get('type')

    if q:
        institutions = institutions.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(city__icontains=q)
        )
    if country:
        institutions = institutions.filter(country__icontains=country)
    if itype:
        institutions = institutions.filter(institution_type_id=itype)

    institutions = institutions.order_by('name')
    page_obj     = paginate_queryset(institutions, request, 20)

    return render(request, 'community/institution_list.html', {
        'page_obj': page_obj,
        'q':        q,
    })


def institution_detail(request, slug):
    institution = get_object_or_404(Institution, slug=slug, is_published=True)
    members     = institution.members.filter(is_active=True).select_related('user')[:20]
    departments = institution.departments.all()

    return render(request, 'community/institution_detail.html', {
        'institution': institution,
        'members':     members,
        'departments': departments,
    })


def researcher_list(request):
    researchers = User.objects.filter(role='researcher', is_active=True)
    q = request.GET.get('q', '')
    if q:
        researchers = researchers.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(profile__institution__icontains=q) | Q(profile__field_of_study__icontains=q)
        )
    researchers = researchers.select_related('profile').order_by('first_name')
    page_obj    = paginate_queryset(researchers, request, 20)
    return render(request, 'community/researcher_list.html', {
        'page_obj': page_obj,
        'q':        q,
    })
