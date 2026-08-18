"""
GARL Global Search Views
"""

from django.shortcuts import render
from django.db.models import Q

from publishing.models import Publication, Book, Journal
from research.models import ResearchPaper, ResearchProject
from learning.models import Course
from innovation.models import InnovationProject
from health_science.models import HealthResource
from events.models import Event
from community.models import Institution
from accounts.models import User
from core.utils import paginate_queryset


def global_search(request):
    q           = request.GET.get('q', '').strip()
    content_type = request.GET.get('type', 'all')

    results = {
        'publications': [],
        'books':        [],
        'papers':       [],
        'courses':      [],
        'projects':     [],
        'innovations':  [],
        'events':       [],
        'institutions': [],
        'health':       [],
        'researchers':  [],
    }
    total = 0

    if q:
        if content_type in ('all', 'publications'):
            pubs = Publication.objects.filter(
                status='published'
            ).filter(Q(title__icontains=q) | Q(abstract__icontains=q) | Q(keywords__icontains=q))[:10]
            results['publications'] = list(pubs)
            total += len(results['publications'])

        if content_type in ('all', 'books'):
            books = Book.objects.filter(is_published=True).filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )[:10]
            results['books'] = list(books)
            total += len(results['books'])

        if content_type in ('all', 'papers'):
            papers = ResearchPaper.objects.filter(status='published').filter(
                Q(title__icontains=q) | Q(abstract__icontains=q) | Q(keywords__icontains=q)
            )[:10]
            results['papers'] = list(papers)
            total += len(results['papers'])

        if content_type in ('all', 'courses'):
            courses = Course.objects.filter(is_published=True).filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )[:10]
            results['courses'] = list(courses)
            total += len(results['courses'])

        if content_type in ('all', 'innovations'):
            innovations = InnovationProject.objects.filter(status='published').filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(technologies__icontains=q)
            )[:10]
            results['innovations'] = list(innovations)
            total += len(results['innovations'])

        if content_type in ('all', 'events'):
            events = Event.objects.filter(is_published=True).filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )[:10]
            results['events'] = list(events)
            total += len(results['events'])

        if content_type in ('all', 'institutions'):
            institutions = Institution.objects.filter(is_published=True).filter(
                Q(name__icontains=q) | Q(description__icontains=q) | Q(country__icontains=q)
            )[:10]
            results['institutions'] = list(institutions)
            total += len(results['institutions'])

        if content_type in ('all', 'health'):
            health = HealthResource.objects.filter(is_published=True).filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )[:10]
            results['health'] = list(health)
            total += len(results['health'])

        if content_type in ('all', 'researchers'):
            researchers = User.objects.filter(role='researcher', is_active=True).filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) |
                Q(profile__institution__icontains=q) | Q(profile__field_of_study__icontains=q)
            ).select_related('profile')[:10]
            results['researchers'] = list(researchers)
            total += len(results['researchers'])

    return render(request, 'search/results.html', {
        'q':            q,
        'results':      results,
        'total':        total,
        'content_type': content_type,
    })
