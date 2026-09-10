#!/usr/bin/env python
"""
DO'KON POS - Production Gunicorn Launcher & Auto-provisioner.
Handles Railway/PaaS environment variable interpolation, database migrations,
static files collection, and initial superuser provisioning.
"""
import os
import re
import sys


def setup_django_and_db():
    if not os.environ.get('DATABASE_URL'):
        return

    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        django.setup()

        from django.core.management import call_command
        print("==> DO'KON POS: Ma'lumotlar bazasi migratsiyalari (migrate)...")
        call_command('migrate', interactive=False)

        print("==> DO'KON POS: Statik fayllarni yig'ish (collectstatic)...")
        call_command('collectstatic', interactive=False)

        # Superuser tekshirish va yaratish
        from accounts.models import User, Company, Branch
        from datetime import timedelta
        from django.utils import timezone

        if not User.objects.filter(is_superuser=True).exists():
            print("==> DO'KON POS: Dastlabki admin foydalanuvchisi yaratilmoqda...")
            company, _ = Company.objects.get_or_create(
                name="Bosh Do'kon",
                defaults={
                    'subscription_end_date': timezone.now().date() + timedelta(days=365),
                    'is_active': True,
                }
            )
            branch, _ = Branch.objects.get_or_create(name="Asosiy filial", company=company)
            admin_user = User.objects.create_superuser('admin', 'admin@dokon.uz', 'admin123')
            admin_user.company = company
            admin_user.branch = branch
            admin_user.role = 'ADMIN'
            admin_user.save()
            print("==> DO'KON POS: Admin yaratildi (Login: admin / Parol: admin123)")
    except Exception as exc:
        print("==> DO'KON POS startup ogohlantirish:", exc)


def main():
    # 1. Portni aniqlash
    raw_port = os.environ.get('PORT', '8000')
    port = raw_port if (raw_port and raw_port.isdigit()) else '8000'

    # 2. Argumentlar orasidagi $PORT yoki ${PORT} ni to'g'ri raqam bilan almashtirish
    cleaned_args = []
    for arg in sys.argv[1:]:
        for needle in ['$PORT', '${PORT}']:
            if needle in arg:
                arg = arg.replace(needle, port)
        cleaned_args.append(arg)

    # Agar hech qanday bind ko'rsatilmagan bo'lsa
    has_bind = any('--bind' in a or '-b' in a for a in cleaned_args)
    if not has_bind:
        cleaned_args.extend(['--bind', f'0.0.0.0:{port}'])

    has_app = any('core.wsgi' in a for a in cleaned_args)
    if not has_app:
        cleaned_args.append('core.wsgi:application')

    # 3. Bazani tayyorlash
    setup_django_and_db()

    # 4. Gunicorn ni ishga tushirish
    from gunicorn.app.wsgiapp import run
    sys.argv = [sys.argv[0]] + cleaned_args
    print(f"==> DO'KON POS: Gunicorn server 0.0.0.0:{port} portida ishga tushmoqda...")
    run()


if __name__ == '__main__':
    main()
