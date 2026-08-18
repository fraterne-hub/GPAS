from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from django.utils import timezone

from .models import FAQ, FAQCategory, SupportTicket, TicketMessage
from core.utils import paginate_queryset, log_action
from notifications.models import send_notification


def support_home(request):
    faq_categories = FAQCategory.objects.filter(is_active=True).prefetch_related(
        Prefetch('faqs', queryset=FAQ.objects.filter(is_published=True))
    )
    return render(request, 'support/home.html', {'faq_categories': faq_categories})


def faq_list(request):
    categories = FAQCategory.objects.filter(is_active=True).prefetch_related(
        Prefetch('faqs', queryset=FAQ.objects.filter(is_published=True))
    )
    return render(request, 'support/faq.html', {'categories': categories})


@login_required
def create_ticket(request):
    from .forms import SupportTicketForm
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            log_action(request, 'create', SupportTicket, ticket.pk, str(ticket), 'Support ticket created')
            messages.success(request, f'Ticket {ticket.ticket_number} submitted successfully.')
            return redirect('support:ticket_detail', pk=ticket.pk)
    else:
        form = SupportTicketForm()
    return render(request, 'support/create_ticket.html', {'form': form})


@login_required
def my_tickets(request):
    tickets = SupportTicket.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'support/my_tickets.html', {'tickets': tickets})


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)

    # Only owner or staff can view
    if ticket.created_by != request.user and not request.user.is_any_admin():
        messages.error(request, 'Permission denied.')
        return redirect('support:my_tickets')

    ticket_messages = ticket.messages.all()
    form = None

    if request.method == 'POST':
        from .forms import TicketReplyForm
        form = TicketReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ticket   = ticket
            reply.author   = request.user
            reply.is_staff = request.user.is_any_admin()
            reply.save()
            if ticket.status == 'waiting' and not reply.is_staff:
                ticket.status = 'in_progress'
                ticket.save(update_fields=['status'])
            messages.success(request, 'Reply submitted.')
            return redirect('support:ticket_detail', pk=pk)
    else:
        from .forms import TicketReplyForm
        form = TicketReplyForm()

    return render(request, 'support/ticket_detail.html', {
        'ticket':          ticket,
        'ticket_messages': ticket_messages,
        'form':            form,
    })
