from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from accounts.models import Company, Branch
from inventory.models import Product, Stock, Category
from sales.models import Sale, Customer

User = get_user_model()


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class CompanyAdminViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    permission_classes = [IsSuperAdmin]

    def get_serializer_class(self):
        from rest_framework import serializers

        class CompanyAdminSerializer(serializers.ModelSerializer):
            user_count = serializers.SerializerMethodField()
            product_count = serializers.SerializerMethodField()
            sale_count = serializers.SerializerMethodField()
            total_sales = serializers.SerializerMethodField()

            class Meta:
                model = Company
                fields = ['id', 'name', 'phone', 'is_active',
                          'subscription_end_date', 'monthly_fee',
                          'user_count', 'product_count', 'sale_count',
                          'total_sales', 'created_at']

            def get_user_count(self, obj):
                return User.objects.filter(company=obj).count()

            def get_product_count(self, obj):
                return Product.objects.filter(company=obj).count()

            def get_sale_count(self, obj):
                return Sale.objects.filter(company=obj).count()

            def get_total_sales(self, obj):
                return float(Sale.objects.filter(company=obj).aggregate(
                    total=Sum('total_amount'))['total'] or 0)

        return CompanyAdminSerializer


class CompanyStatsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        companies = Company.objects.all()
        stats = []
        for co in companies:
            stats.append({
                'id': co.id,
                'name': co.name,
                'is_active': co.is_active,
                'subscription_end': str(co.subscription_end_date),
                'users': User.objects.filter(company=co).count(),
                'products': Product.objects.filter(company=co).count(),
                'categories': Category.objects.filter(company=co).count(),
                'stocks': Stock.objects.filter(branch__company=co).count(),
                'sales': Sale.objects.filter(company=co).count(),
                'customers': Customer.objects.filter(company=co).count(),
                'total_revenue': float(Sale.objects.filter(company=co).aggregate(
                    total=Sum('total_amount'))['total'] or 0),
            })

        return Response({
            'total_companies': companies.count(),
            'active_companies': companies.filter(is_active=True).count(),
            'total_users': User.objects.count(),
            'companies': stats
        })


class BranchAdminViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id:
            return Branch.objects.filter(company_id=company_id)
        return Branch.objects.all()


class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        if company_id:
            return User.objects.filter(company_id=company_id)
        return User.objects.all()
