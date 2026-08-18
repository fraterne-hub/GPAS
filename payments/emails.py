"""
GARL Payment Email Notifications
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sends emails to:
  1. Buyer    — receipt / download link
  2. Publisher — "someone purchased your content"
  3. Platform owner — sale alert (configured via GARL_OWNER_EMAIL in .env)
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone


# ── Helper ────────────────────────────────────────────────────────────────────
def _get_content_title(purchase):
    """Resolve the human-readable title for any purchased content."""
    ct = purchase.content_price.content_type
    oid = purchase.content_price.object_id
    try:
        if ct == 'book':
            from publishing.models import Book
            return Book.objects.get(pk=oid).title
        elif ct == 'publication':
            from publishing.models import Publication
            return Publication.objects.get(pk=oid).title
        elif ct == 'journal':
            from publishing.models import Journal
            return Journal.objects.get(pk=oid).title
    except Exception:
        pass
    return f'Content #{oid}'


def _get_content_url(purchase):
    """Build the absolute URL to access the purchased content."""
    site = getattr(settings, 'GARL_SITE_URL', 'http://localhost:8000')
    ct   = purchase.content_price.content_type
    oid  = purchase.content_price.object_id
    try:
        if ct == 'book':
            from publishing.models import Book
            book = Book.objects.get(pk=oid)
            return f'{site}/payments/download/{ct}/{oid}/{purchase.transaction_id}/'
        elif ct == 'publication':
            from publishing.models import Publication
            pub = Publication.objects.get(pk=oid)
            return f'{site}/payments/download/{ct}/{oid}/{purchase.transaction_id}/'
        elif ct == 'journal':
            return f'{site}/payments/download/{ct}/{oid}/{purchase.transaction_id}/'
    except Exception:
        pass
    return f'{site}/payments/receipt/{purchase.transaction_id}/'


# ── 1. Buyer receipt ──────────────────────────────────────────────────────────
def send_buyer_receipt(purchase):
    """Send purchase confirmation and download link to the buyer."""
    if not purchase.buyer or not purchase.buyer.email:
        return

    content_title = _get_content_title(purchase)
    download_url  = _get_content_url(purchase)
    site_name     = getattr(settings, 'GARL_SITE_NAME', 'GARL')

    subject = f'Your purchase receipt — {content_title}'

    html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;background:#f5f7fa;margin:0;padding:20px;">
  <div style="max-width:580px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);">

    <!-- Header -->
    <div style="background:#0d1b2a;padding:28px 32px;text-align:center;">
      <h1 style="color:#c9a227;margin:0;font-size:22px;font-family:Georgia,serif;">
        &#9679; {site_name}
      </h1>
      <p style="color:rgba(255,255,255,.6);margin:8px 0 0;font-size:13px;">
        Global Academic Research Library
      </p>
    </div>

    <!-- Body -->
    <div style="padding:32px;">
      <h2 style="color:#0d1b2a;font-size:18px;margin-bottom:8px;">
        Thank you for your purchase!
      </h2>
      <p style="color:#555;font-size:15px;line-height:1.6;">
        Hi <strong>{purchase.buyer.get_full_name() or purchase.buyer.username}</strong>,
        your payment was successful. You can now download or access your content.
      </p>

      <!-- Content box -->
      <div style="background:#f5f7fa;border-left:4px solid #c9a227;border-radius:6px;padding:16px 20px;margin:20px 0;">
        <div style="font-size:13px;color:#888;margin-bottom:4px;">PURCHASED CONTENT</div>
        <div style="font-size:16px;font-weight:700;color:#0d1b2a;">{content_title}</div>
        <div style="font-size:13px;color:#555;margin-top:6px;">
          Type: <strong>{purchase.content_price.get_content_type_display()}</strong>
        </div>
      </div>

      <!-- Receipt table -->
      <table style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:24px;">
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Transaction ID</td>
          <td style="padding:10px 0;color:#0d1b2a;font-family:monospace;font-weight:700;">{purchase.transaction_id}</td>
        </tr>
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Amount Paid</td>
          <td style="padding:10px 0;color:#0d1b2a;font-weight:700;">{purchase.currency} {purchase.amount}</td>
        </tr>
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Date</td>
          <td style="padding:10px 0;color:#0d1b2a;">{purchase.completed_at.strftime('%B %d, %Y at %H:%M UTC') if purchase.completed_at else 'Just now'}</td>
        </tr>
        <tr>
          <td style="padding:10px 0;color:#888;">Status</td>
          <td style="padding:10px 0;color:#198754;font-weight:700;">&#10003; Completed</td>
        </tr>
      </table>

      <!-- Download button -->
      <div style="text-align:center;margin:28px 0;">
        <a href="{download_url}"
           style="background:#c9a227;color:#fff;padding:14px 36px;border-radius:8px;
                  text-decoration:none;font-weight:700;font-size:15px;display:inline-block;">
          &#8659; Download / Access Content
        </a>
      </div>

      <p style="color:#888;font-size:13px;line-height:1.6;">
        If the button doesn't work, copy and paste this link into your browser:<br/>
        <a href="{download_url}" style="color:#c9a227;word-break:break-all;">{download_url}</a>
      </p>
    </div>

    <!-- Footer -->
    <div style="background:#f5f7fa;padding:20px 32px;text-align:center;border-top:1px solid #eee;">
      <p style="color:#aaa;font-size:12px;margin:0;">
        &copy; {timezone.now().year} {site_name} &mdash; This is an automated receipt. Keep it for your records.
      </p>
    </div>
  </div>
</body>
</html>"""

    msg = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_content),
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@garl.edu>'),
        to=[purchase.buyer.email],
    )
    msg.attach_alternative(html_content, 'text/html')
    try:
        msg.send(fail_silently=True)
        purchase.buyer_notified = True
        purchase.save(update_fields=['buyer_notified'])
    except Exception:
        pass


