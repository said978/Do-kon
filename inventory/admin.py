from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.db.models import Sum, F
from decimal import Decimal
import openpyxl
from .models import Product, Stock, Category


class StockInline(admin.TabularInline):
    model = Stock
    extra = 0
    fields = ['branch', 'quantity']
    verbose_name = "Ombor qoldig'i"
    verbose_name_plural = "Filiallar bo'yicha qoldiqlar"


@admin.action(description="Tanlangan tovarlarni Excel formatida yuklab olish")
def export_products_to_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tovarlar"
    ws.append(['ID', 'Tovar Nomi', 'Shtrix-kod', 'Kategoriya', 'Tannarx (so\'m)', 'Sotish Narxi (so\'m)', 'Jami Qoldiq'])

    for p in queryset.select_related('category'):
        total_stock = p.stock_set.aggregate(s=Sum('quantity'))['s'] or 0
        ws.append([
            p.id,
            p.name,
            p.barcode,
            p.category.name if p.category else "Umumiy",
            float(p.cost_price or 0),
            float(p.selling_price or 0),
            float(total_stock)
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=tovarlar_royxati.xlsx'
    wb.save(response)
    return response


@admin.action(description="Sotish narxini 5 foizga (+5%%) oshirish")
def increase_price_5_percent(modeladmin, request, queryset):
    count = 0
    for p in queryset:
        if p.selling_price:
            p.selling_price = (p.selling_price * Decimal('1.05')).quantize(Decimal('1.00'))
            p.save(update_fields=['selling_price'])
            count += 1
    modeladmin.message_user(request, f"{count} ta tovarning sotish narxi 5% ga oshirildi.")


@admin.action(description="Sotish narxini 5 foizga (-5%%) tushirish (Chegirma)")
def decrease_price_5_percent(modeladmin, request, queryset):
    count = 0
    for p in queryset:
        if p.selling_price:
            p.selling_price = (p.selling_price * Decimal('0.95')).quantize(Decimal('1.00'))
            p.save(update_fields=['selling_price'])
            count += 1
    modeladmin.message_user(request, f"{count} ta tovarning sotish narxi 5% ga arzonlashtirildi.")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'products_count']
    search_fields = ['name']
    list_filter = ['company']

    def products_count(self, obj):
        count = obj.product_set.count()
        return format_html('<span class="badge" style="background-color: #0d6efd; color: white; padding: 3px 8px; border-radius: 4px;">{} ta tovar</span>', count)
    products_count.short_description = "Tovarlar Soni"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [StockInline]
    list_display = ['name', 'barcode_badge', 'category', 'cost_price', 'selling_price', 'margin_percent', 'total_stock_badge']
    list_editable = ['cost_price', 'selling_price']
    search_fields = ['name', 'barcode']
    list_filter = ['category', 'company']
    actions = [export_products_to_excel, increase_price_5_percent, decrease_price_5_percent]

    def barcode_badge(self, obj):
        if obj.barcode:
            return format_html('<code>{}</code>', obj.barcode)
        return mark_safe('<span style="color: #dc3545; font-weight: bold;">Shtrix-kodsiz</span>')
    barcode_badge.short_description = "Shtrix-kod"

    def margin_percent(self, obj):
        if obj.cost_price and obj.selling_price and obj.cost_price > 0:
            margin = ((obj.selling_price - obj.cost_price) / obj.cost_price) * 100
            color = "#198754" if margin >= 0 else "#dc3545"
            margin_str = f"+{float(margin):.1f}%"
            return format_html('<strong style="color: {};">{}</strong>', color, margin_str)
        return "—"
    margin_percent.short_description = "Marja (%)"

    def total_stock_badge(self, obj):
        total = obj.stock_set.aggregate(s=Sum('quantity'))['s'] or 0
        total_float = float(total)
        color = "#198754" if total_float > 5 else ("#ffc107" if total_float > 0 else "#dc3545")
        text_color = "black" if color == "#ffc107" else "white"
        return format_html('<span style="background-color: {}; color: {}; padding: 2px 7px; border-radius: 4px; font-weight: bold;">{} dona</span>', color, text_color, total_float)
    total_stock_badge.short_description = "Umumiy Qoldiq"

    def save_model(self, request, obj, form, change):
        if not obj.company_id and getattr(request.user, 'company', None):
            obj.company = request.user.company
        super().save_model(request, obj, form, change)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'branch', 'quantity_badge', 'stock_total_value']
    list_editable = ['quantity_badge'] if False else []
    search_fields = ['product__name', 'product__barcode', 'branch__name']
    list_filter = ['branch', 'product__category']

    def quantity_badge(self, obj):
        qty = float(obj.quantity or 0)
        color = "#198754" if qty > 5 else ("#ffc107" if qty > 0 else "#dc3545")
        text_color = "black" if color == "#ffc107" else "white"
        return format_html('<strong style="background-color: {}; color: {}; padding: 2px 7px; border-radius: 4px;">{} dona</strong>', color, text_color, qty)
    quantity_badge.short_description = "Ombor Qoldig'i"

    def stock_total_value(self, obj):
        qty = float(obj.quantity or 0)
        price = float(obj.product.selling_price or 0)
        total = qty * price
        total_str = f"{total:,.2f}"
        return format_html('<strong>{} so\'m</strong>', total_str)
    stock_total_value.short_description = "Qoldiq Qiymati"

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'company_id') and not obj.company_id and getattr(request.user, 'company', None):
            obj.company = request.user.company
        if not obj.branch_id and getattr(request.user, 'branch', None):
            obj.branch = request.user.branch
        super().save_model(request, obj, form, change)