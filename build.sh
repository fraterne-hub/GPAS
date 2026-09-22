#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# One-time superuser bootstrap (inline — prints clearly)
python - <<'PY'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.contrib.auth import get_user_model
U = get_user_model()
u = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
e = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
p = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
print("=== SUPERUSER BOOTSTRAP ===")
print("USERNAME:", u)
print("EMAIL:", e)
print("PASSWORD SET:", bool(p))
if not p:
    print("SKIP: no password")
elif U.objects.filter(username=u).exists():
    print("SKIP: already exists")
else:
    U.objects.create_superuser(username=u, email=e, password=p)
    print("CREATED:", u)
print("=== END BOOTSTRAP ===")
PY