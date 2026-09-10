from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
import openpyxl
from .models import Sale, SaleItem, Customer, DebtPayment, SaleReturn


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    fields = ['product', 'quantity', 'cost_price', 'price', 'get_item_total', 'get_item_profit']
    readonly_fields = ['get_item_total', 'get_item_profit']
    verbose_name = "Sotilgan tovar"
    verbose_name_plural = "Sotilgan tovarlar ro'yxati"

    def get_item_total(self, obj):
        if obj.quantity and obj.price:
            total = float(obj.quantity * obj.price)
            return f"{total:,.2f} so'm"
        return "0 so'm"
    get_item_total.short_description = "Jami Summa"

    def get_item_profit(self, obj):
        if obj.quantity and obj.price:
            cost = obj.cost_price or 0
            profit = float((obj.price - cost) * obj.quantity)
            color = "green" if profit >= 0 else "red"
            profit_str = f"{profit:,.2f}"
            return format_html('<span style="color: {}; font-weight: bold;">{} so\'m</span>', color, profit_str)
        return "0 so'm"
    get_item_profit.short_description = "Sof Foyda"


@admin.action(description="Tanlangan savdolarni Excel formatida yuklab olish")
def export_sales_to_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Savdolar"
    ws.append(['Chek ID', 'Sana va Vaqt', 'Filial', 'Kassir', 'Mijoz', 'To\'lov Turi', 'Jami Summa', 'Tannarx', 'Sof Foyda'])

    for s in queryset.select_related('branch', 'cashier', 'customer'):
        ws.append([
            f"#{s.id}",
            s.created_at.strftime('%Y-%m-%d %H:%M'),
            s.branch.name if s.branch else "Asosiy",
            s.cashier.username if s.cashier else "Admin",
            s.customer.name if s.customer else "Ommaviy mijoz",
            s.get_payment_method_display() if hasattr(s, 'get_payment_method_display') else s.payment_method,
            float(s.total_amount or 0),
            float(s.total_cost or 0),
            float(s.net_profit or 0)
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=savdolar_hisoboti.xlsx'
    wb.save(response)
    return response


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    inlines = [SaleItemInline]
    list_display = ('id_display', 'created_at_fmt', 'branch', 'cashier', 'customer_display', 'payment_badge', 'total_amount_fmt', 'net_profit_fmt')
    list_filter = ('payment_method', 'branch', 'created_at')
    search_fields = ('id', 'customer__name', 'customer__phone', 'cashier__username')
    date_hierarchy = 'created_at'
    actions = [export_sales_to_excel]

    def id_display(self, obj):
        return format_html('<strong>Chek #{}</strong>', obj.id)
    id_display.short_description = "Chek №"

    def created_at_fmt(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_fmt.short_description = "Savdo Vaqti"

    def customer_display(self, obj):
        return obj.customer.name if obj.customer else mark_safe('<span style="color: #6c757d;">Ommaviy</span>')
    customer_display.short_description = "Xaridor"

    def payment_badge(self, obj):
        colors = {
            'CASH': '#198754',
            'CARD': '#0d6efd',
            'DEBT': '#dc3545',
        }
        labels = {
            'CASH': 'Naqd pul',
            'CARD': 'Plastik karta',
            'DEBT': 'Nasiya / Qarz',
        }
        color = colors.get(obj.payment_method, '#6c757d')
        label = labels.get(obj.payment_method, obj.payment_method)
        return format_html('<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>', color, label)
    payment_badge.short_description = "To'lov Usuli"

    def total_amount_fmt(self, obj):
        total_str = f"{float(obj.total_amount or 0):,.2f}"
        return format_html('<strong>{} so\'m</strong>', total_str)
    total_amount_fmt.short_description = "Jami Summa"

    def net_profit_fmt(self, obj):
        profit = float(obj.net_profit or 0)
        color = "green" if profit >= 0 else "red"
        profit_str = f"{profit:,.2f}"
        return format_html('<span style="color: {}; font-weight: bold;">{} so\'m</span>', color, profit_str)
    net_profit_fmt.short_description = "Sof Foyda"


@admin.action(description="Tanlangan mijozlarni Excel formatida yuklab olish")
def export_customers_to_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mijozlar"
    ws.append(['ID', 'Mijoz F.I.Sh', 'Telefon', 'Qarzdorlik Balansi', 'Kompaniya', 'Qo\'shilgan Sana'])

    for c in queryset.select_related('company'):
        ws.append([
            c.id,
            c.name,
            c.phone,
            float(c.debt_balance or 0),
            c.company.name if c.company else "",
            c.created_at.strftime('%Y-%m-%d')
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=mijozlar_royxati.xlsx'
    wb.save(response)
    return response


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'debt_balance_badge', 'company', 'created_at')
    search_fields = ('name', 'phone')
    list_filter = ('company',)
    actions = [export_customers_to_excel]

    def debt_balance_badge(self, obj):
        debt = float(obj.debt_balance or 0)
        if debt > 0:
            debt_str = f"{debt:,.2f}"
            return format_html('<span style="background-color: #dc3545; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold;">{} so\'m</span>', debt_str)
        return mark_safe('<span style="color: #198754; font-weight: bold;">Qarzi yo\'q</span>')
    debt_balance_badge.short_description = "Qarzdorlik"


@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'amount_fmt', 'payment_method_badge', 'cashier', 'branch', 'created_at')
    search_fields = ('customer__name', 'cashier__username')
    list_filter = ('payment_method', 'company', 'branch', 'created_at')

    def amount_fmt(self, obj):
        amt_str = f"{float(obj.amount or 0):,.2f}"
        return format_html('<strong style="color: #198754;">+{} so\'m</strong>', amt_str)
    amount_fmt.short_description = "To'langan Summa"

    def payment_method_badge(self, obj):
        label = "Naqd pul" if obj.payment_method == 'CASH' else "Plastik karta"
        color = "#198754" if obj.payment_method == 'CASH' else "#0d6efd"
        return format_html('<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">{}</span>', color, label)
    payment_method_badge.short_description = "To'lov Turi"


@admin.register(SaleReturn)
class SaleReturnAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'product', 'quantity', 'refund_amount_fmt', 'cashier', 'branch', 'created_at')
    list_filter = ('branch', 'created_at')
    search_fields = ('product__name', 'sale__id', 'cashier__username')

    def refund_amount_fmt(self, obj):
        ref_str = f"{float(obj.refund_amount or 0):,.2f}"
        return format_html('<strong style="color: #dc3545;">-{} so\'m</strong>', ref_str)
    refund_amount_fmt.short_description = "Qaytarilgan Pul"