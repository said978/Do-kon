from rest_framework import serializers
from .models import Category, Product, Stock


from decimal import Decimal


class TenantSerializerMixin:
    def create(self, validated_data):
        request = self.context.get('request')
        company = getattr(request, 'company', None)
        if not company and request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            company = getattr(request.user, 'company', None)
        if company:
            validated_data['company'] = company
        return super().create(validated_data)


class CategorySerializer(TenantSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(TenantSerializerMixin, serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    initial_quantity = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True, required=False, default=0)

    class Meta:
        model = Product
        fields = ['id', 'name', 'barcode', 'cost_price', 'selling_price', 'category', 'category_name', 'initial_quantity']

    def create(self, validated_data):
        initial_quantity = validated_data.pop('initial_quantity', Decimal('0.00'))
        product = super().create(validated_data)

        # Filial omboriga boshlang'ich qoldiqni saqlash
        request = self.context.get('request')
        branch = None
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            branch = getattr(request.user, 'branch', None)
        if not branch and product.company:
            branch = product.company.branches.first()

        if branch:
            Stock.objects.update_or_create(
                branch=branch,
                product=product,
                defaults={'quantity': Decimal(str(initial_quantity or 0))}
            )

        return product


class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    barcode = serializers.CharField(source='product.barcode', read_only=True)
    selling_price = serializers.DecimalField(source='product.selling_price', max_digits=12, decimal_places=2, read_only=True)
    cost_price = serializers.DecimalField(source='product.cost_price', max_digits=12, decimal_places=2, read_only=True)
    category_name = serializers.CharField(source='product.category.name', default='Umumiy', read_only=True)

    class Meta:
        model = Stock
        fields = ['id', 'product', 'product_name', 'barcode', 'selling_price', 'cost_price', 'quantity', 'category_name']
