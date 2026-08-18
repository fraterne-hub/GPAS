import os, traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
lines = []
try:
    import django; django.setup()
    from django.core.management import call_command
    from io import StringIO

    out = StringIO(); err = StringIO()
    call_command('makemigrations', 'payments', '--no-input', stdout=out, stderr=err, interactive=False)
    lines.append("makemigrations:\n" + out.getvalue())
    if err.getvalue(): lines.append("ERR: " + err.getvalue())

    out2 = StringIO(); err2 = StringIO()
    call_command('migrate', '--no-input', stdout=out2, stderr=err2, interactive=False)
    lines.append("migrate:\n" + out2.getvalue())
    if err2.getvalue(): lines.append("ERR: " + err2.getvalue())

    # Quick check
    out3 = StringIO(); err3 = StringIO()
    try: call_command('check', stdout=out3, stderr=err3)
    except SystemExit: pass
    lines.append("check:\n" + (out3.getvalue() or "OK"))

except Exception:
    lines.append(traceback.format_exc())

with open('pay_migrate_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("done")
