from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta
from .models import User, Company, Branch, AuditLog

admin.site.site_header = "DO'KON ERP — Boshqaruv Markazi"
admin.site.site_title = "DO'KON POS Admin"
admin.site.index_title = "Tizim Ma'lumotlari va Modullari"


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0
    verbose_name = "Filial"
    verbose_name_plural = "Kompaniya filiallari"


@admin.action(description="Tanlangan firmalar obunasini 1 oyga uzaytirish")
def extend_subscription_one_month(modeladmin, request, queryset):
    count = 0
    today = timezone.now().date()
    for comp in queryset:
        base_date = comp.subscription_end_date if comp.subscription_end_date and comp.subscription_end_date > today else today
        comp.subscription_end_date = base_date + timedelta(days=30)
        comp.is_active = True
        comp.save(update_fields=['subscription_end_date', 'is_active'])
        count += 1
    modeladmin.message_user(request, f"{count} ta kompaniyaning obunasi 30 kunga uzaytirildi.")


@admin.action(description="Tanlangan firmalarni faollashtirish")
def activate_companies(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} ta kompaniya faollashtirildi.")


@admin.action(description="Tanlangan firmalarni nofaol qilish (Bloklash)")
def deactivate_companies(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} ta kompaniya nofaol qilindi.")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = [BranchInline]
    list_display = ['name', 'phone', 'subscription_badge', 'subscription_end_date', 'days_remaining', 'monthly_fee_fmt', 'is_active']
    list_editable = ['is_active', 'subscription_end_date']
    search_fields = ['name', 'phone']
    list_filter = ['is_active', 'created_at']
    actions = [extend_subscription_one_month, activate_companies, deactivate_companies]

    def subscription_badge(self, obj):
        if obj.is_subscription_valid():
            return mark_safe('<span style="background-color: #198754; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;">Faol</span>')
        return mark_safe('<span style="background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;">Muddati o\'tgan</span>')
    subscription_badge.short_description = "Obuna Holati"

    def days_remaining(self, obj):
        if not obj.subscription_end_date:
            return "—"
        today = timezone.now().date()
        diff = (obj.subscription_end_date - today).days
        if diff > 5:
            return format_html('<span style="color: #198754; font-weight: bold;">{} kun</span>', diff)
        elif diff >= 0:
            return format_html('<span style="color: #ffc107; font-weight: bold;">{} kun (kam qoldi)</span>', diff)
        return format_html('<span style="color: #dc3545; font-weight: bold;">{} kun kechikdi</span>', abs(diff))
    days_remaining.short_description = "Qolgan Vaqt"

    def monthly_fee_fmt(self, obj):
        fee_str = f"{float(obj.monthly_fee or 0):,.0f}"
        return format_html('<strong>{} so\'m</strong>', fee_str)
    monthly_fee_fmt.short_description = "Oylik To'lov"


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'users_count']
    search_fields = ['name', 'company__name']
    list_filter = ['company']

    def users_count(self, obj):
        count = obj.user_set.count()
        return format_html('<span class="badge" style="background-color: #0d6efd; color: white; padding: 2px 6px; border-radius: 4px;">{} xodim</span>', count)
    users_count.short_description = "Xodimlar Soni"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'full_name', 'role_badge', 'company', 'branch', 'is_active']
    list_filter = ['role', 'company', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    fieldsets = UserAdmin.fieldsets + (
        ('Do\'kon va Xodim Roli', {'fields': ('company', 'branch', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Do\'kon va Xodim Roli', {'fields': ('company', 'branch', 'role')}),
    )

    def full_name(self, obj):
        name = obj.get_full_name()
        return name if name else "—"
    full_name.short_description = "F.I.Sh"

    def role_badge(self, obj):
        colors = {
            'ADMIN': '#dc3545',
            'CASHIER': '#198754',
            'VIEWER': '#0d6efd',
        }
        color = colors.get(obj.role, '#6c757d')
        label = obj.get_role_display()
        return format_html('<span style="background-color: {}; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>', color, label)
    role_badge.short_description = "Lavozim"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at_fmt', 'action_badge', 'user', 'company', 'model_name', 'object_repr', 'ip_address']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'object_repr', 'ip_address']
    readonly_fields = ['created_at', 'action', 'user', 'company', 'model_name', 'object_id', 'object_repr', 'changes', 'ip_address']

    def created_at_fmt(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_fmt.short_description = "Vaqt"

    def action_badge(self, obj):
        colors = {
            'CREATE': '#198754',
            'UPDATE': '#ffc107',
            'DELETE': '#dc3545',
            'LOGIN': '#0d6efd',
            'LOGOUT': '#6c757d',
        }
        text_colors = {
            'UPDATE': 'black'
        }
        color = colors.get(obj.action, '#6c757d')
        text_color = text_colors.get(obj.action, 'white')
        return format_html('<span style="background-color: {}; color: {}; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>', color, text_color, obj.get_action_display())
    action_badge.short_description = "Harakat"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False