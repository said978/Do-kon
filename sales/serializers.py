from decimal import Decimal
from rest_framework import serializers
from inventory.models import Stock
from .models import Sale, SaleItem, Customer, DebtPayment


class TenantSerializerMixin:
    def create(self, validated_data):
        request = self.context.get('request')
        company = getattr(request, 'company', None)
        if not company and request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            company = getattr(request.user, 'company', None)
        if company:
            validated_data['company'] = company
        return super().create(validated_data)


class CustomerSerializer(TenantSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'debt_balance', 'created_at']
        read_only_fields = ['debt_balance', 'created_at']


class DebtPaymentSerializer(TenantSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = DebtPayment
        fields = ['id', 'branch', 'customer', 'cashier', 'amount', 'payment_method', 'created_at']
        read_only_fields = ['branch', 'cashier', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        company = getattr(request, 'company', None)
        if not company and request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            company = getattr(request.user, 'company', None)
        if company:
            validated_data['company'] = company

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['cashier'] = request.user
            if not validated_data.get('branch') and getattr(request.user, 'branch', None):
                validated_data['branch'] = request.user.branch

        if not validated_data.get('branch') and company:
            validated_data['branch'] = company.branches.first()

        payment = super().create(validated_data)

        # Mijozning qarz balansini kamaytirish
        customer = payment.customer
        if customer and payment.amount:
            curr_debt = Decimal(str(customer.debt_balance or 0))
            pay_amt = Decimal(str(payment.amount or 0))
            customer.debt_balance = max(Decimal('0.00'), curr_debt - pay_amt)
            customer.save(update_fields=['debt_balance'])

        return payment


class SaleItemSerializer(serializers.ModelSerializer):
    sale = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SaleItem
        fields = ['id', 'sale', 'product', 'quantity', 'cost_price', 'price']


class SaleSerializer(TenantSerializerMixin, serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ['id', 'branch', 'cashier', 'customer', 'is_debt', 'payment_method',
                  'total_amount', 'total_cost', 'net_profit', 'created_at', 'items']
        read_only_fields = ['cashier', 'total_cost', 'net_profit', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')

        company = getattr(request, 'company', None)
        if not company and request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            company = getattr(request.user, 'company', None)
        if company:
            validated_data['company'] = company

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['cashier'] = request.user
            if not validated_data.get('branch') and getattr(request.user, 'branch', None):
                validated_data['branch'] = request.user.branch

        if not validated_data.get('branch') and company:
            validated_data['branch'] = company.branches.first()

        payment_method = validated_data.get('payment_method', 'CASH')
        if payment_method == 'DEBT':
            validated_data['is_debt'] = True

        sale = Sale.objects.create(**validated_data)
        branch = sale.branch

        total_cost = Decimal('0.00')

        for item_data in items_data:
            product = item_data.get('product')
            qty = Decimal(str(item_data.get('quantity', 1)))

            cost_price = item_data.get('cost_price')
            if cost_price is None and product:
                cost_price = getattr(product, 'cost_price', Decimal('0.00')) or Decimal('0.00')
                item_data['cost_price'] = cost_price
            else:
                cost_price = Decimal(str(cost_price or 0))

            total_cost += (cost_price * qty)
            SaleItem.objects.create(sale=sale, **item_data)

            # Ombor qoldig'ini avtomatik kamaytirish
            if branch and product:
                stock, _ = Stock.objects.get_or_create(
                    branch=branch,
                    product=product,
                    defaults={'quantity': Decimal('0.00')}
                )
                curr_stock = Decimal(str(stock.quantity or 0))
                stock.quantity = curr_stock - qty
                stock.save(update_fields=['quantity'])

        # Real tannarx va sof foydani hisoblab saqlash
        sale_total = Decimal(str(sale.total_amount or 0))
        sale.total_cost = total_cost
        sale.net_profit = sale_total - total_cost
        sale.save(update_fields=['total_cost', 'net_profit'])

        # Agar nasiya bo'lsa va mijoz biriktirilgan bo'lsa, mijoz qarzini oshirish
        if sale.payment_method == 'DEBT' and sale.customer:
            cust = sale.customer
            cust.debt_balance = Decimal(str(cust.debt_balance or 0)) + sale_total
            cust.save(update_fields=['debt_balance'])

        return sale

