"""
GARL Payments Views
━━━━━━━━━━━━━━━━━━
Handles: pricing display, checkout, mock payment processing,
         download gate, publisher dashboard, admin revenue dashboard.
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404, FileResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count

from .models import (
    ContentPrice, Purchase, AccessGrant,
    PublisherEarnings, PlatformRevenue, Payout,
    ContentType, PLATFORM_SHARE, PUBLISHER_SHARE,
)
from .emails import (
    send_buyer_receipt, send_publisher_sale_alert,
    send_owner_sale_alert, send_access_notification,
)
from core.decorators import admin_required


# ── Helper: check if user already has access ──────────────────────────────────
def user_has_access(user, content_type, object_id):
    """Return True if user is authenticated and has paid for or has free access."""
    if not user.is_authenticated:
        return False
    return AccessGrant.objects.filter(
        buyer=user, content_type=content_type, object_id=object_id
    ).exists()


def get_price_for_content(content_type, object_id):
    """Return ContentPrice for a piece of content, or None if not priced."""
    try:
        return ContentPrice.objects.get(
            content_type=content_type, object_id=object_id, is_active=True
        )
    except ContentPrice.DoesNotExist:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Checkout — display price and payment form
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def checkout(request, content_type, object_id):
    """Show the payment / checkout page for a content item."""
    if content_type not in [c.value for c in ContentType]:
        raise Http404

    price_obj = get_object_or_404(
        ContentPrice, content_type=content_type, object_id=object_id, is_active=True
    )

    # Already purchased
    if user_has_access(request.user, content_type, object_id):
        return redirect('payments:download', content_type=content_type,
                        object_id=object_id, transaction_id='existing')

    # Resolve content details
    content_title, content_url = _resolve_content(content_type, object_id)

    return render(request, 'payments/checkout.html', {
        'price_obj':     price_obj,
        'content_title': content_title,
        'content_type':  content_type,
        'object_id':     object_id,
        'platform_cut':  price_obj.platform_cut,
        'publisher_cut': price_obj.publisher_cut,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Process payment (mock — ready for real gateway integration)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def process_payment(request, content_type, object_id):
    """
    Process a payment.
    In production: integrate with Stripe, PayPal, Flutterwave, etc.
    This mock always succeeds for demo purposes.
    """
    price_obj = get_object_or_404(
        ContentPrice, content_type=content_type, object_id=object_id, is_active=True
    )

    if user_has_access(request.user, content_type, object_id):
        messages.info(request, _('You already have access to this content.'))
        return redirect('payments:download', content_type=content_type,
                        object_id=object_id, transaction_id='existing')

    # ── Create pending purchase ────────────────────────────────────────────
    purchase = Purchase.objects.create(
        buyer           = request.user,
        content_price   = price_obj,
        amount          = price_obj.price,
        currency        = price_obj.currency,
        platform_amount = price_obj.platform_cut,
        publisher_amount= price_obj.publisher_cut,
        payment_method  = request.POST.get('payment_method', 'card'),
        buyer_email     = request.user.email,
        status          = Purchase.StatusChoice.PENDING,
    )

    # ── Mock payment processing ────────────────────────────────────────────
    # In production: call payment gateway API here, check response,
    # then set status COMPLETED or FAILED based on gateway response.
    payment_successful = True   # ← Replace with real gateway call

    if payment_successful:
        purchase.complete()   # sets status=COMPLETED, creates AccessGrant

        # ── Update earnings ────────────────────────────────────────────────
        publisher = price_obj.owner
        earnings, _ = PublisherEarnings.objects.get_or_create(publisher=publisher)
        earnings.record_sale(price_obj.publisher_cut, price_obj.price)

        platform_rev = PlatformRevenue.get()
        platform_rev.record_sale(price_obj.price, price_obj.platform_cut, price_obj.publisher_cut)

        # ── Send all notification emails ───────────────────────────────────
        send_buyer_receipt(purchase)
        send_publisher_sale_alert(purchase)
        send_owner_sale_alert(purchase)

        messages.success(request, _(
            f'Payment successful! You can now access "{_resolve_content(content_type, object_id)[0]}".'
        ))
        return redirect('payments:receipt', transaction_id=purchase.transaction_id)
    else:
        purchase.status = Purchase.StatusChoice.FAILED
        purchase.save(update_fields=['status'])
        messages.error(request, _('Payment failed. Please try again.'))
        return redirect('payments:checkout', content_type=content_type, object_id=object_id)


# ──────────────────────────────────────────────────────────────────────────────
# Receipt page
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def receipt(request, transaction_id):
    purchase = get_object_or_404(
        Purchase, transaction_id=transaction_id, buyer=request.user
    )
    content_title, _ = _resolve_content(
        purchase.content_price.content_type,
        purchase.content_price.object_id
    )
    return render(request, 'payments/receipt.html', {
        'purchase':      purchase,
        'content_title': content_title,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Gated download / access
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def download_content(request, content_type, object_id, transaction_id):
    """
    Serve the file only if the user has paid (or content is free).
    Also sends access notification email to the content owner.
    """
    if content_type not in [c.value for c in ContentType]:
        raise Http404

    # Admins always get access
    if not (user_has_access(request.user, content_type, object_id) or request.user.is_any_admin()):
        messages.error(request, _('You need to purchase this content to download it.'))
        return redirect('payments:checkout', content_type=content_type, object_id=object_id)

    content_title, content_url = _resolve_content(content_type, object_id)
    file_obj  = _get_file(content_type, object_id)
    price_obj = get_price_for_content(content_type, object_id)

    # Send access notification to owner
    if price_obj:
        accessor_name = request.user.get_full_name() or request.user.username
        send_access_notification(
            content_owner=price_obj.owner,
            content_title=content_title,
            content_type=content_type.replace('_', ' ').title(),
            accessor_name=accessor_name,
        )

    if file_obj:
        from django.http import FileResponse
        try:
            return FileResponse(
                file_obj.open(),
                as_attachment=True,
                filename=file_obj.name.split('/')[-1]
            )
        except Exception:
            pass

    # No file — redirect to content page
    messages.success(request, _('Access granted. Redirecting to content.'))
    if content_url:
        return redirect(content_url)
    return redirect('publishing:publication_list')


# ──────────────────────────────────────────────────────────────────────────────
# Publisher Dashboard
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def publisher_dashboard(request):
    """Publisher sees their sales, earnings, and payout requests."""
    earnings, _ = PublisherEarnings.objects.get_or_create(publisher=request.user)

    # Recent transactions involving this publisher's content
    purchases = Purchase.objects.filter(
        content_price__owner=request.user,
        status=Purchase.StatusChoice.COMPLETED,
    ).select_related('buyer', 'content_price').order_by('-completed_at')[:20]

    # Payout history
    payouts = Payout.objects.filter(publisher=request.user).order_by('-requested_at')[:10]

    # Per-content breakdown
    content_stats = Purchase.objects.filter(
        content_price__owner=request.user,
        status=Purchase.StatusChoice.COMPLETED,
    ).values(
        'content_price__content_type', 'content_price__object_id'
    ).annotate(
        sale_count=Count('id'),
        total_earned=Sum('publisher_amount'),
        total_gross=Sum('amount'),
    ).order_by('-total_earned')

    # Resolve titles for stats
    for row in content_stats:
        title, _ = _resolve_content(row['content_price__content_type'], row['content_price__object_id'])
        row['content_title'] = title

    return render(request, 'payments/publisher_dashboard.html', {
        'earnings':       earnings,
        'purchases':      purchases,
        'payouts':        payouts,
        'content_stats':  content_stats,
        'platform_pct':   int(PLATFORM_SHARE * 100),
        'publisher_pct':  int(PUBLISHER_SHARE * 100),
    })


# ──────────────────────────────────────────────────────────────────────────────
# Request payout
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def request_payout(request):
    """Publisher requests a payout of their pending earnings."""
    earnings, _ = PublisherEarnings.objects.get_or_create(publisher=request.user)

    if earnings.pending_payout <= 0:
        messages.error(request, _('No pending earnings to withdraw.'))
        return redirect('payments:publisher_dashboard')

    amount          = earnings.pending_payout
    payment_details = request.POST.get('payment_details', '').strip()

    if not payment_details:
        messages.error(request, _('Please provide payment details (bank account or mobile money number).'))
        return redirect('payments:publisher_dashboard')

    Payout.objects.create(
        publisher       = request.user,
        amount          = amount,
        currency        = 'USD',
        payment_details = payment_details,
    )
    # Reset pending
    earnings.pending_payout = Decimal('0.00')
    earnings.save(update_fields=['pending_payout'])

    messages.success(request, _(
        f'Payout request of USD {amount} submitted. We will process it within 3-5 business days.'
    ))
    return redirect('payments:publisher_dashboard')


# ──────────────────────────────────────────────────────────────────────────────
# Admin: Revenue Dashboard (platform owner view)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@admin_required
def admin_revenue_dashboard(request):
    """Platform owner sees all revenue, transactions, and payout management."""
    platform_rev = PlatformRevenue.get()

    # Recent transactions
    recent_purchases = Purchase.objects.filter(
        status=Purchase.StatusChoice.COMPLETED
    ).select_related('buyer', 'content_price', 'content_price__owner').order_by('-completed_at')[:50]

    # Pending payout requests
    pending_payouts = Payout.objects.filter(
        status=Payout.StatusChoice.REQUESTED
    ).select_related('publisher').order_by('-requested_at')

    # Top publishers
    top_publishers = PublisherEarnings.objects.select_related('publisher').order_by('-total_revenue')[:10]

    # Revenue by content type
    by_type = Purchase.objects.filter(
        status=Purchase.StatusChoice.COMPLETED
    ).values('content_price__content_type').annotate(
        count=Count('id'),
        gross=Sum('amount'),
        platform=Sum('platform_amount'),
        publisher=Sum('publisher_amount'),
    ).order_by('-gross')

    return render(request, 'payments/admin_revenue.html', {
        'platform_rev':    platform_rev,
        'recent_purchases':recent_purchases,
        'pending_payouts': pending_payouts,
        'top_publishers':  top_publishers,
        'by_type':         by_type,
        'platform_pct':    int(PLATFORM_SHARE * 100),
        'publisher_pct':   int(PUBLISHER_SHARE * 100),
    })


# ──────────────────────────────────────────────────────────────────────────────
# Admin: approve payout
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@admin_required
@require_POST
def approve_payout(request, pk):
    payout = get_object_or_404(Payout, pk=pk)
    payout.status       = Payout.StatusChoice.PAID
    payout.processed_at = timezone.now()
    payout.processed_by = request.user
    payout.admin_note   = request.POST.get('note', '')
    payout.save()

    # Update publisher total paid
    earnings, _ = PublisherEarnings.objects.get_or_create(publisher=payout.publisher)
    earnings.total_paid_out += payout.amount
    earnings.save(update_fields=['total_paid_out'])

    # Notify publisher via email
    _send_payout_notification(payout, approved=True)
    messages.success(request, f'Payout of {payout.currency} {payout.amount} approved and marked as paid.')
    return redirect('payments:admin_revenue')


@login_required
@admin_required
@require_POST
def reject_payout(request, pk):
    payout = get_object_or_404(Payout, pk=pk)
    payout.status       = Payout.StatusChoice.REJECTED
    payout.processed_at = timezone.now()
    payout.processed_by = request.user
    payout.admin_note   = request.POST.get('reason', '')
    payout.save()

    # Restore pending balance
    earnings, _ = PublisherEarnings.objects.get_or_create(publisher=payout.publisher)
    earnings.pending_payout += payout.amount
    earnings.save(update_fields=['pending_payout'])

    _send_payout_notification(payout, approved=False)
    messages.warning(request, f'Payout rejected. Publisher notified.')
    return redirect('payments:admin_revenue')


# ──────────────────────────────────────────────────────────────────────────────
# Admin: Set price for content
# ──────────────────────────────────────────────────────────────────────────────
@login_required
@admin_required
def set_content_price(request, content_type, object_id):
    """Admin/Publisher sets or updates the price for a content item."""
    price_obj, _ = ContentPrice.objects.get_or_create(
        content_type=content_type,
        object_id=object_id,
        defaults={'owner': request.user, 'price': Decimal('0.00'), 'is_free': True},
    )
    content_title, _ = _resolve_content(content_type, object_id)

    if request.method == 'POST':
        is_free   = request.POST.get('is_free') == 'on'
        price_val = request.POST.get('price', '0').strip()
        currency  = request.POST.get('currency', 'USD').strip().upper()
        owner_id  = request.POST.get('owner_id', '').strip()

        try:
            price_decimal = Decimal(price_val) if price_val else Decimal('0.00')
        except Exception:
            price_decimal = Decimal('0.00')

        price_obj.is_free  = is_free
        price_obj.price    = Decimal('0.00') if is_free else price_decimal
        price_obj.currency = currency
        price_obj.is_active = True

        # Allow specifying the publisher (owner) by user id
        if owner_id:
            from accounts.models import User
            try:
                price_obj.owner = User.objects.get(pk=owner_id)
            except User.DoesNotExist:
                pass

        price_obj.save()

        # If free, grant access to everyone automatically via a system flag
        if is_free:
            messages.success(request, f'"{content_title}" marked as free.')
        else:
            messages.success(request, f'Price set: {currency} {price_decimal} for "{content_title}".')

        return redirect('payments:admin_revenue')

    return render(request, 'payments/set_price.html', {
        'price_obj':     price_obj,
        'content_title': content_title,
        'content_type':  content_type,
        'object_id':     object_id,
    })


# ──────────────────────────────────────────────────────────────────────────────
# My purchases (buyer view)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def my_purchases(request):
    purchases = Purchase.objects.filter(
        buyer=request.user, status=Purchase.StatusChoice.COMPLETED
    ).select_related('content_price').order_by('-completed_at')

    # Annotate with content title
    for p in purchases:
        p.content_title, _ = _resolve_content(
            p.content_price.content_type, p.content_price.object_id
        )

    return render(request, 'payments/my_purchases.html', {'purchases': purchases})


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────
def _resolve_content(content_type, object_id):
    """Return (title, url) for a given content type and object id."""
    try:
        if content_type == 'book':
            from publishing.models import Book
            obj = Book.objects.get(pk=object_id)
            return obj.title, f'/publishing/books/{obj.slug}/'
        elif content_type == 'publication':
            from publishing.models import Publication
            obj = Publication.objects.get(pk=object_id)
            return obj.title, f'/publishing/publications/{obj.slug}/'
        elif content_type == 'journal':
            from publishing.models import Journal
            obj = Journal.objects.get(pk=object_id)
            return obj.title, f'/publishing/journals/{obj.slug}/'
    except Exception:
        pass
    return f'Content #{object_id}', '/'


def _get_file(content_type, object_id):
    """Return the FileField for a content item, or None."""
    try:
        if content_type == 'book':
            from publishing.models import Book
            book = Book.objects.get(pk=object_id)
            return book.file if book.file else None
        elif content_type == 'publication':
            from publishing.models import Publication
            pub = Publication.objects.get(pk=object_id)
            return pub.manuscript if pub.manuscript else None
    except Exception:
        pass
    return None


def _send_payout_notification(payout, approved: bool):
    """Send payout status email to publisher."""
    if not payout.publisher.email:
        return
    from django.core.mail import send_mail
    from django.conf import settings
    site_name = getattr(settings, 'GARL_SITE_NAME', 'GARL')
    status    = 'approved and processed' if approved else 'rejected'
    msg       = (
        f'Your payout request of {payout.currency} {payout.amount} has been {status}.'
        + (f'\n\nNote: {payout.admin_note}' if payout.admin_note else '')
    )
    send_mail(
        subject=f'[{site_name}] Payout {status}',
        message=msg,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[payout.publisher.email],
        fail_silently=True,
    )