# ── 2. Publisher sale alert ────────────────────────────────────────────────────
def send_publisher_sale_alert(purchase):
    """Notify the publisher that someone purchased their content."""
    publisher = purchase.content_price.owner
    if not publisher or not publisher.email:
        return

    content_title = _get_content_title(purchase)
    site_name     = getattr(settings, 'GARL_SITE_NAME', 'GARL')
    dashboard_url = f"{getattr(settings, 'GARL_SITE_URL', 'http://localhost:8000')}/payments/publisher/dashboard/"

    subject = f'&#128722; New sale: {content_title} — {purchase.currency} {purchase.publisher_amount}'

    html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;background:#f5f7fa;margin:0;padding:20px;">
  <div style="max-width:560px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08);">
    <div style="background:#0d1b2a;padding:28px 32px;text-align:center;">
      <h1 style="color:#c9a227;margin:0;font-size:22px;font-family:Georgia,serif;">&#128722; New Sale!</h1>
      <p style="color:rgba(255,255,255,.6);margin:8px 0 0;font-size:13px;">{site_name}</p>
    </div>
    <div style="padding:32px;">
      <p style="color:#555;font-size:15px;line-height:1.6;">
        Hi <strong>{publisher.get_full_name() or publisher.username}</strong>,
        congratulations! Someone just purchased your content on {site_name}.
      </p>

      <div style="background:#f5f7fa;border-left:4px solid #c9a227;border-radius:6px;padding:16px 20px;margin:20px 0;">
        <div style="font-size:13px;color:#888;margin-bottom:4px;">CONTENT SOLD</div>
        <div style="font-size:16px;font-weight:700;color:#0d1b2a;">{content_title}</div>
      </div>

      <table style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:24px;">
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Sale Price</td>
          <td style="padding:10px 0;font-weight:700;">{purchase.currency} {purchase.amount}</td>
        </tr>
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Your Earnings (60%)</td>
          <td style="padding:10px 0;font-weight:700;color:#198754;font-size:16px;">
            &#10003; {purchase.currency} {purchase.publisher_amount}
          </td>
        </tr>
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Platform Fee (40%)</td>
          <td style="padding:10px 0;color:#888;">{purchase.currency} {purchase.platform_amount}</td>
        </tr>
        <tr>
          <td style="padding:10px 0;color:#888;">Transaction Date</td>
          <td style="padding:10px 0;">{purchase.completed_at.strftime('%B %d, %Y') if purchase.completed_at else 'Today'}</td>
        </tr>
      </table>

      <div style="background:#e8f5e9;border-radius:8px;padding:16px;margin-bottom:24px;text-align:center;">
        <div style="font-size:13px;color:#555;">Your earnings have been added to your account balance.</div>
        <div style="font-size:24px;font-weight:700;color:#198754;margin-top:6px;">
          + {purchase.currency} {purchase.publisher_amount}
        </div>
      </div>

      <div style="text-align:center;">
        <a href="{dashboard_url}"
           style="background:#0d1b2a;color:#c9a227;padding:12px 28px;border-radius:8px;
                  text-decoration:none;font-weight:700;font-size:14px;display:inline-block;">
          View Your Earnings Dashboard
        </a>
      </div>
    </div>
    <div style="background:#f5f7fa;padding:16px 32px;text-align:center;border-top:1px solid #eee;">
      <p style="color:#aaa;font-size:12px;margin:0;">&copy; {timezone.now().year} {site_name}</p>
    </div>
  </div>
