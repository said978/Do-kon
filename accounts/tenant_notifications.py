from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Q
from accounts.models import Company, Branch
from inventory.models import Product, Stock
from sales.models import Sale

import datetime


def get_company(request):
    return getattr(request, 'company', None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    alerts = []

    # 1. Obuna tugash ogohlantirishi
    days_left = (company.subscription_end_date - timezone.now().date()).days
    if days_left <= 7 and days_left > 0:
        alerts.append({
            'type': 'warning',
            'title': 'Obuna tugayapti!',
            'message': f'Obunangiz {days_left} kundan keyin tugaydi.',
            'action': '/api/tenant/billing/extend/',
        })
    elif days_left <= 0:
        alerts.append({
            'type': 'danger',
            'title': 'Obuna muddati o\'tdi!',
            'message': 'Xizmatdan foydalanish to\'xtatildi.',
            'action': '/api/tenant/billing/extend/',
        })

    # 2. Kam qolgan tovarlar
    low_stock = Stock.objects.filter(
        branch__company=company,
        quantity__lte=5,
        quantity__gt=0
    ).select_related('product', 'branch')

    for stock in low_stock:
        alerts.append({
            'type': 'warning',
            'title': 'Kam qoldi!',
            'message': f'{stock.product.name} — {stock.branch.name} da {stock.quantity} dona qoldi.',
            'action': '/api/inventory/stocks/',
        })

    # 3. Ombori tugagan tovarlar
    out_of_stock = Stock.objects.filter(
        branch__company=company,
        quantity=0
    ).select_related('product', 'branch')

    for stock in out_of_stock:
        alerts.append({
            'type': 'danger',
            'title': 'Tugadi!',
            'message': f'{stock.product.name} — {stock.branch.name} da tugadi.',
            'action': '/api/inventory/stocks/',
        })

    # 4. Bugun daromad yo'q
    today_sales = Sale.objects.filter(
        company=company,
        created_at__date=timezone.now().date()
    )
    if today_sales.count() == 0 and timezone.now().hour >= 10:
        alerts.append({
            'type': 'info',
            'title': 'Bugun hali savdo yo\'q',
            'message': f'{timezone.now().strftime("%d.%m.%Y")} da hali savdo amalga oshirilmagan.',
            'action': '/api/sales/pos/',
        })

    # 5. Filiallar soni
    branch_count = Branch.objects.filter(company=company).count()
    if branch_count == 0:
        alerts.append({
            'type': 'info',
            'title': 'Filiallar yo\'q',
            'message': 'Hali filial yaratilmagan.',
            'action': '/admin/accounts/branch/add/',
        })

    return Response({
        'count': len(alerts),
        'alerts': alerts,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alerts_summary(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Ombor holati
    total_products = Product.objects.filter(company=company).count()
    low_stock_count = Stock.objects.filter(
        branch__company=company,
        quantity__lte=5,
        quantity__gt=0
    ).count()
    out_of_stock_count = Stock.objects.filter(
        branch__company=company,
        quantity=0
    ).count()

    # Savdo holati
    today_sales = Sale.objects.filter(
        company=company,
        created_at__date=today
    )
    today_total = float(today_sales.aggregate(total=Sum('total_amount'))['total'] or 0)

    month_sales = Sale.objects.filter(
        company=company,
        created_at__date__gte=month_start
    )
    month_total = float(month_sales.aggregate(total=Sum('total_amount'))['total'] or 0)

    # Obuna
    days_left = (company.subscription_end_date - today).days

    return Response({
        'products': {
            'total': total_products,
            'low_stock': low_stock_count,
            'out_of_stock': out_of_stock_count,
        },
        'sales': {
            'today_count': today_sales.count(),
            'today_total': today_total,
            'month_count': month_sales.count(),
            'month_total': month_total,
        },
        'subscription': {
            'days_left': max(0, days_left),
            'is_valid': company.is_subscription_valid(),
        }
    })
