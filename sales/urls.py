from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SaleViewSet,
    CustomerViewSet,
    DebtPaymentViewSet,
    pos_view,
    dashboard_view,
    customers_page_view,
    dashboard_stats,
    cashier_shift_report,
    export_sales_excel,
    get_current_user_info,
    reports_view,
    general_report_page_view,
    general_report_api,
    in_out_report_page_view,
    in_out_report_api,
    cash_flow_report_view,
    cash_flow_report_api,
    products_report_view,
    products_report_api,
    categories_report_view,
    categories_report_api,
    staff_report_view,
    customers_report_view,
    customer_turnover_report_view,
    suppliers_report_view,
    staff_turnover_report_view,
    payments_report_view,
    payments_report_api,
    product_sales_report_view, generate_barcode_image, print_barcode_view,
)

router = DefaultRouter()
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'debt-payments', DebtPaymentViewSet, basename='debt-payment')

urlpatterns = [
    path('', include(router.urls)),
    # Asosiy sahifalar va API
    path('pos/', pos_view, name='pos_interface'),
    path('dashboard/', dashboard_view, name='dashboard_interface'),
    path('customers-page/', customers_page_view, name='customers_page'),
    path('dashboard-stats/', dashboard_stats, name='dashboard_stats'),
    path('shift-report/', cashier_shift_report, name='shift_report'),
    path('export-excel/', export_sales_excel, name='export_sales_excel'),
    path('me/', get_current_user_info, name='current_user_info'),
    path('barcode-img/<str:code>/', generate_barcode_image, name='barcode_img'),
    path('print-barcode/<int:product_id>/', print_barcode_view, name='print_barcode'),

    # HTML Sahifalar
    path('reports/', reports_view, name='reports_page'),
    path('reports/general/', general_report_page_view, name='general_report_page'),
    path('reports/in-out/', in_out_report_page_view, name='in_out_report_page'),
    path('reports/cash-flow/', cash_flow_report_view, name='cash_flow_report'),
    path('reports/products/', products_report_view, name='products_report'),
    path('reports/categories/', categories_report_view, name='categories_report'),
    path('reports/staff/', staff_report_view, name='staff_report'),
    path('reports/customers/', customers_report_view, name='customers_report'),
    path('reports/customer-turnover/', customer_turnover_report_view, name='customer_turnover_report'),
    path('reports/suppliers/', suppliers_report_view, name='suppliers_report'),
    path('reports/staff-turnover/', staff_turnover_report_view, name='staff_turnover_report'),
    path('reports/payments/', payments_report_view, name='payments_report'),
    path('reports/product-sales/', product_sales_report_view, name='product_sales_report'),

    # API Data yo'llari
    path('reports/general-data/', general_report_api, name='general_report_api'),
    path('reports/in-out-data/', in_out_report_api, name='in_out_report_api'),
    path('reports/cash-flow-data/', cash_flow_report_api, name='cash_flow_report_api'),
    path('reports/products-data/', products_report_api, name='products_report_api'),
    path('reports/categories-data/', categories_report_api, name='categories_report_api'),
    path('reports/payments-data/', payments_report_api, name='payments_report_api'),

    # DRF Router API
    path('', include(router.urls)),
]