#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # Railway / Cloud PaaS $PORT expander
    port = os.environ.get('PORT', '8000')
    for i in range(len(sys.argv)):
        if '$PORT' in sys.argv[i]:
            sys.argv[i] = sys.argv[i].replace('$PORT', port)

    # Agar Railway muhitida runserver ishga tushirilsa, avtomat migrate va collectstatic qilish
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and os.environ.get('DATABASE_URL'):
        try:
            import django
            django.setup()
            from django.core.management import call_command
            print("==> Railway: Ma'lumotlar bazasi migratsiyalari bajarilmoqda...")
            call_command('migrate', interactive=False)
            print("==> Railway: Statik fayllar yig'ilmoqda (collectstatic)...")
            call_command('collectstatic', interactive=False)
        except Exception as e:
            print("==> Railway startup notice:", e)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

