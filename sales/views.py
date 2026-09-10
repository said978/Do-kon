from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Avg, Count, F
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import openpyxl
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

from .models import Sale, SaleItem, Customer, DebtPayment
from .serializers import SaleSerializer, CustomerSerializer, DebtPaymentSerializer
from inventory.models import Product, Stock


def get_company(request):
    company = getattr(request, 'company', None)
    if not company and hasattr(request, 'user') and request.user and request.user.is_authenticated:
        company = getattr(request.user, 'company', None)
    return company


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().order_by('-id')
    serializer_class = SaleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        company = get_company(self.request)
        return Sale.objects.for_company(company).order_by('-id')

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = get_company(self.request)
        return Customer.objects.for_company(company)

class DebtPaymentViewSet(viewsets.ModelViewSet):
    queryset = DebtPayment.objects.all()
    serializer_class = DebtPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        company = get_company(self.request)
        return DebtPayment.objects.for_company(company)

# ==========================================
# 2. HTML SAHIFALAR (TEMPLATES)
# ==========================================
def pos_view(request):
    return render(request, 'pos.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def customers_page_view(request):
    return render(request, 'customers.html')

def reports_view(request):
    return render(request, 'reports.html')

def general_report_page_view(request):
    return render(request, 'general_trade_report.html')

def in_out_report_page_view(request):
    return render(request, 'in_out_report.html')

def cash_flow_report_view(request):
    return render(request, 'reports/cash_flow.html')

def products_report_view(request):
    return render(request, 'reports/products_report.html')

def categories_report_view(request):
    return render(request, 'reports/categories_report.html')

def staff_report_view(request):
    return render(request, 'reports/staff_report.html')

def customers_report_view(request):
    return render(request, 'reports/customers_report.html')

def customer_turnover_report_view(request):
    return render(request, 'reports/customer_turnover.html')

def suppliers_report_view(request):
    return render(request, 'reports/suppliers_report.html')

def staff_turnover_report_view(request):
    return render(request, 'reports/staff_turnover.html')

def payments_report_view(request):
    return render(request, 'reports/payments_report.html')

def product_sales_report_view(request):
    return render(request, 'reports/product_sales.html')

# ==========================================
# 3. YORDAMCHI API'LAR
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user_info(request):
    company = get_company(request)
    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'company': company.name if company else None,
        'role': request.user.role,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    company = get_company(request)
    sales = Sale.objects.for_company(company)

    today = timezone.localdate()
    today_sales = sales.filter(created_at__date=today)

    today_total = float(today_sales.aggregate(s=Sum('total_amount'))['s'] or 0)
    today_profit = float(today_sales.aggregate(s=Sum('net_profit'))['s'] or 0)
    today_count = today_sales.count()

    today_cash = float(today_sales.filter(payment_method='CASH').aggregate(s=Sum('total_amount'))['s'] or 0)
    today_card = float(today_sales.filter(payment_method='CARD').aggregate(s=Sum('total_amount'))['s'] or 0)
    today_debt = float(today_sales.filter(payment_method='DEBT').aggregate(s=Sum('total_amount'))['s'] or 0)

    total_debt = float(Customer.objects.for_company(company).aggregate(s=Sum('debt_balance'))['s'] or 0)

    # Oxirgi 7 kunlik savdo dinamikasi (Chart.js)
    chart_labels = []
    chart_data = []
    chart_profit = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_sales = sales.filter(created_at__date=day)
        day_total = float(day_sales.aggregate(s=Sum('total_amount'))['s'] or 0)
        day_prof = float(day_sales.aggregate(s=Sum('net_profit'))['s'] or 0)

        chart_labels.append(day.strftime('%d-%b'))
        chart_data.append(day_total)
        chart_profit.append(day_prof)

    # Kam qolgan tovarlar (Qoldig'i 5 yoki undan kam bo'lgan tovarlar)
    low_stocks_qs = Stock.objects.filter(
        branch__company=company,
        quantity__lte=5
    ).select_related('product', 'branch').order_by('quantity')[:10]

    low_stocks = [{
        'product_name': s.product.name,
        'barcode': s.product.barcode,
        'quantity': float(s.quantity),
        'selling_price': float(s.product.selling_price or 0),
        'branch_name': s.branch.name
    } for s in low_stocks_qs]

    # So'nggi 5 ta savdo (Chek)
    recent_sales = [{
        'id': s.id,
        'time': s.created_at.strftime('%H:%M'),
        'total': float(s.total_amount),
        'payment_method': 'Naqd' if s.payment_method == 'CASH' else ('Karta' if s.payment_method == 'CARD' else 'Nasiya'),
        'cashier': s.cashier.username if s.cashier else 'Admin',
        'customer': s.customer.name if s.customer else 'Ommaviy mijoz'
    } for s in sales.select_related('cashier', 'customer').order_by('-id')[:5]]

    return Response({
        'today_total': today_total,
        'today_profit': today_profit,
        'today_count': today_count,
        'today_cash': today_cash,
        'today_card': today_card,
        'today_debt': today_debt,
        'total_debt': total_debt,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'chart_profit': chart_profit,
        'low_stocks': low_stocks,
        'recent_sales': recent_sales,
        # Eski versiyalar uchun moslik
        'total_sales': today_total,
        'total_count': today_count
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cashier_shift_report(request):
    return Response({'status': 'ok'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_sales_excel(request):
    company = get_company(request)
    sales = Sale.objects.for_company(company)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['ID', 'Vaqt', 'Summa', 'To\'lov turi'])
    for s in sales:
        ws.append([s.id, s.created_at.strftime('%Y-%m-%d %H:%M'), float(s.total_amount), s.payment_method])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales.xlsx'
    wb.save(response)
    return response

# ==========================================
# 4. HISOBOTLAR API'LARI
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def general_report_api(request):
    company = get_company(request)
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    sales = Sale.objects.for_company(company)
    if start and end:
        sales = sales.filter(created_at__date__gte=start, created_at__date__lte=end)

    total_sales = float(sales.aggregate(total=Sum('total_amount'))['total'] or 0)
    net_profit = float(sales.aggregate(total=Sum('net_profit'))['total'] or 0)
    receipt_count = sales.count()
    avg_receipt = (total_sales / receipt_count) if receipt_count > 0 else 0

    cash_total = float(sales.filter(payment_method='CASH').aggregate(total=Sum('total_amount'))['total'] or 0)
    card_total = float(sales.filter(payment_method='CARD').aggregate(total=Sum('total_amount'))['total'] or 0)
    debt_total = float(sales.filter(payment_method='DEBT').aggregate(total=Sum('total_amount'))['total'] or 0)

    sales_list = [{
        'id': s.id,
        'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
        'cashier_name': s.cashier.username if s.cashier else 'Admin',
        'customer_name': s.customer.name if s.customer else 'Ommaviy mijoz',
        'branch_name': s.branch.name if s.branch else 'Asosiy filial',
        'payment_method': s.payment_method,
        'payment_method_display': 'Naqd' if s.payment_method == 'CASH' else ('Karta' if s.payment_method == 'CARD' else 'Nasiya'),
        'total_amount': float(s.total_amount),
        'items': [{
            'product_name': item.product.name if item.product else 'Nomsiz tovar',
            'barcode': item.product.barcode if item.product else '',
            'quantity': float(item.quantity),
            'price': float(item.price),
            'total': float(item.price * item.quantity),
        } for item in s.items.select_related('product').all()]
    } for s in sales.select_related('cashier', 'customer', 'branch').prefetch_related('items__product').order_by('-id')]

    return Response({
        'total_sales': total_sales,
        'net_profit': net_profit,
        'receipt_count': receipt_count,
        'avg_receipt': avg_receipt,
        'cash_total': cash_total,
        'card_total': card_total,
        'split_total': 0,
        'debt_total': debt_total,
        'sales_list': sales_list
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def in_out_report_api(request):
    company = get_company(request)
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    sales = Sale.objects.for_company(company)
    if start and end:
        sales = sales.filter(created_at__date__gte=start, created_at__date__lte=end)

    total_income = float(sales.aggregate(total=Sum('total_amount'))['total'] or 0)
    transactions = [{
        'id': s.id,
        'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
        'type': 'INCOME',
        'category': 'Savdo tushumi',
        'amount': float(s.total_amount),
        'description': f"Chek #{s.id} orqali savdo tushumi",
        'user_name': s.cashier.username if s.cashier else 'Admin'
    } for s in sales.order_by('-id')]

    return Response({
        'total_income': total_income,
        'total_expense': 0,
        'net_balance': total_income,
        'transactions': transactions
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cash_flow_report_api(request):
    company = get_company(request)
    sales = Sale.objects.for_company(company)
    total_sales = float(sales.aggregate(total=Sum('total_amount'))['total'] or 0)
    return Response([{
        'kassa_name': 'Asosiy Kassa #1',
        'start_balance': 0,
        'income': total_sales,
        'expense': 0,
        'end_balance': total_sales
    }])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def products_report_api(request):
    company = get_company(request)
    if company:
        items = SaleItem.objects.filter(sale__company=company).values('product__name').annotate(
            total_qty=Sum('quantity'),
            total_sum=Sum(F('quantity') * F('price')),
            avg_price=Avg('price')
        ).order_by('-total_sum')
    else:
        items = SaleItem.objects.none()

    return Response([{
        'name': item['product__name'] or 'Tovar',
        'quantity': item['total_qty'] or 0,
        'avg_price': float(item['avg_price'] or 0),
        'total_sum': float(item['total_sum'] or 0)
    } for item in items])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categories_report_api(request):
    company = get_company(request)
    if company:
        items = SaleItem.objects.filter(sale__company=company).values('product__category__name').annotate(
            total_sum=Sum(F('quantity') * F('price'))
        ).order_by('-total_sum')
        overall = float(Sale.objects.filter(company=company).aggregate(total=Sum('total_amount'))['total'] or 1)
    else:
        items = SaleItem.objects.none()
        overall = 1

    return Response([{
        'category': item['product__category__name'] or 'Umumiy',
        'total_sum': float(item['total_sum'] or 0),
        'percent': round((float(item['total_sum'] or 0) / overall) * 100, 1) if overall > 0 else 0
    } for item in items])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payments_report_api(request):
    company = get_company(request)
    sales = Sale.objects.for_company(company)
    cash = sales.filter(payment_method='CASH').aggregate(total=Sum('total_amount'), count=Count('id'))
    card = sales.filter(payment_method='CARD').aggregate(total=Sum('total_amount'), count=Count('id'))
    debt = sales.filter(payment_method='DEBT').aggregate(total=Sum('total_amount'), count=Count('id'))

    return Response([
        {'method': 'Naqd pul', 'count': cash['count'] or 0, 'total': float(cash['total'] or 0)},
        {'method': 'Plastik karta', 'count': card['count'] or 0, 'total': float(card['total'] or 0)},
        {'method': 'Nasiya / Qarz', 'count': debt['count'] or 0, 'total': float(debt['total'] or 0)},
    ])

# ==========================================
# 5. SHTRIX-KOD
# ==========================================
def generate_barcode_image(request, code):
    EAN = barcode.get_barcode_class('code128')
    ean = EAN(str(code), writer=ImageWriter())
    buffer = BytesIO()
    ean.write(buffer)
    return HttpResponse(buffer.getvalue(), content_type="image/png")

def print_barcode_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.GET.get('quantity', 1))
    context = {
        'product': product,
        'quantity_range': range(quantity),
        'barcode_url': f"/api/sales/barcode-img/{product.barcode}/"
    }
    return render(request, 'barcode_print.html', context)
