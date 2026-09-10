from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from accounts.models import Company
from sales.models import Sale


def get_company(request):
    return getattr(request, 'company', None)


class BillingSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    monthly_revenue = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'is_active', 'subscription_end_date',
                  'monthly_fee', 'days_remaining', 'is_valid',
                  'monthly_revenue']

    def get_days_remaining(self, obj):
        if obj.subscription_end_date:
            delta = obj.subscription_end_date - timezone.now().date()
            return max(0, delta.days)
        return 0

    def get_is_valid(self, obj):
        return obj.is_subscription_valid()

    def get_monthly_revenue(self, obj):
        today = timezone.now().date()
        month_start = today.replace(day=1)
        return float(Sale.objects.filter(
            company=obj,
            created_at__date__gte=month_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_info(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    serializer = BillingSerializer(company)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extend_subscription(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    days = request.data.get('days', 30)
    company.subscription_end_date = timezone.now().date() + timezone.timedelta(days=days)
    company.is_active = True
    company.save()

    return Response({
        'detail': f'Obuna {days} kunga uzaytirildi!',
        'new_end_date': str(company.subscription_end_date),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    today = timezone.now().date()
    history = []
    for i in range(12):
        month_date = today.replace(day=1) - timezone.timedelta(days=30 * i)
        month_start = month_date.replace(day=1)
        if i == 0:
            month_end = today
        else:
            month_end = (month_start + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)

        revenue = float(Sale.objects.filter(
            company=company,
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).aggregate(total=Sum('total_amount'))['total'] or 0)

        history.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': revenue,
            'fee': float(company.monthly_fee),
            'paid': revenue >= float(company.monthly_fee),
        })

    return Response(history)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_active(request):
    company = get_company(request)
    if not company:
        return Response({'detail': 'Firma aniqlanmadi!'}, status=400)

    company.is_active = not company.is_active
    company.save()

    return Response({
        'detail': f'Firma {"faollashtirildi" if company.is_active else "to\'xtatildi"}!',
        'is_active': company.is_active,
    })
