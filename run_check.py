import os, traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
lines = []
try:
    import django; django.setup()
    from django.core.management import call_command
    from io import StringIO
    out = StringIO(); err = StringIO()
    try: call_command('check', stdout=out, stderr=err)
    except SystemExit: pass
    lines.append("CHECK: " + (out.getvalue().strip() or "OK"))
    if err.getvalue(): lines.append("WARNINGS: " + err.getvalue())

    # Test key imports
    from payments.models import ContentPrice, Purchase, AccessGrant, PublisherEarnings, PlatformRevenue, Payout
    from payments.emails import send_buyer_receipt, send_publisher_sale_alert, send_owner_sale_alert, send_access_notification
    from payments.templatetags.payment_tags import content_price_badge, user_has_content_access
    lines.append("IMPORTS: All payment models, emails and template tags import OK")

    # Test URL resolution
    from django.urls import reverse
    urls_to_test = [
        ('payments:checkout', {'content_type':'book','object_id':1}),
        ('payments:publisher_dashboard', {}),
        ('payments:admin_revenue', {}),
        ('payments:my_purchases', {}),
    ]
    for name, kwargs in urls_to_test:
        try:
            url = reverse(name, kwargs=kwargs) if kwargs else reverse(name)
            lines.append(f"URL OK: {name} → {url}")
        except Exception as ex:
            lines.append(f"URL FAIL: {name} — {ex}")

except Exception:
    lines.append(traceback.format_exc())

with open('check_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("done")
