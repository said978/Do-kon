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