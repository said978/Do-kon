from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Min
import pandas as pd

from .models import Category, Product, Stock
from .serializers import CategorySerializer, ProductSerializer, StockSerializer


def get_company(request):
    company = getattr(request, 'company', None)
    if not company and hasattr(request, 'user') and request.user and request.user.is_authenticated:
        company = getattr(request.user, 'company', None)
    return company


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()

    def get_queryset(self):
        company = get_company(self.request)
        return Category.objects.for_company(company)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.all()

    def get_queryset(self):
        company = get_company(self.request)
        return Product.objects.for_company(company)


class StockViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Stock.objects.all()

    def get_queryset(self):
        company = get_company(self.request)
        return Stock.objects.for_company(company)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def import_products_excel(request):
    file = request.FILES.get('file')
    if not file:
        return Response({"detail": "Excel fayli tanlanmadi!"}, status=status.HTTP_400_BAD_REQUEST)

    company = get_company(request)
    if not company:
        return Response({"detail": "Firma aniqlanmadi!"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df = pd.read_excel(file)
        elif file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            return Response({"detail": "Faqat .xlsx, .xls yoki .csv fayllarni yuklashingiz mumkin!"},
                            status=status.HTTP_400_BAD_REQUEST)

        required_columns = ['kategoriya', 'tovar_nomi', 'shtrix_kod', 'tannarx', 'sotish_narxi', 'miqdor']
        for col in required_columns:
            if col not in df.columns:
                return Response({"detail": f"Excel faylda '{col}' ustuni topilmadi!"},
                                status=status.HTTP_400_BAD_REQUEST)

        from decimal import Decimal
        from accounts.models import Branch

        imported_count = 0
        user_branch = getattr(request.user, 'branch', None)
        if not user_branch and company:
            user_branch = company.branches.first()
            if not user_branch:
                user_branch = Branch.objects.create(company=company, name="Asosiy Filial")

        for index, row in df.iterrows():
            cat_name = str(row['kategoriya']).strip() if pd.notna(row['kategoriya']) else "Umumiy"
            prod_name = str(row['tovar_nomi']).strip() if pd.notna(row['tovar_nomi']) else ""
            barcode = str(row['shtrix_kod']).split('.')[0].strip() if pd.notna(row['shtrix_kod']) else ""
            cost_price = float(row['tannarx']) if pd.notna(row['tannarx']) else 0.0
            selling_price = float(row['sotish_narxi']) if pd.notna(row['sotish_narxi']) else 0.0
            quantity = float(row['miqdor']) if pd.notna(row['miqdor']) else 0.0

            if not prod_name or not barcode or barcode.lower() == 'nan':
                continue

            category = Category.objects.filter(name__iexact=cat_name, company=company).first()
            if not category:
                category = Category.objects.create(name=cat_name, company=company)

            product, created = Product.objects.update_or_create(
                company=company,
                barcode=barcode,
                defaults={
                    'category': category,
                    'name': prod_name,
                    'cost_price': cost_price,
                    'selling_price': selling_price,
                }
            )

            if user_branch:
                stock, _ = Stock.objects.get_or_create(branch=user_branch, product=product)
                current_qty = Decimal(str(stock.quantity or 0))
                add_qty = Decimal(str(quantity or 0))
                stock.quantity = current_qty + add_qty
                stock.save()

            imported_count += 1

        branch_name = user_branch.name if user_branch else "ombor"
        return Response({"detail": f"Muvaffaqiyatli yuklandi! {imported_count} ta tovar '{branch_name}' omboriga qo'shildi."},
                        status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": f"Excel faylni o'qishda xatolik: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def download_excel_template(request):
    data = [
        {
            'kategoriya': 'Ichimliklar',
            'tovar_nomi': 'Coca-Cola 1.5L',
            'shtrix_kod': '4780005870012',
            'tannarx': 8000,
            'sotish_narxi': 11000,
            'miqdor': 50
        },
        {
            'kategoriya': 'Oziq-ovqat',
            'tovar_nomi': 'Lays Chips 90g',
            'shtrix_kod': '4820000001234',
            'tannarx': 10000,
            'sotish_narxi': 14000,
            'miqdor': 30
        }
    ]
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=tovarlar_import_shablon.xlsx'
    df.to_excel(response, index=False, sheet_name='Tovarlar')
    return response


def products_management_view(request):
    return render(request, 'inventory/products_management.html')


def products_page_view(request):
    company = get_company(request)
    products = Product.objects.for_company(company).select_related('category')
    return render(request, 'inventory/products_page.html', {'products': products})


def cleanup_view(request):
    return render(request, 'inventory/cleanup.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_duplicate_categories(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)
    qs = Category.objects.for_company(company)
    dupes = qs.values('name').annotate(cnt=Count('id'), min_id=Min('id')).filter(cnt__gt=1)
    deleted = 0
    for d in dupes:
        deleted += Category.objects.filter(name=d['name'], company=company).exclude(id=d['min_id']).delete()[0]
    return Response({'detail': f'{deleted} ta dublikat kategoriya o\'chirildi!', 'deleted': deleted})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_empty_categories(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)
    empty_cats = Category.objects.for_company(company).annotate(cnt=Count('products')).filter(cnt=0)
    deleted = empty_cats.delete()[0]
    return Response({'detail': f'{deleted} ta bo\'sh kategoriya o\'chirildi!', 'deleted': deleted})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_no_stock_products(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)
    products_with_stock = Stock.objects.for_company(company).values_list('product_id', flat=True).distinct()
    no_stock = Product.objects.for_company(company).exclude(id__in=products_with_stock)
    deleted = no_stock.delete()[0]
    return Response({'detail': f'{deleted} ta ombordsiz tovar o\'chirildi!', 'deleted': deleted})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_full(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    cat_qs = Category.objects.for_company(company)
    prod_qs = Product.objects.for_company(company)
    stock_qs = Stock.objects.for_company(company)

    dupes = cat_qs.values('name').annotate(cnt=Count('id'), min_id=Min('id')).filter(cnt__gt=1)
    deleted_cats = 0
    for d in dupes:
        deleted_cats += cat_qs.filter(name=d['name']).exclude(id=d['min_id']).delete()[0]

    empty_cats = cat_qs.annotate(cnt=Count('products')).filter(cnt=0)
    deleted_empty = empty_cats.delete()[0]

    products_with_stock = stock_qs.values_list('product_id', flat=True).distinct()
    no_stock = prod_qs.exclude(id__in=products_with_stock)
    deleted_products = no_stock.delete()[0]

    total = deleted_cats + deleted_empty + deleted_products
    return Response({
        'detail': f'Tozalash tugadi! {deleted_cats} dublikat kategoriya, {deleted_empty} bo\'sh kategoriya, {deleted_products} ombordsiz tovar o\'chirildi. Jami: {total}',
        'deleted_categories': deleted_cats,
        'deleted_empty_categories': deleted_empty,
        'deleted_products': deleted_products,
        'total': total
    })
