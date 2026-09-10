"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from accounts.views import login_page, login_session, init_db
from accounts import tenant_api
from accounts import tenant_invitations
from accounts import tenant_billing
from accounts import tenant_notifications
from accounts import tenant_audit
from accounts import tenant_export
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect

def logout_view(request):
    auth_logout(request)
    return redirect('/login/')

urlpatterns = [
    # Bosh sahifa → Login
    path('', lambda r: redirect('/login/')),

    # Bitta Login Sahifasi
    path('login/', login_page, name='login_page'),
    path('login-session/', login_session, name='login_session'),
    path('logout/', logout_view, name='logout'),
    path('api/init-db/', init_db, name='init_db'),

    # Admin Panel
    path('admin/', admin.site.urls),

    # Auth (JWT Login) API lar
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Biznes API modullari
    path('api/inventory/', include('inventory.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/admin-panel/', include('accounts.urls')),

    # Tenant API (har firma o'zini boshqaradi)
    path('api/tenant/profile/', tenant_api.company_profile, name='company-profile'),
    path('api/tenant/settings/', tenant_api.company_settings, name='company-settings'),
    path('api/tenant/dashboard/', tenant_api.company_dashboard, name='company-dashboard'),
    path('api/tenant/branches/', tenant_api.company_branches, name='company-branches'),
    path('api/tenant/invite-user/', tenant_api.company_invite_user, name='company-invite-user'),
    path('api/tenant/users/', tenant_invitations.company_users, name='company-users'),
    path('api/tenant/users/<int:user_id>/', tenant_invitations.delete_user, name='company-delete-user'),
    path('api/tenant/send-invitation/', tenant_invitations.send_invitation, name='company-send-invitation'),
    path('api/tenant/quick-create/', tenant_invitations.quick_create_user, name='company-quick-create'),
    path('api/tenant/billing/', tenant_billing.billing_info, name='company-billing'),
    path('api/tenant/billing/extend/', tenant_billing.extend_subscription, name='company-extend-subscription'),
    path('api/tenant/billing/history/', tenant_billing.payment_history, name='company-payment-history'),
    path('api/tenant/billing/toggle/', tenant_billing.toggle_active, name='company-toggle-active'),
    path('api/tenant/notifications/', tenant_notifications.notifications, name='company-notifications'),
    path('api/tenant/alerts-summary/', tenant_notifications.alerts_summary, name='company-alerts-summary'),
    path('api/tenant/audit-log/', tenant_audit.audit_log_list, name='company-audit-log'),
    path('api/tenant/export/products/', tenant_export.export_products_csv, name='company-export-products'),
    path('api/tenant/export/sales/', tenant_export.export_sales_csv, name='company-export-sales'),
    path('api/tenant/export/all/', tenant_export.export_all_json, name='company-export-all'),

    # Swagger API Hujjatlari
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]