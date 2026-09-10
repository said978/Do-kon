from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.utils import ProgrammingError, OperationalError
from django.core.management import call_command
import json
import traceback

_db_ready = False


def ensure_db_ready():
    global _db_ready
    if _db_ready:
        return

    from accounts.models import User, Company, Branch
    from inventory.models import Product

    try:
        User.objects.exists()
    except (ProgrammingError, OperationalError, Exception):
        print("==> DO'KON POS: Baza jadvallari mavjud emas. Migratsiyalar bajarilmoqda...")
        call_command('migrate', interactive=False)
        print("==> DO'KON POS: Migratsiyalar muvaffaqiyatli yakunlandi!")

    # Baza ma'lumotlarini (tovarlar, kategoriyalar, filiallar) yuklash:
    try:
        if Product.objects.count() == 0:
            import os
            from django.conf import settings
            fixture_path = os.path.join(settings.BASE_DIR, 'data.json')
            if os.path.exists(fixture_path):
                print("==> DO'KON POS: Asl baza ma'lumotlari (data.json) yuklanmoqda...")
                call_command('loaddata', fixture_path)
                print("==> DO'KON POS: Barcha tovarlar va ma'lumotlar muvaffaqiyatli yuklandi!")
    except Exception as e:
        print("==> DO'KON POS loaddata ogohlantirish:", e)

    try:
        from datetime import timedelta
        from django.utils import timezone

        # Har ikkala admin foydalanuvchisini ham ta'minlash:
        # 1. Admin (parol: 123)
        admin_caps = User.objects.filter(username__iexact='Admin').first()
        if not admin_caps:
            company = Company.objects.first()
            if not company:
                company = Company.objects.create(name="Bosh Do'kon", subscription_end_date=timezone.now().date() + timedelta(days=365))
            branch = Branch.objects.first()
            admin_caps = User.objects.create_superuser('Admin', 'admin@dokon.uz', '123')
            admin_caps.company = company
            admin_caps.branch = branch
            admin_caps.role = 'ADMIN'
            admin_caps.save()
        else:
            admin_caps.set_password('123')
            admin_caps.is_staff = True
            admin_caps.is_superuser = True
            admin_caps.is_active = True
            admin_caps.role = 'ADMIN'
            admin_caps.save()

        # 2. admin (parol: admin123)
        admin_low = User.objects.filter(username='admin').first()
        if not admin_low and admin_caps.username != 'admin':
            admin_low = User.objects.create_superuser('admin', 'admin2@dokon.uz', 'admin123')
            admin_low.company = admin_caps.company
            admin_low.branch = admin_caps.branch
            admin_low.role = 'ADMIN'
            admin_low.save()
        elif admin_low and admin_low != admin_caps:
            admin_low.set_password('admin123')
            admin_low.is_staff = True
            admin_low.is_superuser = True
            admin_low.is_active = True
            admin_low.role = 'ADMIN'
            admin_low.save()

    except Exception as e:
        print("==> DO'KON POS admin yaratish ogohlantirish:", e)

    _db_ready = True


def login_page(request):
    try:
        ensure_db_ready()
        return render(request, 'login.html')
    except Exception as e:
        return HttpResponse(f"<h1>Login Render Error: {e}</h1><pre>{traceback.format_exc()}</pre>", status=500)


@csrf_exempt
@require_POST
def login_session(request):
    try:
        ensure_db_ready()
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        username = data.get('username', '').strip()
        password = data.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error', 'message': "Login yoki parol noto'g'ri"}, status=401)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def init_db(request):
    import io
    import traceback
    try:
        global _db_ready
        _db_ready = False
        ensure_db_ready()
        return HttpResponse("<h1>Baza Muvaffaqiyatli Tayyorlandi!</h1><p>Barcha tovarlar va foydalanuvchilar (Admin / 123, admin / admin123) yuklandi.</p>")
    except Exception as e:
        return HttpResponse(f"<h1>Xatolik: {e}</h1><pre>{traceback.format_exc()}</pre>", status=500)