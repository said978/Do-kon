from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    StockViewSet,
    import_products_excel,
    download_excel_template,
    products_management_view,
    cleanup_view,
    cleanup_duplicate_categories,
    cleanup_empty_categories,
    cleanup_no_stock_products,
    cleanup_full
)

# 1. Avval router obyektini yaratamiz va ViewSet'larni ro'yxatdan o'tkazamiz
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stocks', StockViewSet, basename='stock')

# 2. URL marshrutlarini belgilaymiz
urlpatterns = [
    path('import-excel/', import_products_excel, name='import_products_excel'),
    path('download-template/', download_excel_template, name='download_excel_template'),
    path('products-page/', products_management_view, name='products_management'),
    path('cleanup/', cleanup_view, name='cleanup_view'),
    path('cleanup/duplicate-categories/', cleanup_duplicate_categories, name='cleanup_duplicate_categories'),
    path('cleanup/empty-categories/', cleanup_empty_categories, name='cleanup_empty_categories'),
    path('cleanup/no-stock-products/', cleanup_no_stock_products, name='cleanup_no_stock_products'),
    path('cleanup/full/', cleanup_full, name='cleanup_full'),
    path('', include(router.urls)),  # Router har doim oxirida tursin
]