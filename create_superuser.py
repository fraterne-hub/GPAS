# v3 force update
"""
Superuser bootstrap for Render — always ensures is_staff/is_superuser.
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

print("=== SUPERUSER BOOTSTRAP v3 ===")
print("USERNAME:", USERNAME)
print("EMAIL:", EMAIL)
print("PASSWORD SET:", bool(PASSWORD))

if not PASSWORD:
    print("SKIP: no password")
else:
    # Try to find by email OR username
    user = User.objects.filter(email=EMAIL).first() or User.objects.filter(username=USERNAME).first()

    if user is None:
        user = User.objects.create_superuser(
            email=EMAIL, password=PASSWORD, username=USERNAME,
            first_name="Admin", last_name="GARL",
        )
        print(f"CREATED: {user.email}")
    else:
        print(f"FOUND existing user: email={user.email}, username={user.username}")
        print(f"  is_staff before: {user.is_staff}, is_superuser before: {user.is_superuser}")

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

        user.refresh_from_db()
        print(f"UPDATED: is_staff={user.is_staff}, is_superuser={user.is_superuser}, is_active={user.is_active}")
        print(f"  password check: {user.check_password(PASSWORD)}")

print("=== END BOOTSTRAP v3 ===")