</body>
</html>"""

    msg = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_content),
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@garl.edu>'),
        to=[publisher.email],
    )
    msg.attach_alternative(html_content, 'text/html')
    try:
        msg.send(fail_silently=True)
        purchase.publisher_notified = True
        purchase.save(update_fields=['publisher_notified'])
    except Exception:
        pass


# ── 3. Platform owner sale alert ───────────────────────────────────────────────
def send_owner_sale_alert(purchase):
    """Notify the platform owner of a new sale."""
    owner_email = getattr(settings, 'GARL_OWNER_EMAIL', '')
    if not owner_email:
        return

    content_title = _get_content_title(purchase)
    site_name     = getattr(settings, 'GARL_SITE_NAME', 'GARL')
    admin_url     = f"{getattr(settings, 'GARL_SITE_URL', 'http://localhost:8000')}/payments/admin/revenue/"

    subject = f'[{site_name}] New sale — {purchase.currency} {purchase.platform_amount} platform revenue'

    html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;background:#f5f7fa;margin:0;padding:20px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;">
    <div style="background:#0d1b2a;padding:24px 28px;">
      <h2 style="color:#c9a227;margin:0;font-size:18px;">Platform Sale Notification</h2>
      <p style="color:rgba(255,255,255,.5);margin:4px 0 0;font-size:12px;">{site_name} Revenue Alert</p>
    </div>
    <div style="padding:28px;">
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Content</td>
          <td style="padding:10px 0;font-weight:600;">{content_title}</td>
        </tr>
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Buyer</td>
          <td style="padding:10px 0;">{purchase.buyer.get_full_name() if purchase.buyer else 'Unknown'}</td>
        </tr>
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Total Sale</td>
          <td style="padding:10px 0;font-weight:700;">{purchase.currency} {purchase.amount}</td>
        </tr>
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Platform (40%)</td>
          <td style="padding:10px 0;font-weight:700;color:#c9a227;font-size:16px;">
            {purchase.currency} {purchase.platform_amount}
          </td>
        </tr>
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:10px 0;color:#888;">Publisher (60%)</td>
          <td style="padding:10px 0;">{purchase.currency} {purchase.publisher_amount}</td>
        </tr>
        <tr>
          <td style="padding:10px 0;color:#888;">Transaction ID</td>
          <td style="padding:10px 0;font-family:monospace;font-size:12px;">{purchase.transaction_id}</td>
        </tr>
      </table>
      <div style="text-align:center;margin-top:24px;">
        <a href="{admin_url}"
           style="background:#c9a227;color:#fff;padding:10px 24px;border-radius:6px;
                  text-decoration:none;font-weight:700;font-size:13px;">
          View Revenue Dashboard
        </a>
      </div>
    </div>
  </div>
</body>
</html>"""

    msg = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_content),
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@garl.edu>'),
        to=[owner_email],
    )
    msg.attach_alternative(html_content, 'text/html')
    try:
        msg.send(fail_silently=True)
        purchase.owner_notified = True
        purchase.save(update_fields=['owner_notified'])
    except Exception:
        pass


# ── 4. Access notification (someone viewed/downloaded free content) ────────────
def send_access_notification(content_owner, content_title, content_type, accessor_name, accessor_email=''):
    """
    Notify the publisher when someone accesses (views/downloads) their
    free or paid content — so they know who is reading their work.
    """
    if not content_owner or not content_owner.email:
        return

    site_name = getattr(settings, 'GARL_SITE_NAME', 'GARL')
    subject   = f'[{site_name}] Your {content_type} was accessed: {content_title[:60]}'

    html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;background:#f5f7fa;margin:0;padding:20px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:12px;overflow:hidden;">
    <div style="background:#0d1b2a;padding:24px 28px;">
      <h2 style="color:#c9a227;margin:0;font-size:18px;">&#128214; Your content was accessed</h2>
      <p style="color:rgba(255,255,255,.5);margin:4px 0 0;font-size:12px;">{site_name}</p>
    </div>
    <div style="padding:28px;">
      <p style="color:#555;font-size:14px;line-height:1.6;">
        Hi <strong>{content_owner.get_full_name() or content_owner.username}</strong>,
        someone just accessed your {content_type} on {site_name}.
      </p>
      <div style="background:#f5f7fa;border-left:4px solid #0d6efd;border-radius:6px;padding:14px 18px;margin:16px 0;">
        <div style="font-size:12px;color:#888;margin-bottom:3px;">CONTENT ACCESSED</div>
        <div style="font-size:15px;font-weight:700;color:#0d1b2a;">{content_title}</div>
        <div style="font-size:12px;color:#888;margin-top:4px;">Type: {content_type}</div>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <tr style="border-bottom:1px solid #eee;">
          <td style="padding:8px 0;color:#888;">Accessed by</td>
          <td style="padding:8px 0;font-weight:600;">{accessor_name}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:#888;">Date</td>
          <td style="padding:8px 0;">{timezone.now().strftime('%B %d, %Y at %H:%M UTC')}</td>
        </tr>
      </table>
    </div>
    <div style="background:#f5f7fa;padding:14px 28px;text-align:center;border-top:1px solid #eee;">
      <p style="color:#aaa;font-size:11px;margin:0;">&copy; {timezone.now().year} {site_name}</p>
    </div>
  </div>
</body>
</html>"""

    msg = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_content),
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', f'{site_name} <noreply@garl.edu>'),
        to=[content_owner.email],
    )
    msg.attach_alternative(html_content, 'text/html')
    try:
        msg.send(fail_silently=True)
    except Exception:
        pass
