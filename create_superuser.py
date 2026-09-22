"""
One-time superuser bootstrap for Render free tier (no shell access).
Runs during build; safely no-ops if the user already exists.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
EMAIL    = os.environ.get("DJANGO_SUPERUSER_EMAIL", "nkufrat337@gmail.com")
PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not PASSWORD:
    print("DJANGO_SUPERUSER_PASSWORD not set — skipping superuser creation.")
elif User.objects.filter(username=USERNAME).exists():
    print(f"Superuser '{USERNAME}' already exists — skipping.")
else:
    User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
    print(f"Superuser '{USERNAME}' created.")