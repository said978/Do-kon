from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .super_admin import (
    CompanyAdminViewSet, CompanyStatsView,
    BranchAdminViewSet, UserAdminViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyAdminViewSet)
router.register(r'branches', BranchAdminViewSet)
router.register(r'users', UserAdminViewSet)

urlpatterns = [
    path('stats/', CompanyStatsView.as_view(), name='company-stats'),
    path('', include(router.urls)),
]
