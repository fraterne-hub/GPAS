"""
Superuser bootstrap for Render.
- Creates the superuser if missing.
- Fixes is_staff / is_superuser / password if the user already exists.
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
    print("DJANGO_SUPERUSER_PASSWORD not set — skipping.")
else:
    user = User.objects.filter(email=EMAIL).first()
    if user is None:
        user = User.objects.filter(username=USERNAME).first()

    if user is None:
        user = User.objects.create_superuser(
            email=EMAIL,
            password=PASSWORD,
            username=USERNAME,
            first_name="Admin",
            last_name="GARL",
        )
        print(f"CREATED: {user.email}")
    else:
        user.email = EMAIL
        user.username = USERNAME
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if not user.first_name:
            user.first_name = "Admin"
        if not user.last_name:
            user.last_name = "GARL"
        user.set_password(PASSWORD)
        user.save()
        print(f"UPDATED: {user.email} (is_staff=True, is_superuser=True, password reset)")