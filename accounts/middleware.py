from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone


class SubscriptionCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Ruxsat berilgan ochiq manzillar (tekshirilmaydi)
        allowed_prefixes = (
            '/admin/',
            '/login/',
            '/logout/',
            '/login-session/',
            '/static/',
            '/media/',
            '/api/token/',
            '/favicon.ico',
        )
        if any(request.path.startswith(prefix) for prefix in allowed_prefixes):
            return self.get_response(request)

        # 2. Tizimga kirgan foydalanuvchi va uning do'koni (kompaniyasi)ni tekshiramiz
        if hasattr(request, 'user') and request.user.is_authenticated:
            company = getattr(request.user, 'company', None)

            # Agar do'kon obunasi tugagan yoki nofaol bo'lsa
            if company and not company.is_subscription_valid():
                # JSON API so'rovlarini aniqlash
                accept_header = request.headers.get('accept', '')
                is_html_page = any(request.path.startswith(p) for p in [
                    '/api/sales/pos/',
                    '/api/sales/dashboard/',
                    '/api/sales/customers-page/',
                    '/api/sales/reports/',
                    '/api/inventory/products-page/',
                    '/api/inventory/cleanup-page/',
                ])

                is_json_request = (
                    ('application/json' in accept_header or request.content_type == 'application/json' or request.path.startswith('/api/'))
                    and not is_html_page
                )

                if is_json_request:
                    return JsonResponse({
                        'detail': f"'{company.name}' do'koni uchun oylik obuna muddati tugagan! Tizimdan foydalanish uchun to'lovni amalga oshiring.",
                        'code': 'subscription_expired',
                        'company': company.name,
                        'subscription_end_date': str(company.subscription_end_date),
                        'monthly_fee': float(company.monthly_fee or 0),
                    }, status=403)

                # Brauzer sahifalari (HTML) uchun bloklanganlik xabarnomasi
                return render(request, 'subscription_expired.html', {
                    'company': company,
                    'user': request.user,
                }, status=403)

        return self.get_response(request)