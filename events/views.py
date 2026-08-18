from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Event, EventCategory, EventRegistration
from core.utils import paginate_queryset, log_action
from notifications.models import send_notification


def event_list(request):
    events = Event.objects.filter(is_published=True)

    q        = request.GET.get('q', '')
    etype    = request.GET.get('type')
    upcoming = request.GET.get('upcoming')

    if q:
        events = events.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if etype:
        events = events.filter(event_type=etype)
    if upcoming:
        events = events.filter(start_date__gte=timezone.now())

    events   = events.order_by('start_date')
    page_obj = paginate_queryset(events, request, 12)
    categories = EventCategory.objects.filter(is_active=True)

    return render(request, 'events/list.html', {
        'page_obj':    page_obj,
        'categories':  categories,
        'event_types': Event.EventType.choices,
        'q':           q,
    })


def event_detail(request, slug):
    event   = get_object_or_404(Event, slug=slug, is_published=True)
    speakers = event.speakers.all()
    is_registered = False
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(event=event, user=request.user).exists()

    return render(request, 'events/detail.html', {
        'event':         event,
        'speakers':      speakers,
        'is_registered': is_registered,
    })


@login_required
def register_event(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)

    if event.is_full:
        messages.warning(request, 'This event is fully booked.')
        return redirect('events:detail', slug=slug)

    if event.registration_deadline and timezone.now() > event.registration_deadline:
        messages.warning(request, 'Registration deadline has passed.')
        return redirect('events:detail', slug=slug)

    reg, created = EventRegistration.objects.get_or_create(event=event, user=request.user)
    if created:
        log_action(request, 'create', EventRegistration, reg.pk, str(reg), 'Event registration')
        send_notification(
            request.user, 'event_reg',
            'Event Registration',
            f'You have registered for "{event.title}".',
            link=f'/events/{event.slug}/'
        )
        messages.success(request, f'You have successfully registered for {event.title}.')
    else:
        messages.info(request, 'You are already registered for this event.')

    return redirect('events:detail', slug=slug)


@login_required
def my_events(request):
    registrations = EventRegistration.objects.filter(
        user=request.user
    ).select_related('event').order_by('-registered_at')
    return render(request, 'events/my_events.html', {'registrations': registrations})
