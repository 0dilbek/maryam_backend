from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    WarehouseViewSet, ExpenseCategoryViewSet, DailyReportViewSet, UserProfileView
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet)
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'reports', DailyReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
]
