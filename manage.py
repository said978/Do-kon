#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    # Railway / Production port va gunicorn boshqaruvi:
    raw_port = os.environ.get('PORT', '8000')
    port = raw_port if (raw_port and raw_port.isdigit()) else '8000'

    # Har qanday argumentdagi $PORT ni haqiqiy port raqami bilan almashtirish
    for i in range(len(sys.argv)):
        for needle in ['$PORT', '${PORT}']:
            if needle in sys.argv[i]:
                sys.argv[i] = sys.argv[i].replace(needle, port)

    # Agar Railway yoki PaaS muhitida runserver chaqirilsa, to'g'ridan-to'g'ri gunicorn_run ga o'tish:
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and os.environ.get('DATABASE_URL'):
        try:
            import gunicorn_run
            sys.argv = ['gunicorn', 'core.wsgi:application', '--bind', f'0.0.0.0:{port}', '--workers', '3']
            gunicorn_run.main()
            return
        except Exception as e:
            print("==> gunicorn_run fallback error:", e)

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

