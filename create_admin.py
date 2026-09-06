import subprocess, sys

result = subprocess.run(
    [sys.executable, "manage.py", "shell", "-c",
     """
from django.contrib.auth import get_user_model
User = get_user_model()
email = 'admin@garl.edu'
if not User.objects.filter(email=email).exists():
    u = User.objects.create_superuser(
        email=email,
        password='Admin@1234',
        username='admin',
        first_name='Admin',
        last_name='GARL',
    )
    print('Superuser created!')
else:
    u = User.objects.get(email=email)
    u.set_password('Admin@1234')
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('Superuser password reset!')
print('Email:', email)
print('Password: Admin@1234')
"""],
    capture_output=True,
    text=True,
    cwd=r"c:\Users\USER\Desktop\GPAS"
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("EXIT:", result.returncode)
