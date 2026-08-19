"""
GARL Payment Template Tags
Usage: {% load payment_tags %}

Tags:
  {% content_price_badge 'book' book.pk %} — renders price or FREE badge
  {% user_has_content_access request.user 'book' book.pk %} — True/False
  {% content_price_data 'book' book.pk as price_data %} — full price object
"""

from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()


def _get_price(content_type, object_id):
    from payments.models import ContentPrice
    try:
        return ContentPrice.objects.get(
            content_type=content_type, object_id=object_id, is_active=True
        )
    except ContentPrice.DoesNotExist:
        return None


@register.simple_tag
def content_price_badge(content_type, object_id):
    """Render an HTML badge showing price or FREE."""
    price = _get_price(content_type, object_id)
    if price is None or price.is_free:
        # No format args needed — use mark_safe for static HTML
        return mark_safe(
            '<span class="badge bg-success-subtle text-success-emphasis">'
            '<i class="bi bi-unlock-fill me-1"></i>Free</span>'
        )
    # Dynamic values — use format_html to escape them safely
    return format_html(
        '<span class="badge" style="background:var(--garl-gold);color:#fff;">'
        '<i class="bi bi-lock-fill me-1"></i>{currency} {price}</span>',
        currency=price.currency,
        price=price.price,
    )


@register.simple_tag
def user_has_content_access(user, content_type, object_id):
    """Return True if the user has paid for or has free access to the content."""
    from payments.models import ContentPrice, AccessGrant
    if not user or not user.is_authenticated:
        return False
    try:
        price = ContentPrice.objects.get(
            content_type=content_type, object_id=object_id, is_active=True
        )
        if price.is_free:
            return True
    except ContentPrice.DoesNotExist:
        return True  # no price = free
    return AccessGrant.objects.filter(
        buyer=user, content_type=content_type, object_id=object_id
    ).exists()


@register.simple_tag
def content_checkout_url(content_type, object_id):
    """Return the checkout URL for a piece of content."""
    try:
        from django.urls import reverse
        return reverse('payments:checkout', kwargs={
            'content_type': content_type,
            'object_id': object_id,
        })
    except Exception:
        return '#'


@register.inclusion_tag('payments/partials/price_action.html', takes_context=True)
def price_action_button(context, content_type, object_id, btn_class='btn-garl-gold'):
    """
    Renders the correct button:
      - Free / no price → Download button (passes through to normal download)
      - Paid & user has access → Download button
      - Paid & user doesn't have access → Buy button with price
      - Not authenticated → Sign in to purchase
    """
    from payments.models import ContentPrice, AccessGrant
    user   = context.get('request').user if context.get('request') else None
    price  = _get_price(content_type, object_id)
    has_access = False

    if price is None or price.is_free:
        has_access = True
    elif user and user.is_authenticated:
        if user.is_any_admin():
            has_access = True
        else:
            has_access = AccessGrant.objects.filter(
                buyer=user, content_type=content_type, object_id=object_id
            ).exists()

    return {
        'content_type': content_type,
        'object_id':    object_id,
        'price':        price,
        'has_access':   has_access,
        'user':         user,
        'btn_class':    btn_class,
    }
