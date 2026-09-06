import subprocess, sys

result = subprocess.run(
    [sys.executable, "manage.py", "migrate"],
    capture_output=True,
    text=True,
    cwd=r"c:\Users\USER\Desktop\GPAS"
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("EXIT:", result.returncode)
