from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from accounts.models import Company, Branch
from inventory.models import Product, Stock, Category
from sales.models import Sale, Customer, SaleItem

User = get_user_model()


def get_company(request):
    company = getattr(request, 'company', None)
    if not company and hasattr(request, 'user') and request.user and request.user.is_authenticated:
        company = getattr(request.user, 'company', None)
    return company


class CompanyProfileSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    branch_count = serializers.SerializerMethodField()
    sale_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'phone', 'is_active',
                  'subscription_end_date', 'monthly_fee',
                  'currency', 'timezone', 'language',
                  'user_count', 'product_count', 'branch_count',
                  'sale_count', 'total_revenue', 'created_at']

    def get_user_count(self, obj):
        return User.objects.filter(company=obj).count()

    def get_product_count(self, obj):
        return Product.objects.filter(company=obj).count()

    def get_branch_count(self, obj):
        return Branch.objects.filter(company=obj).count()

    def get_sale_count(self, obj):
        return Sale.objects.filter(company=obj).count()

    def get_total_revenue(self, obj):
        return float(Sale.objects.filter(company=obj).aggregate(
            total=Sum('total_amount'))['total'] or 0)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def company_profile(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    if request.method == 'GET':
        serializer = CompanyProfileSerializer(company)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data
        company.name = data.get('name', company.name)
        company.phone = data.get('phone', company.phone)
        company.currency = data.get('currency', company.currency)
        company.timezone = data.get('timezone', company.timezone)
        company.language = data.get('language', company.language)
        company.save()
        return Response({'detail': 'Profil yangilandi!'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_settings(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    if request.method == 'GET':
        return Response({
            'currency': company.currency,
            'timezone': company.timezone,
            'language': company.language,
        })

    elif request.method == 'PUT':
        data = request.data
        company.currency = data.get('currency', company.currency)
        company.timezone = data.get('timezone', company.timezone)
        company.language = data.get('language', company.language)
        company.save()
        return Response({'detail': 'Sozlamalar yangilandi!'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_dashboard(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    sales = Sale.objects.filter(company=company)
    today = sale_today(sales)
    week = sale_week(sales)
    month = sale_month(sales)

    return Response({
        'company': company.name,
        'today': {
            'count': today['count'],
            'total': float(today['total']),
        },
        'week': {
            'count': week['count'],
            'total': float(week['total']),
        },
        'month': {
            'count': month['count'],
            'total': float(month['total']),
        },
        'totals': {
            'products': Product.objects.filter(company=company).count(),
            'categories': Category.objects.filter(company=company).count(),
            'customers': Customer.objects.filter(company=company).count(),
            'users': User.objects.filter(company=company).count(),
        }
    })


def sale_today(sales):
    from django.utils import timezone
    today = timezone.now().date()
    qs = sales.filter(created_at__date=today)
    return {
        'count': qs.count(),
        'total': qs.aggregate(total=Sum('total_amount'))['total'] or 0,
    }


def sale_week(sales):
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    qs = sales.filter(created_at__date__gte=week_ago, created_at__date__lte=today)
    return {
        'count': qs.count(),
        'total': qs.aggregate(total=Sum('total_amount'))['total'] or 0,
    }


def sale_month(sales):
    from django.utils import timezone
    today = timezone.now().date()
    month_start = today.replace(day=1)
    qs = sales.filter(created_at__date__gte=month_start, created_at__date__lte=today)
    return {
        'count': qs.count(),
        'total': qs.aggregate(total=Sum('total_amount'))['total'] or 0,
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_branches(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    branches = Branch.objects.filter(company=company)
    data = [{
        'id': b.id,
        'name': b.name,
    } for b in branches]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def company_invite_user(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role', 'CASHIER')
    branch_id = request.data.get('branch_id')

    if not username or not password:
        return Response({'detail': 'Login va parol kiritish shart!'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'detail': 'Bu login allaqachon mavjud!'}, status=400)

    branch = None
    if branch_id:
        branch = Branch.objects.filter(id=branch_id, company=company).first()

    user = User.objects.create_user(
        username=username,
        password=password,
        company=company,
        branch=branch,
        role=role,
    )

    return Response({
        'detail': f'{username} muvaffaqiyatli yaratildi!',
        'user_id': user.id,
    })
