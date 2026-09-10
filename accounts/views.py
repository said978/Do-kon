from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


def login_page(request):
    try:
        return render(request, 'login.html')
    except Exception as e:
        import traceback
        return HttpResponse(f"<h1>Login Render Error: {e}</h1><pre>{traceback.format_exc()}</pre>", status=500)


@csrf_exempt
@require_POST
def login_session(request):
    try:
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