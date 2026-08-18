from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    paginator     = Paginator(notifications, 20)
    page          = request.GET.get('page', 1)
    page_obj      = paginator.get_page(page)
    unread_count  = notifications.filter(is_read=False).count()
    return render(request, 'notifications/list.html', {
        'page_obj':    page_obj,
        'unread_count': unread_count,
    })


@login_required
@require_POST
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.mark_read()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
def notification_detail(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.mark_read()
    if notif.link:
        return redirect(notif.link)
    return render(request, 'notifications/detail.html', {'notification': notif})
