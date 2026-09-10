import csv
import json
from io import StringIO, BytesIO
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from accounts.models import Company, Branch, User
from inventory.models import Product, Category, Stock
from sales.models import Sale, SaleItem, Customer


def get_company(request):
    return getattr(request, 'company', None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_products_csv(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    products = Product.objects.filter(company=company).select_related('category')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="products_{company.name}_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nomi', 'Shtrix-kod', 'Kategoriya', 'Tannarx', 'Sotish narxi'])

    for p in products:
        writer.writerow([p.id, p.name, p.barcode, p.category.name, p.cost_price, p.selling_price])

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_sales_csv(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    sales = Sale.objects.filter(company=company).select_related('cashier')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_{company.name}_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Sana', 'Kassir', 'Summa', 'To\'lov turi'])

    for s in sales:
        writer.writerow([
            s.id,
            s.created_at.strftime('%Y-%m-%d %H:%M'),
            s.cashier.username if s.cashier else 'Admin',
            s.total_amount,
            s.payment_method,
        ])

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_all_json(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    data = {
        'company': {
            'name': company.name,
            'phone': company.phone,
            'exported_at': str(timezone.now()),
        },
        'products': list(Product.objects.filter(company=company).values(
            'id', 'name', 'barcode', 'cost_price', 'selling_price'
        )),
        'categories': list(Category.objects.filter(company=company).values('id', 'name')),
        'customers': list(Customer.objects.filter(company=company).values(
            'id', 'name', 'phone', 'debt_balance'
        )),
        'sales': list(Sale.objects.filter(company=company).values(
            'id', 'total_amount', 'payment_method', 'created_at'
        )),
    }

    response = HttpResponse(json.dumps(data, ensure_ascii=False, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="backup_{company.name}_{timezone.now().date()}.json"'
    return response
