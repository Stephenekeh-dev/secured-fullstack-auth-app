from django.urls import path
from .views import AdminRegistrationAPIView, AdminLoginAPIView, FailedLoginAttemptsDashboardAPIView

urlpatterns = [
    path('admin/register/', AdminRegistrationAPIView.as_view(), name='admin-register'),
    path('admin/login/', AdminLoginAPIView.as_view(), name='admin-login'),
    path('admin/failed-login-attempts/', FailedLoginAttemptsDashboardAPIView.as_view(), name='failed-login-attempts-dashboard'),
]
