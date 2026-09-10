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
    try:
        User.objects.exists()
    except (ProgrammingError, OperationalError, Exception):
        print("==> DO'KON POS: Baza jadvallari mavjud emas. Migratsiyalar bajarilmoqda...")
        call_command('migrate', interactive=False)
        print("==> DO'KON POS: Migratsiyalar muvaffaqiyatli yakunlandi!")

    try:
        from datetime import timedelta
        from django.utils import timezone
        if not User.objects.filter(is_superuser=True).exists():
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
            print("==> DO'KON POS: Superuser yaratildi: admin / admin123")
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
        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error'}, status=401)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def init_db(request):
    import io
    import traceback
    from django.core.management import call_command
    out = io.StringIO()
    try:
        call_command('migrate', interactive=False, stdout=out)
        from accounts.models import User, Company, Branch
        from datetime import timedelta
        from django.utils import timezone

        user_status = ""
        if not User.objects.filter(is_superuser=True).exists():
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
            user_status = "Superuser yaratildi: admin / admin123"
        else:
            user_status = "Superuser allaqachon mavjud"

        return HttpResponse(f"<h1>Migratsiya Muvaffaqiyatli!</h1><p>{user_status}</p><pre>{out.getvalue()}</pre>")
    except Exception as e:
        return HttpResponse(f"<h1>Xatolik: {e}</h1><pre>{traceback.format_exc()}</pre><pre>{out.getvalue()}</pre>", status=500)